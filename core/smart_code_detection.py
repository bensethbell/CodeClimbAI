"""
Smart code change detection to distinguish between optimization and new code submission.
Combines similarity threshold and heuristic analysis for robust detection.
"""
import re
from typing import Tuple, Dict, Any
from difflib import SequenceMatcher

class CodeChangeDetector:
    """Detects whether code submission is optimization or entirely new code."""
    
    # Thresholds for similarity-based detection
    VERY_SIMILAR_THRESHOLD = 0.7   # Definitely optimization
    VERY_DIFFERENT_THRESHOLD = 0.3  # Definitely new code
    
    @staticmethod
    def calculate_similarity(code1: str, code2: str) -> float:
        """Calculate similarity between two code strings (0.0 to 1.0)."""
        if not code1 or not code2:
            return 0.0
        
        # Normalize both codes for comparison
        norm1 = CodeChangeDetector._normalize_for_comparison(code1)
        norm2 = CodeChangeDetector._normalize_for_comparison(code2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Use sequence matcher for similarity
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    @staticmethod
    def _normalize_for_comparison(code: str) -> str:
        """Normalize code for similarity comparison."""
        # Remove comments and extra whitespace
        lines = []
        for line in code.strip().split('\n'):
            # Remove comments and strip whitespace
            line = re.sub(r'#.*$', '', line).strip()
            if line:  # Only keep non-empty lines
                lines.append(line)
        return '\n'.join(lines)
    
    @staticmethod
    def extract_structural_features(code: str) -> Dict[str, Any]:
        """Extract structural features for heuristic comparison."""
        features = {
            'function_names': set(),
            'variable_names': set(),
            'import_modules': set(),
            'string_literals': set(),
            'has_pandas': False,
            'has_iterrows': False,
            'has_selenium': False,
            'line_count': 0,
            'complexity_score': 0
        }
        
        lines = code.split('\n')
        features['line_count'] = len([line for line in lines if line.strip()])
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract function names
            func_match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
            if func_match:
                features['function_names'].add(func_match.group(1))
            
            # Extract import modules
            import_match = re.search(r'(?:from\s+(\w+)|import\s+(\w+))', line)
            if import_match:
                module = import_match.group(1) or import_match.group(2)
                features['import_modules'].add(module)
            
            # Extract variable assignments (simple heuristic)
            var_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line)
            if var_match and not re.search(r'def\s+', line):
                features['variable_names'].add(var_match.group(1))
            
            # Extract string literals
            string_matches = re.findall(r'["\']([^"\']+)["\']', line)
            for string_literal in string_matches:
                if len(string_literal) > 3:  # Only meaningful strings
                    features['string_literals'].add(string_literal)
            
            # Check for specific technologies
            if 'pandas' in line.lower() or 'pd.' in line:
                features['has_pandas'] = True
            if 'iterrows' in line.lower():
                features['has_iterrows'] = True
            if 'selenium' in line.lower() or 'webdriver' in line.lower():
                features['has_selenium'] = True
            
            # Simple complexity scoring
            if any(keyword in line for keyword in ['for ', 'if ', 'while ', 'try:']):
                features['complexity_score'] += 1
        
        return features
    
    @staticmethod
    def calculate_structural_similarity(features1: Dict, features2: Dict) -> float:
        """Calculate structural similarity based on features."""
        similarities = []
        
        # Function name similarity
        if features1['function_names'] or features2['function_names']:
            func_overlap = len(features1['function_names'] & features2['function_names'])
            func_total = len(features1['function_names'] | features2['function_names'])
            similarities.append(func_overlap / func_total if func_total > 0 else 0)
        
        # Import similarity
        if features1['import_modules'] or features2['import_modules']:
            import_overlap = len(features1['import_modules'] & features2['import_modules'])
            import_total = len(features1['import_modules'] | features2['import_modules'])
            similarities.append(import_overlap / import_total if import_total > 0 else 0)
        
        # Technology stack similarity
        tech_similarity = 0
        tech_checks = [
            ('has_pandas', 'has_pandas'),
            ('has_iterrows', 'has_iterrows'),
            ('has_selenium', 'has_selenium')
        ]
        
        for tech1, tech2 in tech_checks:
            if features1[tech1] == features2[tech2]:
                tech_similarity += 1
        
        similarities.append(tech_similarity / len(tech_checks))
        
        # Line count similarity (relative)
        if features1['line_count'] > 0 and features2['line_count'] > 0:
            line_ratio = min(features1['line_count'], features2['line_count']) / max(features1['line_count'], features2['line_count'])
            similarities.append(line_ratio)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    @staticmethod
    def detect_change_type(old_code: str, new_code: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Detect whether code change is optimization, new code, or unclear.
        
        Returns:
            - change_type: "OPTIMIZATION", "NEW_CODE", or "UNCLEAR"
            - confidence: 0.0 to 1.0
            - details: Additional information about the detection
        """
        # Calculate text similarity
        text_similarity = CodeChangeDetector.calculate_similarity(old_code, new_code)
        
        # Extract and compare structural features
        old_features = CodeChangeDetector.extract_structural_features(old_code)
        new_features = CodeChangeDetector.extract_structural_features(new_code)
        structural_similarity = CodeChangeDetector.calculate_structural_similarity(old_features, new_features)
        
        # Combine similarities with weights
        combined_similarity = (text_similarity * 0.6) + (structural_similarity * 0.4)
        
        # Make decision based on thresholds
        details = {
            'text_similarity': text_similarity,
            'structural_similarity': structural_similarity,
            'combined_similarity': combined_similarity,
            'old_features': old_features,
            'new_features': new_features
        }
        
        if combined_similarity >= CodeChangeDetector.VERY_SIMILAR_THRESHOLD:
            return "OPTIMIZATION", combined_similarity, details
        elif combined_similarity <= CodeChangeDetector.VERY_DIFFERENT_THRESHOLD:
            return "NEW_CODE", 1.0 - combined_similarity, details
        else:
            # In the unclear range - use additional heuristics
            confidence = abs(combined_similarity - 0.5) * 2  # 0.5 = maximum uncertainty
            
            # Additional heuristics for edge cases
            if old_features['has_iterrows'] and not new_features['has_iterrows']:
                # Likely optimization if iterrows was removed
                return "OPTIMIZATION", max(confidence, 0.7), details
            elif not old_features['import_modules'] & new_features['import_modules']:
                # Completely different imports suggest new code
                return "NEW_CODE", max(confidence, 0.7), details
            
            return "UNCLEAR", confidence, details
    
    @staticmethod
    def create_response_for_change_type(change_type: str, old_code: str, new_code: str, details: Dict) -> str:
        """Create appropriate response based on detected change type."""
        
        if change_type == "OPTIMIZATION":
            # User optimized the example - congratulate and analyze improvements
            improvements = []
            old_features = details['old_features']
            new_features = details['new_features']
            
            if old_features['has_iterrows'] and not new_features['has_iterrows']:
                improvements.append("removed iterrows() usage")
            if old_features['complexity_score'] > new_features['complexity_score']:
                improvements.append("reduced code complexity")
            if new_features['line_count'] < old_features['line_count']:
                improvements.append("made code more concise")
            
            if improvements:
                improvement_text = ", ".join(improvements)
                return f"🎉 **Great optimization work!** I can see you've {improvement_text}. Let's analyze your improved version to see what other enhancements might be possible."
            else:
                return "🔄 **Code updated!** I can see you've made changes to the example. Let's analyze your modifications and see what optimization opportunities remain."
        
        elif change_type == "NEW_CODE":
            # User submitted entirely new code - start fresh analysis
            return "📚 **New code analysis!** I can see this is different code from the example. Let's analyze your code and identify optimization opportunities."
        
        else:  # UNCLEAR
            # Ask user to clarify their intent
            return """🤔 **I notice significant changes to the code.** To provide the best learning experience:

Are you:
**A)** Sharing your optimized version of the previous example
**B)** Submitting your own code for analysis

*This helps me provide more targeted feedback!*"""
