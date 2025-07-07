"""
Data models and enums for the code review assistant.
"""

from datetime import datetime
from typing import List, Any
from dataclasses import dataclass
from core.coaching_models import CoachingState
from enum import Enum

class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class ChatMessage:
    role: MessageRole
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ReviewSession:
    original_code: str
    current_code: str
    goal: str
    conversation_history: List[ChatMessage]
    hint_level: int = 0
    is_active: bool = True
    code_history: List[str] = None  # Track all submitted code states
    coaching_state: CoachingState = None  # Will hold CoachingState instance

    def __post_init__(self):
        if self.code_history is None:
            self.code_history = []
        if self.coaching_state is None:
            self.coaching_state = CoachingState()
        print("DEBUG: coaching_state initialized:", self.coaching_state)