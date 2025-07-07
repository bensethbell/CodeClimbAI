import streamlit as st
import re
from core.models import MessageRole, ChatMessage

class MessageRenderer:
    """Handles rendering of chat messages with BASIC formatting only."""
    
    @staticmethod
    def render_chat_message(message):
        """Render a single chat message with BASIC, non-aggressive CSS."""
        # Detect if this is an assistant message
        is_assistant = False
        
        if hasattr(message, 'role') and message.role == MessageRole.ASSISTANT:
            is_assistant = True
        elif hasattr(message, 'role') and isinstance(message.role, str) and message.role.lower() in ['assistant', 'bot']:
            is_assistant = True
        elif isinstance(message, dict) and message.get('role', '').lower() in ['assistant', 'bot']:
            is_assistant = True
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
        
        # Process content for basic formatting
        processed_content = MessageRenderer.format_message_content(content)
        
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
    def format_message_content(content: str) -> str:
        """Format message content with BASIC styling - no aggressive CSS."""
        
        # Format **bold** text
        content = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong>\1</strong>', content)
        
        # Format italic text
        content = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', content)
        
        # Replace code blocks with BASIC formatting
        def format_code_block(match):
            code_content = match.group(2).strip()
            return f'''<div style="
                background-color: #f5f5f5; 
                border-left: 3px solid #007acc; 
                padding: 8px; 
                margin: 8px 0; 
                font-family: monospace; 
                white-space: pre-wrap;
            ">{code_content}</div>'''
        
        content = re.sub(r'```(\w+)?\n?(.*?)```', format_code_block, content, flags=re.DOTALL)
        
        # Replace inline code with MINIMAL styling
        content = re.sub(
            r'`([^`\n]+)`',
            r'<code style="background-color: #f1f1f1; padding: 2px 4px; border-radius: 3px; font-family: monospace;">\1</code>',
            content
        )
        
        # Format error sections
        content = re.sub(
            r'\*\*Error:\*\* ([^\n]+)',
            r'<div style="color: #d32f2f; font-weight: bold;">🚨 Error: \1</div>',
            content
        )
        
        # Format success messages
        content = re.sub(
            r'✅ \*\*([^*]+)\*\*',
            r'<div style="color: #2e7d2e; font-weight: bold;">✅ \1</div>',
            content
        )
        
        # Format MCQ OPTIONS with BASIC styling
        content = re.sub(
            r'(\*\*Options:\*\*)',
            r'<div style="font-weight: bold; margin: 8px 0 4px 0;">\1</div>',
            content
        )
        
        # Format individual MCQ options with BASIC styling
        content = re.sub(
            r'^([A-D])\) (.+)$',
            r'<div style="margin: 4px 0; padding: 4px;"><strong>\1)</strong> \2</div>',
            content,
            flags=re.MULTILINE
        )
        
        # Format response instructions
        content = re.sub(
            r'(\*\*💬 How to respond:\*\* .+)',
            r'<div style="font-style: italic; color: #666; margin: 8px 0;">\1</div>',
            content
        )
        
        # Convert line breaks to HTML
        content = content.replace('\n', '<br>')
        
        return content
    
    @staticmethod
    def render_welcome_message():
        """Render the welcome message with basic styling."""
        welcome_msg = ChatMessage(
            MessageRole.ASSISTANT,
            "👋 Welcome! Let's learn through discovery.<br><br><strong>Quick start:</strong><br>• <strong>Type \"example\"</strong> below to get sample code<br>• <strong>Paste your own code</strong> on the left<br>• <strong>Click \"📤 Submit Code\"</strong> to begin learning<br><br>📖 <strong>Full instructions available on the right</strong> - click the dropdown to expand! Ready to start? 🚀"
        )
        MessageRenderer.render_chat_message(welcome_msg)