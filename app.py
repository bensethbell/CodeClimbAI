import os
if os.getenv("STREAMLIT_DEBUG") == "1":
    import debugpy
    debugpy.listen(5678)
    print("⏳ Waiting for VS Code to attach…")
    debugpy.wait_for_client()
    debugpy.breakpoint()

import streamlit as st
from datetime import datetime
from core import ClaudeAPIClient, CodeReviewAssistant, SessionManager
from ui import UIManager
from config import ACE_AVAILABLE, API_KEY

# Configure page
st.set_page_config(
    page_title="Learn-as-You-Go Code Review Assistant",
    page_icon="🔍",
    layout="wide"
)

def should_show_welcome_popup():
    """Determine if we should show the welcome popup."""
    # Check if user has seen welcome popup before
    if 'welcome_popup_shown' not in st.session_state:
        st.session_state.welcome_popup_shown = False
    
    # Check if user has any activity (conversation history or code submissions)
    has_activity = (
        (hasattr(st.session_state, 'session') and 
         st.session_state.session and 
         len(st.session_state.session.conversation_history) > 0) or
        (hasattr(st.session_state, 'code_history') and 
         st.session_state.code_history and 
         len(st.session_state.code_history) > 0)
    )
    
    # Show popup if not shown before AND no activity
    return not st.session_state.welcome_popup_shown and not has_activity

def create_welcome_popup():
    """Create an engaging welcome popup for new users."""
    welcome_content = """
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    ">
        <h1 style="margin: 0 0 16px 0; font-size: 2.2rem;">🚀 Welcome to CodeClimbAI!</h1>
        
        <p style="font-size: 1.1rem; margin: 16px 0; opacity: 0.95;">
            <strong>Learn by discovery, not by memorization.</strong>
        </p>
        
        <div style="
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 16px;
            margin: 20px 0;
            text-align: left;
        ">
            <h3 style="margin: 0 0 12px 0; color: #fff;">🧠 Our Philosophy:</h3>
            <ul style="margin: 0; padding-left: 20px; line-height: 1.6;">
                <li><strong>Questions over answers</strong> - We guide you to insights through Socratic questioning</li>
                <li><strong>Practice with real code</strong> - No theoretical examples, work with actual optimization problems</li>
                <li><strong>Adaptive learning</strong> - Questions adjust to your skill level and progress</li>
                <li><strong>Safe exploration</strong> - Experiment freely with code execution in a protected environment</li>
            </ul>
        </div>
        
        <div style="
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 16px;
            margin: 20px 0;
        ">
            <h3 style="margin: 0 0 12px 0; color: #fff;">🎯 Ready to start?</h3>
            <p style="margin: 0 0 8px 0; font-size: 1rem;">
                <strong>Option 1:</strong> Click <strong>"Generate Example"</strong> button in the left panel to load sample code
            </p>
            <p style="margin: 0; font-size: 1rem;">
                <strong>Option 2:</strong> Paste your own Python code in the left editor and click "📤 Submit Code"
            </p>
        </div>
        
        <p style="font-size: 0.9rem; margin: 16px 0 0 0; opacity: 0.8;">
            💡 <em>Remember: There are no wrong answers, only learning opportunities!</em>
        </p>
    </div>
    """
    return welcome_content

def create_simple_welcome_popup():
    """Create a Streamlit-compatible welcome popup using native components."""
    # Use container for better visual grouping
    with st.container():
        st.success("🚀 **Welcome to CodeClimbAI!**")
        
        st.markdown("""
        ### Learn by discovery, not by memorization.
        
        **🧠 Our Philosophy:**
        - **Questions over answers** - We guide you to insights through Socratic questioning
        - **Practice with real code** - No theoretical examples, work with actual optimization problems  
        - **Adaptive learning** - Questions adjust to your skill level and progress
        - **Safe exploration** - Experiment freely with code execution in a protected environment
        
        **🎯 Ready to start?**
        - **Option 1:** Click the **"Generate Example"** button in the left panel to load sample code
        - **Option 2:** Paste your own Python code in the left editor and click "📤 Submit Code"
        
        💡 *Remember: There are no wrong answers, only learning opportunities!*
        """)

def create_compact_welcome_banner():
    """Create a more compact welcome banner for returning users."""
    banner_html = """
    <div style="
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
    ">
        <h3 style="margin: 0; font-size: 1.2rem;">🚀 CodeClimbAI - Learn by Discovery</h3>
        <p style="margin: 4px 0 0 0; font-size: 0.9rem; opacity: 0.9;">
            Click <strong>"Generate Example"</strong> for sample code or paste your own code to begin learning!
        </p>
    </div>
    """
    return banner_html

def create_compact_welcome_banner_streamlit():
    """Create a more compact welcome banner for returning users using Streamlit native."""
    st.info("🚀 **CodeClimbAI** - Click 'Generate Example' for sample code or paste your own code to begin learning!")

def render_welcome_popup():
    """Render the welcome popup if appropriate."""
    if should_show_welcome_popup():
        # Use ONLY Streamlit native approach - no HTML to avoid rendering issues
        create_simple_welcome_popup()
        
        # Create dismissal mechanism
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("✨ Let's Start Learning!", type="primary", use_container_width=True):
                st.session_state.welcome_popup_shown = True
                st.rerun()
        
        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        return True  # Popup was shown
    
    return False  # Popup was not shown

def render_appropriate_welcome():
    """Render the appropriate welcome message based on user status."""
    # For completely new users - show full popup
    if should_show_welcome_popup():
        return render_welcome_popup()
    
    # For users who dismissed popup but have minimal activity - show compact banner
    elif (hasattr(st.session_state, 'welcome_popup_shown') and 
          st.session_state.welcome_popup_shown and
          (not hasattr(st.session_state, 'session') or 
           not st.session_state.session or
           len(st.session_state.session.conversation_history) < 3)):
        
        # Use ONLY Streamlit native approach - no HTML to avoid rendering issues
        create_compact_welcome_banner_streamlit()
        
        return True
    
    return False

def apply_improved_compact_styling():
    """Apply IMPROVED compact CSS styling with much better MCQ formatting."""
    st.markdown("""
    <style>
        /* CONTAINER IMPROVEMENTS */
        .main .block-container {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            max-width: 98% !important;
            margin: 0 auto !important;
        }
        
        /* CHAT MESSAGE IMPROVEMENTS */
        div[style*="background-color: #e3f2fd"], 
        div[style*="background-color: #e8f5e8"] {
            padding: 6px 10px !important;
            margin-bottom: 4px !important;
            border-radius: 10px !important;
            font-size: 13px !important;
            line-height: 1.2 !important;
        }
        
        /* MCQ SPECIFIC IMPROVEMENTS - CRITICAL FIX FOR SPACING */
        .mcq-options {
            margin: 4px 0 !important;
            padding: 0 !important;
        }
        
        .mcq-option {
            margin: 1px 0 !important;
            padding: 2px 6px !important;
            background-color: #f8f9fa !important;
            border-radius: 4px !important;
            border-left: 2px solid #007bff !important;
            font-size: 12px !important;
            line-height: 1.1 !important;
            display: block !important;
        }
        
        .mcq-option:hover {
            background-color: #e9ecef !important;
        }
        
        /* TIGHT SPACING FOR QUESTION ELEMENTS */
        .question-title {
            margin: 2px 0 4px 0 !important;
            font-size: 14px !important;
            font-weight: bold !important;
        }
        
        .question-text {
            margin: 2px 0 4px 0 !important;
            font-size: 13px !important;
            line-height: 1.2 !important;
        }
        
        .response-instructions {
            margin: 2px 0 1px 0 !important;
            font-size: 11px !important;
            font-style: italic !important;
            color: #666 !important;
            background-color: #f1f3f4 !important;
            padding: 2px 4px !important;
            border-radius: 3px !important;
        }
        
        /* REMOVE EXCESSIVE STREAMLIT SPACING */
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.05rem !important;
        }
        
        div[data-testid="column"] {
            padding: 0.1rem !important;
        }
        
        /* MARKDOWN IMPROVEMENTS */
        .main p {
            margin: 0.1rem 0 !important;
        }
        
        .main ul, .main ol {
            margin: 0.1rem 0 !important;
            padding-left: 0.8rem !important;
        }
        
        .main li {
            margin: 0.05rem 0 !important;
        }
        
        /* BUTTON IMPROVEMENTS */
        .stButton > button {
            height: 2rem !important;
            font-size: 12px !important;
            padding: 0.1rem 0.5rem !important;
            margin: 0.05rem 0 !important;
        }
        
        /* TEXT AREA IMPROVEMENTS */
        .stTextArea textarea {
            font-size: 12px !important;
            line-height: 1.1 !important;
            padding: 0.3rem !important;
        }
        
        /* FORM IMPROVEMENTS */
        .stForm {
            border: none !important;
            padding: 0.1rem !important;
            margin: 0.05rem 0 !important;
        }
        
        /* INFO BOX IMPROVEMENTS */
        .stInfo, .stSuccess, .stError, .stWarning {
            padding: 0.2rem !important;
            margin: 0.1rem 0 !important;
            font-size: 12px !important;
        }
        
        /* HEADER IMPROVEMENTS */
        .main h1 {
            font-size: 1.4rem !important;
            margin-bottom: 0.05rem !important;
            margin-top: 0.05rem !important;
        }
        
        .main h2, .main h3, .main h4 {
            font-size: 0.9rem !important;
            margin-bottom: 0.1rem !important;
            margin-top: 0.1rem !important;
        }
        
        /* STRONG TEXT IMPROVEMENTS */
        strong {
            font-weight: 600 !important;
        }
        
        /* ELEMENT CONTAINER IMPROVEMENTS */
        .element-container {
            margin-bottom: 0.05rem !important;
        }
        
        /* EXPANDER IMPROVEMENTS */
        .streamlit-expanderHeader {
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            padding: 0.2rem !important;
        }
        
        .streamlit-expanderContent {
            padding: 0.2rem !important;
        }
        
        /* SPECIFIC STREAMLIT SPACING FIXES */
        .css-1r6slb0, .css-12oz5g7 {
            gap: 0.2rem !important;
        }
        
        .css-1544g2n, .css-1d391kg, .css-18e3th9 {
            padding: 0.1rem !important;
        }
        
        /* FINAL OVERRIDE FOR REMAINING SPACING */
        .main > div {
            gap: 0.1rem !important;
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
        1. **Click "Generate Example"** in the left panel to load sample code
        2. **Click "📤 Submit Code"** to begin learning
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
def render_sidebar_instructions():
    """Render comprehensive instructions in the sidebar."""
    with st.sidebar:
        st.markdown("# 📖 Instructions & Help")
        
        # Quick Start section
        st.markdown("## 🚀 Quick Start")
        st.markdown("""
        1. **Click "Generate Example"** in the left panel to load sample code
        2. **Click "📤 Submit Code"** to begin learning
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
        **UI Actions:**
        - Click "Generate Example" - Load sample code
        - Type 'test' - Test your current code
        - Type 'hint' - Get a helpful hint
        
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
        
        # CRITICAL DEBUG: Show what example code is being generated
        if hasattr(st.session_state, 'current_code') and st.session_state.current_code:
            with st.expander("🐛 Example Debug Info", expanded=False):
                st.markdown("**Current Code Preview:**")
                preview = st.session_state.current_code[:100] + "..." if len(st.session_state.current_code) > 100 else st.session_state.current_code
                st.code(preview, language="python")
                
                # Check for optimization issues
                has_iterrows = 'iterrows' in st.session_state.current_code.lower()
                has_string_concat = '+=' in st.session_state.current_code
                has_nested_loops = st.session_state.current_code.count('for ') > 1
                
                st.markdown("**Issue Detection:**")
                st.write(f"❌ Has iterrows(): {has_iterrows}")
                st.write(f"❌ Has string concat: {has_string_concat}")  
                st.write(f"❌ Has nested loops: {has_nested_loops}")
                
                if not (has_iterrows or has_string_concat or has_nested_loops):
                    st.error("🚨 NO ISSUES DETECTED - Example appears optimized!")
                else:
                    st.success("✅ Learning issues detected in code")

def main():
    """Main application function."""
    if "editor_key" not in st.session_state:
        st.session_state.editor_key = 0
    if "current_code" not in st.session_state:
        st.session_state.current_code = ""
    if "learning_started" not in st.session_state:  # NEW: Track learning state
        st.session_state.learning_started = False
    
    # Apply IMPROVED compact styling with MCQ fixes
    apply_improved_compact_styling()
    
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
    
    # RENDER WELCOME POPUP/BANNER FIRST (before main UI)
    welcome_shown = render_appropriate_welcome()
    
    # Main UI title (always show)
    st.title("🚀 CodeClimbAI")
    st.markdown(
        "<h4 style='color: gray; font-weight: normal; margin-top: -10px;'>Don't code faster — code better.</h4>",
        unsafe_allow_html=True
    )
    
    # CONDITIONAL UI: Only show main interface if learning has started OR welcome popup dismissed
    if st.session_state.get('learning_started', False) or st.session_state.get('welcome_popup_shown', False):
        # Create TWO columns
        col1, col2 = st.columns([1, 1])
        
        # Left column - Code Input
        with col1:
            UIManager.render_code_input_panel()
        
        # Right column - Claude Assistant
        with col2:
            UIManager.render_chat_panel(assistant)
    else:
        # Show minimal interface until user starts learning
        st.markdown("### 👆 Click the button above to start your learning journey!")
        st.info("💡 **Welcome!** Click 'Let's Start Learning!' to begin exploring code optimization with interactive guidance.")

if __name__ == "__main__":
    main()