"""
Code analysis and API client components with retry logic for 529 errors.
"""
import anthropic
import time
import random
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
    """Handles all Claude API interactions with retry logic for 529 errors."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self._cache = {}  # Simple prompt caching
    
    def call_claude(self, prompt: str, use_cache: bool = True) -> str:
        """Make a call to Claude API with retry logic for 529 errors."""
        # Simple cache key based on prompt hash
        cache_key = hash(prompt) if use_cache else None
        
        if cache_key and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Retry logic for 529 errors
        max_retries = 3
        base_delay = 1.0  # Start with 1 second delay
        
        for attempt in range(max_retries):
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
                error_message = str(e)
                
                # Handle 529 overloaded errors with retry
                if "529" in error_message or "overloaded" in error_message.lower():
                    if attempt < max_retries - 1:  # Don't retry on last attempt
                        # Exponential backoff with jitter
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        print(f"API overloaded (529), retrying in {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        return "🚨 **API Temporarily Overloaded**: Anthropic's servers are experiencing high load. Please try again in a few moments, or continue with a different question."
                
                # Handle other API errors normally
                elif "rate_limit" in error_message.lower():
                    return "⏳ **Rate Limit Reached**: You've hit the API rate limit. Please wait a moment before trying again."
                elif "authentication" in error_message.lower():
                    return "🔑 **Authentication Error**: Please check your API key configuration."
                else:
                    return f"⚠️ **API Error**: {str(e)}. Please try again."
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    # Retry on unexpected errors too
                    delay = base_delay * (2 ** attempt)
                    print(f"Unexpected error, retrying in {delay:.1f} seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    return f"❌ **Unexpected Error**: {str(e)}. Please try again."
        
        # This shouldn't be reached, but just in case
        return "🚨 **Service Temporarily Unavailable**: Please try again in a few moments."