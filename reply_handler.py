import re
from typing import Dict, Any

from models import ReplyRequest, ReplyResponse, ReplyAction, ConversationState

# Auto-reply patterns based on prompt
AUTO_REPLY_PATTERNS = [
    "thank you for contacting",
    "thanks for contacting",
    "we will get back to you",
    "our business hours",
    "currently unavailable",
    "away message",
    "auto reply",
    "automated response",
    "welcome to",
    "please wait",
    "we are closed",
    "will respond shortly",
    "our team will contact you"
]

POSITIVE_INTENT_PATTERNS = [
    "yes", "interested", "ok", "send", "do it", "start", 
    "join", "haan", "chalo", "sure", "proceed", "please share"
]

NEGATIVE_INTENT_PATTERNS = [
    "no", "stop", "not interested", "unsubscribe", 
    "don't message", "do not message", "band karo", "nahi"
]

def is_auto_reply(message: str) -> bool:
    msg_lower = message.lower()
    for pattern in AUTO_REPLY_PATTERNS:
        if pattern in msg_lower:
            return True
    return False

def detect_intent(message: str) -> str:
    msg_lower = message.lower().strip()
    # Exact match or starts with for simple words
    for p in POSITIVE_INTENT_PATTERNS:
        if p in msg_lower.split() or msg_lower.startswith(p):
            return "positive"
            
    for p in NEGATIVE_INTENT_PATTERNS:
        if p in msg_lower.split() or msg_lower.startswith(p):
            return "negative"
            
    if "?" in message:
        return "question"
        
    return "neutral"

def handle_reply(request: ReplyRequest, state: ConversationState) -> ReplyResponse:
    if is_auto_reply(request.message):
        return ReplyResponse(
            action=ReplyAction.wait,
            wait_seconds=3600,
            rationale="Detected WhatsApp Business auto-reply; backing off instead of wasting turns."
        )

    intent = detect_intent(request.message)

    if intent == "negative":
        return ReplyResponse(
            action=ReplyAction.end,
            rationale="Merchant declined or opted out."
        )

    if intent == "positive":
        # Example direct continuation
        return ReplyResponse(
            action=ReplyAction.send,
            body="Great! I've set that up for you. It will go live shortly.",
            cta="none",
            rationale="Merchant agreed. Proceeding with action without further qualification."
        )

    if intent == "question":
        return ReplyResponse(
            action=ReplyAction.send,
            body="I can certainly help with that. Is there anything specific you need clarified?",
            cta="open_ended",
            rationale="Merchant asked a question; answering contextually."
        )

    # Neutral fallback
    return ReplyResponse(
        action=ReplyAction.send,
        body="Understood. Let me know if you need anything else.",
        cta="open_ended",
        rationale="Neutral response."
    )

