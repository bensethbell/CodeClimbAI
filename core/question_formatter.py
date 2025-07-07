"""
Question formatting utilities for the adaptive coaching system.
FIXED: Removed circular import by deferring model imports.
"""


def safe_debug_log(msg: str):
    """Safe debug logging that won't fail on import issues."""
    try:
        # Try relative import first
        from .session_manager import add_debug_message
        add_debug_message(msg)
    except ImportError:
        try:
            # Try absolute import
            from core.session_manager import add_debug_message
            add_debug_message(msg)
        except ImportError:
            # Fall back to print for debugging
            print(f"DEBUG: {msg}")
    except Exception:
        # Silent fallback - don't let debug logging break functionality
        print(f"DEBUG: {msg}")


class QuestionFormatter:
    """Handles formatting of learning questions for display in chat."""
    
    @staticmethod
    def format_question_message(question) -> str:
        """
        Format a learning question for display in chat.
        Enhanced error handling and cloud deployment compatibility.
        FIXED: Uses duck typing instead of importing models to avoid circular imports.
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
            # BUILD MESSAGE STEP BY STEP with validation at each step
            message_parts = []
            
            # 1. Header with validation
            if hasattr(question, 'title') and question.title:
                header = f"📚 **{question.title}**"
                if hasattr(question, 'question_type') and hasattr(question.question_type, 'value'):
                    header += f" ({question.question_type.value.upper()})"
                message_parts.append(header)
            
            # 2. Question text with validation
            if hasattr(question, 'question_text') and question.question_text:
                message_parts.append(question.question_text)
            else:
                safe_debug_log("❌ Question text is missing or empty")
                return "**Error:** Question text is missing. Please try submitting your code again."
            
            # 3. Toy code if present
            if hasattr(question, 'toy_code') and question.toy_code:
                message_parts.append(f"```python\n{question.toy_code}\n```")
            
            # 4. MCQ OPTIONS - CRITICAL SECTION with enhanced validation
            if (hasattr(question, 'question_type') and 
                hasattr(question.question_type, 'value') and
                question.question_type.value == 'mcq'):
                
                safe_debug_log("🔍 Processing MCQ options...")
                
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
                    
                    # Build options section
                    options_section = ["**Options:**"]
                    
                    for i, option in enumerate(question.options):
                        if not option:
                            safe_debug_log(f"❌ Option {i} is None")
                            continue
                        
                        letter = chr(ord('A') + i)
                        
                        # Safely get option text
                        option_text = ""
                        if hasattr(option, 'text') and option.text:
                            option_text = option.text
                        else:
                            safe_debug_log(f"❌ Option {i} missing text attribute")
                            option_text = f"[Option {letter} - text missing]"
                        
                        options_section.append(f"{letter}) {option_text}")
                    
                    # Add options to message
                    message_parts.extend(options_section)
                    message_parts.append("**💬 How to respond:** Type just the letter (A, B, C, or D)")
                    
                    safe_debug_log(f"✅ MCQ formatted successfully with {len(question.options)} options")
            
            # 5. Response instructions for other question types
            elif hasattr(question, 'question_type'):
                if (hasattr(question.question_type, 'value') and 
                    question.question_type.value == 'tf'):
                    message_parts.append("**💬 How to respond:** Type 'True' or 'False'")
                elif (hasattr(question.question_type, 'value') and 
                      question.question_type.value == 'toy_example'):
                    message_parts.append("**💬 How to respond:** Tell me which option you think is better and briefly why")
                elif (hasattr(question.question_type, 'value') and 
                      question.question_type.value == 'spot_bug'):
                    message_parts.append("**💬 How to respond:** Describe what you think the issue is")
                elif (hasattr(question.question_type, 'value') and 
                      question.question_type.value == 'what_if'):
                    message_parts.append("**💬 How to respond:** Explain what you think would happen")
                else:
                    message_parts.append("**💬 How to respond:** Share your thoughts")
            
            # 6. Build final message
            final_message = "\n\n".join(message_parts)
            
            # FINAL VALIDATION: Ensure message is substantial
            if len(final_message.strip()) < 50:
                safe_debug_log("❌ Final message too short, potential formatting failure")
                return f"**Question:** {question.question_text}\n\n**How to respond:** Share your thoughts"
            
            safe_debug_log(f"✅ Question formatted successfully: {len(final_message)} characters")
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