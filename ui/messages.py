import streamlit as st
import re
from core.models import MessageRole, ChatMessage

class MessageRenderer:
    """Handles rendering of chat messages with proper formatting."""
    
    @staticmethod
    def render_chat_message(message):
        """
        Render a single chat message with compact, proper code formatting.
        FIXED: Streamlit Cloud-optimized CSS for proper chat bubble containment.
        """
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
            <div style="display: flex; justify-content: flex-start; margin-bottom: 8px; width: 100%;">
                <div style="
                    background-color: #e3f2fd; 
                    padding: 8px 12px; 
                    border-radius: 12px; 
                    max-width: 80%; 
                    min-width: 200px;
                    width: auto;
                    word-wrap: break-word !important; 
                    overflow-wrap: break-word !important;
                    word-break: break-word !important;
                    hyphens: auto;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1); 
                    font-size: 14px; 
                    line-height: 1.4;
                    overflow: hidden !important;
                    position: relative;
                    box-sizing: border-box !important;
                ">
                    <strong style="font-size: 13px;">🤖 Claude:</strong><br>{processed_content}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 8px; width: 100%;">
                <div style="
                    background-color: #e8f5e8; 
                    padding: 8px 12px; 
                    border-radius: 12px; 
                    max-width: 80%; 
                    min-width: 200px;
                    width: auto;
                    word-wrap: break-word !important; 
                    overflow-wrap: break-word !important;
                    word-break: break-word !important;
                    hyphens: auto;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1); 
                    font-size: 14px; 
                    line-height: 1.4;
                    overflow: hidden !important;
                    position: relative;
                    box-sizing: border-box !important;
                ">
                    <strong style="font-size: 13px;">👤 You:</strong><br>{processed_content}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def format_message_content(content: str) -> str:
        """
        Format message content with proper code blocks and compact styling.
        FIXED: Enhanced CSS for better containment and responsive design.
        """
        # Format **bold** text FIRST (before single asterisks)
        content = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong style="font-size: 14px;">\1</strong>', content)
        
        # Format italic text AFTER bold (for submission messages) - be more careful about asterisks
        content = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em style="color: #666; font-style: italic; font-size: 13px;">\1</em>', content)
        
        # Replace code blocks with STREAMLIT CLOUD-OPTIMIZED formatting
        def format_code_block(match):
            code_content = match.group(2).strip()
            return f'''<div style="
                background-color: #f5f5f5; 
                border-left: 3px solid #007acc; 
                padding: 4px 6px; 
                margin: 4px 0; 
                border-radius: 3px; 
                font-family: 'Courier New', monospace; 
                white-space: pre-wrap !important; 
                overflow-x: hidden !important; 
                font-size: 10px !important;
                max-width: 100% !important;
                width: 100% !important;
                box-sizing: border-box !important;
                word-break: break-all !important;
                overflow-wrap: break-word !important;
                hyphens: none !important;
            "><code style="
                display: block !important;
                max-width: 100% !important;
                width: 100% !important;
                overflow-wrap: break-word !important;
                word-break: break-all !important;
                white-space: pre-wrap !important;
                font-family: 'Courier New', monospace !important;
                font-size: 10px !important;
            ">{code_content}</code></div>'''
        
        content = re.sub(r'```(\w+)?\n?(.*?)```', format_code_block, content, flags=re.DOTALL)
        
        # Replace inline code with STREAMLIT CLOUD-OPTIMIZED formatting
        content = re.sub(
            r'`([^`\n]+)`',
            r'<code style="background-color: #f1f1f1 !important; padding: 1px 2px !important; border-radius: 2px !important; font-family: \'Courier New\', monospace !important; font-size: 10px !important; word-break: break-all !important; overflow-wrap: break-word !important; max-width: 100% !important; display: inline-block !important;">\1</code>',
            content
        )
        
        # Format error sections with RESPONSIVE styling
        content = re.sub(
            r'\*\*Error:\*\* ([^\n]+)',
            r'<div style="color: #d32f2f; font-weight: bold; margin: 3px 0; font-size: 13px; word-wrap: break-word; overflow-wrap: break-word;">🚨 Error: \1</div>',
            content
        )
        
        # Format success messages with RESPONSIVE styling
        content = re.sub(
            r'✅ \*\*([^*]+)\*\*',
            r'<div style="color: #2e7d2e; font-weight: bold; margin: 3px 0; font-size: 13px; word-wrap: break-word; overflow-wrap: break-word;">✅ \1</div>',
            content
        )
        
        # Format MCQ OPTIONS with STREAMLIT CLOUD-OPTIMIZED styling
        content = re.sub(
            r'(\*\*Options:\*\*)',
            r'<div style="font-weight: bold !important; margin: 6px 0 3px 0 !important; font-size: 12px !important; word-wrap: break-word !important; width: 100% !important; box-sizing: border-box !important;">\1</div>',
            content
        )
        
        # Format individual MCQ options with AGGRESSIVE containment for Streamlit Cloud
        # Use simpler string formatting to avoid quote conflicts
        mcq_style = (
            "margin: 1px 0 !important; "
            "padding: 2px 3px !important; "
            "font-size: 11px !important; "
            "line-height: 1.2 !important; "
            "word-wrap: break-word !important; "
            "overflow-wrap: break-word !important; "
            "word-break: break-word !important; "
            "max-width: 100% !important; "
            "width: 100% !important; "
            "box-sizing: border-box !important; "
            "hyphens: auto !important; "
            "display: block !important;"
        )
        
        content = re.sub(
            r'^([A-D])\) (.+)$',
            f'<div style="{mcq_style}"><strong>\\1)</strong> \\2</div>',
            content,
            flags=re.MULTILINE
        )
        
        # Format response instructions with RESPONSIVE styling
        content = re.sub(
            r'(\*\*💬 How to respond:\*\* .+)',
            r'<div style="font-style: italic; color: #666; margin: 6px 0; font-size: 12px; word-wrap: break-word; overflow-wrap: break-word;">\1</div>',
            content
        )
        
        # Convert line breaks to HTML
        content = content.replace('\n', '<br>')
        
        return content
    
    @staticmethod
    def render_welcome_message():
        """Render the welcome message with compact styling."""
        welcome_msg = ChatMessage(
            MessageRole.ASSISTANT,
            "👋 Welcome! Let's learn through discovery.<br><br><strong>Quick start:</strong><br>• <strong>Type \"example\"</strong> below to get sample code<br>• <strong>Paste your own code</strong> on the left<br>• <strong>Click \"📤 Submit Code\"</strong> to begin learning<br><br>📖 <strong>Full instructions available on the right</strong> - click the dropdown to expand! Ready to start? 🚀"
        )
        MessageRenderer.render_chat_message(welcome_msg)