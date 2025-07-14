"""
Smart code snippet extraction for long code files.
FIXED: Preserves MCQ structure when inserting snippets.
"""
import re
from typing import List, Dict, Tuple, Optional

class CodeSnippetAnalyzer:
    """Analyzes code and extracts relevant snippets for coaching questions."""
    
    # Threshold for considering code "long" (approximate lines that fit in editor without scrolling)
    LONG_CODE_THRESHOLD = 25
    
    # Lines of context to include around problematic code
    CONTEXT_LINES = 3
    
    @classmethod
    def is_code_long(cls, code: str) -> bool:
        """
        Check if code is long enough to benefit from snippet extraction.
        """
        lines = code.split('\n')
        return len(lines) > cls.LONG_CODE_THRESHOLD
    
    @classmethod
    def find_issue_locations(cls, code: str, analysis: Dict[str, bool]) -> List[Dict[str, any]]:
        """
        Find specific lines where optimization issues occur.
        """
        lines = code.split('\n')
        issue_locations = []
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip().lower()
            
            # Check for iterrows usage
            if analysis.get('has_iterrows', False) and 'iterrows' in line_stripped:
                issue_locations.append({
                    'line_num': line_num,
                    'issue_type': 'iterrows',
                    'description': 'pandas iterrows() usage',
                    'severity': 'high',
                    'line_content': line.strip()
                })
            
            # Check for string concatenation in loops
            if (analysis.get('has_string_concat', False) and 
                '+=' in line and any(s in line_stripped for s in ['str', '"', "'"])):
                issue_locations.append({
                    'line_num': line_num,
                    'issue_type': 'string_concat',
                    'description': 'string concatenation in loop',
                    'severity': 'medium',
                    'line_content': line.strip()
                })
            
            # Check for nested loops
            if analysis.get('has_nested_loops', False) and 'for ' in line_stripped:
                # Count indentation to detect nesting
                indent_level = len(line) - len(line.lstrip())
                if indent_level > 4:  # Likely inside another block
                    issue_locations.append({
                        'line_num': line_num,
                        'issue_type': 'nested_loops',
                        'description': 'nested loop structure',
                        'severity': 'medium',
                        'line_content': line.strip()
                    })
            
            # Check for manual indexing
            if analysis.get('has_manual_loop', False) and 'range(len(' in line_stripped:
                issue_locations.append({
                    'line_num': line_num,
                    'issue_type': 'manual_indexing',
                    'description': 'manual indexing with range(len())',
                    'severity': 'low',
                    'line_content': line.strip()
                })
        
        # Sort by severity (high first) then by line number
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        issue_locations.sort(key=lambda x: (severity_order[x['severity']], x['line_num']))
        
        return issue_locations
    
    @classmethod
    def extract_snippet_around_line(cls, code: str, target_line: int, context_lines: int = None) -> Dict[str, any]:
        """
        Extract code snippet around a specific line with context.
        """
        if context_lines is None:
            context_lines = cls.CONTEXT_LINES
            
        lines = code.split('\n')
        total_lines = len(lines)
        
        # Calculate snippet boundaries
        start_line = max(1, target_line - context_lines)
        end_line = min(total_lines, target_line + context_lines)
        
        # Extract the snippet (convert back to 0-indexed for slicing)
        snippet_lines = lines[start_line-1:end_line]
        
        # Add line numbers for clarity
        numbered_lines = []
        for i, line in enumerate(snippet_lines, start_line):
            marker = "→" if i == target_line else " "
            numbered_lines.append(f"{i:2d}{marker} {line}")
        
        return {
            'start_line': start_line,
            'end_line': end_line,
            'target_line': target_line,
            'snippet': '\n'.join(numbered_lines),
            'context_lines': context_lines
        }
    
    @classmethod
    def create_snippet_for_question(cls, code: str, analysis: Dict[str, bool], main_issue: str = None) -> Optional[str]:
        """
        Create a code snippet for inclusion in questions if code is long.
        """
        # Only create snippets for long code
        if not cls.is_code_long(code):
            return None
        
        # Find issue locations
        issue_locations = cls.find_issue_locations(code, analysis)
        
        if not issue_locations:
            return None
        
        # Choose the most relevant issue
        target_issue = None
        if main_issue:
            # Find the issue that matches the main issue
            issue_type_mapping = {
                'has_iterrows': 'iterrows',
                'has_string_concat': 'string_concat',
                'has_nested_loops': 'nested_loops',
                'has_manual_loop': 'manual_indexing'
            }
            target_type = issue_type_mapping.get(main_issue)
            target_issue = next((issue for issue in issue_locations if issue['issue_type'] == target_type), None)
        
        # Fall back to highest severity issue
        if not target_issue:
            target_issue = issue_locations[0]
        
        # Extract snippet around the issue
        snippet_info = cls.extract_snippet_around_line(code, target_issue['line_num'])
        
        # Format the snippet for inclusion in question
        formatted_snippet = f"""**Looking at this section** (around line {target_issue['line_num']}):

```
{snippet_info['snippet']}
```

*The arrow (→) points to the line in question.*"""
        
        return formatted_snippet
    
    @classmethod
    def enhance_question_with_snippet(cls, question: str, code: str, analysis: Dict[str, bool], main_issue: str = None) -> str:
        """
        FIXED: Enhanced question with snippet FIRST, then question (better flow).
        """
        snippet = cls.create_snippet_for_question(code, analysis, main_issue)
        
        if not snippet:
            return question
        
        lines = question.split('\n')
        
        # FIXED: Better flow - put snippet at the BEGINNING after title
        # Look for the question title to insert snippet right after it
        title_end_index = 0
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            # Find end of title section (look for lines that end title content)
            if (line_stripped.endswith('**') and line_stripped.startswith('📚') or
                line_stripped.endswith('(MCQ)**') or 
                line_stripped.endswith('Question**')):
                title_end_index = i + 1
                break
        
        # If no clear title found, insert after first non-empty line
        if title_end_index == 0:
            for i, line in enumerate(lines):
                if line.strip():
                    title_end_index = i + 1
                    break
        
        # FIXED: Insert snippet right after title, before question text
        if title_end_index < len(lines):
            new_lines = (
                lines[:title_end_index] +          # Title
                ['', snippet, ''] +               # Snippet with spacing
                lines[title_end_index:]           # Question text, options, etc.
            )
        else:
            # Fallback: prepend snippet at beginning
            new_lines = [snippet, ''] + lines
        
        return '\n'.join(new_lines)