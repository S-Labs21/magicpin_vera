import os
import time
from datetime import datetime
import uuid
import logging
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from models import (
    ContextPayload, ContextResponse, TickRequest, TickResponse, 
    ActionResponse, ReplyRequest, ReplyResponse, ContextScope
)
from context_store import store
from dataset_loader import load_dataset
from composer import compose
from reply_handler import handle_reply

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Magicpin Vera Bot API")

# Add CORS for the frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up... loading dataset.")
    load_dataset("./dataset")

# --- v1 Endpoints ---

@app.get("/v1/healthz")
async def healthz():
    return {
        "status": "ok",
        "uptime_seconds": int(time.time() - START_TIME),
        "contexts_loaded": store.get_counts()
    }

@app.get("/v1/metadata")
async def metadata():
    return {
        "team_name": "Shakti Magicpin Vera Bot",
        "team_members": ["Shakti Labhaniya"],
        "model": "rule-based + optional LLM composer",
        "approach": "stateful FastAPI bot using 4-context composition, trigger prioritization, category-aware templates, multi-turn reply handling, and dashboard-driven endpoint testing",
        "contact_email": os.getenv("CONTACT_EMAIL", "your-email@example.com"),
        "version": "1.0.0",
        "submitted_at": datetime.utcnow().isoformat() + "Z"
    }

@app.post("/v1/context", response_model=ContextResponse)
async def submit_context(payload: ContextPayload):
    try:
        response = store.store_context(payload)
        if not response.accepted and response.reason == "stale_version":
            return JSONResponse(status_code=409, content=response.dict(exclude_none=True))
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1/tick", response_model=TickResponse)
async def process_tick(request: TickRequest):
    actions = []
    
    for trigger_id in request.available_triggers:
        trigger_context = store.get_context(ContextScope.trigger, trigger_id)
        if not trigger_context:
            logger.warning(f"Trigger {trigger_id} not found in store.")
            continue
            
        merchant_id = trigger_context.get("merchant_id") or trigger_context.get("payload", {}).get("merchant_id")
        if not merchant_id:
            logger.warning(f"Merchant ID not found for trigger {trigger_id}")
            continue
            
        merchant_context = store.get_context(ContextScope.merchant, merchant_id)
        if not merchant_context:
            logger.warning(f"Merchant {merchant_id} not found in store.")
            continue
            
        category_slug = merchant_context.get("category_slug")
        category_context = store.get_context(ContextScope.category, category_slug)
        if not category_context:
            logger.warning(f"Category {category_slug} not found in store.")
            continue
            
        customer_id = trigger_context.get("customer_id")
        customer_context = None
        if customer_id:
            customer_context = store.get_context(ContextScope.customer, customer_id)
            
        # Compose message
        try:
            composed = compose(category_context, merchant_context, trigger_context, customer_context)
            
            action = ActionResponse(
                conversation_id=f"conv_{uuid.uuid4().hex[:8]}",
                merchant_id=merchant_id,
                customer_id=customer_id,
                send_as=composed["send_as"],
                trigger_id=trigger_id,
                template_name=composed["template_name"],
                template_params=composed["template_params"],
                body=composed["body"],
                cta=composed["cta"],
                suppression_key=composed["suppression_key"],
                rationale=composed["rationale"]
            )
            actions.append(action)
        except Exception as e:
            logger.error(f"Error composing action for trigger {trigger_id}: {e}")
            
    return TickResponse(actions=actions)

@app.post("/v1/reply", response_model=ReplyResponse)
async def process_reply(request: ReplyRequest):
    # For a real implementation, we'd fetch the conversation state.
    # Here we mock a generic active state for the reply handler.
    # If state tracking is strictly needed across tick/reply,
    # we would retrieve it from store.conversations.
    
    state = store.get_conversation(request.conversation_id)
    # Even without explicit prior state, handle_reply can parse intent
    
    response = handle_reply(request, state)
    return response

# --- Debug Endpoints ---

@app.get("/debug/contexts")
async def debug_contexts_overview():
    return store.get_counts()

@app.get("/debug/contexts/{scope}")
async def debug_contexts_scope(scope: str):
    try:
        return store.get_all(scope)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/debug/contexts/{scope}/{context_id}")
async def debug_context_single(scope: str, context_id: str):
    try:
        ctx = store.get_context(scope, context_id)
        if not ctx:
            raise HTTPException(status_code=404, detail="Not found")
        return ctx
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

class ComposeDebugRequest(BaseModel):
    category_id: str
    merchant_id: str
    trigger_id: str
    customer_id: str | None = None

@app.post("/debug/compose")
async def debug_compose(request: ComposeDebugRequest):
    cat = store.get_context("category", request.category_id)
    merch = store.get_context("merchant", request.merchant_id)
    trig = store.get_context("trigger", request.trigger_id)
    
    if not (cat and merch and trig):
        raise HTTPException(status_code=404, detail="Missing required context")
        
    cust = None
    if request.customer_id:
        cust = store.get_context("customer", request.customer_id)
        
    return compose(cat, merch, trig, cust)

@app.get("/debug/triggers")
async def debug_triggers():
    triggers = store.get_all("trigger")
    return list(triggers.keys())

# --- Frontend Serving ---

frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")

@app.get("/")
@app.get("/dashboard")
async def serve_dashboard():
    index_file = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse(
        status_code=200,
        content={"message":"Magicpin Vera Bot API is running. Check endpoints '/v1/tick', '/v1/healthz', '/v1/metadata', '/v1/context', '/v1/reply', '/debug/*'"}
    )

# # Mount static files correctly so assets load
# if os.path.exists(frontend_dist):
#     app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

