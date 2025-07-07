"""
Helper functions for the adaptive coaching system.
Extracted from adaptive_coach.py to reduce file size and manage dependencies.
"""

from typing import Dict, Any, Tuple
from .coaching_models import AnswerStatus, LearningQuestion, QuestionType


class AnswerEvaluator:
    """Handles evaluation of user answers to questions."""
    
    @staticmethod
    def evaluate_answer(user_answer: str, question: LearningQuestion) -> Tuple[bool, str]:
        """
        Evaluate user's answer to a question.
        
        Returns:
            Tuple of (is_correct, feedback_message)
        """
        user_answer = user_answer.strip().lower()
        
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            return AnswerEvaluator._evaluate_mcq_answer(user_answer, question)
        
        elif question.question_type == QuestionType.TRUE_FALSE:
            return AnswerEvaluator._evaluate_tf_answer(user_answer, question)
        
        else:
            return AnswerEvaluator._evaluate_open_answer(user_answer, question)
    
    @staticmethod
    def _evaluate_mcq_answer(user_answer: str, question: LearningQuestion) -> Tuple[bool, str]:
        """Evaluate multiple choice question answer."""
        correct_letter = question.correct_answer.lower()
        is_correct = user_answer == correct_letter
        
        # Find the selected option for feedback
        option_map = {chr(ord('a') + i): opt for i, opt in enumerate(question.options)}
        selected_option = option_map.get(user_answer)
        
        if is_correct:
            feedback = f"✅ **Correct!** Great job!\n\n{question.explanation}"
        else:
            if selected_option:
                feedback = f"❌ **Not quite.** {selected_option.explanation}\n\n**Correct answer:** {question.correct_answer}) {option_map[correct_letter].text}\n\n{question.explanation}"
            else:
                feedback = f"❌ **Invalid answer.** Please choose A, B, C, or D.\n\n**Correct answer:** {question.correct_answer}) {option_map[correct_letter].text}"
        
        return is_correct, feedback
    
    @staticmethod
    def _evaluate_tf_answer(user_answer: str, question: LearningQuestion) -> Tuple[bool, str]:
        """Evaluate true/false question answer."""
        correct_answer = question.correct_answer.lower()
        is_correct = user_answer in ['true', 't'] if correct_answer == 'true' else user_answer in ['false', 'f']
        
        if is_correct:
            feedback = f"✅ **Correct!** {question.explanation}"
        else:
            feedback = f"❌ **Not quite.** The correct answer is **{question.correct_answer}**.\n\n{question.explanation}"
        
        return is_correct, feedback
    
    @staticmethod
    def _evaluate_open_answer(user_answer: str, question: LearningQuestion) -> Tuple[bool, str]:
        """Evaluate open-ended question answer."""
        # For open-ended questions, be more generous with partial credit
        correct_keywords = question.correct_answer.lower().split()
        has_keywords = any(keyword in user_answer for keyword in correct_keywords)
        
        if has_keywords:
            feedback = f"✅ **Good thinking!** {question.explanation}"
        else:
            feedback = f"💭 **Interesting perspective.** Here's what I was thinking: {question.explanation}"
        
        return has_keywords, feedback


class CodeAnalysisHelper:
    """Helper functions for code analysis in coaching."""
    
    @staticmethod
    def analyze_code_for_coaching(code: str) -> Dict[str, Any]:
        """Analyze code to identify coaching opportunities."""
        analysis = {
            'has_iterrows': 'iterrows' in code.lower(),
            'has_string_concat': '+=' in code and any(s in code.lower() for s in ['str', '"', "'"]),
            'has_nested_loops': code.count('for ') > 1,
            'line_count': len(code.split('\n')),
            'complexity_score': CodeAnalysisHelper._calculate_complexity_score(code)
        }
        return analysis
    
    @staticmethod
    def _calculate_complexity_score(code: str) -> int:
        """Calculate a simple complexity score for the code."""
        score = 0
        score += code.count('for ') * 2  # Loops add complexity
        score += code.count('if ') * 1   # Conditionals add complexity
        score += code.count('def ') * 1  # Functions add complexity
        return score


class ResponseGenerator:
    """Generates clean, intelligent responses for coaching interactions."""
    
    @staticmethod
    def create_clean_correct_response(base_feedback: str, coaching_state) -> str:
        """Create clean, intelligent response for correct answers without duplication."""
        # Extract core feedback without generic next steps
        lines = base_feedback.split('\n')
        clean_parts = []
        
        for line in lines:
            # Keep the main feedback but skip redundant next steps
            if any(skip_phrase in line for skip_phrase in [
                'Next step:', 'Submit your improved', 'ask for a hint', 
                'when ready', 'if you need guidance'
            ]):
                break
            clean_parts.append(line)
        
        # Build clean response with intelligent next step
        result = '\n'.join(clean_parts).strip()
        
        # Add single, intelligent next step based on user performance
        success_rate = coaching_state.get_success_rate()
        
        if success_rate > 0.8 and coaching_state.total_questions_asked >= 2:
            # High performer - advanced challenge
            result += "\n\n🎯 **Advanced Challenge:** Now that you understand this concept, what do you think happens to performance when you have nested loops processing large datasets? Can you predict the time complexity?"
            result += "\n\n💡 **Learning Options:** Want a hint to guide your thinking, or prefer another hands-on question to test your understanding?"
        elif success_rate > 0.6:
            # Good performer - practical application
            result += "\n\n🔧 **Apply It:** Try modifying your code to use vectorized operations. Replace the loop with direct column operations and submit your improved version!"
            result += "\n\n💡 **Learning Options:** Need a hint on vectorized syntax, or want to explore this concept with another question first?"
        else:
            # Building confidence - supportive guidance
            result += "\n\n✨ **Great progress!** Now try changing just the calculation part to work with entire columns instead of individual rows. You've got this!"
            result += "\n\n💡 **Learning Options:** Ask for a hint if you need guidance, or request another question to practice this concept more!"
        
        return result
    
    @staticmethod
    def create_clean_incorrect_response(base_feedback: str, coaching_state) -> str:
        """Create clean, supportive response for incorrect answers."""
        # Extract core feedback without generic encouragement
        lines = base_feedback.split('\n')
        clean_parts = []
        
        for line in lines:
            # Keep explanation but skip generic encouragement
            if any(skip_phrase in line for skip_phrase in [
                'Keep learning:', 'try another question', 'ask for a hint about'
            ]):
                break
            clean_parts.append(line)
        
        result = '\n'.join(clean_parts).strip()
        
        # Add intelligent guidance based on struggle pattern
        recent_interactions = coaching_state.interaction_history[-3:] if coaching_state.interaction_history else []
        incorrect_count = sum(1 for i in recent_interactions if i.answer_status == AnswerStatus.INCORRECT)
        
        if incorrect_count >= 2:
            # Multiple wrong answers - concrete help
            result += "\n\n💡 **Concrete Hint:** Replace `for idx, row in df.iterrows():` with direct operations like `df['new_column'] = df['price'] * 0.2 + df['tax']`. This works on entire columns at once!"
            result += "\n\n🎓 **Learning Options:** Want to try applying this directly, or explore more with another question to solidify your understanding?"
        else:
            # Single wrong answer - conceptual encouragement
            result += "\n\n🤔 **Think about this:** Pandas is designed to work with entire columns of data. Instead of processing one row at a time, what if you could do the math on all rows simultaneously?"
            result += "\n\n💡 **Learning Options:** Ask for a more specific hint, or try another question to explore this concept further!"
        
        return result


class NudgeGenerator:
    """Generates nudges for direct coaching guidance."""
    
    @staticmethod
    def create_nudge(code: str, analysis: Dict[str, Any], coaching_state) -> Tuple[str, str]:
        """Create a direct nudge to help the user improve their code."""
        
        if analysis['has_iterrows']:
            nudge = """🎯 **Optimization Opportunity**: I notice you're using `df.iterrows()` which is quite slow for large datasets. 

**Hint**: Pandas shines with vectorized operations that work on entire columns at once. Try replacing your loop with direct column operations like `df['column1'] * df['column2']`.

Would you like to try optimizing this part of your code?

💡 **Learning Options:** Want a more specific hint, or prefer to explore this with a hands-on question first?"""
        
        elif analysis['has_string_concat']:
            nudge = """🎯 **Performance Tip**: Building strings with `+=` in a loop can be slow for large amounts of text.

**Hint**: Consider collecting your strings in a list and using `''.join(list)` at the end for better performance.

Want to give it a try?

💡 **Learning Options:** Need a hint on the exact syntax, or want to explore this concept with another question?"""
        
        elif analysis['complexity_score'] > 6:
            nudge = """🎯 **Readability Opportunity**: Your code is getting a bit complex. 

**Hint**: Consider breaking it into smaller functions with descriptive names. This makes it easier to test and understand.

What do you think about refactoring this?

💡 **Learning Options:** Ask for guidance on refactoring approaches, or try a question about code organization principles?"""
        
        else:
            nudge = """🎯 **Good work!** Your code looks functional. Let's explore some potential optimizations or improvements together.

What aspect would you like to focus on: performance, readability, or error handling?

💡 **Learning Options:** Want me to ask you a targeted question about optimization, or prefer to dive straight into improving the code?"""
        
        return nudge, "nudge"
