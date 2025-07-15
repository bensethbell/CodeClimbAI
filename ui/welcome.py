"""
Welcome flow management for CodeClimbAI.
Handles welcome popups, banners, and first-time user experience.
"""
import streamlit as st

class WelcomeManager:
    """Manages welcome popups and first-time user experience."""
    
    @staticmethod
    def should_show_welcome_popup():
        """Determine if we should show the welcome popup."""
        # Check if user has seen welcome popup before
        if 'welcome_popup_shown' not in st.session_state:
            st.session_state.welcome_popup_shown = False
        
        # Check if user has any activity (conversation history or code submissions)
        has_activity = (
            (hasattr(st.session_state, 'session') and 
             st.session_state.session and 
             len(st.session_state.session.conversation_history) > 0) or
            (hasattr(st.session_state, 'code_history') and 
             st.session_state.code_history and 
             len(st.session_state.code_history) > 0)
        )
        
        # Show popup if not shown before AND no activity
        return not st.session_state.welcome_popup_shown and not has_activity
    
    @staticmethod
    def create_simple_welcome_popup():
        """Create a Streamlit-compatible welcome popup using native components."""
        with st.container():
            st.success("🚀 **Welcome to CodeClimbAI!**")
            
            st.markdown("""
            ### Transform YOUR code into learning opportunities
            
            **🎯 Learn from your actual code, not textbook examples:**
            - **Submit your real projects** - We analyze YOUR coding patterns and habits
            - **Discover through questioning** - Instead of giving answers, we guide you to insights
            - **Build lasting skills** - Learn optimization thinking that transfers to any codebase
            - **Practice interview scenarios** - Identify and fix performance issues that matter in job interviews
            
            **🚀 Ready to become a better coder?**
            - **Option 1:** Click **"📚 Get Example"** in the left panel to see how it works
            - **Option 2:** Paste your own Python code and click "📤 Submit Code" to start learning from YOUR code
            
            💡 *This isn't about coding faster—it's about coding better through understanding your own patterns.*
            """)
    
    @staticmethod
    def create_compact_welcome_banner():
        """Create a more compact welcome banner for returning users."""
        st.info("🚀 **CodeClimbAI** - Click 'Generate Example' for sample code or paste your own code to begin learning!")
    
    @staticmethod
    def render_welcome_popup():
        """Render the welcome popup if appropriate."""
        if WelcomeManager.should_show_welcome_popup():
            WelcomeManager.create_simple_welcome_popup()
            
            # Create dismissal mechanism
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col2:
                if st.button("✨ Let's Start Learning!", type="primary", use_container_width=True):
                    st.session_state.welcome_popup_shown = True
                    st.session_state.learning_started = True
                    st.rerun()
            
            # Add some spacing
            st.markdown("<br>", unsafe_allow_html=True)
            
            return True  # Popup was shown
        
        return False  # Popup was not shown
    
    @staticmethod
    def render_appropriate_welcome():
        """Render the appropriate welcome message based on user status."""
        # For completely new users - show full popup
        if WelcomeManager.should_show_welcome_popup():
            return WelcomeManager.render_welcome_popup()
        
        # For users who dismissed popup but have minimal activity - show compact banner
        elif (hasattr(st.session_state, 'welcome_popup_shown') and 
              st.session_state.welcome_popup_shown and
              (not hasattr(st.session_state, 'session') or 
               not st.session_state.session or
               len(st.session_state.session.conversation_history) < 3)):
            
            WelcomeManager.create_compact_welcome_banner()
            return True
        
        return False
