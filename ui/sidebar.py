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
            st.markdown("# 📚 CodeClimbAI Guide")
            
            SidebarManager._render_quick_start_section()
            SidebarManager._render_how_cody_helps_section()
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
        1. **Load Example** - Click "Get Example" for sample code
        2. **Submit Code** - Click "Submit Code" to begin
        3. **Answer Questions** - Cody guides you through discovery
        4. **Apply Learning** - Modify code and resubmit to see progress
        """)
    
    @staticmethod
    def _render_how_cody_helps_section():
        """Render the How Cody Helps section."""
        st.markdown("## 🤖 How Cody Helps")
        st.markdown("""
        **Socratic Learning:** Cody asks questions to guide you to discoveries rather than just giving answers.
        
        **Adaptive Coaching:** Questions adjust based on your progress and understanding level.
        
        **Real Code Testing:** Your code is executed with generated test data to ensure it works.
        
        **Interview Focus:** Prioritizes performance issues that matter in coding interviews.
        """)
    
    @staticmethod
    def _render_during_sessions_section():
        """Render the During Learning Sessions section."""
        st.markdown("## 🎯 During Learning Sessions")
        st.markdown("""
        **Answer Thoughtfully:** Take time to think through questions - discovery learning works best when you engage deeply.
        
        **Ask for Hints:** If stuck, use the hint system to get progressive guidance without revealing the full answer.
        
        **Experiment Freely:** Try different approaches and submit variations to see how they perform.
        
        **Focus on Concepts:** Look for underlying patterns and principles, not just syntax fixes.
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
        
        **Best Practices:**
        - Read questions carefully before answering
        - Think about performance implications
        - Consider maintainability and readability
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
                for entry in st.session_state.learning_log[-3:]:  # Last 3 entries
                    timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%m/%d %H:%M")
                    st.text(f"{timestamp}: {entry['goal']} (hints: {entry['hints_used']})")
    
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