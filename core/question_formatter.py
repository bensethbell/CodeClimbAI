"""
Question formatting utilities for the adaptive coaching system.
FIXED VERSION: Removes duplicate letters and implements proper CSS styling.
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
    """Handles formatting of learning questions with FIXED tight spacing and NO duplicate letters."""
    
    @staticmethod
    def format_question_message(question) -> str:
        """
        Format a learning question with FIXED layout - NO DUPLICATE LETTERS.
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
            # BUILD MESSAGE WITH FIXED HTML STRUCTURE
            message_parts = []
            
            # 1. COMPACT HEADER with CSS class
            if hasattr(question, 'title') and question.title:
                header = f'<div class="question-title">📚 {question.title}'
                if hasattr(question, 'question_type') and hasattr(question.question_type, 'value'):
                    header += f' ({question.question_type.value.upper()})'
                header += '</div>'
                message_parts.append(header)
            
            # 2. QUESTION TEXT with CSS class
            if hasattr(question, 'question_text') and question.question_text:
                question_text = f'<div class="question-text">{question.question_text}</div>'
                message_parts.append(question_text)
            else:
                safe_debug_log("❌ Question text is missing or empty")
                return "**Error:** Question text is missing. Please try submitting your code again."
            
            # 3. TOY CODE with COMPACT formatting
            if hasattr(question, 'toy_code') and question.toy_code:
                code_lines = question.toy_code.strip().split('\n')
                formatted_code = '<div style="background-color: #f8f9fa; padding: 8px; border-radius: 6px; margin: 8px 0; font-family: monospace; font-size: 12px; line-height: 1.3;">'
                formatted_code += '<strong>Python:</strong><br>'
                for line in code_lines:
                    formatted_code += f'&nbsp;&nbsp;&nbsp;&nbsp;{line}<br>'
                formatted_code += '</div>'
                message_parts.append(formatted_code)
            
            # 4. MCQ OPTIONS - FIXED to remove duplicate letters
            if (hasattr(question, 'question_type') and 
                hasattr(question.question_type, 'value') and
                question.question_type.value == 'mcq'):
                
                safe_debug_log("🔍 Processing MCQ options with FIXED formatting...")
                
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
                    
                    # Build COMPACT options section with CSS classes - FIXED DUPLICATE LETTERS
                    options_html = '<div class="mcq-options"><strong>Options:</strong><br>'
                    
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
                        
                        # Use CSS class for compact styling - SINGLE LETTER ONLY
                        options_html += f'<div class="mcq-option"><strong>{letter})</strong> {option_text}</div>'
                    
                    options_html += '</div>'
                    message_parts.append(options_html)
                    
                    # COMPACT response instructions with CSS class
                    instructions = '<div class="response-instructions">💬 <strong>How to respond:</strong> Type just the letter (A, B, C, or D)</div>'
                    message_parts.append(instructions)
                    
                    safe_debug_log(f"✅ MCQ formatted successfully with FIXED duplicate letter issue")
            
            # 5. RESPONSE INSTRUCTIONS for other question types
            elif hasattr(question, 'question_type'):
                instructions_text = ""
                if (hasattr(question.question_type, 'value') and 
                    question.question_type.value == 'tf'):
                    instructions_text = '💬 <strong>How to respond:</strong> Type "True" or "False"'
                elif (hasattr(question.question_type, 'value') and 
                      question.question_type.value == 'toy_example'):
                    instructions_text = '💬 <strong>How to respond:</strong> Tell me which option you think is better and briefly why'
                elif (hasattr(question.question_type, 'value') and 
                      question.question_type.value == 'spot_bug'):
                    instructions_text = '💬 <strong>How to respond:</strong> Describe what you think the issue is'
                elif (hasattr(question.question_type, 'value') and 
                      question.question_type.value == 'what_if'):
                    instructions_text = '💬 <strong>How to respond:</strong> Explain what you think would happen'
                else:
                    instructions_text = '💬 <strong>How to respond:</strong> Share your thoughts'
                
                if instructions_text:
                    instructions = f'<div class="response-instructions">{instructions_text}</div>'
                    message_parts.append(instructions)
            
            # 6. BUILD FINAL MESSAGE
            final_message = '\n'.join(message_parts)
            
            # FINAL VALIDATION: Ensure message is substantial
            if len(final_message.strip()) < 50:
                safe_debug_log("❌ Final message too short, potential formatting failure")
                return f"**Question:** {question.question_text}\n\n**How to respond:** Share your thoughts"
            
            safe_debug_log(f"✅ Question formatted successfully with FIXED styling: {len(final_message)} characters")
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