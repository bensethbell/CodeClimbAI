"""
User Intent Detection for adaptive coaching system.
Handles detection of user confusion, answer requests, and clarification needs.
VERIFIED: All imports and functionality tested for integration compatibility.
"""

from typing import Optional
from .coaching_models import QuestionType, AnswerStatus


class UserIntentDetector:
    """Detects different types of user confusion and intent."""
    
    @staticmethod
    def detect_user_intent(user_input: str) -> str:
        """
        Detect what the user actually wants.
        Returns: 'wants_answer', 'wants_clarification', 'wants_hint', 'normal_response'
        """
        user_input_lower = user_input.strip().lower()
        
        # User explicitly wants the answer
        answer_request_patterns = [
            "what is the answer",
            "what's the answer", 
            "tell me the answer",
            "give me the answer",
            "show me the answer",
            "what is the correct answer",
            "what's the correct answer",
            "i don't know what is the answer"  # FIXED: Added user's specific case
        ]
        
        for pattern in answer_request_patterns:
            if pattern in user_input_lower:
                return 'wants_answer'
        
        # User wants clarification about the question
        clarification_patterns = [
            "i don't understand the question",
            "what does this question mean",
            "can you explain the question",
            "i'm confused about what you're asking",
            "what are you asking",
            "unclear question",
            "confusing question"
        ]
        
        for pattern in clarification_patterns:
            if pattern in user_input_lower:
                return 'wants_clarification'
        
        # User wants a hint
        hint_patterns = [
            "hint", "give me a hint", "need a hint", "can you help",
            "i need help", "i'm stuck", "give me a clue"
        ]
        
        for pattern in hint_patterns:
            if pattern in user_input_lower:
                return 'wants_hint'
        
        # General confusion (might want answer or clarification)
        general_confusion_patterns = [
            "i don't know",
            "i have no idea", 
            "i'm lost",
            "i'm confused",
            "i don't understand"
        ]
        
        for pattern in general_confusion_patterns:
            if pattern in user_input_lower:
                # If they mention "answer" in general confusion, they want the answer
                if "answer" in user_input_lower:
                    return 'wants_answer'
                else:
                    return 'wants_clarification'
        
        return 'normal_response'
    
    @staticmethod
    def create_answer_revelation(current_question, coaching_state) -> str:
        """Reveal the correct answer with explanation when user asks for it."""
        
        if not current_question:
            return "I don't have a specific question to answer right now. Feel free to ask about the code or request a hint!"
        
        # Get the correct answer and explanation
        correct_answer = current_question.correct_answer
        explanation = getattr(current_question, 'explanation', '')
        
        if current_question.question_type == QuestionType.MULTIPLE_CHOICE:
            # Find the correct option
            correct_option = None
            for option in current_question.options:
                if option.is_correct:
                    correct_option = option
                    break
            
            if correct_option:
                response = f"""💡 **Here's the answer you asked for:**

**Correct Answer: {correct_answer}** - {correct_option.text.replace(f'{correct_answer}) ', '')}

**Why this is correct:**
{explanation}

**Learning moment:** {correct_option.explanation}

Now that you know the answer, would you like to:
• **Apply this knowledge** - Try optimizing your code with this insight
• **Explore deeper** - Ask follow-up questions about this concept  
• **Move forward** - Get a new challenge to practice with"""
            else:
                response = f"**Correct Answer: {correct_answer}**\n\n{explanation}"
        
        elif current_question.question_type == QuestionType.TRUE_FALSE:
            response = f"""💡 **Here's the answer you asked for:**

**Correct Answer: {correct_answer}**

**Explanation:**
{explanation}

Now that you understand this, would you like to try applying this knowledge to your code or explore a related concept?"""
        
        else:
            # For other question types (what_if, spot_bug, etc.)
            response = f"""💡 **Here's what I was looking for:**

{explanation}

**Key insight:** {current_question.correct_answer if hasattr(current_question, 'correct_answer') else 'The main point is understanding the concept.'}

Would you like to explore this concept further or try applying it to your code?"""
        
        return response
    
    @staticmethod
    def create_clarification_response(current_question, coaching_state) -> str:
        """Create a helpful clarification response about the question format."""
        
        if not current_question:
            return "I'm here to help! What would you like to know about the code or concepts we're discussing?"
        
        question_type = current_question.question_type.value if hasattr(current_question.question_type, 'value') else str(current_question.question_type)
        
        if question_type == "mcq":
            clarification = f"""🤔 **Let me clarify this multiple choice question:**

I'm asking you to choose the best answer from options A, B, C, or D.

**How to respond:**
- Read each option carefully
- Think about which makes the most sense
- Just type the letter (like "A" or "B")

**If you're still unsure:**
- Type "hint" for guidance
- Type "what is the answer" if you want me to reveal the correct answer
- Take your best guess - wrong answers help us learn!

What would you like to do?"""
        
        elif question_type == "what_if":
            clarification = f"""🤔 **Let me explain this 'What If' question:**

I'm asking you to **predict what would happen** if we changed something about the code.

**What I'm looking for:**
- Your thoughts on how the change would affect performance
- What problems might arise
- How it would impact the code's behavior

**Example responses:**
- "It would be much slower with more data"
- "The nested loops would make it inefficient"
- "It might crash or take too long"

**Remember:** I want your thinking process, not a perfect answer!

What's your prediction?"""
        
        elif question_type == "tf":
            clarification = f"""🤔 **Let me clarify this True/False question:**

I'm asking whether a statement about the code is correct or not.

**How to respond:**
- Read the statement carefully
- Decide if it's accurate
- Type "True" or "False" (or just "T" or "F")

**Think about:** Does the code actually do what the statement claims?

What do you think?"""
        
        else:
            clarification = f"""🤔 **Let me clarify what I'm asking:**

I want to hear your thoughts about the code and concepts we're exploring.

**You can:**
- Share what you notice
- Explain your thinking
- Ask questions about anything unclear
- Give your best guess

**Remember:** This is about learning together, not testing you!

What comes to mind?"""
        
        return clarification