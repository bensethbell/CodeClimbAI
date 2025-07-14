"""
Interview-critical issue analysis for adaptive coaching.
Identifies and prioritizes code issues that matter most in technical interviews.
VERIFIED: Self-contained module with no complex dependencies.
"""

from typing import List, Dict, Any


class InterviewCriticalAnalyzer:
    """Analyzes code for interview-critical optimization opportunities."""
    
    @staticmethod
    def get_interview_critical_issues(code_analysis: Dict[str, Any]) -> List[str]:
        """
        Identify issues that would be critical to fix in a coding interview.
        Returns list of issues in order of interview importance.
        """
        critical_issues = []
        
        print(f"DEBUG: Analyzing code_analysis: {code_analysis}")
        
        # TIER 1: Performance killers (absolutely critical in interviews)
        if code_analysis.get('has_iterrows', False):
            critical_issues.append('has_iterrows')
            print("DEBUG: Found has_iterrows issue")
        if code_analysis.get('has_nested_loops', False):
            critical_issues.append('has_nested_loops')
            print("DEBUG: Found has_nested_loops issue")
        if code_analysis.get('has_string_concat', False):
            critical_issues.append('has_string_concat')
            print("DEBUG: Found has_string_concat issue")
        if code_analysis.get('has_inefficient_data_structure', False):
            critical_issues.append('has_inefficient_data_structure')
            print("DEBUG: Found has_inefficient_data_structure issue")
            
        # TIER 2: Code quality issues (important for senior roles)
        if code_analysis.get('has_manual_loop', False):
            critical_issues.append('has_manual_loop')
            print("DEBUG: Found has_manual_loop issue")
        if code_analysis.get('has_inefficient_filtering', False):
            critical_issues.append('has_inefficient_filtering')
            print("DEBUG: Found has_inefficient_filtering issue")
        if code_analysis.get('has_repetitive_code', False):
            critical_issues.append('has_repetitive_code')
            print("DEBUG: Found has_repetitive_code issue")
            
        # TIER 3: Best practices (nice to have)
        if code_analysis.get('has_unclear_variables', False):
            critical_issues.append('has_unclear_variables')
            print("DEBUG: Found has_unclear_variables issue")
        if code_analysis.get('has_missing_error_handling', False):
            critical_issues.append('has_missing_error_handling')
            print("DEBUG: Found has_missing_error_handling issue")
        
        print(f"DEBUG: Total critical issues found: {len(critical_issues)} - {critical_issues}")
        
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