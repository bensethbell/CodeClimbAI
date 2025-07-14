"""
Adaptive coaching system core - enhanced with smart code snippet inclusion.
ENHANCED VERSION: Automatically includes relevant code snippets for long code files.
"""

import uuid
from typing import Optional, Dict, Any, Tuple, List
from .coaching_models import (
    CoachingState, CoachingInteraction, CoachingMode, 
    AnswerStatus, LearningQuestion, QuestionType
)
from .question_templates import QuestionSelector, QuestionTemplates
from .coaching_helpers import AnswerEvaluator, CodeAnalysisHelper, ResponseGenerator, NudgeGenerator
from .analyzer import CodeAnalyzer
from .code_snippet_analyzer import CodeSnippetAnalyzer  # NEW: Import snippet analyzer
from templates.examples import ExampleGenerator, get_example_code

# ENHANCED: Import session memory and learning continuity components
try:
    from .learning_continuity_system import (
        SessionMemory, EnhancedQuestionSelector, 
        EnhancedCoachingState, LearningProgress, QuestionMemory
    )
    ENHANCED_COACHING_AVAILABLE = True
except ImportError:
    ENHANCED_COACHING_AVAILABLE = False

# Import enhanced response generators
from .user_intent_detector import UserIntentDetector
from .interview_analyzer import InterviewCriticalAnalyzer
from .enhanced_response_generators import EnhancedResponseGenerator, EnhancedNudgeGenerator


class AdaptiveCoach:
    """
    Main coaching system with enhanced confusion detection, learning continuity, and smart code snippets.
    ENHANCED: Automatically includes relevant code snippets for long code files.
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
    
    def enhanced_process_code_submission(self, code: str, coaching_state: CoachingState) -> Tuple[str, CoachingMode]:
        """
        ENHANCED: Process code submission with interview-critical issue detection and smart code snippets.
        """
        print("Processing code submission with interview-critical analysis and snippet enhancement...")
        code_analysis = CodeAnalysisHelper.analyze_code_for_coaching(code)
        print("DEBUG: Enhanced code_analysis =", code_analysis)

        # Set main issue if not already set
        if not coaching_state.main_issue:
            # Get interview-critical issues in priority order
            critical_issues = InterviewCriticalAnalyzer.get_interview_critical_issues(code_analysis)
            
            if critical_issues:
                coaching_state.main_issue = critical_issues[0]
                print(f"DEBUG: Set main issue to top critical issue: {coaching_state.main_issue}")
            else:
                # Fallback to Claude detection if no critical issues found
                coaching_state.main_issue = self.detect_main_issue_with_claude(code)
                print(f"DEBUG: No critical issues, using Claude detection: {coaching_state.main_issue}")
        
        print("DEBUG: Enhanced main_issue =", coaching_state.main_issue)
        
        # Check if main issue is resolved with broader flags
        issue_flags = {
            'has_iterrows': code_analysis.get('has_iterrows', False),
            'has_string_concat': code_analysis.get('has_string_concat', False),
            'has_nested_loops': code_analysis.get('has_nested_loops', False),
            'has_manual_loop': code_analysis.get('has_manual_loop', False),
            'has_inefficient_filtering': code_analysis.get('has_inefficient_filtering', False),
            'has_unclear_variables': code_analysis.get('has_unclear_variables', False),
            'has_list_comprehension_opportunity': code_analysis.get('has_list_comprehension_opportunity', False),
            'has_missing_error_handling': code_analysis.get('has_missing_error_handling', False),
            'has_repetitive_code': code_analysis.get('has_repetitive_code', False),
            'has_inefficient_data_structure': code_analysis.get('has_inefficient_data_structure', False),
        }
        
        print("DEBUG: Enhanced issue_flags =", issue_flags)
        
        # Check if main issue is resolved
        main_issue = coaching_state.main_issue
        if main_issue and main_issue in issue_flags and not issue_flags[main_issue]:
            print("DEBUG: Main issue resolved, checking for next critical issues...")
            coaching_state.resolved_issues.add(main_issue)
            
            # Look for next interview-critical issue
            remaining_critical_issues = [
                issue for issue in InterviewCriticalAnalyzer.get_interview_critical_issues(code_analysis)
                if issue not in coaching_state.resolved_issues and issue_flags.get(issue, False)
            ]
            
            if remaining_critical_issues:
                next_critical_issue = remaining_critical_issues[0]
                coaching_state.main_issue = next_critical_issue
                
                # Explain why this next issue is important
                priority_explanation = InterviewCriticalAnalyzer.get_issue_priority_explanation(next_critical_issue)
                
                base_response = f"""🎉 **Great progress!** You've addressed the {main_issue.replace('_', ' ')} issue.

**🚨 Interview Alert:** I notice another critical optimization opportunity that would be **essential to fix in a coding interview**:

{priority_explanation}

**Your options:**
• **Continue optimizing** - Address this critical issue (recommended for interview prep)
• **Generate new example** - Click the 'Generate Example' button for different practice
• **See best solution** - I can show you the optimal approach and explain why it's better

What would you like to focus on?"""
                
                # ENHANCED: Add code snippet for long code
                enhanced_response = CodeSnippetAnalyzer.enhance_question_with_snippet(
                    base_response, code, code_analysis, next_critical_issue
                )
                
                return enhanced_response, CoachingMode.NUDGE
            
            else:
                # Check for any remaining non-critical issues
                remaining_issues = [flag for flag, value in issue_flags.items() if value and flag not in coaching_state.resolved_issues]
                
                if remaining_issues:
                    print("DEBUG: Found remaining non-critical issues:", remaining_issues)
                    coaching_state.main_issue = remaining_issues[0]
                    
                    base_response = f"""🎉 **Excellent work!** You've addressed all the critical interview-level issues.

There are still some minor optimizations possible, but your code is now **interview-ready** for the main performance concerns.

**Your options:**
• **Polish further** - Address remaining minor optimizations  
• **See best solution** - Compare your approach with the optimal solution
• **New challenge** - Click 'Generate Example' for a different optimization problem

How would you like to proceed?"""
                    
                    # ENHANCED: Add code snippet for long code
                    enhanced_response = CodeSnippetAnalyzer.enhance_question_with_snippet(
                        base_response, code, code_analysis, remaining_issues[0]
                    )
                    
                    return enhanced_response, CoachingMode.NUDGE
                
                else:
                    print("DEBUG: No remaining issues, code is fully optimized")
                    
                    return f"""🎉 **Outstanding!** You've created **interview-level optimized code**.

All major performance issues have been resolved. Your solution demonstrates:
• Strong optimization awareness
• Good algorithmic thinking  
• Interview-ready code quality

**Your options:**
• **Compare solutions** - See the optimal approach and learn advanced techniques
• **New challenge** - Click 'Generate Example' for different optimization practice
• **Analyze your own code** - Paste your real code for optimization review

Ready for the next challenge?""", CoachingMode.NUDGE
                
        # Continue with existing logic for questions vs nudges
        should_question = self.question_selector.should_ask_question(coaching_state, code_analysis)
        print("Should ask question?", should_question)
        
        if should_question:
            return self._create_enhanced_learning_question(code, coaching_state, code_analysis)
        else:
            return self._create_enhanced_nudge(code, code_analysis, coaching_state)

    def process_code_submission(self, code: str, coaching_state: CoachingState) -> Tuple[str, CoachingMode]:
        """Use enhanced processing by default."""
        return self.enhanced_process_code_submission(code, coaching_state)

    def handle_user_answer(self, user_answer: str, coaching_state) -> str:
        """Process user's answer with session memory updates."""
        user_answer_lower = user_answer.strip().lower()
        
        # Ensure coaching_state has session memory
        if not hasattr(coaching_state, 'session_memory'):
            coaching_state.session_memory = SessionMemory()
        
        # Detect user intent first
        user_intent = UserIntentDetector.detect_user_intent(user_answer)
        
        if user_intent == 'wants_answer':
            # User explicitly wants the correct answer revealed
            if coaching_state.is_waiting_for_answer():
                response = UserIntentDetector.create_answer_revelation(
                    coaching_state.current_interaction.question,
                    coaching_state
                )
                # Complete the interaction as if they got it right (they asked for help)
                coaching_state.complete_current_interaction(user_answer, AnswerStatus.CORRECT)
                return response
            else:
                return "I don't have a specific question to answer right now. Feel free to ask about the code or request a hint!"
        
        elif user_intent == 'wants_clarification':
            # User wants clarification about the question format/meaning
            return UserIntentDetector.create_clarification_response(
                coaching_state.current_interaction.question if coaching_state.current_interaction else None,
                coaching_state
            )
        
        elif user_intent == 'wants_hint':
            # User wants a hint
            return self._provide_contextual_hint_with_memory(coaching_state)
        
        # Handle explicit 'explore' requests
        if user_answer_lower in ['explore', 'explore further', 'tell me more']:
            return self._provide_exploration_guidance_with_memory(coaching_state)
        
        # Handle 'example' command
        if user_answer_lower == 'example':
            print("DEBUG: 'example' command received.")
            example_code, category = self.load_example_code()
            print("DEBUG: Example loaded:", example_code, category)
            return f"Example loaded! Here's a {category} example:\n\n**Python:**\n    {chr(10).join('    ' + line for line in example_code.split(chr(10)))}"
        
        # If waiting for answer to a specific question (normal flow)
        if coaching_state.is_waiting_for_answer():
            current_question = coaching_state.current_interaction.question
            is_correct, base_feedback = AnswerEvaluator.evaluate_answer(user_answer, current_question)
            
            # Complete the interaction (this will update session memory)
            status = AnswerStatus.CORRECT if is_correct else AnswerStatus.INCORRECT
            coaching_state.complete_current_interaction(user_answer, status)
            
            # Add learning progress info to response
            base_response = ""
            if is_correct:
                base_response = EnhancedResponseGenerator.create_clean_correct_response(base_feedback, coaching_state)
            else:
                base_response = EnhancedResponseGenerator.create_clean_incorrect_response(base_feedback, coaching_state)
            
            # Add session learning context if appropriate
            if coaching_state.total_questions_asked > 1:  # Only after first question
                session_summary = coaching_state.session_memory.get_learning_summary()
                if session_summary and session_summary != "This is your first question in this session.":
                    base_response += f"\n\n📈 **Your Learning Progress:**\n{session_summary}"
            
            return base_response
        
        # General conversation
        return self._handle_general_conversation(user_answer, coaching_state)

    def _provide_contextual_hint_with_memory(self, coaching_state) -> str:
        """Provide hint considering session learning history."""
        
        # Get basic hint
        basic_hint = self._provide_contextual_hint(coaching_state)
        
        # Add learning context if we have session memory
        if hasattr(coaching_state, 'session_memory') and coaching_state.session_memory.question_history:
            current_concept = None
            if coaching_state.current_interaction and coaching_state.current_interaction.question:
                # Try to determine current concept
                current_concept = self._determine_question_concept(coaching_state.current_interaction.question)
            
            if current_concept:
                concept_status = coaching_state.session_memory.learning_progress.get_concept_status(current_concept)
                
                if concept_status == 'mastered':
                    basic_hint += f"\n\n💪 **You've mastered {current_concept.replace('_', ' ')} before!** Apply that same insight here."
                elif concept_status == 'learning':
                    basic_hint += f"\n\n📚 **Building on your {current_concept.replace('_', ' ')} knowledge...** Think about patterns you've seen."
                elif concept_status == 'struggling':
                    basic_hint += f"\n\n🔄 **Let's reinforce {current_concept.replace('_', ' ')}** - this is a key concept worth mastering."
        
        return basic_hint

    def _provide_exploration_guidance_with_memory(self, coaching_state) -> str:
        """Provide exploration considering session learning history."""
        
        # Get basic exploration guidance
        basic_guidance = self._provide_exploration_guidance(coaching_state)
        
        # Add connections to previous learning
        if hasattr(coaching_state, 'session_memory') and coaching_state.session_memory.session_concepts:
            concepts_learned = list(coaching_state.session_memory.session_concepts)
            if len(concepts_learned) > 1:
                concept_names = [c.replace('_', ' ').title() for c in concepts_learned[-3:]]  # Last 3 concepts
                basic_guidance += f"\n\n🔗 **Connecting concepts:** You've been exploring {', '.join(concept_names)}. How do these optimization patterns relate to each other?"
        
        return basic_guidance

    def _determine_question_concept(self, question) -> Optional[str]:
        """Determine the main concept of a question."""
        if not question or not hasattr(question, 'question_text'):
            return None
        
        question_text = question.question_text.lower()
        
        if 'iterrows' in question_text or 'pandas' in question_text:
            return 'pandas_iterrows'
        elif 'string' in question_text or 'concatenat' in question_text:
            return 'string_concatenation'
        elif 'nested' in question_text or 'loop' in question_text:
            return 'nested_loops'
        elif 'index' in question_text:
            return 'manual_indexing'
        else:
            return 'general_optimization'
    
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
    
    def _create_enhanced_learning_question(self, code: str, coaching_state, analysis: Dict[str, Any]) -> Tuple[str, CoachingMode]:
        """
        ENHANCED: Create learning question with session memory, continuity, and smart code snippets.
        """
        
        # Lazy import QuestionFormatter only when needed
        from .question_formatter import QuestionFormatter
        
        # Ensure coaching_state has session memory
        if not hasattr(coaching_state, 'session_memory'):
            coaching_state.session_memory = SessionMemory()
        
        # Select question considering session history
        question = EnhancedQuestionSelector.select_question_with_memory(
            code, coaching_state, coaching_state.session_memory
        )
        
        # Format the question
        formatted_question = QuestionFormatter.format_question_message(question)
        
        # ENHANCED: Add code snippet for long code
        enhanced_question = CodeSnippetAnalyzer.enhance_question_with_snippet(
            formatted_question, code, analysis, coaching_state.main_issue
        )
        
        # Create coaching interaction
        interaction = CoachingInteraction(
            interaction_id=str(uuid.uuid4()),
            mode=CoachingMode.QUESTION,
            content=enhanced_question,
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
    
    def _create_enhanced_nudge(self, code: str, analysis: Dict[str, Any], coaching_state: CoachingState) -> Tuple[str, CoachingMode]:
        """
        ENHANCED: Create an enhanced nudge with interview focus and smart code snippets.
        """
        nudge_text, mode = EnhancedNudgeGenerator.create_nudge(code, analysis, coaching_state)
        
        # ENHANCED: Add code snippet for long code
        enhanced_nudge = CodeSnippetAnalyzer.enhance_question_with_snippet(
            nudge_text, code, analysis, coaching_state.main_issue
        )
        
        return enhanced_nudge, CoachingMode.NUDGE