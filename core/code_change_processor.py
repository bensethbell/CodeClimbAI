"""
Code change processing for CodeClimbAI session management.
Handles different execution scenarios and code evaluation.
Extracted from session_manager.py for better modularity.
"""
import streamlit as st
from .models import MessageRole
from .import_handler import ImportHandler
from .coaching_integration import CoachingIntegration
from .session_utils import normalize_code, add_debug_message, add_message_to_session
from utils.execution import CodeExecutor


class CodeChangeProcessor:
    """Handles code change evaluation and processing."""
    
    @staticmethod
    def handle_code_change_evaluation(current_actual_code):
        """Handle evaluation of code changes with robust coaching integration."""
        try:
            # Normalize code for comparison
            current_normalized = normalize_code(current_actual_code)
            session_normalized = normalize_code(st.session_state.session.current_code) 
            original_normalized = st.session_state.original_session_code
            code_history = st.session_state.code_history if st.session_state.code_history else []
            
            # Check if code has actually changed
            if current_normalized != session_normalized:
                # Check for import dependencies
                unavailable_imports = ImportHandler.detect_unavailable_imports(current_actual_code)
                
                # Test the modified code
                execution_result = CodeExecutor.execute_code_safely(current_actual_code)
                
                # Handle import errors gracefully
                if (not execution_result['success'] and unavailable_imports and
                    ImportHandler.is_import_error(execution_result['error'], unavailable_imports)):
                    
                    CodeChangeProcessor._handle_import_error_in_change(
                        current_actual_code, current_normalized, original_normalized, 
                        code_history, unavailable_imports
                    )
                
                elif not execution_result['success']:
                    # Non-import execution error
                    CodeChangeProcessor._handle_execution_error_in_change(
                        current_actual_code, current_normalized, execution_result, code_history
                    )
                
                else:
                    # Code runs successfully
                    CodeChangeProcessor._handle_successful_execution_in_change(
                        current_actual_code, current_normalized, original_normalized, 
                        code_history, execution_result
                    )
            else:
                # No changes made
                add_message_to_session(
                    st.session_state.session, 
                    MessageRole.ASSISTANT, 
                    "I see you submitted the same code. Did you want to ask a question about it, or are you working on making changes?"
                )
                
        except Exception as e:
            st.error(f"Error in code change evaluation: {str(e)}")
            add_debug_message(f"❌ Error in evaluation: {str(e)}")
    
    @staticmethod
    def _handle_import_error_in_change(current_actual_code, current_normalized, original_normalized, 
                                     code_history, unavailable_imports):
        """Handle import errors during code changes with robust coaching state sync."""
        
        # Use robust coaching system that handles Streamlit reruns properly
        coaching_state, adaptive_coach = CoachingIntegration.force_coaching_sync()
        add_debug_message(f"✅ Using robust coaching_state: {id(coaching_state)}")
        
        # Update session coaching state to match
        st.session_state.session.coaching_state = coaching_state
        
        # Get coaching response with SAME state that will handle input
        coaching_response, _ = adaptive_coach.process_code_submission(
            current_actual_code, coaching_state
        )
        add_debug_message(f"✅ Import error coaching response generated with synchronized state: {id(coaching_state)}")
        
        # Import message goes at the END as a graceful note
        import_note = ImportHandler.create_import_limitation_message(unavailable_imports)
        
        # Determine change type and create appropriate message
        if current_normalized == original_normalized:
            evaluation = f"""🔄 **Back to original code!**

{coaching_response}

*Note: {import_note}*"""
        elif current_normalized in code_history:
            state_index = code_history.index(current_normalized) + 1
            evaluation = f"""🔄 **Returned to previous version** (#{state_index})!

{coaching_response}

*Note: {import_note}*"""
        else:
            evaluation = f"""✨ **Code updated!**

{coaching_response}

*Note: {import_note}*"""
            code_history.append(current_normalized)
            st.session_state.code_history = code_history
        
        st.session_state.session.current_code = current_actual_code
        add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, evaluation)
    
    @staticmethod
    def _handle_execution_error_in_change(current_actual_code, current_normalized, 
                                        execution_result, code_history):
        """Handle execution errors during code changes."""
        from .session_utils import create_error_message
        error_response = create_error_message(execution_result)
        
        # Add to code history if it's new
        if current_normalized not in code_history:
            code_history.append(current_normalized)
            st.session_state.code_history = code_history
        
        st.session_state.session.current_code = current_actual_code
        add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, error_response)
    
    @staticmethod
    def _handle_successful_execution_in_change(current_actual_code, current_normalized, 
                                             original_normalized, code_history, execution_result):
        """Handle successful execution during code changes with robust coaching."""
        
        # Use robust coaching system for consistency
        coaching_state, adaptive_coach = CoachingIntegration.force_coaching_sync()
        add_debug_message(f"✅ Using robust coaching_state for successful execution: {id(coaching_state)}")
        
        # Update session coaching state
        st.session_state.session.coaching_state = coaching_state
        
        # Determine change type and get appropriate response
        coaching_response, _ = adaptive_coach.process_code_submission(
            current_actual_code, coaching_state
        )
        
        if current_normalized == original_normalized:
            evaluation = f"🔄 **You've returned to the original code!**\n\n{coaching_response}"
        elif current_normalized in code_history:
            state_index = code_history.index(current_normalized) + 1
            evaluation = f"🔄 **You've reverted to a previous code version** (submission #{state_index})!\n\n{coaching_response}"
        else:
            evaluation = coaching_response
            code_history.append(current_normalized)
            st.session_state.code_history = code_history
        
        # Add execution success info
        if execution_result['fake_data_info']:
            evaluation += f"\n\n✅ **Code executed successfully!** {execution_result['fake_data_info']}"
        
        st.session_state.session.current_code = current_actual_code
        add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, evaluation)
