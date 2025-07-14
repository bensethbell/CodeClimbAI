"""
Question formatting utilities for the adaptive coaching system.
CLEAN VERSION: Generates markdown instead of HTML for better compatibility.
"""


def safe_debug_log(msg: str):
    """Safe debug logging that won't fail on import issues."""
    try:
        from .session_manager import add_debug_message
        add_debug_message(msg)
    except ImportError:
        try:
            from core.session_manager import add_debug_message
            add_debug_message(msg)
        except ImportError:
            print(f"DEBUG: {msg}")
    except Exception:
        print(f"DEBUG: {msg}")


class QuestionFormatter:
    """Handles formatting of learning questions with CLEAN MARKDOWN output."""
    
    @staticmethod
    def format_question_message(question) -> str:
        """
        Format a learning question with CLEAN MARKDOWN - NO HTML DIVS.
        """
        # VALIDATION: Ensure question object is properly formed
        if not question:
            print("ERROR: format_question_message received None question")
            return "**Error:** Question object is None. Please try submitting your code again."
        
        # VALIDATION: Check required attributes using duck typing
        required_attrs = ['question_type', 'title', 'question_text']
        for attr in required_attrs:
            if not hasattr(question, attr):
                print(f"ERROR: Question missing required attribute: {attr}")
                return f"**Error:** Question object missing {attr}. Please try submitting your code again."
        
        try:
            # BUILD MESSAGE WITH CLEAN MARKDOWN
            message_parts = []
            
            # 1. CLEAN TITLE
            if hasattr(question, 'title') and question.title:
                title = f'📚 **{question.title}'
                if hasattr(question, 'question_type') and hasattr(question.question_type, 'value'):
                    title += f' ({question.question_type.value.upper()})'
                title += '**'
                message_parts.append(title)
            
            # 2. QUESTION TEXT
            if hasattr(question, 'question_text') and question.question_text:
                message_parts.append(question.question_text)
            else:
                safe_debug_log("❌ Question text is missing or empty")
                return "**Error:** Question text is missing. Please try submitting your code again."
            
            # 3. TOY CODE with CLEAN formatting (already in code blocks from templates)
            if hasattr(question, 'toy_code') and question.toy_code:
                # The toy_code should already be properly formatted from the templates
                message_parts.append(f"```python\n{question.toy_code}\n```")
            
            # 4. MCQ OPTIONS - CLEAN MARKDOWN
            if (hasattr(question, 'question_type') and 
                hasattr(question.question_type, 'value') and
                question.question_type.value == 'mcq'):
                
                safe_debug_log("🔍 Processing MCQ options with CLEAN markdown...")
                
                # Validate options exist
                if not hasattr(question, 'options'):
                    safe_debug_log("❌ MCQ question missing options attribute")
                    message_parts.append("**Error:** Multiple choice options missing.")
                elif not question.options:
                    safe_debug_log("❌ MCQ question has empty options list")
                    message_parts.append("**Error:** Multiple choice options list is empty.")
                elif len(question.options) == 0:
                    safe_debug_log("❌ MCQ question has zero options")
                    message_parts.append("**Error:** No multiple choice options available.")
                else:
                    safe_debug_log(f"✅ MCQ has {len(question.options)} options")
                    
                    # Build CLEAN options section
                    options_parts = ["**Options:**"]
                    
                    for i, option in enumerate(question.options):
                        if not option:
                            safe_debug_log(f"❌ Option {i} is None")
                            continue
                        
                        letter = chr(ord('A') + i)
                        
                        # Safely get option text
                        option_text = ""
                        if hasattr(option, 'text') and option.text:
                            option_text = option.text
                            # CRITICAL FIX: Remove duplicate letter if it starts with the same letter
                            if option_text.startswith(f"{letter}) "):
                                option_text = option_text[3:]  # Remove "A) " from the beginning
                        else:
                            safe_debug_log(f"❌ Option {i} missing text attribute")
                            option_text = f"[Option {letter} - text missing]"
                        
                        # Use clean markdown formatting
                        options_parts.append(f"**{letter})** {option_text}")
                    
                    message_parts.append("\n".join(options_parts))
                    
                    # CLEAN response instructions
                    message_parts.append("💬 **How to respond:** Type just the letter (A, B, C, or D)")
                    
                    safe_debug_log(f"✅ MCQ formatted successfully with clean markdown")
            
            # 5. RESPONSE INSTRUCTIONS for other question types
            elif hasattr(question, 'question_type'):
                if (hasattr(question.question_type, 'value') and 
                    question.question_type.value == 'tf'):
                    message_parts.append('💬 **How to respond:** Type "True" or "False"')
                elif (hasattr(question.question_type, 'value') and 
                      question.question_type.value == 'toy_example'):
                    message_parts.append('💬 **How to respond:** Tell me which option you think is better and briefly why')
                elif (hasattr(question.question_type, 'value') and 
                      question.question_type.value == 'spot_bug'):
                    message_parts.append('💬 **How to respond:** Describe what you think the issue is')
                elif (hasattr(question.question_type, 'value') and 
                      question.question_type.value == 'what_if'):
                    message_parts.append('💬 **How to respond:** Explain what you think would happen')
                else:
                    message_parts.append('💬 **How to respond:** Share your thoughts')
            
            # 6. BUILD FINAL MESSAGE WITH CLEAN SEPARATORS
            final_message = '\n\n'.join(message_parts)
            
            # FINAL VALIDATION: Ensure message is substantial
            if len(final_message.strip()) < 50:
                safe_debug_log("❌ Final message too short, potential formatting failure")
                return f"**Question:** {question.question_text}\n\n**How to respond:** Share your thoughts"
            
            safe_debug_log(f"✅ Question formatted successfully with CLEAN markdown: {len(final_message)} characters")
            return final_message
            
        except Exception as e:
            # ROBUST ERROR HANDLING: Log error but provide fallback
            error_msg = str(e)
            safe_debug_log(f"❌ Question formatting error: {error_msg}")
            
            # Try to provide basic question at minimum
            try:
                if hasattr(question, 'question_text') and question.question_text:
                    return f"**Question:** {question.question_text}\n\n**How to respond:** Share your thoughts"
                else:
                    return "**Error:** Question formatting failed. Please try submitting your code again."
            except:
                return "**Error:** Critical question formatting failure. Please try submitting your code again."