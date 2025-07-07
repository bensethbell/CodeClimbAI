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

def _load_debug_example():
    """
    FIXED: Callback to inject a random example into the code editor.
    Now properly excludes the first example and handles session state correctly.
    """
    try:
        print("DEBUG: _load_debug_example called")
        
        # Get the first example code for exclusion
        from templates.examples import get_example_code, ExampleGenerator
        first_example = get_example_code()
        
        # Also try to get it from adaptive coach if available
        exclude_code = first_example
        if (hasattr(st.session_state, 'session') and 
            st.session_state.session and
            hasattr(st.session_state.session, 'coaching_state') and
            st.session_state.session.coaching_state):
            
            # Try to get from session if available
            coaching_state = st.session_state.session.coaching_state
            if hasattr(coaching_state, 'first_example_code') and coaching_state.first_example_code:
                exclude_code = coaching_state.first_example_code
                print(f"DEBUG: Using first_example_code from coaching_state: {exclude_code[:30]}...")
        
        print(f"DEBUG: Excluding code: {exclude_code[:30]}...")
        
        # Get random example with proper exclusion
        code, category = ExampleGenerator.get_random_example(exclude_code=exclude_code)
        print(f"DEBUG: Got random example from {category}: {code[:30]}...")
        
        # Ensure session state is properly initialized
        if "current_code" not in st.session_state:
            st.session_state["current_code"] = ""
        if "editor_key" not in st.session_state:
            st.session_state["editor_key"] = 0
            
        # Update session state
        st.session_state.current_code = code
        st.session_state.editor_key += 1
        
        print(f"DEBUG: Updated session state - editor_key: {st.session_state.editor_key}")
        print(f"DEBUG: Current code set to: {st.session_state.current_code[:50]}...")
        
        # Add success message to chat if session exists
        if hasattr(st.session_state, 'session') and st.session_state.session:
            from core.session_manager import add_message_to_session
            add_message_to_session(
                st.session_state.session, 
                MessageRole.ASSISTANT, 
                f"🎲 **Random example loaded!** New {category} example is now in the editor. Click '📤 Submit Code' to analyze it!"
            )
        
        print("DEBUG: _load_debug_example completed successfully")
        
    except Exception as e:
        print(f"ERROR in _load_debug_example: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # Fallback: at least try to load something
        try:
            fallback_code = '''def simple_calculation(numbers):
    result = 0
    for num in numbers:
        result += num * 2
    return result'''
            
            st.session_state.current_code = fallback_code
            st.session_state.editor_key += 1
            print("DEBUG: Loaded fallback code")
        except:
            print("ERROR: Even fallback failed")

class PanelRenderer:
    """Handles rendering of main UI panels."""
    @staticmethod
    def render_code_input_panel():
        # ───── Initialize editor state ─────
        if "editor_key" not in st.session_state:
            st.session_state["editor_key"] = 0
        if "current_code" not in st.session_state:
            st.session_state["current_code"] = ""

        st.markdown("### 📝 Your Code")
        
        # ENHANCED: Random example button with better UX
        col1, col2 = st.columns([3, 1])
        
        with col2:
            if st.button("🎲 Random Example", 
                        key="load_random_example", 
                        help="Load a different example for practice",
                        use_container_width=True):
                _load_debug_example()
                st.rerun()

        # IDE-like code input area with dynamic key
        dynamic_key = f"code_editor_{st.session_state['editor_key']}"
        if ACE_AVAILABLE:
            code_input = st_ace(
                value=st.session_state["current_code"],
                key=dynamic_key,
                language='python',
                theme=CODE_EDITOR_THEME,
                height=CODE_EDITOR_HEIGHT,
                auto_update=True,
                tab_size=CODE_EDITOR_TAB_SIZE,
                wrap=False,
                font_size=CODE_EDITOR_FONT_SIZE,
                show_gutter=True,
                show_print_margin=True
            )
        else:
            st.info("💡 **For better code editing:** `pip install streamlit-ace` then restart")
            code_input = st.text_area(
                "Enter your code here:",
                value=st.session_state["current_code"],
                key=dynamic_key,
                height=CODE_EDITOR_HEIGHT,
                placeholder="Type 'example' in the chat to get sample code, or paste your own code here..."
            )

        # Persist editor contents back into session state
        if code_input != st.session_state["current_code"]:
            st.session_state["current_code"] = code_input

        # Submit button
        if st.button("📤 Submit Code", type="primary", use_container_width=True):
            SessionManager.handle_code_submission(code_input)

        PanelRenderer.render_getting_started_section()

    
    @staticmethod
    def render_getting_started_section():
        """Render the getting started instructions."""
        st.info(
            "Paste or write your code here, run it, or ask Claude for an example — and learn as you go!"
        )
    
    @staticmethod
    def render_chat_panel(assistant):
        """Render the middle panel for chat interface."""
        st.markdown("### 🤖 Claude Assistant")
        
        # Show current goal if session is active
        if st.session_state.session and st.session_state.session.is_active:
            st.info(f"🎯 **Primary Focus:** {st.session_state.session.goal}")
        
        # Conversation area with native Streamlit container and max height
        st.markdown("#### 💬 Conversation")
        
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
        st.markdown("#### 💭 Your Response")
        
        # Simple form without complex keys
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_area(
                "Type your message:",
                height=80,  # Reduced from 100 for compact styling
                placeholder="Type 'example' to get sample code, or ask me anything...",
                help="Press Ctrl+Enter to send"
            )
            submitted = st.form_submit_button("💬 Send", use_container_width=True)
        
        if submitted and user_input.strip():
            InputHandler.handle_user_message(user_input.strip(), assistant)
            print("DEBUG: st.rerun triggered")
            st.rerun()  # Immediately rerun to show the new message
            
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
        st.markdown("#### 🎯 Session Actions")
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
    # NOTE: render_instructions_panel() method REMOVED - now handled by sidebar