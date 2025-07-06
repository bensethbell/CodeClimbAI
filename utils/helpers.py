"""
Helper utility functions for code analysis and session management.
"""

class CodeDiffer:
    """Utility for comparing code differences."""
    
    @staticmethod
    def get_simple_diff(original: str, modified: str) -> dict:
        """Get a simple diff between two code strings."""
        original_lines = original.splitlines()
        modified_lines = modified.splitlines()
        
        changes = {
            'added_lines': [],
            'removed_lines': [],
            'modified_lines': [],
            'line_count_change': len(modified_lines) - len(original_lines)
        }
        
        # Simple line-by-line comparison
        max_lines = max(len(original_lines), len(modified_lines))
        
        for i in range(max_lines):
            orig_line = original_lines[i] if i < len(original_lines) else None
            mod_line = modified_lines[i] if i < len(modified_lines) else None
            
            if orig_line is None and mod_line is not None:
                changes['added_lines'].append((i + 1, mod_line))
            elif orig_line is not None and mod_line is None:
                changes['removed_lines'].append((i + 1, orig_line))
            elif orig_line != mod_line:
                changes['modified_lines'].append((i + 1, orig_line, mod_line))
        
        return changes
    
    @staticmethod
    def has_significant_changes(original: str, modified: str, threshold: int = 3) -> bool:
        """Check if there are significant changes between code versions."""
        diff = CodeDiffer.get_simple_diff(original, modified)
        total_changes = (
            len(diff['added_lines']) + 
            len(diff['removed_lines']) + 
            len(diff['modified_lines'])
        )
        return total_changes >= threshold

class FileUtils:
    """Utility functions for file operations."""
    
    @staticmethod
    def validate_python_syntax(code: str) -> tuple[bool, str]:
        """Validate Python syntax without executing."""
        try:
            compile(code, '<string>', 'exec')
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax Error on line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Compilation Error: {str(e)}"
    
    @staticmethod
    def extract_function_names(code: str) -> list:
        """Extract function names from Python code."""
        import ast
        
        try:
            tree = ast.parse(code)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
            
            return functions
        except:
            return []
    
    @staticmethod
    def count_code_metrics(code: str) -> dict:
        """Get basic code metrics."""
        lines = code.splitlines()
        
        metrics = {
            'total_lines': len(lines),
            'non_empty_lines': len([line for line in lines if line.strip()]),
            'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
            'function_count': len(FileUtils.extract_function_names(code)),
            'estimated_complexity': 0  # Could implement cyclomatic complexity
        }
        
        # Simple complexity estimation based on control structures
        complexity_keywords = ['if', 'elif', 'for', 'while', 'try', 'except', 'with']
        for line in lines:
            stripped = line.strip().lower()
            for keyword in complexity_keywords:
                if stripped.startswith(keyword + ' ') or stripped.startswith(keyword + ':'):
                    metrics['estimated_complexity'] += 1
        
        return metrics

class SessionUtils:
    """Utilities for managing session state and data."""
    
    @staticmethod
    def serialize_session(session) -> dict:
        """Serialize a session for storage."""
        if not session:
            return {}
        
        return {
            'original_code': session.original_code,
            'current_code': session.current_code,
            'goal': session.goal,
            'hint_level': session.hint_level,
            'is_active': session.is_active,
            'conversation_count': len(session.conversation_history)
        }
    
    @staticmethod
    def get_session_summary(session) -> str:
        """Get a human-readable session summary."""
        if not session:
            return "No active session"
        
        summary = f"Goal: {session.goal}\n"
        summary += f"Hints used: {session.hint_level}/3\n"
        summary += f"Messages exchanged: {len(session.conversation_history)}\n"
        summary += f"Status: {'Active' if session.is_active else 'Completed'}"
        
        return summary