# ===== FIXED PANELS.PY =====

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

def _load_example_with_first_time_logic():
    """
    FIXED: Callback to load examples with proper first-time logic.
    First time = built-in example, subsequent times = random examples.
    """
    try:
        print("DEBUG: _load_example_with_first_time_logic called")
        
        # Check if this is the first time loading an example
        if 'first_example_loaded' not in st.session_state:
            st.session_state.first_example_loaded = False
        
        if not st.session_state.first_example_loaded:
            # FIRST TIME: Load the built-in example
            from templates.examples import get_example_code
            code = get_example_code()
            category = "performance"
            st.session_state.first_example_loaded = True
            print(f"DEBUG: Loading FIRST example (built-in): {code[:30]}...")
        else:
            # SUBSEQUENT TIMES: Load random examples
            from templates.examples import ExampleGenerator, get_example_code
            first_example = get_example_code()
            
            # Get random example excluding the first one
            code, category = ExampleGenerator.get_random_example(exclude_code=first_example)
            print(f"DEBUG: Loading RANDOM example from {category}: {code[:30]}...")
        
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
            
            if not st.session_state.first_example_loaded:
                message = f"✅ **First example loaded!** Main pandas optimization example is now in the editor. Click '📤 Submit Code' to begin learning!"
            else:
                message = f"🎲 **Random example loaded!** New {category} example is now in the editor. Click '📤 Submit Code' to analyze it!"
            
            add_message_to_session(
                st.session_state.session, 
                MessageRole.ASSISTANT, 
                message
            )
        
        print("DEBUG: _load_example_with_first_time_logic completed successfully")
        
    except Exception as e:
        print(f"ERROR in _load_example_with_first_time_logic: {str(e)}")
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
        
        # FIXED: Single example button with proper logic
        col1, col2 = st.columns([3, 1])
        
        with col2:
            # Check if first example has been loaded
            if 'first_example_loaded' not in st.session_state:
                st.session_state.first_example_loaded = False
            
            button_text = "📚 Get Example" if not st.session_state.first_example_loaded else "🎲 Random Example"
            button_help = "Load the main pandas example" if not st.session_state.first_example_loaded else "Load a different example for practice"
            
            if st.button(button_text, 
                        key="load_example_button", 
                        help=button_help,
                        use_container_width=True):
                _load_example_with_first_time_logic()
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
                placeholder="Click the 'Get Example' button above to load sample code, or paste your own code here..."
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
            "Click 'Get Example' for sample code, or paste your own code and click 'Submit Code' to start learning!"
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
                placeholder="Ask me anything about the code or optimization...",
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

# ===== FIXED HANDLERS.PY =====

def get_example_code():
    """Get the main pandas optimization example with proper imports."""
    return '''import pandas as pd

def add_metrics(df):
    results = []
    for idx, row in df.iterrows():
        results.append(row["price"] * 0.2 + row["tax"])
    df["total"] = results
    return df'''

class InputHandler:
    """Handles user input processing and special commands."""
    
    @staticmethod
    def handle_user_message(clean_input, assistant):
        """Handle user message processing."""
        try:
            from core.session_manager import add_debug_message
            add_debug_message(f"Processing input: {clean_input}")
            
            # Handle special commands - REMOVED 'example' command since we have button now
            if clean_input.lower() == "test" and st.session_state.session:
                InputHandler.handle_test_command()
            else:
                InputHandler.handle_regular_chat(clean_input, assistant)
            
        except Exception as e:
            st.error(f"Error processing message: {str(e)}")
            from core.session_manager import add_debug_message
            add_debug_message(f"❌ Error in handle_user_message: {str(e)}")
    
    @staticmethod
    def handle_test_command():
        """Handle the 'test' command."""
        try:
            from utils.execution import CodeExecutor
            from core.session_manager import add_message_to_session
            
            if st.session_state.session.current_code.strip():
                execution_result = CodeExecutor.execute_code_safely(st.session_state.session.current_code)
                    
                if execution_result['success']:
                    output_block = f"**Output:**\n```\n{execution_result['output']}\n```" if execution_result['output'] else ""
                    response = f"""✅ **Code executed successfully!**

                {execution_result['fake_data_info'] if execution_result['fake_data_info'] else ''}

                {output_block}

                Great! Your code runs without errors. Now let's focus on optimization."""
                else:
                    response = f"""❌ **Code execution failed:**

**Error:** {execution_result['error']}

**Traceback:**
```
{execution_result['traceback']}
```

{execution_result['fake_data_info'] if execution_result['fake_data_info'] else ''}

Let's fix this error first. Can you identify what's causing the issue?"""
                
                add_message_to_session(st.session_state.session, MessageRole.USER, "test")
                add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, response)
            else:
                add_message_to_session(st.session_state.session, MessageRole.USER, "test")
                add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, "No code to test! Please add some code first.")
        
        except Exception as e:
            st.error(f"Error in test command: {str(e)}")
            from core.session_manager import add_debug_message
            add_debug_message(f"❌ Error in handle_test_command: {str(e)}")
    
    @staticmethod
    def handle_regular_chat(clean_input, assistant):
        """Handle regular chat messages with adaptive coaching."""
        try:
            from core.session_manager import add_message_to_session
            
            if not st.session_state.session:
                from core.models import ReviewSession
                st.session_state.session = ReviewSession("", "", "", [])
            
            # Check if we're waiting for an answer to a coaching question
            if (hasattr(st.session_state.session, 'coaching_state') and 
                st.session_state.session.coaching_state and
                st.session_state.session.coaching_state.is_waiting_for_answer()):
                
                # Process the answer with adaptive coach
                from core.adaptive_coach import AdaptiveCoach
                from core.analyzer import CodeAnalyzer
                
                code_analyzer = CodeAnalyzer()
                adaptive_coach = AdaptiveCoach(code_analyzer)
                
                feedback = adaptive_coach.handle_user_answer(clean_input, st.session_state.session.coaching_state)
                add_message_to_session(st.session_state.session, MessageRole.USER, clean_input)
                add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, feedback)
                return
            
            add_message_to_session(st.session_state.session, MessageRole.USER, clean_input)
            
            # Generate response
            if st.session_state.session.is_active and st.session_state.session.goal:
                if "hint" in clean_input.lower():
                    st.session_state.session.hint_level += 1
                    if st.session_state.session.hint_level <= 3:
                        response = assistant.provide_hint(
                            st.session_state.session.current_code,
                            st.session_state.session.goal,
                            st.session_state.session.hint_level
                        )
                    else:
                        response = assistant.show_solution(st.session_state.session)
                else:
                    response = assistant.evaluate_response(st.session_state.session, clean_input)
            else:
                # General chat
                response = f"I'm here to help! {clean_input if len(clean_input) < 50 else 'Thanks for your message.'} To get started with code review, click the 'Get Example' button to load sample code or paste your own code in the left panel."
                
                # Add helpful commands
                if st.session_state.session and st.session_state.session.current_code.strip():
                    response += "\n\n💡 **Tip:** Type 'test' to run your current code and check for errors."
            
            add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, response)
            
        except Exception as e:
            st.error(f"Error in regular chat: {str(e)}")
            from core.session_manager import add_debug_message
            add_debug_message(f"❌ Error in handle_regular_chat: {str(e)}")