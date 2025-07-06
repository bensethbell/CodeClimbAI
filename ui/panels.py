import streamlit as st
from datetime import datetime
from config import ACE_AVAILABLE, CODE_EDITOR_HEIGHT, CODE_EDITOR_THEME, CODE_EDITOR_FONT_SIZE, CODE_EDITOR_TAB_SIZE, CHAT_CONTAINER_HEIGHT
from .messages import MessageRenderer
from .handlers import InputHandler
from core.models import ChatMessage, MessageRole
from core.session_manager import SessionManager

# Import ace editor if available
if ACE_AVAILABLE:
    from streamlit_ace import st_ace

class PanelRenderer:
    """Handles rendering of main UI panels."""
    
    @staticmethod
    def render_code_input_panel():
        """Render the left panel for code input."""
        st.markdown("### 📝 Your Code")  # CHANGED: st.header() → st.markdown() for compact
        
        # IDE-like code input area
        if ACE_AVAILABLE:
            # Use proper code editor with syntax highlighting and tab support
            code_input = st_ace(
                value=st.session_state.current_code,
                language='python',
                theme=CODE_EDITOR_THEME,
                key="code_editor",
                height=CODE_EDITOR_HEIGHT,
                auto_update=True,
                tab_size=CODE_EDITOR_TAB_SIZE,
                wrap=False,
                font_size=CODE_EDITOR_FONT_SIZE,
                show_gutter=True,
                show_print_margin=True
            )
        else:
            # Fallback to enhanced text_area with better tab support
            st.info("💡 **For better code editing:** `pip install streamlit-ace` then restart the app")
            
            code_input = st.text_area(
                "Enter your code here:",
                value=st.session_state.current_code,
                height=CODE_EDITOR_HEIGHT,
                placeholder="Type 'example' in the chat to get sample code, or paste your own code here...",
                help="Install streamlit-ace for syntax highlighting and better tab support",
                key="main_code_input"
            )
        
        # Update current_code when user types
        if code_input != st.session_state.current_code:
            st.session_state.current_code = code_input
        
        # Buttons for code actions - single submit button
        if st.button("📤 Submit Code", type="primary", use_container_width=True):
            SessionManager.handle_code_submission(code_input)
        
        # Getting started instructions
        PanelRenderer.render_getting_started_section()
    
    @staticmethod
    def render_getting_started_section():
        """Render the getting started instructions."""
        # st.subheader("How To Use")
        
        # if ACE_AVAILABLE:
        #     st.success("✅ Code editor with syntax highlighting and proper tab indentation is active!")
        # else:
        #     st.info("💡 **Pro tip:** Install `streamlit-ace` for a better code editing experience with syntax highlighting!")
        #     st.markdown("**To install the enhanced code editor:**")
        #     st.code("pip install streamlit-ace", language="bash")
        
        st.info(
            "Paste or write your code here, run it, or ask Claude for an example — and learn as you go!"
        )
    
    @staticmethod
    def render_chat_panel(assistant):
        """Render the middle panel for chat interface."""
        st.markdown("### 🤖 Claude Assistant")  # CHANGED: st.header() → st.markdown() for compact
        
        # Show current goal if session is active
        if st.session_state.session and st.session_state.session.is_active:
            st.info(f"🎯 **Primary Focus:** {st.session_state.session.goal}")
        
        # Conversation area with native Streamlit container and max height
        st.markdown("#### 💬 Conversation")  # CHANGED: st.subheader() → st.markdown() for compact
        
        # Use native Streamlit container with height limit and auto-scroll
        with st.container(height=CHAT_CONTAINER_HEIGHT):
            # Show conversation in REVERSE order (newest first)
            if st.session_state.session and st.session_state.session.conversation_history:
                # Reverse the conversation history to show newest first
                reversed_messages = list(reversed(st.session_state.session.conversation_history))
                for message in reversed_messages:
                    MessageRenderer.render_chat_message(message)
            else:
                MessageRenderer.render_welcome_message()
        
        # User input area
        PanelRenderer.render_user_input_area(assistant)
        
        # Action buttons for active sessions
        if st.session_state.session and st.session_state.session.is_active:
            PanelRenderer.render_session_action_buttons(assistant)
    
    @staticmethod
    def render_user_input_area(assistant):
        """Render user input area and handle message submission."""
        st.markdown("#### 💭 Your Response")  # CHANGED: st.subheader() → st.markdown() for compact
        
        # Simple form without complex keys
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "Type your message:",
                height=80,  # CHANGED: height=100 → height=80 for compact
                placeholder="Type 'example' to get sample code, or ask me anything...",
                help="Press Ctrl+Enter to send"
            )
            submitted = st.form_submit_button("💬 Send", use_container_width=True)
        
        if submitted and user_input.strip():
            InputHandler.handle_user_message(user_input.strip(), assistant)
    
    @staticmethod
    def render_session_action_buttons(assistant):
        """Render action buttons for active sessions."""
        col2_1, col2_2 = st.columns(2)
        
        with col2_1:
            if st.button("💡 Need Hint"):
                try:
                    st.session_state.session.hint_level += 1
                    if st.session_state.session.hint_level <= 3:
                        hint = assistant.provide_hint(
                            st.session_state.session.current_code,
                            st.session_state.session.goal,
                            st.session_state.session.hint_level
                        )
                        response = f"**Hint Level {st.session_state.session.hint_level}:** {hint}"
                    else:
                        response = assistant.show_solution(st.session_state.session)
                    
                    st.session_state.session.conversation_history.append(
                        ChatMessage(MessageRole.ASSISTANT, response)
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"Error providing hint: {str(e)}")
        
        with col2_2:
            if st.button("🔄 Different Question"):
                try:
                    new_question = assistant.get_focused_question(
                        st.session_state.session.current_code,
                        st.session_state.session.goal
                    )
                    st.session_state.session.conversation_history.append(
                        ChatMessage(MessageRole.ASSISTANT, f"**Different approach:** {new_question}")
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"Error getting new question: {str(e)}")
        
        # Session control buttons
        st.markdown("#### 🎯 Session Actions")  # CHANGED: st.subheader() → st.markdown() for compact
        col2_4, col2_5 = st.columns(2)
        
        with col2_4:
            if st.button("✅ Show Solution"):
                try:
                    solution = assistant.show_solution(st.session_state.session)
                    st.session_state.session.conversation_history.append(
                        ChatMessage(MessageRole.ASSISTANT, f"**Solution:** {solution}")
                    )
                    
                    # Add to learning log (simplified)
                    log_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "goal": st.session_state.session.goal,
                        "hints_used": st.session_state.session.hint_level
                    }
                    st.session_state.learning_log.append(log_entry)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error showing solution: {str(e)}")
        
        with col2_5:
            if st.button("🆕 New Session"):
                SessionManager.reset_session()
                st.rerun()
    
    @staticmethod
    def render_instructions_panel():
        """Render the right panel with properly collapsible instructions."""
        st.markdown("### 📖 Help")  # CHANGED: st.header() → st.markdown() for compact
        
        # Quick tips always visible at top  
        st.markdown("**🚀 Quick Start:**")
        st.markdown("• Type **'example'** in chat")
        st.markdown("• Click **📤 Submit Code**")  
        st.markdown("• Follow my questions!")
        
        # Always show debug info at top for visibility
        if hasattr(st.session_state, 'debug_messages') and st.session_state.debug_messages:
            with st.expander("🔧 **Debug Info**", expanded=True):
                st.markdown("**Latest activity:**")
                for debug_msg in st.session_state.debug_messages[-4:]:  # KEPT: Show last 4 debug messages as original
                    st.text(debug_msg)
        
        # Compact collapsible detailed instructions
        with st.expander("📚 **Instructions**", expanded=False):
            st.markdown("""
            **🤖 How I Help:**
            I guide you to discover optimizations through questions.
            
            **Getting Started:**
            - Type "example" for sample code
            - Click "📤 Submit Code" to begin
            
            **During Sessions:**
            - Answer questions in chat
            - Modify code and resubmit  
            - Ask for hints if stuck
            """)
        
        # Learning log section (compact)
        if st.session_state.learning_log:
            with st.expander("📚 **Learning Log**", expanded=False):
                for i, entry in enumerate(st.session_state.learning_log, 1):
                    timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%m/%d %H:%M")
                    st.write(f"**{i}.** {entry['goal']} ({timestamp})")
        
        # Code history for current session (compact)
        if st.session_state.code_history and len(st.session_state.code_history) > 1:
            with st.expander(f"🔄 **Code History** ({len(st.session_state.code_history)} versions)", expanded=False):
                for i, code in enumerate(st.session_state.code_history, 1):
                    st.markdown(f"**Version {i}:**")
                    st.code(code[:80] + "..." if len(code) > 80 else code, language="python")  # KEPT: Original 80 chars
                    if i < len(st.session_state.code_history):
                        st.markdown("---")