"""
Adaptive coaching system for the Learn-As-You-Go Code Review Assistant.
ENHANCED VERSION: Includes interview-critical issue detection and advanced coaching logic.
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
from templates.examples import ExampleGenerator, get_example_code


class InterviewCriticalAnalyzer:
    """Analyzes code for interview-critical optimization opportunities."""
    
    @staticmethod
    def get_interview_critical_issues(code_analysis: Dict[str, Any]) -> List[str]:
        """
        Identify issues that would be critical to fix in a coding interview.
        Returns list of issues in order of interview importance.
        """
        critical_issues = []
        
        # TIER 1: Performance killers (absolutely critical in interviews)
        if code_analysis.get('has_iterrows', False):
            critical_issues.append('has_iterrows')
        if code_analysis.get('has_nested_loops', False):
            critical_issues.append('has_nested_loops')
        if code_analysis.get('has_string_concat', False):
            critical_issues.append('has_string_concat')
        if code_analysis.get('has_inefficient_data_structure', False):
            critical_issues.append('has_inefficient_data_structure')
            
        # TIER 2: Code quality issues (important for senior roles)
        if code_analysis.get('has_manual_loop', False):
            critical_issues.append('has_manual_loop')
        if code_analysis.get('has_inefficient_filtering', False):
            critical_issues.append('has_inefficient_filtering')
        if code_analysis.get('has_repetitive_code', False):
            critical_issues.append('has_repetitive_code')
            
        # TIER 3: Best practices (nice to have)
        if code_analysis.get('has_unclear_variables', False):
            critical_issues.append('has_unclear_variables')
        if code_analysis.get('has_missing_error_handling', False):
            critical_issues.append('has_missing_error_handling')
            
        return critical_issues
    
    @staticmethod
    def is_interview_critical(issue: str) -> bool:
        """Check if an issue is critical for coding interviews."""
        tier_1_critical = [
            'has_iterrows', 'has_nested_loops', 'has_string_concat', 
            'has_inefficient_data_structure'
        ]
        tier_2_important = [
            'has_manual_loop', 'has_inefficient_filtering', 'has_repetitive_code'
        ]
        return issue in tier_1_critical or issue in tier_2_important
    
    @staticmethod
    def get_issue_priority_explanation(issue: str) -> str:
        """Get explanation of why an issue is interview-critical."""
        explanations = {
            'has_iterrows': "Using iterrows() in interviews shows lack of pandas optimization knowledge - could be a deal-breaker",
            'has_nested_loops': "O(n²) complexity is a classic interview red flag - optimizing this shows algorithmic thinking", 
            'has_string_concat': "String concatenation in loops shows poor performance awareness - easily optimizable",
            'has_inefficient_data_structure': "Using wrong data structures shows fundamental CS knowledge gaps",
            'has_manual_loop': "Manual loops instead of built-ins shows lack of Python proficiency",
            'has_inefficient_filtering': "Not using list comprehensions shows missed optimization opportunities",
            'has_repetitive_code': "Repetitive code violates DRY principle - important for maintainability",
            'has_unclear_variables': "Poor variable naming reduces code readability",
            'has_missing_error_handling': "Missing error handling shows lack of production-ready thinking"
        }
        return explanations.get(issue, "This optimization would improve code quality")


class EnhancedResponseGenerator:
    """Enhanced response generation with best solution offerings."""
    
    @staticmethod
    def create_clean_correct_response(base_feedback: str, coaching_state) -> str:
        """Create clean, intelligent response for correct answers with solution offering."""
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
            # High performer - challenge with best solution comparison
            result += "\n\n🎯 **Advanced Challenge:** You're demonstrating strong optimization skills!"
            result += "\n\n💡 **Options:** Ready to optimize your code, see the best solution approach, or try a new example?"
        elif success_rate > 0.6:
            # Good performer - practical application with guidance
            result += "\n\n🔧 **Apply It:** Try modifying your code to use the optimization approach we discussed."
            result += "\n\n💡 **Options:** Need guidance on implementation, want to see the optimal solution, or prefer a new challenge?"
        else:
            # Building confidence - supportive guidance with solution option
            result += "\n\n✨ **Great progress!** You're understanding the concepts well."
            result += "\n\n💡 **Options:** Try implementing the optimization, ask for specific guidance, or see how the experts would solve this!"
        
        return result
    
    @staticmethod
    def create_clean_incorrect_response(base_feedback: str, coaching_state) -> str:
        """Create clean, supportive response for incorrect answers with help options."""
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
            # Multiple wrong answers - offer solution
            result += "\n\n💡 **Let me help:** This concept can be tricky. Would you like me to show you the optimal solution and explain the approach step by step?"
            result += "\n\n🎓 **Options:** See the best solution, try a different example, or get more specific guidance?"
        else:
            # Single wrong answer - gentle guidance with solution option
            result += "\n\n🤔 **Think about it differently:** Sometimes seeing the optimal approach helps clarify the concept."
            result += "\n\n💡 **Options:** Try again with a hint, see the expert solution, or explore this with a different example?"
        
        return result


class EnhancedNudgeGenerator:
    """Enhanced nudge generation with interview focus and solution offerings."""
    
    @staticmethod
    def create_nudge(code: str, analysis: Dict[str, Any], coaching_state) -> Tuple[str, str]:
        """Create a nudge with interview context and solution offerings."""
        
        # Determine if any issues are interview-critical
        critical_issues = InterviewCriticalAnalyzer.get_interview_critical_issues(analysis)
        has_critical_issues = len(critical_issues) > 0
        
        if analysis['has_iterrows']:
            nudge = """🎯 **Interview-Critical Issue**: Using `df.iterrows()` is a major performance bottleneck that interviewers specifically look for.

**Why this matters in interviews:** Shows you understand pandas optimization fundamentals.

**Hint**: Pandas vectorized operations like `df['column1'] * df['column2']` are typically 10-100x faster.

**Your options:**
• **Fix this issue** - Essential for interview success
• **See optimal solution** - Learn the best approach and why it works  
• **Generate Example** - Try a different optimization challenge"""
        
        elif analysis['has_string_concat']:
            nudge = """🎯 **Performance Issue**: Building strings with `+=` in loops is inefficient and interviewers notice this.

**Interview impact:** Shows understanding of Python string immutability and performance.

**Hint**: Collect strings in a list, then use `''.join(list)` for much better performance.

**Your options:**
• **Optimize the string building** - Show your performance awareness
• **See best solution** - Compare with the expert approach
• **Generate Example** - Practice with a different optimization"""
        
        elif analysis['has_nested_loops']:
            nudge = """🎯 **Algorithm Alert**: Nested loops often create O(n²) complexity - a classic interview concern.

**Why interviewers care:** Demonstrates algorithmic thinking and optimization skills.

**Hint**: Consider using sets, dictionaries, or other data structures to reduce complexity.

**Your options:**
• **Optimize the algorithm** - Critical for interview success
• **See optimal approach** - Learn advanced optimization techniques
• **Generate Example** - Try another algorithmic challenge"""
        
        elif analysis['has_manual_loop']:
            nudge = """🎯 **Optimization Opportunity**: Manual loops can often be replaced with more Pythonic approaches.

**Interview relevance:** Shows proficiency with Python's built-in functions and idioms.

**Hint**: Consider list comprehensions, `sum()`, `filter()`, or other built-ins.

**Your options:**
• **Modernize the code** - Use more Pythonic approaches
• **See expert solution** - Learn advanced Python techniques
• **Generate Example** - Practice with different optimization patterns"""
        
        elif has_critical_issues:
            issue = critical_issues[0]
            explanation = InterviewCriticalAnalyzer.get_issue_priority_explanation(issue)
            
            nudge = f"""🎯 **Interview-Important Issue**: {explanation}

**Your options:**
• **Address this issue** - Improve your interview readiness
• **See optimal solution** - Learn the best practices approach
• **Generate Example** - Try a different optimization challenge"""
        
        else:
            nudge = """🎯 **Good foundation!** Your code is functional and shows solid programming skills.

**Level up your code:** Even good code can often be optimized further for interviews.

**Your options:**
• **Explore optimizations** - Polish your code to interview standards
• **See expert solution** - Compare with best practices approach  
• **Generate Example** - Challenge yourself with a new optimization problem"""
        
        return nudge, "nudge"


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
    
    def enhanced_process_code_submission(self, code: str, coaching_state: CoachingState) -> Tuple[str, CoachingMode]:
        """
        ENHANCED: Process code submission with interview-critical issue detection.
        """
        print("Processing code submission with interview-critical analysis...")
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
            
            # ENHANCED: Look for next interview-critical issue
            remaining_critical_issues = [
                issue for issue in InterviewCriticalAnalyzer.get_interview_critical_issues(code_analysis)
                if issue not in coaching_state.resolved_issues and issue_flags.get(issue, False)
            ]
            
            if remaining_critical_issues:
                next_critical_issue = remaining_critical_issues[0]
                coaching_state.main_issue = next_critical_issue
                
                # ENHANCED: Explain why this next issue is important
                priority_explanation = InterviewCriticalAnalyzer.get_issue_priority_explanation(next_critical_issue)
                
                return f"""🎉 **Great progress!** You've addressed the {main_issue.replace('_', ' ')} issue.

**🚨 Interview Alert:** I notice another critical optimization opportunity that would be **essential to fix in a coding interview**:

{priority_explanation}

**Your options:**
• **Continue optimizing** - Address this critical issue (recommended for interview prep)
• **Generate new example** - Click the 'Generate Example' button for different practice
• **See best solution** - I can show you the optimal approach and explain why it's better

What would you like to focus on?""", CoachingMode.NUDGE
            
            else:
                # Check for any remaining non-critical issues
                remaining_issues = [flag for flag, value in issue_flags.items() if value and flag not in coaching_state.resolved_issues]
                
                if remaining_issues:
                    print("DEBUG: Found remaining non-critical issues:", remaining_issues)
                    coaching_state.main_issue = remaining_issues[0]
                    
                    return f"""🎉 **Excellent work!** You've addressed all the critical interview-level issues.

There are still some minor optimizations possible, but your code is now **interview-ready** for the main performance concerns.

**Your options:**
• **Polish further** - Address remaining minor optimizations  
• **See best solution** - Compare your approach with the optimal solution
• **New challenge** - Click 'Generate Example' for a different optimization problem

How would you like to proceed?""", CoachingMode.NUDGE
                
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
            return self._create_learning_question(code, coaching_state, code_analysis)
        else:
            return self._create_enhanced_nudge(code, code_analysis, coaching_state)

    def process_code_submission(self, code: str, coaching_state: CoachingState) -> Tuple[str, CoachingMode]:
        """Use enhanced processing by default."""
        return self.enhanced_process_code_submission(code, coaching_state)

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
            
            # Create clean, intelligent response using enhanced generator
            if is_correct:
                return EnhancedResponseGenerator.create_clean_correct_response(base_feedback, coaching_state)
            else:
                return EnhancedResponseGenerator.create_clean_incorrect_response(base_feedback, coaching_state)
        
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
    
    def _create_enhanced_nudge(self, code: str, analysis: Dict[str, Any], coaching_state: CoachingState) -> Tuple[str, CoachingMode]:
        """Create an enhanced nudge with interview focus."""
        nudge_text, mode = EnhancedNudgeGenerator.create_nudge(code, analysis, coaching_state)
        return nudge_text, CoachingMode.NUDGE