from typing import Dict, Any, Optional
from datetime import datetime
import uuid
import logging

from models import ContextPayload, ContextResponse, ContextScope, ConversationState

logger = logging.getLogger(__name__)

class ContextStore:
    def __init__(self):
        self.categories: Dict[str, Dict[str, Any]] = {}
        self.merchants: Dict[str, Dict[str, Any]] = {}
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.triggers: Dict[str, Dict[str, Any]] = {}
        self.conversations: Dict[str, ConversationState] = {}
        
        # Keep track of version for each (scope, context_id)
        # Key: "scope:context_id", Value: (version, stored_at)
        self.versions: Dict[str, tuple[int, datetime]] = {}

    def get_counts(self) -> Dict[str, int]:
        return {
            "category": len(self.categories),
            "merchant": len(self.merchants),
            "customer": len(self.customers),
            "trigger": len(self.triggers)
        }

    def store_context(self, payload: ContextPayload) -> ContextResponse:
        key = f"{payload.scope.value}:{payload.context_id}"
        current_version = -1
        
        if key in self.versions:
            current_version, _ = self.versions[key]
            
        if payload.version == current_version:
            # Idempotent no-op
            return ContextResponse(
                accepted=True,
                ack_id=f"ack_noop_{uuid.uuid4().hex[:8]}",
                stored_at=datetime.utcnow()
            )
            
        if payload.version < current_version:
            return ContextResponse(
                accepted=False,
                reason="stale_version",
                current_version=current_version
            )
            
        # Store or replace
        target_dict = self._get_dict_for_scope(payload.scope)
        target_dict[payload.context_id] = payload.payload
        self.versions[key] = (payload.version, datetime.utcnow())
        
        return ContextResponse(
            accepted=True,
            ack_id=f"ack_{uuid.uuid4().hex[:8]}",
            stored_at=datetime.utcnow()
        )

    def get_context(self, scope: str, context_id: str) -> Optional[Dict[str, Any]]:
        target_dict = self._get_dict_for_scope(ContextScope(scope))
        return target_dict.get(context_id)

    def get_all(self, scope: str) -> Dict[str, Any]:
        return self._get_dict_for_scope(ContextScope(scope))

    def _get_dict_for_scope(self, scope: ContextScope) -> Dict[str, Any]:
        if scope == ContextScope.category:
            return self.categories
        elif scope == ContextScope.merchant:
            return self.merchants
        elif scope == ContextScope.customer:
            return self.customers
        elif scope == ContextScope.trigger:
            return self.triggers
        raise ValueError(f"Unknown scope: {scope}")

    def save_conversation(self, state: ConversationState):
        self.conversations[state.conversation_id] = state

    def get_conversation(self, conversation_id: str) -> Optional[ConversationState]:
        return self.conversations.get(conversation_id)

# Singleton instance
store = ContextStore()
