"""
Core business logic package for the code review assistant.
"""

from .models import MessageRole, ChatMessage, ReviewSession
from .analyzer import CodeAnalyzer, ClaudeAPIClient
from .assistant import CodeReviewAssistant
from .session_manager import SessionManager, add_debug_message, add_message_to_session

# For direct imports like "from core import ClaudeAPIClient"
__all__ = [
    'MessageRole', 
    'ChatMessage', 
    'ReviewSession',
    'CodeAnalyzer',
    'ClaudeAPIClient', 
    'CodeReviewAssistant',
    'SessionManager',
    'add_debug_message',
    'add_message_to_session'
]