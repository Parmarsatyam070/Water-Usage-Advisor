"""
Smart Water Usage Advisor - Conversation Session Manager
Location: 5_AI_COMPONENTS/chatbot/conversation_manager.py
Phase 3C - Week 6 Implementation

Manages multi-turn conversation state, session tracking, dialogue history,
and persistence to the authoritative `chatbot_conversations` PostgreSQL table.
"""

import os
import sys
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class ConversationTurn:
    """Represents a single conversational turn."""
    turn_number: int
    user_message: str
    chatbot_response: str
    intent_detected: Optional[str] = None
    confidence_score: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    was_helpful: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConversationSessionManager:
    """
    In-memory multi-turn session manager with optional database persistence
    to the authoritative `chatbot_conversations` table.
    """

    def __init__(self, max_history_turns: int = 5, db_engine: Optional[Any] = None):
        self.max_history_turns = max_history_turns
        self.sessions: Dict[str, List[ConversationTurn]] = {}
        self.db_engine = db_engine
        if self.db_engine is None:
            self._try_init_db_engine()

    def _try_init_db_engine(self):
        """Attempts to load database engine from backend db_config if available."""
        try:
            db_mod_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "4_DEVELOPMENT", "backend", "database")
            )
            if db_mod_dir not in sys.path:
                sys.path.append(db_mod_dir)
            from db_config import create_db_engine
            self.db_engine = create_db_engine()
        except Exception:
            self.db_engine = None

    def create_session(self, user_id: int = 1) -> str:
        """Generates a new unique session identifier."""
        session_id = f"sess-{user_id}-{uuid.uuid4().hex[:8]}"
        self.sessions[session_id] = []
        return session_id

    def record_turn(
        self,
        session_id: str,
        user_message: str,
        chatbot_response: str,
        user_id: int = 1,
        intent_detected: Optional[str] = None,
        confidence_score: Optional[float] = 0.95
    ) -> ConversationTurn:
        """
        Records a completed interaction turn into the session and optionally persists to database.
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        turn_num = len(self.sessions[session_id]) + 1
        turn = ConversationTurn(
            turn_number=turn_num,
            user_message=user_message,
            chatbot_response=chatbot_response,
            intent_detected=intent_detected,
            confidence_score=confidence_score,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        self.sessions[session_id].append(turn)

        # Persist to database if engine is available
        self._persist_to_database(user_id, session_id, turn)
        return turn

    def get_history_for_prompt(self, session_id: str) -> List[Dict[str, str]]:
        """Returns dialogue history formatted for prompt injection."""
        turns = self.sessions.get(session_id, [])
        recent_turns = turns[-self.max_history_turns:]
        return [
            {"user": t.user_message, "assistant": t.chatbot_response}
            for t in recent_turns
        ]

    def get_session_turns(self, session_id: str) -> List[ConversationTurn]:
        """Returns all turns recorded in a session."""
        return list(self.sessions.get(session_id, []))

    def _persist_to_database(self, user_id: int, session_id: str, turn: ConversationTurn):
        """Safely persists turn into chatbot_conversations table."""
        if not self.db_engine:
            return

        try:
            from sqlalchemy import text
            with self.db_engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO chatbot_conversations (
                        user_id, session_id, turn_number, user_message, chatbot_response,
                        intent_detected, confidence_score, timestamp
                    ) VALUES (
                        :uid, :sid, :tnum, :umsg, :cresp, :intent, :conf, :ts
                    )
                """), {
                    "uid": user_id,
                    "sid": session_id,
                    "tnum": turn.turn_number,
                    "umsg": turn.user_message,
                    "cresp": turn.chatbot_response,
                    "intent": turn.intent_detected,
                    "conf": turn.confidence_score,
                    "ts": turn.timestamp
                })
        except Exception as e:
            # Non-blocking: conversation state continues in-memory without crash
            pass
