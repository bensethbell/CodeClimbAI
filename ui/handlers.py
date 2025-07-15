# ui/handlers.py
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
    """FIXED: Handles user input with guaranteed coaching state consistency."""
    
    @staticmethod
    def handle_user_message(clean_input, assistant):
        """Handle user message processing with FIXED coaching system."""
        try:
            add_debug_message(f"Processing input: {clean_input}")
            
            # Handle special commands - MODIFIED: Updated to use button instead of 'example'
            if clean_input.lower() == "example":
                # Provide guidance to use the button instead
                InputHandler.handle_example_guidance()
            elif clean_input.lower() == "test" and st.session_state.session:
                InputHandler.handle_test_command()
            else:
                InputHandler.handle_regular_chat(clean_input, assistant)
            
        except Exception as e:
            st.error(f"Error processing message: {str(e)}")
            add_debug_message(f"❌ Error in handle_user_message: {str(e)}")
    
    @staticmethod
    def handle_example_guidance():
        """MODIFIED: Guide users to use the button instead of 'example' command."""
        try:
            add_debug_message("📝 Providing example button guidance")
            
            # Ensure session exists
            if not st.session_state.session:
                st.session_state.session = ReviewSession("", "", "", [])
                add_debug_message("📝 Created new session for guidance")
            
            # Add guidance message
            add_message_to_session(st.session_state.session, MessageRole.USER, "example")
            add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, 
                "👋 I see you typed 'example'! To load sample code, please click the **'📚 Get Example'** button in the left panel above the code editor. This will load the main pandas optimization example for you to analyze!")
            
            add_debug_message("📝 Example guidance provided successfully")
            
        except Exception as e:
            st.error(f"Error providing example guidance: {str(e)}")
            add_debug_message(f"❌ Error in handle_example_guidance: {str(e)}")
    
    @staticmethod
    def handle_example_command():
        """ENHANCED: Original example command logic with proper code formatting."""
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
            
            # ENHANCED: Add to conversation with proper code formatting
            add_message_to_session(st.session_state.session, MessageRole.USER, "example")
            
            # Format response with code block
            response = f"""✅ **Example loaded!** Pandas optimization code is now in the editor.

```python
{example_code}
```

Click '📤 Submit Code' to begin learning!"""
            
            add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, response)
            
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
        """ENHANCED: Handle the 'test' command with proper output formatting."""
        try:
            if st.session_state.session.current_code.strip():
                execution_result = CodeExecutor.execute_code_safely(st.session_state.session.current_code)
                    
                if execution_result['success']:
                    # Format successful execution with code blocks
                    output_block = f"""
**Execution Output:**
```text
{execution_result['output']}
```""" if execution_result['output'] else ""
                    
                    response = f"""✅ **Code executed successfully!**

{execution_result['fake_data_info'] if execution_result['fake_data_info'] else ''}
{output_block}

Great! Your code runs without errors. Now let's focus on optimization."""
                
                else:
                    # Format execution error with code blocks
                    response = f"""❌ **Code execution failed:**

**Error:** {execution_result['error']}

**Traceback:**
```text
{execution_result['traceback']}
```

{execution_result['fake_data_info'] if execution_result['fake_data_info'] else ''}

Let's fix this error first. Can you identify what's causing this issue and how to fix it?

Take a look at the error message and share your thoughts, or ask for a hint if you need guidance."""
                
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
        """FIXED: Handle regular chat messages with ABSOLUTE coaching state consistency."""
        try:
            if not st.session_state.session:
                st.session_state.session = ReviewSession("", "", "", [])
            
            # CRITICAL FIX: Ensure coaching system consistency before processing
            from core.coaching_integration import CoachingIntegration
            
            # STEP 1: Validate coaching system consistency
            CoachingIntegration.validate_coaching_consistency()
            
            # STEP 2: Force synchronization if needed
            coaching_state, adaptive_coach = CoachingIntegration.force_coaching_sync()
            
            # STEP 3: Check if we're waiting for an answer to a coaching question
            if coaching_state and coaching_state.is_waiting_for_answer():
                
                add_debug_message(f"🎯 COACHING: Processing MCQ answer '{clean_input}'")
                add_debug_message(f"🎯 Using coaching state ID: {id(coaching_state)}")
                add_debug_message(f"🎯 Using adaptive coach ID: {id(adaptive_coach)}")
                add_debug_message(f"🎯 Current interaction: {coaching_state.current_interaction}")
                
                # CRITICAL: Ensure session coaching state is synced
                if (hasattr(st.session_state.session, 'coaching_state') and 
                    st.session_state.session.coaching_state != coaching_state):
                    add_debug_message(f"⚠️ Syncing session coaching state")
                    st.session_state.session.coaching_state = coaching_state
                
                # Process the answer with the SAME adaptive coach that created the question
                feedback = adaptive_coach.handle_user_answer(clean_input, coaching_state)
                add_message_to_session(st.session_state.session, MessageRole.USER, clean_input)
                add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, feedback)
                
                add_debug_message(f"✅ COACHING: MCQ answer processed successfully")
                return
            else:
                add_debug_message(f"💬 REGULAR: Not waiting for answer, processing as regular chat")
                add_debug_message(f"💬 Coaching state waiting: {coaching_state.is_waiting_for_answer() if coaching_state else 'No state'}")
            
            add_debug_message(f"💬 REGULAR: Processing regular chat message")
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
                # General chat - UPDATED: Mention button instead of 'example' command
                response = f"I'm here to help! {clean_input if len(clean_input) < 50 else 'Thanks for your message.'} To get started with code review, click the '📚 Get Example' button to load sample code or paste your own code in the left panel."
                
                # Add helpful commands
                if st.session_state.session and st.session_state.session.current_code.strip():
                    response += "\n\n💡 **Tip:** Type 'test' to run your current code and check for errors."
            
            add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, response)
            
        except Exception as e:
            st.error(f"Error in regular chat: {str(e)}")
            add_debug_message(f"❌ Error in handle_regular_chat: {str(e)}")
            import traceback
            add_debug_message(f"❌ Traceback: {traceback.format_exc()}")