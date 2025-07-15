"""
Session utility functions for CodeClimbAI.
Extracted from session_manager.py for better modularity.
"""
import streamlit as st
from datetime import datetime
from .models import MessageRole, ChatMessage


def normalize_code(code: str) -> str:
    """Normalize code for comparison by removing extra whitespace and newlines."""
    if not code:
        return ""
    return '\n'.join(line.strip() for line in code.strip().split('\n') if line.strip())


def add_debug_message(message: str):
    """Add debug message directly to session state."""
    if 'debug_messages' not in st.session_state:
        st.session_state.debug_messages = []
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    debug_msg = f"[{timestamp}] {message}"
    st.session_state.debug_messages.append(debug_msg)
    
    # Keep only last 8 messages
    if len(st.session_state.debug_messages) > 8:
        st.session_state.debug_messages = st.session_state.debug_messages[-8:]


def add_message_to_session(session, role, content):
    """Add a message to session with proper role handling."""
    if session is None:
        return
        
    # Ensure we're using the enum
    if isinstance(role, str):
        role = MessageRole.USER if role.lower() in ['user', 'human'] else MessageRole.ASSISTANT
        
    message = ChatMessage(role, content)
    session.conversation_history.append(message)


def create_error_message(execution_result) -> str:
    """Create standardized error message for execution failures."""
    return f"""I tried to run your code and found an error that needs to be fixed first:

**Error:** {execution_result['error']}

**Traceback:**
```
{execution_result['traceback']}
```

{execution_result['fake_data_info'] if execution_result['fake_data_info'] else ''}

Let's fix this error before we optimize the code. Can you identify what's causing this issue and how to fix it?

Take a look at the error message and share your thoughts, or ask for a hint if you need guidance."""


def initialize_session_defaults():
    """Initialize default session state variables."""
    defaults = {
        'current_code': "",
        'session': None,
        'learning_log': [],
        'last_input_key': 0,
        'code_history': [],
        'original_session_code': "",
        'debug_messages': []
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    
    # Ensure current_code is always a string
    if not isinstance(st.session_state.current_code, str):
        st.session_state.current_code = ""
