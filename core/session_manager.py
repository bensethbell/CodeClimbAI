import streamlit as st
from datetime import datetime
from .models import ReviewSession, ChatMessage, MessageRole
from .coaching_models import CoachingState
from .adaptive_coach import AdaptiveCoach
from .assistant import CodeReviewAssistant
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
    """Manages session state and code submission logic."""
    
    @staticmethod
    def initialize_session_state():
        """Initialize all session state variables - CRITICAL: current_code MUST be initialized."""
        defaults = {
            'current_code': "",  # CRITICAL: Initialize this first before any UI renders
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
        
        # CRITICAL: Ensure current_code is always a string
        if not isinstance(st.session_state.current_code, str):
            st.session_state.current_code = ""
            
        add_debug_message("Session state initialized with current_code")
    
    @staticmethod
    def start_new_session(code: str, assistant: CodeReviewAssistant) -> ReviewSession:
        """Start a new review session with adaptive coaching."""
        try:
            # Import here to ensure it's available in deployment
            from .coaching_models import CoachingState
            from .adaptive_coach import AdaptiveCoach
            
            # Initialize coaching state
            if 'coaching_state' not in st.session_state:
                st.session_state.coaching_state = CoachingState()
            if 'adaptive_coach' not in st.session_state:
                st.session_state.adaptive_coach = AdaptiveCoach(assistant.analyzer)

            coaching_state = st.session_state.coaching_state
            adaptive_coach = st.session_state.adaptive_coach
            # First, try to execute the code to check for errors
            execution_result = CodeExecutor.execute_code_safely(code)
            
            if not execution_result['success']:
                # If there's an error, create a session focused on debugging
                goal = "Error debugging"
                question = f"""I tried to run your code and found an error that needs to be fixed first:

**Error:** {execution_result['error']}

**Traceback:**
```
{execution_result['traceback']}
```

{execution_result['fake_data_info'] if execution_result['fake_data_info'] else ''}

Let's fix this error before we optimize the code. Can you identify what's causing this issue and how to fix it?

Take a look at the error message and share your thoughts, or ask for a hint if you need guidance."""
            else:
                # Code runs successfully - use adaptive coaching
                coaching_response, coaching_mode = adaptive_coach.process_code_submission(code, coaching_state)
                goal = "Active learning and optimization"
                question = coaching_response
                
                # Add debug info for deployment troubleshooting
                add_debug_message(f"MCQ system activated: {coaching_mode}")
                add_debug_message(f"Question length: {len(question)} chars")
                
                # Add execution info if we generated data
                if execution_result['fake_data_info']:
                    question += f"\n\n*Note: {execution_result['fake_data_info']} to test your code.*"
        
        except ImportError as e:
            # Fallback if adaptive coaching fails to import
            add_debug_message(f"❌ Import error in adaptive coaching: {str(e)}")
            goal = "Performance optimization"
            question = assistant.get_focused_question(code, goal)
            coaching_state = None
        except Exception as e:
            # Fallback for any other adaptive coaching errors
            add_debug_message(f"❌ Error in adaptive coaching: {str(e)}")
            goal = "Performance optimization" 
            question = assistant.get_focused_question(code, goal)
            coaching_state = None
        
        session = ReviewSession(
            original_code=code,
            current_code=code,
            goal=goal,
            conversation_history=[ChatMessage(MessageRole.ASSISTANT, question)],
            coaching_state=coaching_state
        )
        
        return session
    
    @staticmethod
    def handle_code_submission(code_input):
        """Handle code submission logic with adaptive coaching."""
        if not code_input.strip():
            st.error("Please enter some code first!")
            return
        
        try:
            # Add debug info
            add_debug_message(f"Code submitted at {datetime.now()}")
            
            # Add "code submitted" message to chat
            if not st.session_state.session:
                st.session_state.session = ReviewSession("", "", "", [])
            
            # Add submission message
            add_message_to_session(
                st.session_state.session, 
                MessageRole.USER, 
                "*Code submitted*"
            )
            
            current_actual_code = code_input.strip()
            
            # Check if this is a new session or code change
            if not st.session_state.session or not st.session_state.session.original_code:
                # New session - start fresh with coaching
                from .analyzer import ClaudeAPIClient
                api_client = ClaudeAPIClient(API_KEY)
                assistant = CodeReviewAssistant(api_client)
                session = SessionManager.start_new_session(current_actual_code, assistant)
                # Keep the submission message and add the analysis
                session.conversation_history = st.session_state.session.conversation_history + session.conversation_history
                st.session_state.session = session
                st.session_state.current_code = current_actual_code
                # Initialize code history in session state
                normalized_code = normalize_code(current_actual_code)
                st.session_state.code_history = [normalized_code]
                st.session_state.original_session_code = normalized_code
                add_debug_message(f"New session - Original: {normalized_code[:20]}...")
            else:
                # Code change evaluation with coaching
                SessionManager.handle_code_change_evaluation(current_actual_code)
            
            st.rerun()
        except Exception as e:
            st.error(f"Error processing code: {str(e)}")
            add_debug_message(f"❌ Error: {str(e)}")
    
    @staticmethod
    def handle_code_change_evaluation(current_actual_code):
        """Handle evaluation of code changes with adaptive coaching."""
        try:
            # Normalize all code for comparison
            current_normalized = normalize_code(current_actual_code)
            session_normalized = normalize_code(st.session_state.session.current_code) 
            original_normalized = st.session_state.original_session_code
            
            # Get code history from session state
            code_history = st.session_state.code_history if st.session_state.code_history else []
            
            # Add comprehensive debug info
            add_debug_message(f"Comparing codes:")
            add_debug_message(f"Current: {current_normalized[:30]}...")
            add_debug_message(f"Original: {original_normalized[:30]}...")
            add_debug_message(f"Match original: {current_normalized == original_normalized}")
            add_debug_message(f"In history: {current_normalized in code_history}")
            add_debug_message(f"History count: {len(code_history)}")
            
            # Check if code has actually changed from current session state
            if current_normalized != session_normalized:
                # Test the modified code first
                execution_result = CodeExecutor.execute_code_safely(current_actual_code)
                
                if not execution_result['success']:
                    # If there's an error, focus on debugging
                    error_response = f"""❌ **Your code has an error that needs to be fixed:**

**Error:** {execution_result['error']}

**Traceback:**
```
{execution_result['traceback']}
```

{execution_result['fake_data_info'] if execution_result['fake_data_info'] else ''}

Let's fix this error first before continuing with optimization. Can you identify and fix the issue?"""
                    
                    # Add to code history if it's truly new
                    if current_normalized not in code_history:
                        code_history.append(current_normalized)
                        st.session_state.code_history = code_history
                    
                    st.session_state.session.current_code = current_actual_code
                    add_message_to_session(
                        st.session_state.session, 
                        MessageRole.ASSISTANT, 
                        error_response
                    )
                else:
                    # Code runs successfully - use adaptive coaching for evaluation
                    from .analyzer import ClaudeAPIClient
                    api_client = ClaudeAPIClient(API_KEY)
                    assistant = CodeReviewAssistant(api_client)
                    
                    # Initialize coaching if not present
                    if not hasattr(st.session_state.session, 'coaching_state') or not st.session_state.session.coaching_state:
                        st.session_state.session.coaching_state = CoachingState()
                    
                    adaptive_coach = AdaptiveCoach(assistant.analyzer)
                    
                    # Check what type of code change this is
                    if current_normalized == original_normalized:
                        # Returned to original code - ask coaching question
                        coaching_response, coaching_mode = adaptive_coach.process_code_submission(
                            current_actual_code, st.session_state.session.coaching_state
                        )
                        evaluation = f"""🔄 **You've returned to the original code!** 

{coaching_response}"""
                        
                    elif current_normalized in code_history:
                        # Returned to a previous state - ask coaching question
                        state_index = code_history.index(current_normalized) + 1
                        coaching_response, coaching_mode = adaptive_coach.process_code_submission(
                            current_actual_code, st.session_state.session.coaching_state
                        )
                        evaluation = f"""🔄 **You've reverted to a previous code version** (submission #{state_index})! 

{coaching_response}"""
                        
                    else:
                        # Completely new code state - use adaptive coaching
                        coaching_response, coaching_mode = adaptive_coach.process_code_submission(
                            current_actual_code, st.session_state.session.coaching_state
                        )
                        evaluation = coaching_response
                        # Add to code history
                        code_history.append(current_normalized)
                        st.session_state.code_history = code_history
                    
                    # Add execution success info
                    if execution_result['fake_data_info']:
                        evaluation += f"\n\n✅ **Code executed successfully!** {execution_result['fake_data_info']}"
                    
                    st.session_state.session.current_code = current_actual_code
                    add_message_to_session(
                        st.session_state.session, 
                        MessageRole.ASSISTANT, 
                        evaluation
                    )
            else:
                # No changes made
                add_debug_message("ℹ️ DETECTED: No changes made")
                add_message_to_session(
                    st.session_state.session, 
                    MessageRole.ASSISTANT, 
                    "I see you submitted the same code. Did you want to ask a question about it, or are you working on making changes?"
                )
                
        except Exception as e:
            st.error(f"Error in code change evaluation: {str(e)}")
            add_debug_message(f"❌ Error in evaluation: {str(e)}")
    
    @staticmethod
    def reset_session():
        """Reset session state for new session."""
        st.session_state.session = None
        st.session_state.current_code = ""
        st.session_state.code_history = []
        st.session_state.original_session_code = ""
        st.session_state.debug_messages = []
        st.session_state.coaching_state = CoachingState()
        st.session_state.adaptive_coach = AdaptiveCoach(None)  # Pass `None` or reinitialize as needed