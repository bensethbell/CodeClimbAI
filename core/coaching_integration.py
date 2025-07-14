"""
Coaching system integration helpers for CodeClimbAI.
Extracted from session_manager.py to improve modularity and reduce complexity.
"""
import streamlit as st
from .coaching_models import CoachingState
from .adaptive_coach import AdaptiveCoach

# ENHANCED: Import session memory components
try:
    from .learning_continuity_system import EnhancedCoachingState, SessionMemory
    ENHANCED_COACHING_AVAILABLE = True
except ImportError:
    ENHANCED_COACHING_AVAILABLE = False


class CoachingIntegration:
    """Handles setup and integration of the adaptive coaching system."""
    
    @staticmethod
    def initialize_coaching_state():
        """
        Initialize coaching state with session memory if available.
        
        Returns:
            Initialized coaching state object
        """
        if ENHANCED_COACHING_AVAILABLE:
            coaching_state = EnhancedCoachingState()
        else:
            coaching_state = CoachingState()
        
        return coaching_state
    
    @staticmethod
    def ensure_session_memory(coaching_state):
        """
        Ensure coaching state has session memory if enhanced coaching is available.
        
        Args:
            coaching_state: The coaching state to enhance
        """
        if (ENHANCED_COACHING_AVAILABLE and 
            not hasattr(coaching_state, 'session_memory')):
            coaching_state.session_memory = SessionMemory()
    
    @staticmethod
    def setup_session_coaching():
        """
        Set up coaching state and adaptive coach for the session.
        
        Returns:
            Tuple of (coaching_state, adaptive_coach)
        """
        # Initialize coaching state if not present
        if 'coaching_state' not in st.session_state:
            st.session_state.coaching_state = CoachingIntegration.initialize_coaching_state()
        
        # Initialize adaptive coach if not present
        if 'adaptive_coach' not in st.session_state:
            from .analyzer import CodeAnalyzer
            code_analyzer = CodeAnalyzer()
            st.session_state.adaptive_coach = AdaptiveCoach(code_analyzer)
        
        coaching_state = st.session_state.coaching_state
        adaptive_coach = st.session_state.adaptive_coach
        
        # Ensure session memory exists
        CoachingIntegration.ensure_session_memory(coaching_state)
        
        return coaching_state, adaptive_coach
    
    @staticmethod
    def reset_coaching_state():
        """Reset coaching state for new session."""
        st.session_state.coaching_state = CoachingIntegration.initialize_coaching_state()
        st.session_state.adaptive_coach = None  # Will be reinitialized when needed
    
    @staticmethod
    def get_coaching_goal() -> str:
        """Get the appropriate coaching goal based on available features."""
        if ENHANCED_COACHING_AVAILABLE:
            return "Active learning and optimization with session memory"
        else:
            return "Active learning and optimization"
