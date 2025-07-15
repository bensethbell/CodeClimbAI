"""
Main code review assistant class.
FIXED: Now uses persistent coaching system instead of creating new AdaptiveCoach instances.
"""
from .prompts import PromptTemplates
from .analyzer import ClaudeAPIClient, CodeAnalyzer
from .models import ReviewSession
from .coaching_integration import CoachingIntegration


class CodeReviewAssistant:
    """Main assistant class with improved separation of concerns and persistent coaching."""
    
    def __init__(self, api_client: ClaudeAPIClient):
        self.api_client = api_client
        self.analyzer = CodeAnalyzer()

        # FIXED: Use persistent coaching system instead of creating new AdaptiveCoach
        coaching_state, self.coach = CoachingIntegration.get_existing_coaching_system()
    
    def analyze_code_and_get_goal(self, code: str) -> str:
        """Analyze code and return improvement goal."""
        prompt = self.analyzer.get_analysis_prompt(code)
        return self.api_client.call_claude(prompt)
    
    def get_focused_question(self, code: str, goal: str) -> str:
        """Get a focused question based on the goal."""
        prompt = PromptTemplates.FOCUSED_QUESTION_PROMPT.format(code=code, goal=goal)
        return self.api_client.call_claude(prompt, use_cache=False)  # Never cache questions
    
    def provide_hint(self, code: str, goal: str, hint_level: int) -> str:
        """Provide a leveled hint."""
        hint_descriptions = {
            1: "gentle nudge in the right direction",
            2: "more specific guidance about the approach", 
            3: "detailed explanation of the solution"
        }
        
        prompt = PromptTemplates.HINT_PROMPT.format(
            code=code,
            goal=goal,
            hint_level=hint_level,
            hint_description=hint_descriptions[hint_level]
        )
        
        return self.api_client.call_claude(prompt, use_cache=False)
    
    def evaluate_response(self, session: ReviewSession, user_response: str) -> str:
        """Evaluate user's response and provide feedback."""
        history_text = "\n".join([f"{msg.role.value}: {msg.content}" for msg in session.conversation_history[-5:]])  # Last 5 messages
        
        prompt = PromptTemplates.RESPONSE_EVALUATION_PROMPT.format(
            goal=session.goal,
            current_code=session.current_code,
            original_code=session.original_code,
            user_response=user_response,
            history=history_text
        )
        
        return self.api_client.call_claude(prompt, use_cache=False)  # Never cache responses
    
    def evaluate_code_changes(self, session: ReviewSession, modified_code: str) -> str:
        """Evaluate user's code modifications."""
        prompt = PromptTemplates.CODE_EVALUATION_PROMPT.format(
            goal=session.goal,
            original_code=session.original_code,
            modified_code=modified_code
        )
        
        return self.api_client.call_claude(prompt, use_cache=False)
    
    def show_solution(self, session: ReviewSession) -> str:
        """Show the optimized solution with explanation."""
        prompt = PromptTemplates.SOLUTION_PROMPT.format(
            original_code=session.original_code,
            goal=session.goal
        )
        
        return self.api_client.call_claude(prompt, use_cache=False)  # Don't cache solutions