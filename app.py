import streamlit as st
from core import ClaudeAPIClient, CodeReviewAssistant, SessionManager
from ui import UIManager
from config import ACE_AVAILABLE, API_KEY

# Configure page
st.set_page_config(
    page_title="Learn-as-You-Go Code Review Assistant",
    page_icon="🔍",
    layout="wide"
)

def apply_compact_styling():
    """Apply compact CSS styling to make the UI more appropriately sized."""
    st.markdown("""
    <style>
        /* Main container adjustments */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            max-width: 98%;
        }
        
        /* Header and title styling */
        h1 {
            font-size: 2rem !important;
            margin-bottom: 0.5rem !important;
            margin-top: 0.5rem !important;
        }
        
        h2 {
            font-size: 1.3rem !important;
            margin-bottom: 0.5rem !important;
            margin-top: 0.5rem !important;
        }
        
        h3, h4 {
            font-size: 1.1rem !important;
            margin-bottom: 0.3rem !important;
            margin-top: 0.3rem !important;
        }
        
        /* Subtitle styling */
        .main h4 {
            color: gray;
            font-weight: normal;
            margin-top: -10px;
        }
        
        /* Text area and input styling */
        .stTextArea textarea {
            font-size: 13px !important;
            line-height: 1.3 !important;
        }
        
        .stTextInput input {
            font-size: 14px !important;
            height: 2.5rem !important;
        }
        
        /* Button styling */
        .stButton > button {
            height: 2.8rem !important;
            font-size: 14px !important;
            padding: 0.5rem 1rem !important;
        }
        
        /* Column spacing */
        .css-1r6slb0 {
            gap: 1rem !important;
        }
        
        /* Chat container adjustments */
        .stContainer {
            padding: 0.5rem !important;
        }
        
        /* Form styling */
        .stForm {
            border: none !important;
            padding: 0.5rem !important;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-size: 1rem !important;
            font-weight: 600 !important;
        }
        
        /* Info boxes */
        .stInfo {
            padding: 0.5rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .stSuccess {
            padding: 0.5rem !important;
            margin: 0.5rem 0 !important;
        }
        
        .stError {
            padding: 0.5rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Code blocks */
        .stCode {
            font-size: 12px !important;
        }
        
        /* Reduce excessive spacing */
        .element-container {
            margin-bottom: 0.5rem !important;
        }
        
        /* Chat message styling improvements */
        .chat-message {
            padding: 8px 12px !important;
            margin-bottom: 8px !important;
            border-radius: 12px !important;
            font-size: 14px !important;
            line-height: 1.4 !important;
        }
        
        /* Sidebar adjustments if used */
        .css-1d391kg {
            padding-top: 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main application function."""
    # Apply compact styling first
    apply_compact_styling()
    
    # Initialize session state
    SessionManager.initialize_session_state()
    
    # Initialize API client and assistant
    try:
        api_client = ClaudeAPIClient(API_KEY)
        assistant = CodeReviewAssistant(api_client)
    except Exception as e:
        st.error(f"Failed to initialize assistant: {str(e)}")
        return
    
    # Main UI
    st.title("🚀 CodeClimbAI")
    st.markdown(
        "<h4 style='color: gray; font-weight: normal; margin-top: -10px;'>Don't code faster — code better.</h4>",
        unsafe_allow_html=True
    )
    
    # Create three columns with better proportions for compact view
    col1, col2, col3 = st.columns([1, 1, 0.55])
    
    # Left column - Code Input
    with col1:
        UIManager.render_code_input_panel()
    
    # Middle column - Claude Assistant
    with col2:
        UIManager.render_chat_panel(assistant)
    
    # Right column - Instructions (more compact)
    with col3:
        UIManager.render_instructions_panel()

if __name__ == "__main__":
    main()