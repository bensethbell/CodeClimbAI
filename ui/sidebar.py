"""
Sidebar management for CodeClimbAI.
Handles instructions, help content, debug info, and learning logs.
"""
import streamlit as st
from datetime import datetime

class SidebarManager:
    """Manages sidebar content including instructions, debug info, and learning logs."""
    
    @staticmethod
    def render_sidebar_instructions():
        """Render comprehensive instructions in the sidebar."""
        with st.sidebar:
            st.markdown("# 📖 Instructions & Help")
            
            SidebarManager._render_quick_start_section()
            SidebarManager._render_how_claude_helps_section()
            SidebarManager._render_during_sessions_section()
            SidebarManager._render_tips_and_commands_section()
            SidebarManager._render_debug_info_section()
            SidebarManager._render_learning_log_section()
            SidebarManager._render_code_history_section()
    
    @staticmethod
    def _render_quick_start_section():
        """Render the Quick Start section."""
        st.markdown("## 🚀 Quick Start")
        st.markdown("""
        1. **Click "Generate Example"** in the left panel to load sample code
        2. **Click "📤 Submit Code"** to begin learning
        3. **Answer the questions** Claude asks about your code
        4. **Make improvements** and resubmit to continue learning
        """)
    
    @staticmethod
    def _render_how_claude_helps_section():
        """Render the How Claude Helps section."""
        st.markdown("## 🤖 How Claude Helps")
        st.markdown("""
        **Socratic Learning:** Claude asks questions to guide you to discoveries rather than just giving answers.
        
        **Adaptive Coaching:** Questions adjust based on your progress and understanding level.
        
        **Real Code Testing:** Your code is executed with generated test data to ensure it works.
        """)
    
    @staticmethod
    def _render_during_sessions_section():
        """Render the During Learning Sessions section."""
        st.markdown("## 🎯 During Learning Sessions")
        st.markdown("""
        **Answer Questions:** Engage with Claude's questions about optimization opportunities
        
        **Ask for Hints:** Type 'hint' or click hint buttons when you're stuck
        
        **Submit Improvements:** Make changes to your code and resubmit to see how you're progressing
        
        **Explore Deeper:** Ask follow-up questions about concepts you're learning
        """)
    
    @staticmethod
    def _render_tips_and_commands_section():
        """Render the Tips & Commands section."""
        st.markdown("## 💡 Tips & Commands")
        st.markdown("""
        **UI Actions:**
        - Click "Generate Example" - Load sample code
        - Type 'test' - Test your current code
        - Type 'hint' - Get a helpful hint
        
        **Learning Tips:**
        - Try to answer questions before asking for hints
        - Experiment with small changes to see their impact
        - Don't worry about getting answers wrong - that's how you learn!
        """)
    
    @staticmethod
    def _render_debug_info_section():
        """Render the Debug Info section if available."""
        if hasattr(st.session_state, 'debug_messages') and st.session_state.debug_messages:
            with st.expander("🔧 Debug Info", expanded=False):
                st.markdown("**Latest activity:**")
                for debug_msg in st.session_state.debug_messages[-4:]:
                    st.text(debug_msg)
    
    @staticmethod
    def _render_learning_log_section():
        """Render the Learning Log section if available."""
        if hasattr(st.session_state, 'learning_log') and st.session_state.learning_log:
            with st.expander("📚 Learning Log", expanded=False):
                for i, entry in enumerate(st.session_state.learning_log, 1):
                    timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%m/%d %H:%M")
                    st.write(f"**{i}.** {entry['goal']} ({timestamp})")
    
    @staticmethod
    def _render_code_history_section():
        """Render the Code History section if available."""
        if (hasattr(st.session_state, 'code_history') and 
            st.session_state.code_history and 
            len(st.session_state.code_history) > 1):
            
            with st.expander(f"🔄 Code History ({len(st.session_state.code_history)} versions)", expanded=False):
                for i, code in enumerate(st.session_state.code_history, 1):
                    st.markdown(f"**Version {i}:**")
                    st.code(code[:60] + "..." if len(code) > 60 else code, language="python")
                    if i < len(st.session_state.code_history):
                        st.markdown("---")
