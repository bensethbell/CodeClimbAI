import streamlit as st
from datetime import datetime
import re
from core.models import MessageRole, ChatMessage, ReviewSession
from core.coaching_models import CoachingState
from templates.examples import get_example_code
from utils.execution import CodeExecutor
from config import ACE_AVAILABLE, CODE_EDITOR_HEIGHT, CODE_EDITOR_THEME, CODE_EDITOR_FONT_SIZE, CODE_EDITOR_TAB_SIZE, CHAT_CONTAINER_HEIGHT, MAX_DEBUG_MESSAGES, MAX_CODE_PREVIEW_LENGTH

# Import ace editor if available
if ACE_AVAILABLE:
    from streamlit_ace import st_ace

class UIComponents:
    """UI component rendering methods."""
    
    @staticmethod
    def render_chat_message(message):
        """Render a single chat message with proper formatting - NO CODE BLOCKS."""
        # Multiple ways to detect if this is an assistant message
        is_assistant = False
        
        # Method 1: Check if it's our enum
        if hasattr(message, 'role') and message.role == MessageRole.ASSISTANT:
            is_assistant = True
            
        # Method 2: Check if role is string "assistant" 
        elif hasattr(message, 'role') and isinstance(message.role, str) and message.role.lower() in ['assistant', 'bot']:
            is_assistant = True
            
        # Method 3: Check if it's a dict with assistant role
        elif isinstance(message, dict) and message.get('role', '').lower() in ['assistant', 'bot']:
            is_assistant = True
            
        # Method 4: Check the enum value directly
        elif hasattr(message, 'role') and hasattr(message.role, 'value') and message.role.value.lower() in ['assistant', 'bot']:
            is_assistant = True
        
        # Force a test: if content contains "Claude:" assume it's assistant
        if "🤖 Claude:" in content or content.startswith("Perfect! I've loaded") or content.startswith("👋 Welcome"):
            is_assistant = True
        
        # Get content safely
        content = ""
        if hasattr(message, 'content'):
            content = message.content
        elif isinstance(message, dict):
            content = message.get('content', str(message))
        else:
            content = str(message)
        
        # Process content for better formatting - NO CODE BLOCKS
        processed_content = UIComponents.format_message_content(content)
        
        if is_assistant:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 15px;">
                <div style="background-color: #e3f2fd; padding: 12px 16px; border-radius: 18px; max-width: 75%; word-wrap: break-word; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                    <strong>🤖 Claude:</strong><br>{processed_content}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 15px;">
                <div style="background-color: #e8f5e8; padding: 12px 16px; border-radius: 18px; max-width: 75%; word-wrap: break-word; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                    <strong>👤 You:</strong><br>{processed_content}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def format_message_content(content: str) -> str:
        """Format message content - NO CODE BLOCKS, preserve all other formatting."""
        # Format **bold** text FIRST (before single asterisks)
        content = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong>\1</strong>', content)
        
        # Format italic text AFTER bold (for submission messages) - be more careful about asterisks
        content = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em style="color: #666; font-style: italic;">\1</em>', content)
        
        # REPLACE CODE BLOCKS WITH INDENTED TEXT - NO BACKGROUNDS
        def format_code_as_text(match):
            language = match.group(1) if match.group(1) else "Code"
            code_content = match.group(2).strip()
            
            # Format as simple indented text
            lines = code_content.split('\n')
            formatted_lines = [f"<strong>{language.upper()}:</strong>"]
            for line in lines:
                formatted_lines.append(f"&nbsp;&nbsp;&nbsp;&nbsp;{line}")
            
            return '<br>'.join(formatted_lines)
        
        # Replace code blocks with formatted text - NO MORE ``` BLOCKS
        content = re.sub(
            r'```(\w+)?\n?(.*?)```', 
            format_code_as_text,
            content, 
            flags=re.DOTALL
        )
        
        # Replace inline code with simple formatting - NO BACKGROUND
        content = re.sub(
            r'`([^`\n]+)`',
            r'<strong style="font-family: monospace;">\1</strong>',
            content
        )
        
        # Format error sections with better styling - PRESERVE
        content = re.sub(
            r'\*\*Error:\*\* ([^\n]+)',
            r'<div style="color: #d32f2f; font-weight: bold; margin: 4px 0;">🚨 Error: \1</div>',
            content
        )
        
        # Format success messages - PRESERVE
        content = re.sub(
            r'✅ \*\*([^*]+)\*\*',
            r'<div style="color: #2e7d2e; font-weight: bold; margin: 4px 0;">✅ \1</div>',
            content
        )
        
        # Convert line breaks to HTML
        content = content.replace('\n', '<br>')
        
        return content
    
    @staticmethod
    def render_welcome_message():
        """Render the welcome message."""
        welcome_msg = ChatMessage(
            MessageRole.ASSISTANT,
            "👋 Welcome! Let's learn through discovery.<br><br><strong>Quick start:</strong><br>• <strong>Type \"example\"</strong> below to get sample code<br>• <strong>Paste your own code</strong> on the left<br>• <strong>Click \"📤 Submit Code\"</strong> to begin learning<br><br>📖 <strong>Full instructions available on the right</strong> - click the dropdown to expand! Ready to start? 🚀"
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