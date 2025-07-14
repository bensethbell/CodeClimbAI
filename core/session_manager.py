"""
Streamlined session state and lifecycle management for CodeClimbAI.
FIXED: Coaching state synchronization bug that broke MCQ input for selenium code.
"""
import streamlit as st
from datetime import datetime
from .models import ReviewSession, ChatMessage, MessageRole
from .import_handler import ImportHandler
from .coaching_integration import CoachingIntegration
from utils.execution import CodeExecutor
from config import API_KEY


def normalize_code(code: str) -> str:
    """Normalize code for comparison by removing extra whitespace and newlines."""
    if not code:
        return ""
    return '\n'.join(line.strip() for line in code.strip().split('\n') if line.strip())


def add_debug_message(message: str):
    """Add debug message directly to session state."""
    if 'debug_messages' not in st.session_state:
        st.session_state.debug_messages = []
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    debug_msg = f"[{timestamp}] {message}"
    st.session_state.debug_messages.append(debug_msg)
    
    # Keep only last 8 messages
    if len(st.session_state.debug_messages) > 8:
        st.session_state.debug_messages = st.session_state.debug_messages[-8:]


def add_message_to_session(session, role, content):
    """Add a message to session with proper role handling."""
    if session is None:
        return
        
    # Ensure we're using the enum
    if isinstance(role, str):
        role = MessageRole.USER if role.lower() in ['user', 'human'] else MessageRole.ASSISTANT
        
    message = ChatMessage(role, content)
    session.conversation_history.append(message)


class SessionManager:
    """Manages session state and code submission logic with enhanced coaching."""
    
    @staticmethod
    def initialize_session_state():
        """Initialize all session state variables."""
        defaults = {
            'current_code': "",
            'session': None,
            'learning_log': [],
            'last_input_key': 0,
            'code_history': [],
            'original_session_code': "",
            'debug_messages': []
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
        
        # Ensure current_code is always a string
        if not isinstance(st.session_state.current_code, str):
            st.session_state.current_code = ""
            
        add_debug_message("Session state initialized")
    
    @staticmethod    
    def start_new_session(code: str, assistant) -> ReviewSession:
        """Start a new review session with graceful import handling."""
        try:
            # FIXED: Set up coaching system with proper state management
            coaching_state, adaptive_coach = CoachingIntegration.setup_session_coaching()
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
                    question = SessionManager._create_error_message(execution_result)
            
            elif not execution_result['success']:
                # Non-import execution error
                goal = "Error debugging"
                question = SessionManager._create_error_message(execution_result)
            
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
    def _create_error_message(execution_result) -> str:
        """Create standardized error message."""
        return f"""I tried to run your code and found an error that needs to be fixed first:

**Error:** {execution_result['error']}

**Traceback:**
```
{execution_result['traceback']}
```

{execution_result['fake_data_info'] if execution_result['fake_data_info'] else ''}

Let's fix this error before we optimize the code. Can you identify what's causing this issue and how to fix it?

Take a look at the error message and share your thoughts, or ask for a hint if you need guidance."""
    
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
                
                session = SessionManager.start_new_session(current_actual_code, assistant)
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
                SessionManager.handle_code_change_evaluation(current_actual_code)
            
            st.rerun()
        except Exception as e:
            st.error(f"Error processing code: {str(e)}")
            add_debug_message(f"❌ Error: {str(e)}")
    
    @staticmethod
    def handle_code_change_evaluation(current_actual_code):
        """Handle evaluation of code changes with import-aware error handling."""
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
                    
                    SessionManager._handle_import_error_in_change(
                        current_actual_code, current_normalized, original_normalized, 
                        code_history, unavailable_imports
                    )
                
                elif not execution_result['success']:
                    # Non-import execution error
                    SessionManager._handle_execution_error_in_change(
                        current_actual_code, current_normalized, execution_result, code_history
                    )
                
                else:
                    # Code runs successfully
                    SessionManager._handle_successful_execution_in_change(
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
        """FIXED: Handle import errors during code changes with proper coaching state sync."""
        
        # CRITICAL FIX: Use EXISTING coaching state instead of creating new one
        if (hasattr(st.session_state.session, 'coaching_state') and 
            st.session_state.session.coaching_state):
            coaching_state = st.session_state.session.coaching_state
            add_debug_message(f"✅ Using existing coaching_state: {id(coaching_state)}")
        else:
            # Fallback: set up new coaching system if none exists
            coaching_state, adaptive_coach = CoachingIntegration.setup_session_coaching()
            st.session_state.session.coaching_state = coaching_state
            st.session_state.coaching_state = coaching_state
            add_debug_message(f"⚠️ Created new coaching_state: {id(coaching_state)}")
        
        # Get adaptive coach (reuse existing if available)
        if hasattr(st.session_state, 'adaptive_coach') and st.session_state.adaptive_coach:
            adaptive_coach = st.session_state.adaptive_coach
        else:
            from .analyzer import CodeAnalyzer
            from .adaptive_coach import AdaptiveCoach
            code_analyzer = CodeAnalyzer()
            adaptive_coach = AdaptiveCoach(code_analyzer)
            st.session_state.adaptive_coach = adaptive_coach
        
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
        error_response = SessionManager._create_error_message(execution_result)
        
        # Add to code history if it's new
        if current_normalized not in code_history:
            code_history.append(current_normalized)
            st.session_state.code_history = code_history
        
        st.session_state.session.current_code = current_actual_code
        add_message_to_session(st.session_state.session, MessageRole.ASSISTANT, error_response)
    
    @staticmethod
    def _handle_successful_execution_in_change(current_actual_code, current_normalized, 
                                             original_normalized, code_history, execution_result):
        """Handle successful execution during code changes."""
        
        # FIXED: Use existing coaching state for consistency
        if (hasattr(st.session_state.session, 'coaching_state') and 
            st.session_state.session.coaching_state):
            coaching_state = st.session_state.session.coaching_state
            add_debug_message(f"✅ Using existing coaching_state for successful execution: {id(coaching_state)}")
        else:
            coaching_state, adaptive_coach = CoachingIntegration.setup_session_coaching()
            st.session_state.session.coaching_state = coaching_state
            st.session_state.coaching_state = coaching_state
            add_debug_message(f"⚠️ Created new coaching_state for successful execution: {id(coaching_state)}")
        
        # Get adaptive coach
        if hasattr(st.session_state, 'adaptive_coach') and st.session_state.adaptive_coach:
            adaptive_coach = st.session_state.adaptive_coach
        else:
            from .analyzer import CodeAnalyzer
            from .adaptive_coach import AdaptiveCoach
            code_analyzer = CodeAnalyzer()
            adaptive_coach = AdaptiveCoach(code_analyzer)
            st.session_state.adaptive_coach = adaptive_coach
        
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
    
    @staticmethod
    def reset_session():
        """Reset session state for new session."""
        st.session_state.session = None
        st.session_state.current_code = ""
        st.session_state.code_history = []
        st.session_state.original_session_code = ""
        st.session_state.debug_messages = []
        
        # Reset coaching state
        CoachingIntegration.reset_coaching_state()
        add_debug_message("Session reset completed")