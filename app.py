import os
if os.getenv("STREAMLIT_DEBUG") == "1":
    import debugpy
    debugpy.listen(5678)
    print("⏳ Waiting for VS Code to attach…")
    debugpy.wait_for_client()
    debugpy.breakpoint()

import streamlit as st
from core import ClaudeAPIClient, CodeReviewAssistant, SessionManager
from ui import UIManager
from ui.welcome import WelcomeManager
from ui.sidebar import SidebarManager
from config import API_KEY

# Configure page
st.set_page_config(
    page_title="Learn-as-You-Go Code Review Assistant",
    page_icon="🔍",
    layout="wide"
)

def main():
    """Main application function."""
    # Initialize session state
    if "editor_key" not in st.session_state:
        st.session_state.editor_key = 0
    if "current_code" not in st.session_state:
        st.session_state.current_code = ""
    if "learning_started" not in st.session_state:
        st.session_state.learning_started = False
    
    SessionManager.initialize_session_state()
    
    # Initialize API client and assistant
    try:
        api_client = ClaudeAPIClient(API_KEY)
        assistant = CodeReviewAssistant(api_client)
    except Exception as e:
        st.error(f"Failed to initialize assistant: {str(e)}")
        return
    
    # Render sidebar instructions
    SidebarManager.render_sidebar_instructions()
    
    # Handle welcome flow
    welcome_shown = WelcomeManager.render_appropriate_welcome()
    
    # Main UI title
    st.title("🚀 CodeClimbAI")
    st.markdown(
        "<h4 style='color: gray; font-weight: normal; margin-top: -10px;'>Don't code faster — code better.</h4>",
        unsafe_allow_html=True
    )
    
    # Show main interface if learning started or welcome dismissed
    if st.session_state.get('learning_started', False) or st.session_state.get('welcome_popup_shown', False):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            UIManager.render_code_input_panel()
        
        with col2:
            UIManager.render_chat_panel(assistant)
    else:
        st.markdown("### 👆 Click the button above to start your learning journey!")
        st.info("💡 **Welcome!** Click 'Let's Start Learning!' to begin exploring code optimization with interactive guidance.")

if __name__ == "__main__":
    main()