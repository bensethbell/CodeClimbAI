"""
Session handling logic for CodeClimbAI.
Manages session creation, code submission, and lifecycle.
Extracted from session_manager.py for better modularity.
"""
import streamlit as st
from datetime import datetime
from .models import ReviewSession, ChatMessage, MessageRole
from .import_handler import ImportHandler
from .coaching_integration import CoachingIntegration
from .session_utils import normalize_code, add_debug_message, add_message_to_session, create_error_message
from .code_change_processor import CodeChangeProcessor
from utils.execution import CodeExecutor
from config import API_KEY


class SessionHandlers:
    """Handles session creation and code submission processing."""
    
    @staticmethod    
    def start_new_session(code: str, assistant) -> ReviewSession:
        """Start a new review session with graceful import handling."""
        try:
            # FIXED: Use persistent coaching system instead of creating new
            coaching_state, adaptive_coach = CoachingIntegration.get_existing_coaching_system()
            add_debug_message(f"✅ Coaching state created: {id(coaching_state)}")
            
            # Check for import dependencies
            unavailable_imports = ImportHandler.detect_unavailable_imports(code)
            
            # Try to execute the code
            execution_result = CodeExecutor.execute_code_safely(code)
            
            # Handle different execution scenarios
            if not execution_result['success'] and unavailable_imports:
                # Check if error is due to missing imports
                if ImportHandler.is_import_error(execution_result['error'], unavailable_imports):
                    # FIXED: Use the SAME coaching_state throughout
                    coaching_response, _ = adaptive_coach.process_code_submission(code, coaching_state)
                    add_debug_message(f"✅ Import error coaching response generated with state: {id(coaching_state)}")
                    
                    goal = "Learning optimization patterns despite import limitations"
                    
                    # Import message goes at the END as a graceful note
                    import_note = ImportHandler.create_import_limitation_message(unavailable_imports)
                    
                    question = f"""📚 **Code Analysis Ready!**

{coaching_response}

*Note: {import_note}*"""
                    
                else:
                    # Other execution error - standard debugging flow
                    goal = "Error debugging"
                    question = create_error_message(execution_result)
            
            elif not execution_result['success']:
                # Non-import execution error
                goal = "Error debugging"
                question = create_error_message(execution_result)
            
            else:
                # Code runs successfully - use adaptive coaching
                coaching_response, _ = adaptive_coach.process_code_submission(code, coaching_state)
                add_debug_message(f"✅ Successful execution coaching response generated with state: {id(coaching_state)}")
                goal = CoachingIntegration.get_coaching_goal()
                question = coaching_response
                
                # Add execution info if we generated data
                if execution_result['fake_data_info']:
                    question += f"\n\n*Note: {execution_result['fake_data_info']} to test your code.*"
        
        except Exception as e:
            # Fallback for any errors
            add_debug_message(f"❌ Error in session start: {str(e)}")
            goal = "Performance optimization"
            question = assistant.get_focused_question(code, goal)
            coaching_state = CoachingIntegration.initialize_coaching_state()
        
        # FIXED: Create session with the SAME coaching_state
        session = ReviewSession(
            original_code=code,
            current_code=code,
            goal=goal,
            conversation_history=[ChatMessage(MessageRole.ASSISTANT, question)],
            coaching_state=coaching_state  # CRITICAL: Same state used for MCQ generation
        )
        
        add_debug_message(f"✅ Session created with coaching_state: {id(coaching_state)}")
        return session
    
    @staticmethod
    def handle_code_submission(code_input):
        """Handle code submission with enhanced error handling."""
        if not code_input.strip():
            st.error("Please enter some code first!")
            return

        try:
            add_debug_message(f"Code submitted at {datetime.now()}")
            
            # Ensure session exists
            if not st.session_state.session:
                st.session_state.session = ReviewSession("", "", "", [])
            
            # Add submission message
            add_message_to_session(st.session_state.session, MessageRole.USER, "*Code submitted*")
            
            current_actual_code = code_input.strip()
            
            # Check if this is a new session or code change
            if not st.session_state.session or not st.session_state.session.original_code:
                # New session
                from .analyzer import ClaudeAPIClient
                api_client = ClaudeAPIClient(API_KEY)
                from .assistant import CodeReviewAssistant
                assistant = CodeReviewAssistant(api_client)
                
                session = SessionHandlers.start_new_session(current_actual_code, assistant)
                session.conversation_history = st.session_state.session.conversation_history + session.conversation_history
                st.session_state.session = session
                st.session_state.current_code = current_actual_code
                
                # CRITICAL: Ensure coaching states are synchronized
                if hasattr(session, 'coaching_state') and session.coaching_state:
                    # Update both session state locations for consistency
                    st.session_state.coaching_state = session.coaching_state
                    add_debug_message(f"✅ Coaching state synchronized: {id(session.coaching_state)}")
                
                # Initialize code history
                normalized_code = normalize_code(current_actual_code)
                st.session_state.code_history = [normalized_code]
                st.session_state.original_session_code = normalized_code
                add_debug_message(f"New session started")
            else:
                # Code change evaluation
                CodeChangeProcessor.handle_code_change_evaluation(current_actual_code)
            
            st.rerun()
        except Exception as e:
            st.error(f"Error processing code: {str(e)}")
            add_debug_message(f"❌ Error: {str(e)}")
