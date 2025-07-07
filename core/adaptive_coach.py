"""
Adaptive coaching system for the Learn-As-You-Go Code Review Assistant.
FINAL VERSION: Uses helper functions to reduce file size and eliminate circular imports.
"""

import uuid
from typing import Optional, Dict, Any, Tuple
from .coaching_models import (
    CoachingState, CoachingInteraction, CoachingMode, 
    AnswerStatus, LearningQuestion, QuestionType
)
from .question_templates import QuestionSelector, QuestionTemplates
from .coaching_helpers import AnswerEvaluator, CodeAnalysisHelper, ResponseGenerator, NudgeGenerator
from .analyzer import CodeAnalyzer
from templates.examples import ExampleGenerator, get_example_code


class AdaptiveCoach:
    """
    Main coaching system that decides between asking questions or giving nudges.
    Tracks user progress and adapts teaching strategy accordingly.
    """
    
    def __init__(self, code_analyzer: CodeAnalyzer):
        print("DEBUG: AdaptiveCoach instance created.")
        self.code_analyzer = code_analyzer
        self.question_selector = QuestionSelector()
        self.first_example_shown = False
        self.first_example_code = None
        print("DEBUG: Initial state - first_example_shown:", self.first_example_shown)
        print("DEBUG: Initial state - first_example_code:", self.first_example_code)
    
    def load_example_code(self) -> Tuple[str, str]:
        """Returns a tuple of (code_snippet, category)."""
        if not self.first_example_shown:
            self.first_example_shown = True
            self.first_example_code = get_example_code()
            return self.first_example_code, "performance"

        example_code, category = ExampleGenerator.get_random_example(
            exclude_code=self.first_example_code
        )
        while example_code == self.first_example_code:
            example_code, category = ExampleGenerator.get_random_example(
                exclude_code=self.first_example_code
            )
        return example_code, category
    
    def detect_main_issue_with_claude(self, code: str) -> str:
        """Use Claude/LLM to detect the main issue or learning goal in the user's code."""
        prompt = (
            "Analyze the following Python code and identify the single most important optimization or learning opportunity for the user. "
            "Respond with a short keyword (e.g., 'vectorization', 'readability', 'no_issue').\n\n"
            f"Code:\n{code}"
        )
        return self.code_analyzer.api_client.call_claude(prompt).strip().lower()
    
    def process_code_submission(self, code: str, coaching_state: CoachingState) -> Tuple[str, CoachingMode]:
        print("Processing code submission...")
        code_analysis = CodeAnalysisHelper.analyze_code_for_coaching(code)

        # Set main issue if not already set
        if not coaching_state.main_issue:
            if code_analysis['has_iterrows']:
                coaching_state.main_issue = 'has_iterrows'
            elif code_analysis['has_string_concat']:
                coaching_state.main_issue = 'has_string_concat'
            elif code_analysis['has_nested_loops']:
                coaching_state.main_issue = 'has_nested_loops'
            else:
                coaching_state.main_issue = self.detect_main_issue_with_claude(code)
        
        print("DEBUG: main_issue =", coaching_state.main_issue)
        
        # Map issue keys to analysis flags
        issue_flags = {
            'has_iterrows': code_analysis.get('has_iterrows', False),
            'has_string_concat': code_analysis.get('has_string_concat', False),
            'has_nested_loops': code_analysis.get('has_nested_loops', False),
        }
        print("DEBUG: code_analysis =", code_analysis)
        print("DEBUG: issue_flags =", issue_flags)
        
        # Check if main issue is resolved
        main_issue = coaching_state.main_issue
        if main_issue and main_issue in issue_flags and not issue_flags[main_issue]:
            print("DEBUG: Exiting early due to resolved main issue")
            coaching_state.resolved_issues.add(main_issue)
            return """🎉 **Congratulations!** You've solved the main problem for this example.

            Would you like to:
            • Paste in your own code to analyze?
            • Or type 'example' to load a new sample code snippet?

            Let me know how you'd like to proceed!""", CoachingMode.NUDGE
            
        # Decide between question or nudge
        print("Questions asked:", coaching_state.total_questions_asked)
        print("Success rate:", coaching_state.get_success_rate())
        should_question = self.question_selector.should_ask_question(coaching_state, code_analysis)
        print("Should ask question?", should_question)
        
        if should_question:
            return self._create_learning_question(code, coaching_state, code_analysis)
        else:
            return self._create_nudge(code, code_analysis, coaching_state)

    def handle_user_answer(self, user_answer: str, coaching_state: CoachingState) -> str:
        """Process user's answer with intelligent decision-making."""
        user_answer_lower = user_answer.strip().lower()
        
        # Handle explicit requests first
        if user_answer_lower in ['hint', 'give me a hint', 'need a hint']:
            return self._provide_contextual_hint(coaching_state)
        
        if user_answer_lower in ['explore', 'explore further', 'tell me more']:
            return self._provide_exploration_guidance(coaching_state)
        
        if user_answer_lower == 'example':
            print("DEBUG: 'example' command received.")
            example_code, category = self.load_example_code()
            print("DEBUG: Example loaded:", example_code, category)
            # NO CODE BLOCKS - format as plain text
            return f"Example loaded! Here's a {category} example:\n\n**Python:**\n    {chr(10).join('    ' + line for line in example_code.split(chr(10)))}"
        
        # If waiting for answer to a specific question
        if coaching_state.is_waiting_for_answer():
            current_question = coaching_state.current_interaction.question
            is_correct, base_feedback = AnswerEvaluator.evaluate_answer(user_answer, current_question)
            
            # Complete the interaction
            status = AnswerStatus.CORRECT if is_correct else AnswerStatus.INCORRECT
            coaching_state.complete_current_interaction(user_answer, status)
            
            # Create clean, intelligent response
            if is_correct:
                return ResponseGenerator.create_clean_correct_response(base_feedback, coaching_state)
            else:
                return ResponseGenerator.create_clean_incorrect_response(base_feedback, coaching_state)
        
        # General conversation
        return self._handle_general_conversation(user_answer, coaching_state)
    
    def _provide_contextual_hint(self, coaching_state: CoachingState) -> str:
        """Provide hint based on current context and user progress."""
        recent_interactions = coaching_state.interaction_history[-3:] if coaching_state.interaction_history else []
        incorrect_count = sum(1 for i in recent_interactions 
                             if i.answer_status == AnswerStatus.INCORRECT)
        
        if incorrect_count >= 2:
            return "💡 **Specific Help:** Look at your loop - instead of 'for idx, row in df.iterrows():', try 'df['result'] = df['column1'] * value + df['column2']'. This processes all rows at once!"
        elif coaching_state.get_success_rate() > 0.7:
            return "🧠 **Conceptual Hint:** Think about the difference between imperative (telling the computer how to do each step) and declarative (telling it what you want). Pandas excels at declarative operations."
        else:
            return "💭 **Balanced Hint:** Consider that pandas can perform mathematical operations on entire columns. What would happen if you applied your calculation directly to the columns?"
    
    def _provide_exploration_guidance(self, coaching_state: CoachingState) -> str:
        """Provide exploration guidance based on current learning context."""
        if (coaching_state.interaction_history and 
            coaching_state.interaction_history[-1].answer_status == AnswerStatus.CORRECT):
            return "🔍 **Deeper Question:** Great question! Now think about this: Why do you think vectorized operations are faster? What's happening under the hood that makes column operations more efficient than loops?"
        
        return "🎯 **Let's Explore:** That's a great mindset! Let's dive into the core concept: How do you think pandas handles operations on entire columns vs. processing one row at a time?"
    
    def _handle_general_conversation(self, user_answer: str, coaching_state: CoachingState) -> str:
        """Handle general conversation when not waiting for specific answer."""
        return "I'm here to help with your code! Please submit some code to get started, or ask a specific question about optimization."
    
    def _create_learning_question(self, code: str, coaching_state: CoachingState, 
                                analysis: Dict[str, Any]) -> Tuple[str, CoachingMode]:
        """Create an appropriate learning question using LAZY IMPORT."""
        # LAZY IMPORT: Import QuestionFormatter only when needed to break circular dependency
        from .question_formatter import QuestionFormatter
        
        # Select the best question for this code
        question = self.question_selector.select_question_for_code(code, coaching_state)
        
        # Create coaching interaction using the external formatter
        interaction = CoachingInteraction(
            interaction_id=str(uuid.uuid4()),
            mode=CoachingMode.QUESTION,
            content=QuestionFormatter.format_question_message(question),
            question=question
        )
        
        # Update coaching state
        coaching_state.current_interaction = interaction
        coaching_state.total_questions_asked += 1
        
        return interaction.content, CoachingMode.QUESTION
    
    def _create_nudge(self, code: str, analysis: Dict[str, Any], coaching_state: CoachingState) -> Tuple[str, CoachingMode]:
        """Create a direct nudge to help the user improve their code."""
        nudge_text, mode = NudgeGenerator.create_nudge(code, analysis, coaching_state)
        return nudge_text, CoachingMode.NUDGE