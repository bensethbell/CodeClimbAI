# ui/panels.py - FIXED VERSION with proper code block support
import streamlit as st
from datetime import datetime
from config import ACE_AVAILABLE, CODE_EDITOR_HEIGHT, CODE_EDITOR_THEME, CODE_EDITOR_FONT_SIZE, CODE_EDITOR_TAB_SIZE, CHAT_CONTAINER_HEIGHT
from .components import UIComponents  # Use the FIXED UIComponents
from .handlers import InputHandler
from core.models import ChatMessage, MessageRole
from core.session_manager import SessionManager

# Import ace editor if available
if ACE_AVAILABLE:
    from streamlit_ace import st_ace

def _analyze_example_for_optimization(code):
    """
    Analyze example code to ensure it has optimization opportunities.
    Returns True if code needs optimization, False if already optimized.
    """
    try:
        from core.coaching_helpers import CodeAnalysisHelper
        
        # Analyze the code for coaching opportunities
        analysis = CodeAnalysisHelper.analyze_code_for_coaching(code)
        
        # Check for key optimization issues
        optimization_issues = [
            'has_iterrows',
            'has_string_concat', 
            'has_nested_loops',
            'has_manual_loop',
            'has_inefficient_filtering'
        ]
        
        # Count how many issues are present
        issue_count = sum(1 for issue in optimization_issues if analysis.get(issue, False))
        
        print(f"DEBUG: Example analysis - Issues found: {issue_count}")
        print(f"DEBUG: Analysis details: {analysis}")
        
        # Consider it optimizable if it has at least one major issue
        return issue_count > 0
        
    except ImportError:
        print("DEBUG: CodeAnalysisHelper not available, assuming example needs optimization")
        return True
    except Exception as e:
        print(f"DEBUG: Error analyzing example: {e}")
        return True

def _reset_coaching_state():
    """
    CRITICAL FIX: Reset coaching state when loading new examples.
    This prevents previous resolved_issues from carrying over.
    """
    try:
        print("DEBUG: Resetting coaching state for new example")
        
        # Reset coaching state in session - use dynamic import to avoid circular imports
        if hasattr(st.session_state, 'session') and st.session_state.session:
            try:
                from core.coaching_models import CoachingState
                st.session_state.session.coaching_state = CoachingState()
                print("DEBUG: Reset session coaching_state")
            except ImportError:
                print("DEBUG: CoachingState not available, skipping session reset")
        
        # Reset global coaching state if it exists
        if hasattr(st.session_state, 'coaching_state'):
            try:
                from core.coaching_models import CoachingState
                st.session_state.coaching_state = CoachingState()
                print("DEBUG: Reset global coaching_state")
            except ImportError:
                print("DEBUG: CoachingState not available, clearing state manually")
                st.session_state.coaching_state = None
            
        # Clear any cached coaching data
        if hasattr(st.session_state, 'adaptive_coach'):
            try:
                # Reset the adaptive coach state if it exists
                from core.adaptive_coach import AdaptiveCoach
                from core.analyzer import CodeAnalyzer
                code_analyzer = CodeAnalyzer()
                st.session_state.adaptive_coach = AdaptiveCoach(code_analyzer)
                print("DEBUG: Reset adaptive_coach")
            except ImportError:
                print("DEBUG: AdaptiveCoach/CodeAnalyzer not available, clearing manually")
                st.session_state.adaptive_coach = None
            except Exception as e:
                print(f"DEBUG: Error creating new adaptive_coach: {e}")
                st.session_state.adaptive_coach = None
            
        print("DEBUG: Coaching state reset completed")
        
    except Exception as e:
        print(f"DEBUG: Error resetting coaching state: {e}")
        # Graceful fallback - just clear the state variables
        try:
            if hasattr(st.session_state, 'session') and st.session_state.session:
                st.session_state.session.coaching_state = None
            if hasattr(st.session_state, 'coaching_state'):
                st.session_state.coaching_state = None
            if hasattr(st.session_state, 'adaptive_coach'):
                st.session_state.adaptive_coach = None
            print("DEBUG: Fallback coaching state clear completed")
        except:
            print("DEBUG: Even fallback clear failed")

def _load_debug_example():
    """
    ENHANCED: Callback to inject an example with verified optimization opportunities.
    FIXED: Now properly resets coaching state to prevent issue carryover.
    """
    try:
        print("DEBUG: _load_debug_example called with coaching state reset")
        
        # CRITICAL FIX: Reset coaching state first
        _reset_coaching_state()
        
        # ENHANCED: Add first-time logic while preserving original behavior
        if 'first_example_loaded' not in st.session_state:
            st.session_state.first_example_loaded = False
        
        max_attempts = 5  # Prevent infinite loops
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            
            if not st.session_state.first_example_loaded:
                # First time: Load the built-in example
                from templates.examples import get_example_code
                code = get_example_code()
                category = "performance" 
                st.session_state.first_example_loaded = True
                print(f"DEBUG: Loading FIRST example (built-in): {code[:30]}...")
            else:
                # PRESERVED ORIGINAL LOGIC: Get the first example code for exclusion
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
            
            # ANALYZE EXAMPLE FOR OPTIMIZATION OPPORTUNITIES
            needs_optimization = _analyze_example_for_optimization(code)
            
            if needs_optimization:
                print(f"DEBUG: Example approved - has optimization opportunities (attempt {attempt})")
                break
            else:
                print(f"DEBUG: Example rejected - already optimized (attempt {attempt})")
                if not st.session_state.first_example_loaded:
                    # If even the first example is optimized, something is wrong
                    print("WARNING: First example appears optimized - using anyway")
                    break
                # For random examples, try again
                continue
        
        if attempt >= max_attempts:
            print("WARNING: Max attempts reached, using last generated example")
        
        # PRESERVED ORIGINAL: Ensure session state is properly initialized
        if "current_code" not in st.session_state:
            st.session_state["current_code"] = ""
        if "editor_key" not in st.session_state:
            st.session_state["editor_key"] = 0
            
        # PRESERVED ORIGINAL: Update session state
        st.session_state.current_code = code
        st.session_state.editor_key += 1
        
        # ADDITIONAL FIX: Clear code history for fresh start
        if hasattr(st.session_state, 'code_history'):
            st.session_state.code_history = []
            print("DEBUG: Cleared code history")
        if hasattr(st.session_state, 'original_session_code'):
            st.session_state.original_session_code = ""
            print("DEBUG: Cleared original session code")
        
        print(f"DEBUG: Updated session state - editor_key: {st.session_state.editor_key}")
        print(f"DEBUG: Current code set to: {st.session_state.current_code[:50]}...")
        
        # PRESERVED ORIGINAL: Add success message to chat if session exists
        if hasattr(st.session_state, 'session') and st.session_state.session:
            from core.session_manager import add_message_to_session
            
            # ENHANCED: Better message based on first-time vs random with analysis info
            if not st.session_state.first_example_loaded:
                message = f"✅ **Fresh example loaded!** Pandas optimization example with confirmed learning opportunities is now in the editor. Click '📤 Submit Code' to begin!"
            else:
                message = f"🎲 **New example loaded!** Fresh {category} example with optimization opportunities is ready. Click '📤 Submit Code' to analyze it!"
            
            add_message_to_session(
                st.session_state.session, 
                MessageRole.ASSISTANT, 
                message
            )
        
        print("DEBUG: _load_debug_example completed successfully with coaching state reset")
        
    except Exception as e:
        print(f"ERROR in _load_debug_example: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # PRESERVED ORIGINAL: Fallback code with known issues
        try:
            fallback_code = '''def process_data(df):
    results = []
    for idx, row in df.iterrows():  # Inefficient - has iterrows issue
        results.append(row["value"] * 2)
    return results'''
            
            st.session_state.current_code = fallback_code
            st.session_state.editor_key += 1
            print("DEBUG: Loaded fallback code with known iterrows issue")
        except:
            print("ERROR: Even fallback failed")

class PanelRenderer:
    """Handles rendering of main UI panels with FIXED message rendering."""
    
    @staticmethod
    def render_code_input_panel():
        # PRESERVED ORIGINAL: Initialize editor state
        if "editor_key" not in st.session_state:
            st.session_state["editor_key"] = 0
        if "current_code" not in st.session_state:
            st.session_state["current_code"] = ""

        st.markdown("### 📝 Your Code")
        
        # ENHANCED: Smart button text while preserving original layout
        col1, col2 = st.columns([3, 1])
        
        with col2:
            # ENHANCED: Smart button text based on state
            if 'first_example_loaded' not in st.session_state:
                st.session_state.first_example_loaded = False
            
            # ENHANCED: Dynamic button text and help
            if not st.session_state.first_example_loaded:
                button_text = "📚 Get Example"
                button_help = "Load verified example with optimization opportunities"
            else:
                button_text = "🎲 Random Example" 
                button_help = "Load different example with confirmed learning value"
            
            if st.button(button_text, 
                        key="load_random_example", 
                        help=button_help,
                        use_container_width=True):
                _load_debug_example()
                st.rerun()

        # PRESERVED ORIGINAL: IDE-like code input area with dynamic key
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
                placeholder="Click the button above to load sample code, or paste your own code here..."
            )

        # PRESERVED ORIGINAL: Persist editor contents back into session state
        if code_input != st.session_state["current_code"]:
            st.session_state["current_code"] = code_input

        # PRESERVED ORIGINAL: Submit button
        if st.button("📤 Submit Code", type="primary", use_container_width=True):
            SessionManager.handle_code_submission(code_input)

        PanelRenderer.render_getting_started_section()

    
    @staticmethod
    def render_getting_started_section():
        """ENHANCED: Render the getting started instructions."""
        st.info(
            "Click 'Get Example' for verified learning code, or paste your own code and click 'Submit Code' to start learning!"
        )
    
    @staticmethod
    def render_chat_panel(assistant):
        """PRESERVED ORIGINAL: Render the middle panel for chat interface with FIXED message rendering."""
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
                    # FIXED: Use UIComponents with proper code block support
                    UIComponents.render_chat_message(message)
            else:
                # FIXED: Use UIComponents welcome message
                UIComponents.render_welcome_message()
        
        # User input area
        PanelRenderer.render_user_input_area(assistant)
        
        # Action buttons for active sessions
        if st.session_state.session and st.session_state.session.is_active:
            PanelRenderer.render_session_action_buttons(assistant)
    
    @staticmethod
    def render_user_input_area(assistant):
        """PRESERVED ORIGINAL: Render user input area and handle message submission."""
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
        """PRESERVED ORIGINAL: Render action buttons for active sessions."""
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