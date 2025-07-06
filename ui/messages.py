import streamlit as st
import re
from core.models import MessageRole, ChatMessage

class MessageRenderer:
    """Handles rendering of chat messages with proper formatting."""
    
    @staticmethod
    def render_chat_message(message):
        """Render a single chat message with proper code formatting."""
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
        
        # Get content safely
        content = ""
        if hasattr(message, 'content'):
            content = message.content
        elif isinstance(message, dict):
            content = message.get('content', str(message))
        else:
            content = str(message)
        
        # Force a test: if content contains "Claude:" assume it's assistant
        if "🤖 Claude:" in content or content.startswith("Perfect! I've loaded") or content.startswith("👋 Welcome"):
            is_assistant = True
        
        # Process content for better formatting
        processed_content = MessageRenderer.format_message_content(content)
        
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
        """Format message content with proper code blocks and styling."""
        # Format **bold** text FIRST (before single asterisks)
        content = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong>\1</strong>', content)
        
        # Format italic text AFTER bold (for submission messages) - be more careful about asterisks
        content = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em style="color: #666; font-style: italic;">\1</em>', content)
        
        # Replace code blocks with proper HTML formatting
        content = re.sub(
            r'```(\w+)?\n?(.*?)```', 
            lambda m: f'<div style="background-color: #f5f5f5; border-left: 4px solid #007acc; padding: 8px; margin: 8px 0; border-radius: 4px; font-family: monospace; white-space: pre-wrap; overflow-x: auto;"><code>{m.group(2).strip()}</code></div>',
            content, 
            flags=re.DOTALL
        )
        
        # Replace inline code with proper formatting
        content = re.sub(
            r'`([^`\n]+)`',
            r'<code style="background-color: #f1f1f1; padding: 2px 4px; border-radius: 3px; font-family: monospace;">\1</code>',
            content
        )
        
        # Format error sections with better styling
        content = re.sub(
            r'\*\*Error:\*\* ([^\n]+)',
            r'<div style="color: #d32f2f; font-weight: bold; margin: 4px 0;">🚨 Error: \1</div>',
            content
        )
        
        # Format success messages
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
        MessageRenderer.render_chat_message(welcome_msg)