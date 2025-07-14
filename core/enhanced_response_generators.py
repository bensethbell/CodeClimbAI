"""
Enhanced response generation for adaptive coaching with interview focus.
Handles intelligent response creation and solution offerings.
VERIFIED: Imports tested, integration with interview_analyzer confirmed.
"""

from typing import Dict, Any, Tuple
from .coaching_models import AnswerStatus
from .interview_analyzer import InterviewCriticalAnalyzer


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
        
        if analysis.get('has_iterrows', False):
            nudge = """🎯 **Interview-Critical Issue**: Using `df.iterrows()` is a major performance bottleneck that interviewers specifically look for.

**Why this matters in interviews:** Shows you understand pandas optimization fundamentals.

**Hint**: Pandas vectorized operations like `df['column1'] * df['column2']` are typically 10-100x faster.

**Your options:**
• **Fix this issue** - Essential for interview success
• **See optimal solution** - Learn the best approach and why it works  
• **Generate Example** - Try a different optimization challenge"""
        
        elif analysis.get('has_string_concat', False):
            nudge = """🎯 **Performance Issue**: Building strings with `+=` in loops is inefficient and interviewers notice this.

**Interview impact:** Shows understanding of Python string immutability and performance.

**Hint**: Collect strings in a list, then use `''.join(list)` for much better performance.

**Your options:**
• **Optimize the string building** - Show your performance awareness
• **See best solution** - Compare with the expert approach
• **Generate Example** - Practice with a different optimization"""
        
        elif analysis.get('has_nested_loops', False):
            nudge = """🎯 **Algorithm Alert**: Nested loops often create O(n²) complexity - a classic interview concern.

**Why interviewers care:** Demonstrates algorithmic thinking and optimization skills.

**Hint**: Consider using sets, dictionaries, or other data structures to reduce complexity.

**Your options:**
• **Optimize the algorithm** - Critical for interview success
• **See optimal approach** - Learn advanced optimization techniques
• **Generate Example** - Try another algorithmic challenge"""
        
        elif analysis.get('has_manual_loop', False):
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