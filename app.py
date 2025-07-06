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

def main():
    """Main application function."""
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
        "<h4 style='color: gray; font-weight: normal; margin-top: -10px;'>Don’t code faster — code better.</h4>",
        unsafe_allow_html=True
    )
    
    # Create three columns: Code (left), Chat (middle), Instructions (right)
    col1, col2, col3 = st.columns([1, 1, 0.6])
    
    # Left column - Code Input
    with col1:
        UIManager.render_code_input_panel()
    
    # Middle column - Claude Assistant
    with col2:
        UIManager.render_chat_panel(assistant)
    
    # Right column - Instructions (collapsible)
    with col3:
        UIManager.render_instructions_panel()

if __name__ == "__main__":
    main()