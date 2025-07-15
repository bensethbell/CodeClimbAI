"""
Streamlined session state and lifecycle management for CodeClimbAI.
REFACTORED: Main orchestrator delegating to specialized modules.
"""
import streamlit as st
from .coaching_integration import CoachingIntegration
from .session_utils import add_debug_message, initialize_session_defaults
from .session_handlers import SessionHandlers

# Re-export commonly used utilities for backwards compatibility
from .session_utils import add_message_to_session, normalize_code


class SessionManager:
    """Main session manager - orchestrates session lifecycle and delegates to specialized handlers."""
    
    @staticmethod
    def initialize_session_state():
        """Initialize all session state variables."""
        initialize_session_defaults()
        add_debug_message("Session state initialized")
    
    @staticmethod    
    def start_new_session(code: str, assistant):
        """Start a new review session - delegates to SessionHandlers."""
        return SessionHandlers.start_new_session(code, assistant)
    
    @staticmethod
    def handle_code_submission(code_input):
        """Handle code submission - delegates to SessionHandlers."""
        return SessionHandlers.handle_code_submission(code_input)
    
    @staticmethod
    def reset_session():
        """Reset session state for new session."""
        st.session_state.session = None
        st.session_state.current_code = ""
        st.session_state.code_history = []
        st.session_state.original_session_code = ""
        st.session_state.debug_messages = []
        
        # Reset coaching state
        CoachingIntegration.reset_coaching_state()
        add_debug_message("Session reset completed")


# Backwards compatibility - expose the static methods at module level
def initialize_session_state():
    """Backwards compatibility wrapper."""
    return SessionManager.initialize_session_state()

def start_new_session(code: str, assistant):
    """Backwards compatibility wrapper.""" 
    return SessionManager.start_new_session(code, assistant)

def handle_code_submission(code_input):
    """Backwards compatibility wrapper."""
    return SessionManager.handle_code_submission(code_input)

def reset_session():
    """Backwards compatibility wrapper."""
    return SessionManager.reset_session()