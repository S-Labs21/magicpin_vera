from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# --- Context Models ---

class ContextScope(str, Enum):
    category = "category"
    merchant = "merchant"
    customer = "customer"
    trigger = "trigger"

class ContextPayload(BaseModel):
    scope: ContextScope
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: datetime

class ContextResponse(BaseModel):
    accepted: bool
    ack_id: Optional[str] = None
    stored_at: Optional[datetime] = None
    reason: Optional[str] = None
    current_version: Optional[int] = None

# --- Tick Models ---

class TickRequest(BaseModel):
    now: datetime
    available_triggers: List[str]

class ActionResponse(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    send_as: str  # "vera" or "merchant_on_behalf"
    trigger_id: str
    template_name: str
    template_params: List[str] = []
    body: str
    cta: str
    suppression_key: str
    rationale: str

class TickResponse(BaseModel):
    actions: List[ActionResponse]

# --- Reply Models ---

class FromRole(str, Enum):
    merchant = "merchant"
    customer = "customer"

class ReplyRequest(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    from_role: FromRole
    message: str
    received_at: datetime
    turn_number: int

class ReplyAction(str, Enum):
    send = "send"
    wait = "wait"
    end = "end"

class ReplyResponse(BaseModel):
    action: ReplyAction
    body: Optional[str] = None
    cta: Optional[str] = None
    wait_seconds: Optional[int] = None
    rationale: str

# --- Internal State Models ---

class ConversationState(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    trigger_id: str
    last_body: str
    turn_count: int
    status: str # "active", "ended", "waiting"
    created_at: datetime
    last_action: str
    suppression_key: str

