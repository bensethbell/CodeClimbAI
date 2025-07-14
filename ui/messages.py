import streamlit as st
import re
from core.models import MessageRole, ChatMessage

class MessageRenderer:
    """Handles rendering of chat messages with TRULY WORKING code blocks."""
    
    @staticmethod
    def render_chat_message(message):
        """Render a single chat message with proper code block support."""
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
        
        # Check if content has code blocks
        has_code_blocks = '```' in content
        
        if has_code_blocks:
            # For messages with code blocks, use PURE Streamlit rendering
            MessageRenderer.render_message_with_code_blocks_pure_streamlit(content, is_assistant)
        else:
            # For messages without code blocks, use HTML styling
            processed_content = MessageRenderer.format_message_content_html(content)
            
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
    def render_message_with_code_blocks_pure_streamlit(content: str, is_assistant: bool):
        """Render message with code blocks using PURE Streamlit with HTML preprocessing."""
        
        # PREPROCESS: Remove any HTML divs that might be in the content
        import re
        
        # Remove HTML div tags but keep their content
        content = re.sub(r'<div[^>]*class="question-title"[^>]*>', '**', content)
        content = re.sub(r'<div[^>]*class="question-text"[^>]*>', '', content)
        content = re.sub(r'<div[^>]*class="response-instructions"[^>]*>', '\n\n💬 ', content)
        content = re.sub(r'</div>', '**' if 'question-title' in content else '', content)
        
        # Clean up any remaining HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up extra whitespace and line breaks
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        content = content.strip()
        
        # Create alignment using columns but render content with pure Streamlit
        if is_assistant:
            # Assistant message - left aligned
            col1, col2 = st.columns([4, 1])
            with col1:
                # Use Streamlit's native styling - NO HTML WRAPPERS
                with st.container():
                    st.markdown("🤖 **Claude:**")
                    # KEY FIX: Pure st.markdown() with NO HTML wrapper
                    st.markdown(content)
                    st.divider()  # Visual separator
        else:
            # User message - right aligned  
            col1, col2 = st.columns([1, 4])
            with col2:
                with st.container():
                    st.markdown("👤 **You:**")
                    # Pure st.markdown() with NO HTML wrapper
                    st.markdown(content)
                    st.divider()  # Visual separator
    
    @staticmethod
    def format_message_content_html(content: str) -> str:
        """Format message content for HTML rendering (no code blocks)."""
        
        # Format **bold** text
        content = re.sub(r'\*\*([^*\n]+)\*\*', r'<strong>\1</strong>', content)
        
        # Format italic text
        content = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', content)
        
        # Replace inline code with simple styling
        content = re.sub(
            r'`([^`\n]+)`',
            r'<code style="font-family: monospace; font-weight: bold; background-color: #f0f0f0; padding: 2px 4px; border-radius: 3px;">\1</code>',
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
        
        # Convert line breaks to HTML
        content = content.replace('\n', '<br>')
        
        return content
    
    @staticmethod
    def render_welcome_message():
        """Render the welcome message."""
        welcome_msg = ChatMessage(
            MessageRole.ASSISTANT,
            "👋 Welcome! Let's learn through discovery.\n\n**Quick start:**\n• Click **'📚 Get Example'** to load sample code\n• **Paste your own code** on the left\n• **Click '📤 Submit Code'** to begin learning\n\nReady to start? 🚀"
        )
        MessageRenderer.render_chat_message(welcome_msg)