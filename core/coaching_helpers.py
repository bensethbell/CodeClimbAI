"""
Helper functions for the adaptive coaching system.
Extracted from adaptive_coach.py to reduce file size and manage dependencies.
FIXED: Smart string concatenation detection that recognizes optimal .join() usage.
"""
from typing import Dict, Any, Tuple
from .coaching_models import AnswerStatus, LearningQuestion, QuestionType


class AnswerEvaluator:
    """Handles evaluation of user answers to questions."""
    
    @staticmethod
    def evaluate_answer(user_answer: str, question: LearningQuestion) -> Tuple[bool, str]:
        """
        Evaluate user's answer and provide appropriate feedback.
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
        correct_keywords = question.correct_answer.lower().split()
        has_keywords = any(keyword in user_answer for keyword in correct_keywords)
        
        if has_keywords:
            feedback = f"✅ **Good thinking!** {question.explanation}"
        else:
            feedback = f"💭 **Interesting perspective.** Here's what I was thinking: {question.explanation}"
        
        return has_keywords, feedback


class CodeAnalysisHelper:
    """Helper functions for code analysis in coaching with SMART detection."""
    
    @staticmethod
    def analyze_code_for_coaching(code: str) -> Dict[str, Any]:
        """Analyze code to identify coaching opportunities with smart detection."""
        analysis = {
            # FIXED: Smart string concatenation detection
            'has_string_concat': CodeAnalysisHelper._detect_string_concatenation_issues(code),
            'has_iterrows': '.iterrows()' in code,
            'has_nested_loops': code.count('for ') > 1,
            'has_manual_loop': 'range(len(' in code,
            'has_inefficient_filtering': CodeAnalysisHelper._detect_inefficient_filtering(code),
            'has_unclear_variables': CodeAnalysisHelper._detect_unclear_variables(code),
            'has_list_comprehension_opportunity': CodeAnalysisHelper._detect_list_comp_opportunity(code),
            'has_missing_error_handling': CodeAnalysisHelper._detect_missing_error_handling(code),
            'has_repetitive_code': CodeAnalysisHelper._detect_repetitive_code(code),
            'has_inefficient_data_structure': CodeAnalysisHelper._detect_inefficient_data_structure(code),
            'line_count': len(code.split('\n')),
            'complexity_score': CodeAnalysisHelper._calculate_complexity_score(code)
        }
        
        return analysis
    
    @staticmethod
    def _detect_string_concatenation_issues(code: str) -> bool:
        """
        SMART detection of string concatenation issues.
        Returns True only if there are ACTUAL inefficient concatenation patterns.
        """
        # Check for inefficient += string concatenation in loops
        has_string_concat_in_loop = (
            '+=' in code and 
            'for ' in code and 
            any(s in code.lower() for s in ['str', '"', "'"])
        )
        
        # SMART: If code already uses .join(), it's optimized!
        already_optimized = '.join(' in code
        
        # SMART: Only flag as issue if inefficient pattern exists AND not already optimized
        return has_string_concat_in_loop and not already_optimized
    
    @staticmethod
    def _detect_inefficient_filtering(code: str) -> bool:
        """Detect manual filtering that could use list comprehensions."""
        # Look for manual filtering patterns
        manual_filter_patterns = [
            'for ' in code and 'if ' in code and 'append(' in code,
            'for ' in code and 'if ' in code and '+=' in code
        ]
        
        # If already uses list comprehension, it's optimized
        already_optimized = '[' in code and 'for ' in code and 'if ' in code
        
        return any(manual_filter_patterns) and not already_optimized
    
    @staticmethod
    def _detect_unclear_variables(code: str) -> bool:
        """Detect unclear variable naming."""
        import re
        
        # Look for single-letter variables (except common loop counters)
        single_letters = re.findall(r'\b[a-z]\s*=', code.lower())
        unclear_vars = [var for var in single_letters if var.strip('= ') not in ['i', 'j', 'k', 'x', 'y', 'z']]
        
        return len(unclear_vars) > 2
    
    @staticmethod
    def _detect_list_comp_opportunity(code: str) -> bool:
        """Detect opportunities for list comprehensions."""
        # Look for manual list building that could be comprehensions
        has_manual_building = (
            'for ' in code and 
            'append(' in code and 
            '[]' in code
        )
        
        # If already uses comprehensions, less likely to need more
        already_uses_comprehensions = '[' in code and 'for ' in code
        
        return has_manual_building and not already_uses_comprehensions
    
    @staticmethod
    def _detect_missing_error_handling(code: str) -> bool:
        """Detect missing error handling."""
        has_risky_operations = any([
            'open(' in code,
            'requests.' in code,
            'urllib' in code,
            'json.load' in code,
            '.get(' in code and 'dict' not in code.lower()
        ])
        
        has_error_handling = any([
            'try:' in code,
            'except' in code,
            'finally:' in code
        ])
        
        return has_risky_operations and not has_error_handling
    
    @staticmethod
    def _detect_repetitive_code(code: str) -> bool:
        """Detect repetitive code patterns."""
        lines = [line.strip() for line in code.split('\n') if line.strip()]
        
        # Look for very similar lines (more than 70% similarity)
        similar_count = 0
        for i, line1 in enumerate(lines):
            for line2 in lines[i+1:]:
                if len(line1) > 10 and len(line2) > 10:
                    # Simple similarity check
                    common_chars = len(set(line1) & set(line2))
                    total_chars = len(set(line1) | set(line2))
                    if total_chars > 0 and common_chars / total_chars > 0.7:
                        similar_count += 1
        
        return similar_count > 3
    
    @staticmethod
    def _detect_inefficient_data_structure(code: str) -> bool:
        """Detect inefficient data structure usage."""
        # Look for list usage where set would be better
        inefficient_patterns = [
            'in ' in code and 'list' in code.lower(),
            'for ' in code and 'if ' in code and 'in ' in code and '[' in code
        ]
        
        return any(inefficient_patterns) and 'set(' not in code
    
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
        lines = base_feedback.split('\n')
        clean_parts = []
        
        for line in lines:
            if any(skip_phrase in line for skip_phrase in [
                'Next step:', 'Submit your improved', 'ask for a hint'
            ]):
                break
            clean_parts.append(line)
        
        result = '\n'.join(clean_parts).strip()
        
        # Add intelligent guidance based on struggle pattern
        recent_interactions = coaching_state.interaction_history[-3:] if coaching_state.interaction_history else []
        incorrect_count = sum(1 for i in recent_interactions if i.answer_status == AnswerStatus.INCORRECT)
        
        if incorrect_count >= 2:
            result += "\n\n💡 **Concrete Hint:** Replace `for idx, row in df.iterrows():` with direct operations like `df['new_column'] = df['price'] * 0.2 + df['tax']`. This works on entire columns at once!"
            result += "\n\n🎓 **Learning Options:** Want to try applying this directly, or explore more with another question to solidify your understanding?"
        else:
            result += "\n\n🤔 **Think about this:** Pandas is designed to work with entire columns of data. Instead of processing one row at a time, what if you could do the math on all rows simultaneously?"
            result += "\n\n💡 **Learning Options:** Ask for a more specific hint, or try another question to explore this concept further!"
        
        return result


class NudgeGenerator:
    """Generates nudges for direct coaching guidance."""
    
    @staticmethod
    def create_nudge(code: str, analysis: Dict[str, Any], coaching_state) -> Tuple[str, str]:
        """Create a direct nudge to help the user improve their code."""
        if analysis.get('has_iterrows', False):
            nudge = """🎯 **Optimization Opportunity**: I notice you're using `df.iterrows()` which is quite slow for large datasets. 

**Hint**: Pandas shines with vectorized operations that work on entire columns at once. Try replacing your loop with direct column operations like `df['column1'] * df['column2']`.

Would you like to try optimizing this part of your code?

💡 **Learning Options:** Want a more specific hint, or prefer to explore this with a hands-on question first?"""
        
        elif analysis.get('has_string_concat', False):
            nudge = """🎯 **Performance Tip**: I notice some string building patterns that could be optimized.

**Hint**: Consider using more efficient string operations for better performance with large amounts of text.

Want to give it a try?

💡 **Learning Options:** Need a hint on the exact syntax, or want to explore this concept with another question?"""
        
        elif analysis.get('has_nested_loops', False):
            nudge = """🎯 **Readability Opportunity**: Your code is getting a bit complex. 

**Hint**: Consider breaking it into smaller functions with descriptive names. This makes it easier to test and understand.

What do you think about refactoring this?

💡 **Learning Options:** Ask for guidance on refactoring approaches, or try a question about code organization principles?"""
        
        else:
            nudge = """🎯 **Good work!** Your code looks functional. Let's explore some potential optimizations or improvements together.

What aspect would you like to focus on: performance, readability, or error handling?

💡 **Learning Options:** Want me to ask you a targeted question about optimization, or prefer to dive straight into improving the code?"""
        
        return nudge, "nudge"