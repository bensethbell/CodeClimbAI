import streamlit as st
from datetime import datetime
from core.models import MessageRole, ChatMessage, ReviewSession
from utils.execution import CodeExecutor
from core.session_manager import add_message_to_session, add_debug_message

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
            add_debug_message(f"Processing input: {clean_input}")
            
            # Handle special commands
            if clean_input.lower() == "example":
                InputHandler.handle_example_command()
            elif clean_input.lower() == "test" and st.session_state.session:
                InputHandler.handle_test_command()
            else:
                InputHandler.handle_regular_chat(clean_input, assistant)
            
        except Exception as e:
            st.error(f"Error processing message: {str(e)}")
            add_debug_message(f"❌ Error in handle_user_message: {str(e)}")
    
    @staticmethod
    def handle_example_command():
        """Handle the 'example' command with UI refresh fix."""
        try:
            add_debug_message("📝 Starting example command")
            
            # Get example code
            example_code = get_example_code()
            add_debug_message(f"📝 Got example code: {len(example_code)} chars")
            
            # Ensure session state exists
            if 'current_code' not in st.session_state:
                st.session_state.current_code = ""
                add_debug_message("📝 Initialized current_code in session state")
            
            # CRITICAL: Force UI refresh by rotating component key
            if 'editor_key' not in st.session_state:
                st.session_state.editor_key = 0
            st.session_state.editor_key += 1
            add_debug_message(f"📝 Rotated editor key to: {st.session_state.editor_key}")
            
            # Set the code in session state
            st.session_state.current_code = example_code
            add_debug_message(f"📝 Set current_code to: {st.session_state.current_code[:50]}...")
            
            # Ensure session exists
            if not st.session_state.session:
                st.session_state.session = ReviewSession("", "", "", [])
                add_debug_message("📝 Created new session")
            
            # Reset code history when loading new example
            if 'code_history' not in st.session_state:
                st.session_state.code_history = []
            if 'original_session_code' not in st.session_state:
                st.session_state.original_session_code = ""
                
            st.session_state.code_history = []
            st.session_state.original_session_code = ""
            add_debug_message("📝 Reset code history")
            
            # Add to conversation using the helper
            add_message_to_session(st.session_state.session, MessageRole.USER, "example")
            add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, 
                "✅ **Example loaded!** Pandas optimization code is now in the editor. Click '📤 Submit Code' to begin learning!")
            
            add_debug_message("📝 Example command completed successfully")
            
            # CRITICAL: Force rerun OUTSIDE of form context
            st.rerun()
            
        except Exception as e:
            st.error(f"Error loading example: {str(e)}")
            add_debug_message(f"❌ Error in handle_example_command: {str(e)}")
            import traceback
            add_debug_message(f"❌ Traceback: {traceback.format_exc()}")
    
    @staticmethod
    def handle_test_command():
        """Handle the 'test' command."""
        try:
            if st.session_state.session.current_code.strip():
                execution_result = CodeExecutor.execute_code_safely(st.session_state.session.current_code)
                
                if execution_result['success']:
                    response = f"""✅ **Code executed successfully!**

{execution_result['fake_data_info'] if execution_result['fake_data_info'] else ''}

{f"**Output:**\n```\n{execution_result['output']}\n```" if execution_result['output'] else ""}

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
            add_debug_message(f"❌ Error in handle_test_command: {str(e)}")
    
    @staticmethod
    def handle_regular_chat(clean_input, assistant):
        """Handle regular chat messages with adaptive coaching."""
        try:
            if not st.session_state.session:
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
                response = f"I'm here to help! {clean_input if len(clean_input) < 50 else 'Thanks for your message.'} To get started with code review, you can type 'example' for sample code or paste your own code in the left panel."
                
                # Add helpful commands
                if st.session_state.session and st.session_state.session.current_code.strip():
                    response += "\n\n💡 **Tip:** Type 'test' to run your current code and check for errors."
            
            add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, response)
            
        except Exception as e:
            st.error(f"Error in regular chat: {str(e)}")
            add_debug_message(f"❌ Error in handle_regular_chat: {str(e)}")