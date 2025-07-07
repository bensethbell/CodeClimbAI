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

def apply_aggressive_compact_styling():
    """Apply very aggressive compact CSS styling to match local appearance."""
    st.markdown("""
    <style>
        /* AGGRESSIVE container reduction */
        .main .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 98% !important;
            margin: 0 auto !important;
        }
        
        /* AGGRESSIVE title and header reduction */
        .main h1 {
            font-size: 1.8rem !important;
            margin-bottom: 0.2rem !important;
            margin-top: 0.2rem !important;
            padding: 0 !important;
        }
        
        .main h2, .main h3, .main h4 {
            font-size: 1.1rem !important;
            margin-bottom: 0.3rem !important;
            margin-top: 0.3rem !important;
            padding: 0 !important;
        }
        
        /* Subtitle compact */
        .main h4[style*="color: gray"] {
            margin-top: -0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* AGGRESSIVE column spacing */
        .css-1r6slb0, .css-12oz5g7 {
            gap: 0.5rem !important;
        }
        
        /* AGGRESSIVE element spacing reduction */
        .element-container {
            margin-bottom: 0.2rem !important;
        }
        
        /* Text inputs and areas - more compact */
        .stTextArea textarea {
            font-size: 12px !important;
            line-height: 1.2 !important;
            padding: 0.4rem !important;
        }
        
        .stTextInput input {
            font-size: 13px !important;
            height: 2.2rem !important;
            padding: 0.3rem !important;
        }
        
        /* Buttons - more compact */
        .stButton > button {
            height: 2.4rem !important;
            font-size: 13px !important;
            padding: 0.3rem 0.8rem !important;
            margin: 0.2rem 0 !important;
        }
        
        /* Forms - reduce padding */
        .stForm {
            border: none !important;
            padding: 0.3rem !important;
            margin: 0.2rem 0 !important;
        }
        
        /* Info boxes - much more compact */
        .stInfo, .stSuccess, .stError, .stWarning {
            padding: 0.4rem !important;
            margin: 0.3rem 0 !important;
        }
        
        /* Expanders - more compact */
        .streamlit-expanderHeader {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            padding: 0.3rem !important;
        }
        
        .streamlit-expanderContent {
            padding: 0.4rem !important;
        }
        
        /* Container heights - more compact */
        .stContainer {
            padding: 0.3rem !important;
        }
        
        /* Markdown spacing - very tight */
        .main .markdown-text-container {
            margin-bottom: 0.2rem !important;
        }
        
        /* Code blocks - more compact */
        .stCode {
            font-size: 11px !important;
            margin: 0.2rem 0 !important;
        }
        
        /* Remove excessive spacing from specific Streamlit elements */
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.2rem !important;
        }
        
        div[data-testid="column"] {
            padding: 0.2rem !important;
        }
        
        /* Chat message styling - more compact */
        .chat-message {
            padding: 6px 10px !important;
            margin-bottom: 6px !important;
            border-radius: 10px !important;
            font-size: 13px !important;
            line-height: 1.3 !important;
        }
        
        /* Sidebar adjustments if used */
        .css-1d391kg {
            padding-top: 0.5rem !important;
        }
        
        /* AGGRESSIVE markdown list spacing */
        .main ul, .main ol {
            margin: 0.2rem 0 !important;
            padding-left: 1rem !important;
        }
        
        .main li {
            margin: 0.1rem 0 !important;
        }
        
        /* Target specific streamlit spacing classes */
        .css-1544g2n, .css-1d391kg, .css-18e3th9 {
            padding: 0.2rem !important;
        }
        
        /* Final override for any remaining spacing */
        .main > div {
            gap: 0.3rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Main application function."""
    # Apply aggressive compact styling first
    apply_aggressive_compact_styling()
    
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
    
    # Create three columns with tighter proportions
    col1, col2, col3 = st.columns([1, 1, 0.5])
    
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