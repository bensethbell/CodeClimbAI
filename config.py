# Configuration file for the Learn-as-You-Go Code Review Assistant
import streamlit as st

# Try to import streamlit-ace for code editor, fallback if not available
try:
    from streamlit_ace import st_ace
    ACE_AVAILABLE = True
except ImportError:
    ACE_AVAILABLE = False

# API Configuration
API_KEY = st.secrets["ANTHROPIC_API_KEY"]

# UI Configuration - Compact sizing
CHAT_CONTAINER_HEIGHT = 280  # Reduced from 350
CODE_EDITOR_HEIGHT = 320     # Reduced from 400
CODE_EDITOR_THEME = 'monokai'
CODE_EDITOR_FONT_SIZE = 13   # Reduced from 14
CODE_EDITOR_TAB_SIZE = 4

# Debug Configuration
MAX_DEBUG_MESSAGES = 5
MAX_CODE_PREVIEW_LENGTH = 80  # Reduced from 100