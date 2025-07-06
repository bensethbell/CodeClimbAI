"""
Code analysis and API client components.
"""

import anthropic
from .prompts import PromptTemplates

class CodeAnalyzer:
    """Handles code analysis logic separately from UI concerns."""
    
    @staticmethod
    def get_analysis_prompt(code: str) -> str:
        return PromptTemplates.CODE_ANALYSIS_PROMPT.format(code=code)
    
    @staticmethod
    def get_question_prompt(code: str, goal: str) -> str:
        return PromptTemplates.QUESTION_GENERATION_PROMPT.format(code=code, goal=goal)

class ClaudeAPIClient:
    """Handles all Claude API interactions with proper error handling and caching."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self._cache = {}  # Simple prompt caching
    
    def call_claude(self, prompt: str, use_cache: bool = True) -> str:
        """Make a call to Claude API with caching and error handling."""
        # Simple cache key based on prompt hash
        cache_key = hash(prompt) if use_cache else None
        
        if cache_key and cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            result = message.content[0].text
            
            if cache_key:
                self._cache[cache_key] = result
            
            return result
            
        except anthropic.APIError as e:
            return f"API Error: {str(e)}. Please check your API key and try again."
        except Exception as e:
            return f"Unexpected error: {str(e)}. Please try again."