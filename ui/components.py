import streamlit as st
from datetime import datetime
import re
from core.models import MessageRole, ChatMessage, ReviewSession
from core.coaching_models import CoachingState
from templates.examples import get_example_code
from utils.execution import CodeExecutor
from config import ACE_AVAILABLE, CODE_EDITOR_HEIGHT, CODE_EDITOR_THEME, CODE_EDITOR_FONT_SIZE, CODE_EDITOR_TAB_SIZE, CHAT_CONTAINER_HEIGHT, MAX_DEBUG_MESSAGES, MAX_CODE_PREVIEW_LENGTH

try:
    from streamlit_ace import st_ace
except ImportError:
    pass

class UIComponents:
    """UI component rendering methods with FIXED MCQ support in code block messages."""
    
    @staticmethod
    def render_chat_message(message):
        """Render a single chat message with FIXED MCQ formatting when code blocks present."""
        is_assistant = False
        
        # Determine if this is an assistant message
        if hasattr(message, 'role') and message.role == MessageRole.ASSISTANT:
            is_assistant = True
        elif hasattr(message, 'role') and str(message.role).lower() == 'assistant':
            is_assistant = True
        elif isinstance(message, dict) and message.get('role') == 'assistant':
            is_assistant = True
        elif str(message).startswith('🤖') or 'Claude:' in str(message):
            is_assistant = True
        
        # Extract content
        content = ""
        if hasattr(message, 'content'):
            content = message.content
        elif isinstance(message, dict):
            content = message.get('content', str(message))
        else:
            content = str(message)
        
        # FIXED: Check for code blocks AND handle MCQ formatting properly
        has_code_blocks = '```' in content
        
        if has_code_blocks:
            # FIXED: Use enhanced method that preserves MCQ formatting
            UIComponents.render_message_with_code_blocks_and_mcq_support(content, is_assistant)
        else:
            # Use original HTML rendering for non-code-block messages
            processed_content = UIComponents.format_message_content_html(content)
            
            if is_assistant:
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-start; margin-bottom: 8px;">
                    <div style="
                        background-color: #e3f2fd; 
                        padding: 10px; 
                        border-radius: 10px; 
                        max-width: 75%;
                        word-wrap: break-word;
                    ">
                        <strong>🤖 Claude:</strong><br>{processed_content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 8px;">
                    <div style="
                        background-color: #e8f5e8; 
                        padding: 10px; 
                        border-radius: 10px; 
                        max-width: 75%;
                        word-wrap: break-word;
                    ">
                        <strong>👤 You:</strong><br>{processed_content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    @staticmethod
    def render_message_with_code_blocks_and_mcq_support(content: str, is_assistant: bool):
        """FIXED: Render message with code blocks while preserving MCQ formatting."""
        
        # PREPROCESS: Clean up any HTML artifacts but preserve MCQ structure
        content = re.sub(r'<div[^>]*class="question-title"[^>]*>', '**', content)
        content = re.sub(r'<div[^>]*class="question-text"[^>]*>', '', content)
        content = re.sub(r'<div[^>]*class="response-instructions"[^>]*>', '\n\n💬 ', content)
        content = re.sub(r'</div>', '**' if 'question-title' in content else '', content)
        content = re.sub(r'<[^>]+>', '', content)
        
        # CRITICAL FIX: Simple, reliable MCQ option formatting
        # Detect if this is MCQ content
        has_mcq_options = bool(re.search(r'\*\*[A-D]\)\*\*', content))
        
        if has_mcq_options:
            # SIMPLE FIX: Just ensure newlines before each option marker
            content = re.sub(r'(\S)\s*(\*\*[A-D]\)\*\*)', r'\1\n\n\2', content)
            
            # Clean up any double newlines that might be excessive
            content = re.sub(r'\n\n\n+', '\n\n', content)
        
        # Clean up extra whitespace but preserve intentional line breaks
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = content.strip()
        
        # Create alignment using columns and render with pure Streamlit
        if is_assistant:
            # Assistant message - left aligned
            col1, col2 = st.columns([4, 1])
            with col1:
                with st.container():
                    st.markdown("🤖 **Claude:**")
                    # CRITICAL: Use pure st.markdown() to preserve MCQ formatting
                    st.markdown(content)
                    st.divider()
        else:
            # User message - right aligned  
            col1, col2 = st.columns([1, 4])
            with col2:
                with st.container():
                    st.markdown("👤 **You:**")
                    st.markdown(content)
                    st.divider()
    
    @staticmethod
    def render_message_with_code_blocks_pure_streamlit(content: str, is_assistant: bool):
        """DEPRECATED: Use render_message_with_code_blocks_and_mcq_support instead."""
        return UIComponents.render_message_with_code_blocks_and_mcq_support(content, is_assistant)
    
    @staticmethod
    def format_message_content_html(content: str) -> str:
        """Format message content for HTML rendering (no code blocks)."""
        # Basic markdown to HTML conversion
        content = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', content)
        
        # Format inline code
        content = re.sub(
            r'`([^`]+)`',
            r'<code style="font-family: monospace; font-weight: bold; background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px;">\1</code>',
            content
        )
        
        # Format error messages
        content = re.sub(
            r'🚨 Error: ([^\n]+)',
            r'<div style="color: #d32f2f; font-weight: bold;">🚨 Error: \1</div>',
            content
        )
        
        # Format success messages
        content = re.sub(
            r'✅ ([^\n]+)',
            r'<div style="color: #2e7d2e; font-weight: bold;">✅ \1</div>',
            content
        )
        
        # Convert newlines to HTML breaks
        content = content.replace('\n', '<br>')
        
        return content
    
    @staticmethod
    def render_welcome_message():
        """Render the welcome message."""
        welcome_msg = ChatMessage(
            MessageRole.ASSISTANT,
            "👋 Welcome! Let's learn through discovery.\n\n**Quick start:**\n• Click **'📚 Get Example'** to load sample code\n• **Paste your own code** on the left\n• **Click '📤 Submit Code'** to begin learning\n\nReady to start? 🚀"
        )
        UIComponents.render_chat_message(welcome_msg)

class UIManager:
    """Manages all UI rendering and user interactions."""
    
    @staticmethod
    def render_code_input_panel():
        """Render the left panel for code input."""
        from .panels import PanelRenderer
        PanelRenderer.render_code_input_panel()
    
    @staticmethod
    def render_chat_panel(assistant):
        """Render the middle panel for chat interface."""
        from .panels import PanelRenderer
        PanelRenderer.render_chat_panel(assistant)
    
    @staticmethod
    def render_instructions_panel():
        """Render the right panel with properly collapsible instructions."""
        from .panels import PanelRenderer
        PanelRenderer.render_instructions_panel()