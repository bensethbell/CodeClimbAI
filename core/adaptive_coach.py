"""
Adaptive coaching system for the Learn-As-You-Go Code Review Assistant.
"""

import uuid
from typing import Optional, Dict, Any, Tuple
from .coaching_models import (
    CoachingState, CoachingInteraction, CoachingMode, 
    AnswerStatus, LearningQuestion, QuestionType
)
from .question_templates import QuestionSelector, QuestionTemplates
from .analyzer import CodeAnalyzer

class AdaptiveCoach:
    """
    Main coaching system that decides between asking questions or giving nudges.
    Tracks user progress and adapts teaching strategy accordingly.
    """
    
    def __init__(self, code_analyzer: CodeAnalyzer):
        self.code_analyzer = code_analyzer
        self.question_selector = QuestionSelector()
    
    def process_code_submission(self, code: str, coaching_state: CoachingState) -> Tuple[str, CoachingMode]:
        """
        Process a new code submission and decide on coaching approach.
        
        Args:
            code: The user's submitted code
            coaching_state: Current coaching state
            
        Returns:
            Tuple of (response_message, coaching_mode)
        """
        # Analyze the code for patterns and issues
        code_analysis = self._analyze_code_for_coaching(code)
        
        # Decide whether to ask a question or give a nudge
        should_question = self.question_selector.should_ask_question(coaching_state, code_analysis)
        
        if should_question:
            return self._create_learning_question(code, coaching_state, code_analysis)
        else:
            return self._create_nudge(code, code_analysis)
    
    def handle_user_answer(self, user_answer: str, coaching_state: CoachingState) -> str:
        """
        Process user's answer with intelligent decision-making between hints and questions.
        
        Args:
            user_answer: The user's response
            coaching_state: Current coaching state
            
        Returns:
            Feedback message for the user
        """
        user_answer_lower = user_answer.strip().lower()
        
        # Handle explicit requests first
        if user_answer_lower in ['hint', 'give me a hint', 'need a hint']:
            return self._provide_contextual_hint(coaching_state)
        
        if user_answer_lower in ['explore', 'explore further', 'tell me more']:
            return self._provide_exploration_guidance(coaching_state)
        
        # If waiting for answer to a specific question
        if coaching_state.is_waiting_for_answer():
            current_question = coaching_state.current_interaction.question
            is_correct, base_feedback = self._evaluate_answer(user_answer, current_question)
            
            # Complete the interaction
            status = AnswerStatus.CORRECT if is_correct else AnswerStatus.INCORRECT
            coaching_state.complete_current_interaction(user_answer, status)
            
            # Create clean, intelligent response (no concatenation)
            if is_correct:
                return self._create_clean_correct_response(base_feedback, coaching_state)
            else:
                return self._create_clean_incorrect_response(base_feedback, coaching_state)
        
        # General conversation - not waiting for specific answer
        return self._handle_general_conversation(user_answer, coaching_state)
    
    def _create_clean_correct_response(self, base_feedback: str, coaching_state: CoachingState) -> str:
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
    
    def _create_clean_incorrect_response(self, base_feedback: str, coaching_state: CoachingState) -> str:
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
    
    def _provide_contextual_hint(self, coaching_state: CoachingState) -> str:
        """Provide hint based on current context and user progress."""
        # Check what they're struggling with
        recent_interactions = coaching_state.interaction_history[-3:] if coaching_state.interaction_history else []
        incorrect_count = sum(1 for i in recent_interactions 
                             if i.answer_status == AnswerStatus.INCORRECT)
        
        if incorrect_count >= 2:
            # User is struggling - provide concrete hint
            return "💡 **Specific Help:** Look at your loop - instead of `for idx, row in df.iterrows():`, try `df['result'] = df['column1'] * value + df['column2']`. This processes all rows at once!"
        elif coaching_state.get_success_rate() > 0.7:
            # User doing well - provide conceptual hint
            return "🧠 **Conceptual Hint:** Think about the difference between imperative (telling the computer how to do each step) and declarative (telling it what you want). Pandas excels at declarative operations."
        else:
            # Balanced approach
            return "💭 **Balanced Hint:** Consider that pandas can perform mathematical operations on entire columns. What would happen if you applied your calculation directly to the columns?"
    
    def _provide_exploration_guidance(self, coaching_state: CoachingState) -> str:
        """Provide exploration guidance based on current learning context."""
        # If they just answered correctly, dive deeper
        if (coaching_state.interaction_history and 
            coaching_state.interaction_history[-1].answer_status == AnswerStatus.CORRECT):
            return "🔍 **Deeper Question:** Great question! Now think about this: Why do you think vectorized operations are faster? What's happening under the hood that makes column operations more efficient than loops?"
        
        # If they're exploring without specific context, guide them
        return "🎯 **Let's Explore:** That's a great mindset! Let's dive into the core concept: How do you think pandas handles operations on entire columns vs. processing one row at a time?"
    
    def _handle_general_conversation(self, user_answer: str, coaching_state: CoachingState) -> str:
        """Handle general conversation when not waiting for specific answer."""
        return "I'm here to help with your code! Please submit some code to get started, or ask a specific question about optimization."
    
    # PRESERVED ORIGINAL METHODS - All existing functionality maintained
    
    def _analyze_code_for_coaching(self, code: str) -> Dict[str, Any]:
        """Analyze code to identify coaching opportunities."""
        analysis = {
            'has_iterrows': 'iterrows' in code.lower(),
            'has_string_concat': '+=' in code and any(s in code.lower() for s in ['str', '"', "'"]),
            'has_nested_loops': code.count('for ') > 1,
            'line_count': len(code.split('\n')),
            'complexity_score': self._calculate_complexity_score(code)
        }
        return analysis
    
    def _calculate_complexity_score(self, code: str) -> int:
        """Calculate a simple complexity score for the code."""
        score = 0
        score += code.count('for ') * 2  # Loops add complexity
        score += code.count('if ') * 1   # Conditionals add complexity
        score += code.count('def ') * 1  # Functions add complexity
        return score
    
    def _create_learning_question(self, code: str, coaching_state: CoachingState, 
                                analysis: Dict[str, Any]) -> Tuple[str, CoachingMode]:
        """Create an appropriate learning question."""
        # Select the best question for this code
        question = self.question_selector.select_question_for_code(code, coaching_state)
        
        # Create coaching interaction
        interaction = CoachingInteraction(
            interaction_id=str(uuid.uuid4()),
            mode=CoachingMode.QUESTION,
            content=self._format_question_message(question),
            question=question
        )
        
        # Update coaching state
        coaching_state.current_interaction = interaction
        coaching_state.total_questions_asked += 1
        
        return interaction.content, CoachingMode.QUESTION
    
    def _create_nudge(self, code: str, analysis: Dict[str, Any]) -> Tuple[str, CoachingMode]:
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
        
        return nudge, CoachingMode.NUDGE
    
    def _format_question_message(self, question: LearningQuestion) -> str:
        """Format a learning question for display in chat."""
        message = f"📚 **{question.title}** ({question.question_type.value.upper()})\n\n"
        message += f"{question.question_text}\n\n"
        
        # Add toy code if present
        if question.toy_code:
            message += f"```python\n{question.toy_code}\n```\n\n"
        
        # Add options for multiple choice with clear response format
        if question.is_multiple_choice():
            for option in question.options:
                message += f"{option.text}\n"
            message += "\n**💬 How to respond:** Type just the letter (A, B, C, or D)"
        
        elif question.question_type == QuestionType.TRUE_FALSE:
            message += "**💬 How to respond:** Type 'True' or 'False'"
        
        elif question.question_type == QuestionType.TOY_EXAMPLE:
            message += "**💬 How to respond:** Tell me which option you think is better and briefly why"
        
        elif question.question_type == QuestionType.SPOT_BUG:
            message += "**💬 How to respond:** Describe what you think the issue is"
        
        elif question.question_type == QuestionType.WHAT_IF:
            message += "**💬 How to respond:** Explain what you think would happen"
        
        else:
            message += "**💬 How to respond:** Share your thoughts"
        
        return message
    
    def _evaluate_answer(self, user_answer: str, question: LearningQuestion) -> Tuple[bool, str]:
        """
        Evaluate user's answer to a question.
        
        Returns:
            Tuple of (is_correct, feedback_message)
        """
        user_answer = user_answer.strip().lower()
        
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            return self._evaluate_mcq_answer(user_answer, question)
        
        elif question.question_type == QuestionType.TRUE_FALSE:
            return self._evaluate_tf_answer(user_answer, question)
        
        else:
            return self._evaluate_open_answer(user_answer, question)
    
    def _evaluate_mcq_answer(self, user_answer: str, question: LearningQuestion) -> Tuple[bool, str]:
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
    
    def _evaluate_tf_answer(self, user_answer: str, question: LearningQuestion) -> Tuple[bool, str]:
        """Evaluate true/false question answer."""
        correct_answer = question.correct_answer.lower()
        is_correct = user_answer in ['true', 't'] if correct_answer == 'true' else user_answer in ['false', 'f']
        
        if is_correct:
            feedback = f"✅ **Correct!** {question.explanation}"
        else:
            feedback = f"❌ **Not quite.** The correct answer is **{question.correct_answer}**.\n\n{question.explanation}"
        
        return is_correct, feedback
    
    def _evaluate_open_answer(self, user_answer: str, question: LearningQuestion) -> Tuple[bool, str]:
        """Evaluate open-ended question answer."""
        # For open-ended questions, be more generous with partial credit
        correct_keywords = question.correct_answer.lower().split()
        has_keywords = any(keyword in user_answer for keyword in correct_keywords)
        
        if has_keywords:
            feedback = f"✅ **Good thinking!** {question.explanation}"
        else:
            feedback = f"💭 **Interesting perspective.** Here's what I was thinking: {question.explanation}"
        
        return has_keywords, feedback