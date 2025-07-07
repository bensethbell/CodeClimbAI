import os
if os.getenv("STREAMLIT_DEBUG") == "1":
    import debugpy
    debugpy.listen(5678)            # pick any free port
    print("⏳ Waiting for VS Code to attach…")
    debugpy.wait_for_client()       # pause until the debugger connects
    debugpy.breakpoint()            # optionally drop into debugger immediately

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

def apply_safe_compact_styling():
    """Apply SAFE compact CSS styling - NO CODE BLOCK INTERFERENCE."""
    st.markdown("""
    <style>
        /* SAFE container reduction */
        .main .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 98% !important;
            margin: 0 auto !important;
        }
        
        /* SAFE title and header reduction */
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
        
        /* SAFE column spacing */
        .css-1r6slb0, .css-12oz5g7 {
            gap: 0.5rem !important;
        }
        
        /* SAFE element spacing reduction */
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
        
        /* REMOVED .stCode STYLING - LET STREAMLIT HANDLE CODE NATURALLY */
        /* This was causing the huge code blocks */
        
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
        
        /* Sidebar styling - collapsible from right */
        .css-1d391kg {
            padding-top: 0.5rem !important;
        }
        
        /* SAFE markdown list spacing */
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

def render_sidebar_instructions():
    """Render comprehensive instructions in the sidebar."""
    with st.sidebar:
        st.markdown("# 📖 Instructions & Help")
        
        # Quick Start section
        st.markdown("## 🚀 Quick Start")
        st.markdown("""
        1. **Type 'example'** in the chat to load sample code
        2. **Click '📤 Submit Code'** to begin learning
        3. **Answer the questions** Claude asks about your code
        4. **Make improvements** and resubmit to continue learning
        """)
        
        # How Claude Helps section
        st.markdown("## 🤖 How Claude Helps")
        st.markdown("""
        **Socratic Learning:** Claude asks questions to guide you to discoveries rather than just giving answers.
        
        **Adaptive Coaching:** Questions adjust based on your progress and understanding level.
        
        **Real Code Testing:** Your code is executed with generated test data to ensure it works.
        """)
        
        # During Sessions section  
        st.markdown("## 🎯 During Learning Sessions")
        st.markdown("""
        **Answer Questions:** Engage with Claude's questions about optimization opportunities
        
        **Ask for Hints:** Type 'hint' or click hint buttons when you're stuck
        
        **Submit Improvements:** Make changes to your code and resubmit to see how you're progressing
        
        **Explore Deeper:** Ask follow-up questions about concepts you're learning
        """)
        
        # Tips & Commands section
        st.markdown("## 💡 Tips & Commands")
        st.markdown("""
        **Chat Commands:**
        - `example` - Load sample code
        - `test` - Test your current code
        - `hint` - Get a helpful hint
        
        **Learning Tips:**
        - Try to answer questions before asking for hints
        - Experiment with small changes to see their impact
        - Don't worry about getting answers wrong - that's how you learn!
        """)
        
        # Debug info if available
        if hasattr(st.session_state, 'debug_messages') and st.session_state.debug_messages:
            with st.expander("🔧 Debug Info", expanded=False):
                st.markdown("**Latest activity:**")
                for debug_msg in st.session_state.debug_messages[-4:]:
                    st.text(debug_msg)
        
        # Learning log if available
        if hasattr(st.session_state, 'learning_log') and st.session_state.learning_log:
            with st.expander("📚 Learning Log", expanded=False):
                for i, entry in enumerate(st.session_state.learning_log, 1):
                    timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%m/%d %H:%M")
                    st.write(f"**{i}.** {entry['goal']} ({timestamp})")
        
        # Code history for current session
        if hasattr(st.session_state, 'code_history') and st.session_state.code_history and len(st.session_state.code_history) > 1:
            with st.expander(f"🔄 Code History ({len(st.session_state.code_history)} versions)", expanded=False):
                for i, code in enumerate(st.session_state.code_history, 1):
                    st.markdown(f"**Version {i}:**")
                    st.code(code[:60] + "..." if len(code) > 60 else code, language="python")
                    if i < len(st.session_state.code_history):
                        st.markdown("---")

def main():
    """Main application function."""
    if "editor_key" not in st.session_state:
        st.session_state.editor_key = 0
    if "current_code" not in st.session_state:
        st.session_state.current_code = ""
    
    # Apply SAFE compact styling - NO CODE INTERFERENCE
    apply_safe_compact_styling()
    
    # Initialize session state
    SessionManager.initialize_session_state()
    
    # Initialize API client and assistant
    try:
        api_client = ClaudeAPIClient(API_KEY)
        assistant = CodeReviewAssistant(api_client)
    except Exception as e:
        st.error(f"Failed to initialize assistant: {str(e)}")
        return
    
    # Render sidebar instructions
    render_sidebar_instructions()
    
    # Main UI
    st.title("🚀 CodeClimbAI")
    st.markdown(
        "<h4 style='color: gray; font-weight: normal; margin-top: -10px;'>Don't code faster — code better.</h4>",
        unsafe_allow_html=True
    )
    
    # Create TWO columns instead of three (no more Help panel)
    col1, col2 = st.columns([1, 1])
    
    # Left column - Code Input
    with col1:
        UIManager.render_code_input_panel()
    
    # Right column - Claude Assistant (no more Help panel)
    with col2:
        UIManager.render_chat_panel(assistant)
        # ─────────── DEBUG: Force a random example ───────────
        if st.button("🐞 Debug Random Example"):
            # This will _always_ call get_random_example()
            from templates.examples import ExampleGenerator

            # Exclude the first example so we get a truly random one
            code, category = ExampleGenerator.get_random_example(
                exclude_code=assistant.coach.first_example_code
            )

            # Show debug info in the UI
            st.markdown(f"**DEBUG** random‐example category: `{category}`")
            # NO CODE BLOCKS - just show as text
            st.text(code)

if __name__ == "__main__":
    main()