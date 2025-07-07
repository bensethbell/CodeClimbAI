"""
Main code review assistant class.
"""

from .prompts import PromptTemplates
from .analyzer import ClaudeAPIClient, CodeAnalyzer
from .models import ReviewSession
from .adaptive_coach import AdaptiveCoach

class CodeReviewAssistant:
    """Main assistant class with improved separation of concerns."""
    
    def __init__(self, api_client: ClaudeAPIClient):
        self.api_client = api_client

        # Instantiate the adaptive coach so we can call its example loader:
        code_analyzer = CodeAnalyzer()            # no constructor args
        code_analyzer.api_client = api_client     # attach the API client manually

        self.coach = AdaptiveCoach(code_analyzer)
        self.analyzer = CodeAnalyzer()
    
    def analyze_code_and_get_goal(self, code: str) -> str:
        """Analyze code and return improvement goal."""
        prompt = self.analyzer.get_analysis_prompt(code)
        return self.api_client.call_claude(prompt).strip()
    
    def get_focused_question(self, code: str, goal: str) -> str:
        """Get a focused question based on the goal."""
        prompt = PromptTemplates.FOCUSED_QUESTION_PROMPT.format(code=code, goal=goal)
        return self.api_client.call_claude(prompt, use_cache=False)  # Never cache questions
    
    def provide_hint(self, code: str, goal: str, hint_level: int) -> str:
        """Provide a leveled hint."""
        hint_descriptions = {
            1: "Give a conceptual hint about what to look for, without revealing the solution.",
            2: "Provide a more specific hint about the approach or technique to use.",
            3: "Give a concrete hint about the specific line or method to focus on."
        }
        
        prompt = PromptTemplates.HINT_PROMPT.format(
            code=code,
            goal=goal,
            hint_level=hint_level,
            hint_description=hint_descriptions[hint_level]
        )
        
        return self.api_client.call_claude(prompt)
    
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