"""
Coaching system integration helpers for CodeClimbAI.
FIXED: Ensures absolute coaching state persistence and object consistency.
"""
import streamlit as st
from .coaching_models import CoachingState

try:
    from .learning_continuity_system import EnhancedCoachingState, SessionMemory
    ENHANCED_COACHING_AVAILABLE = True
except ImportError:
    ENHANCED_COACHING_AVAILABLE = False

class CoachingIntegration:
    """FIXED: Handles setup and integration with guaranteed object persistence."""
    
    @staticmethod
    def initialize_coaching_state():
        """Initialize a new coaching state object."""
        if ENHANCED_COACHING_AVAILABLE:
            coaching_state = EnhancedCoachingState()
        else:
            coaching_state = CoachingState()
        
        return coaching_state
    
    @staticmethod
    def ensure_session_memory(coaching_state):
        """Ensure coaching state has session memory if available."""
        if (ENHANCED_COACHING_AVAILABLE and 
            not hasattr(coaching_state, 'session_memory')):
            coaching_state.session_memory = SessionMemory()
    
    @staticmethod
    def get_existing_coaching_system():
        """
        FIXED: Get existing coaching system with guaranteed object consistency.
        This method MUST return the exact same objects every time.
        """
        # CRITICAL: Use the most robust session state keys possible
        coaching_state_key = "ccai_persistent_coaching_state"
        adaptive_coach_key = "ccai_persistent_adaptive_coach"
        
        # DEFENSIVE: Ensure session_state exists
        if not hasattr(st, 'session_state'):
            raise RuntimeError("Streamlit session_state not available")
        
        coaching_state = None
        adaptive_coach = None
        
        # STEP 1: Get or create coaching state with maximum robustness
        if coaching_state_key in st.session_state and st.session_state[coaching_state_key] is not None:
            coaching_state = st.session_state[coaching_state_key]
            print(f"DEBUG: Retrieved existing coaching_state ID: {id(coaching_state)}")
        else:
            coaching_state = CoachingIntegration.initialize_coaching_state()
            st.session_state[coaching_state_key] = coaching_state
            print(f"DEBUG: Created NEW coaching_state ID: {id(coaching_state)}")
        
        # STEP 2: Get or create adaptive coach with maximum robustness
        if adaptive_coach_key in st.session_state and st.session_state[adaptive_coach_key] is not None:
            adaptive_coach = st.session_state[adaptive_coach_key]
            print(f"DEBUG: Retrieved existing adaptive_coach ID: {id(adaptive_coach)}")
        else:
            from .analyzer import CodeAnalyzer
            from .adaptive_coach import AdaptiveCoach
            
            code_analyzer = CodeAnalyzer()
            adaptive_coach = AdaptiveCoach(code_analyzer)
            st.session_state[adaptive_coach_key] = adaptive_coach
            print(f"DEBUG: Created NEW adaptive_coach ID: {id(adaptive_coach)}")
        
        # STEP 3: Ensure session memory exists
        CoachingIntegration.ensure_session_memory(coaching_state)
        
        # STEP 4: CRITICAL - Set up legacy compatibility keys for backwards compatibility
        st.session_state.coaching_state = coaching_state
        st.session_state.adaptive_coach = adaptive_coach
        
        # STEP 5: VALIDATION - Ensure objects are properly linked
        if coaching_state is None or adaptive_coach is None:
            raise RuntimeError("CRITICAL: Failed to create coaching objects")
        
        print(f"DEBUG: Returning coaching_state ID: {id(coaching_state)}, coach ID: {id(adaptive_coach)}")
        
        return coaching_state, adaptive_coach
    
    @staticmethod
    def get_coach_for_state(coaching_state):
        """FIXED: Get the adaptive coach instance that should be used with this coaching state."""
        adaptive_coach_key = "ccai_persistent_adaptive_coach"
        
        # Return the persistent adaptive coach
        if adaptive_coach_key in st.session_state and st.session_state[adaptive_coach_key] is not None:
            adaptive_coach = st.session_state[adaptive_coach_key]
            print(f"DEBUG: get_coach_for_state returning coach ID: {id(adaptive_coach)}")
            return adaptive_coach
        else:
            # Fallback: get the full system
            print("DEBUG: get_coach_for_state falling back to full system retrieval")
            _, adaptive_coach = CoachingIntegration.get_existing_coaching_system()
            return adaptive_coach
    
    @staticmethod
    def validate_coaching_consistency():
        """FIXED: Validate that coaching objects are consistent across session state."""
        coaching_state_key = "ccai_persistent_coaching_state"
        adaptive_coach_key = "ccai_persistent_adaptive_coach"
        
        issues = []
        
        # Check if persistent keys exist
        if coaching_state_key not in st.session_state:
            issues.append("Missing persistent coaching state key")
        if adaptive_coach_key not in st.session_state:
            issues.append("Missing persistent adaptive coach key")
        
        # Check if session has coaching state
        if hasattr(st.session_state, 'session') and st.session_state.session:
            session = st.session_state.session
            if hasattr(session, 'coaching_state') and session.coaching_state:
                session_state_id = id(session.coaching_state)
                
                if coaching_state_key in st.session_state:
                    persistent_state_id = id(st.session_state[coaching_state_key])
                    if session_state_id != persistent_state_id:
                        issues.append(f"Session coaching state mismatch: {session_state_id} != {persistent_state_id}")
        
        # Log validation results
        if issues:
            for issue in issues:
                print(f"DEBUG: VALIDATION ISSUE: {issue}")
        else:
            print("DEBUG: VALIDATION PASSED: Coaching consistency OK")
        
        return len(issues) == 0
    
    @staticmethod
    def force_coaching_sync():
        """FIXED: Force synchronization of all coaching objects."""
        print("DEBUG: Forcing coaching synchronization...")
        
        # Get the authoritative coaching system
        coaching_state, adaptive_coach = CoachingIntegration.get_existing_coaching_system()
        
        # Ensure session has the same coaching state
        if hasattr(st.session_state, 'session') and st.session_state.session:
            if hasattr(st.session_state.session, 'coaching_state'):
                if st.session_state.session.coaching_state != coaching_state:
                    print(f"DEBUG: Syncing session coaching state: {id(st.session_state.session.coaching_state)} -> {id(coaching_state)}")
                    st.session_state.session.coaching_state = coaching_state
        
        print("DEBUG: Coaching synchronization complete")
        return coaching_state, adaptive_coach
    
    @staticmethod
    def setup_session_coaching():
        """
        DEPRECATED: Use get_existing_coaching_system() instead.
        Kept for backwards compatibility.
        """
        return CoachingIntegration.get_existing_coaching_system()
    
    @staticmethod
    def reset_coaching_state():
        """Reset coaching state for new session - FIXED to clear all keys."""
        keys_to_clear = [
            "ccai_persistent_coaching_state",
            "ccai_persistent_adaptive_coach", 
            "coaching_state",
            "adaptive_coach",
            "persistent_coaching_state",
            "persistent_adaptive_coach"
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        print("DEBUG: All coaching state keys cleared")
    
    @staticmethod
    def get_coaching_goal() -> str:
        """Get the appropriate coaching goal based on available features."""
        if ENHANCED_COACHING_AVAILABLE:
            return "Active learning and optimization with session memory"
        else:
            return "Active learning and optimization"
    
    @staticmethod
    def debug_coaching_state():
        """Debug helper to check coaching state persistence."""
        coaching_state_key = "ccai_persistent_coaching_state"
        adaptive_coach_key = "ccai_persistent_adaptive_coach"
        
        print("DEBUG: === COACHING STATE DEBUG ===")
        
        if coaching_state_key in st.session_state:
            coaching_state = st.session_state[coaching_state_key]
            print(f"DEBUG: Persistent coaching state exists: ID {id(coaching_state)}")
            print(f"DEBUG: Is waiting for answer: {coaching_state.is_waiting_for_answer() if coaching_state else 'N/A'}")
        else:
            print("DEBUG: No persistent coaching state found")
        
        if adaptive_coach_key in st.session_state:
            adaptive_coach = st.session_state[adaptive_coach_key]
            print(f"DEBUG: Persistent adaptive coach exists: ID {id(adaptive_coach)}")
        else:
            print("DEBUG: No persistent adaptive coach found")
        
        # Check session coaching state
        if hasattr(st.session_state, 'session') and st.session_state.session:
            if hasattr(st.session_state.session, 'coaching_state') and st.session_state.session.coaching_state:
                session_coaching_id = id(st.session_state.session.coaching_state)
                print(f"DEBUG: Session coaching state: ID {session_coaching_id}")
            else:
                print("DEBUG: Session has no coaching state")
        else:
            print("DEBUG: No session found")
        
        print("DEBUG: === END DEBUG ===")