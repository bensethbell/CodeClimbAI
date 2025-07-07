"""
Enhanced example code snippets with both problematic and optimized versions.
ENHANCED VERSION: Each example includes both problem and solution for comparison.
"""
print("👀 enhanced_examples.py loaded!")
import random
import re
from typing import Dict, Tuple
from dataclasses import dataclass

@dataclass
class ExamplePair:
    """Represents a problematic example with its optimized solution."""
    name: str
    category: str
    problem_code: str
    solution_code: str
    learning_focus: str
    performance_improvement: str

def normalize_code(code: str) -> str:
    """Normalize code for comparison by removing extra whitespace and comments."""
    if not code:
        return ""
    # Remove comments, extra whitespace, and normalize line endings
    lines = []
    for line in code.strip().split('\n'):
        # Remove comments and strip whitespace
        line = re.sub(r'#.*$', '', line).strip()
        if line:  # Only keep non-empty lines
            lines.append(line)
    return '\n'.join(lines)

def get_example_code() -> str:
    """Get the main pandas optimization example (problematic version)."""
    return '''def add_metrics(df):
    results = []
    for idx, row in df.iterrows():
        results.append(row["price"] * 0.2 + row["tax"])
    df["total"] = results
    return df'''

def get_enhanced_performance_examples() -> Dict[str, ExamplePair]:
    """Get performance examples with both problematic and optimized versions."""
    return {
        "pandas_iterrows": ExamplePair(
            name="pandas_iterrows",
            category="performance",
            problem_code='''def process_sales_data(df):
    totals = []
    for idx, row in df.iterrows():  # ISSUE: Uses iterrows()
        if row['region'] == 'North':
            totals.append(row['sales'] * 1.1)
        else:
            totals.append(row['sales'])
    df['adjusted_sales'] = totals
    return df''',
            solution_code='''def process_sales_data(df):
    # Vectorized solution - much faster
    df['adjusted_sales'] = df['sales'].where(df['region'] != 'North', df['sales'] * 1.1)
    return df''',
            learning_focus="Pandas vectorization vs iterrows()",
            performance_improvement="10-100x faster execution"
        ),
        
        "nested_loops": ExamplePair(
            name="nested_loops", 
            category="performance",
            problem_code='''def find_duplicates(data1, data2):
    duplicates = []
    for item1 in data1:  # ISSUE: Nested loops O(n²)
        for item2 in data2:
            if item1['id'] == item2['id']:
                duplicates.append(item1)
    return duplicates''',
            solution_code='''def find_duplicates(data1, data2):
    # Use set for O(1) lookup - O(n) complexity
    ids_in_data2 = {item['id'] for item in data2}
    duplicates = [item for item in data1 if item['id'] in ids_in_data2]
    return duplicates''',
            learning_focus="Algorithm optimization - set lookups vs nested loops",
            performance_improvement="O(n²) to O(n) complexity reduction"
        ),
        
        "string_concatenation": ExamplePair(
            name="string_concatenation",
            category="performance", 
            problem_code='''def build_report(items):
    report = ""
    for item in items:  # ISSUE: String concatenation in loop
        report = report + f"Item: {item['name']}, Price: ${item['price']}\\n"
    return report''',
            solution_code='''def build_report(items):
    # Collect in list, then join - much more efficient
    lines = []
    for item in items:
        lines.append(f"Item: {item['name']}, Price: ${item['price']}")
    return "\\n".join(lines)''',
            learning_focus="Efficient string building techniques",
            performance_improvement="Linear vs quadratic string operations"
        ),
        
        "inefficient_filtering": ExamplePair(
            name="inefficient_filtering",
            category="performance",
            problem_code='''def filter_expensive_items(products):
    expensive = []
    for product in products:  # ISSUE: Manual filtering instead of list comprehension
        if product['price'] > 100:
            expensive.append(product)
    return expensive''',
            solution_code='''def filter_expensive_items(products):
    # List comprehension - more Pythonic and efficient
    return [product for product in products if product['price'] > 100]''',
            learning_focus="List comprehensions vs manual loops",
            performance_improvement="More readable and typically faster"
        ),
        
        "manual_indexing": ExamplePair(
            name="manual_indexing",
            category="performance",
            problem_code='''def calculate_total(numbers):
    total = 0
    for i in range(len(numbers)):  # ISSUE: Manual indexing instead of direct iteration
        total = total + numbers[i]
    return total''',
            solution_code='''def calculate_total(numbers):
    # Built-in sum function - optimized and readable
    return sum(numbers)''',
            learning_focus="Built-in functions vs manual implementation",
            performance_improvement="Leverages C-level optimizations"
        ),
        
        "inefficient_search": ExamplePair(
            name="inefficient_search",
            category="performance",
            problem_code='''def find_user_by_id(users, target_id):
    for user in users:  # ISSUE: Linear search in list
        if user['id'] == target_id:
            return user
    return None''',
            solution_code='''def find_user_by_id(users_dict, target_id):
    # Use dictionary for O(1) lookup instead of O(n) search
    return users_dict.get(target_id)
    
# Usage: users_dict = {user['id']: user for user in users}''',
            learning_focus="Data structure choice for efficient lookups",
            performance_improvement="O(n) to O(1) lookup time"
        )
    }

def get_enhanced_readability_examples() -> Dict[str, ExamplePair]:
    """Get readability examples with both problematic and clean versions."""
    return {
        "unclear_variables": ExamplePair(
            name="unclear_variables",
            category="readability",
            problem_code='''def calc(x, y, z):  # ISSUE: Unclear variable names
    a = x * 0.1  # ISSUE: Single letter variables, no comments
    b = y + z
    c = a + b
    return c''',
            solution_code='''def calculate_total_with_tax(price, base_fee, additional_fee):
    """Calculate total cost including tax and fees."""
    tax_amount = price * 0.1  # 10% tax rate
    total_fees = base_fee + additional_fee
    final_total = tax_amount + total_fees
    return final_total''',
            learning_focus="Clear variable naming and documentation",
            performance_improvement="Dramatically improved maintainability"
        ),
        
        "repetitive_code": ExamplePair(
            name="repetitive_code",
            category="readability",
            problem_code='''def process_regions(df):  # ISSUE: Repetitive code patterns
    north_data = df[df['region'] == 'North']
    north_result = north_data['sales'].sum()
    south_data = df[df['region'] == 'South']  # REPETITIVE
    south_result = south_data['sales'].sum()
    east_data = df[df['region'] == 'East']    # REPETITIVE
    east_result = east_data['sales'].sum()
    west_data = df[df['region'] == 'West']    # REPETITIVE
    west_result = west_data['sales'].sum()
    return [north_result, south_result, east_result, west_result]''',
            solution_code='''def process_regions(df):
    """Process sales data by region using DRY principle."""
    regions = ['North', 'South', 'East', 'West']
    results = []
    for region in regions:
        region_data = df[df['region'] == region]
        region_total = region_data['sales'].sum()
        results.append(region_total)
    return results
    
    # Even better: return df.groupby('region')['sales'].sum().to_dict()''',
            learning_focus="DRY principle and code deduplication",
            performance_improvement="Easier to maintain and extend"
        ),
        
        "long_function": ExamplePair(
            name="long_function",
            category="readability",
            problem_code='''def analyze_sales(df):  # ISSUE: Function doing too many things
    df['tax'] = df['price'] * 0.08
    df['shipping'] = df['price'] * 0.05
    df['total'] = df['price'] + df['tax'] + df['shipping']
    df['discount'] = 0
    df.loc[df['total'] > 100, 'discount'] = df['total'] * 0.1
    df['final_price'] = df['total'] - df['discount']
    north_sales = df[df['region'] == 'North']['final_price'].sum()
    south_sales = df[df['region'] == 'South']['final_price'].sum()
    east_sales = df[df['region'] == 'East']['final_price'].sum()
    west_sales = df[df['region'] == 'West']['final_price'].sum()
    return {'North': north_sales, 'South': south_sales, 'East': east_sales, 'West': west_sales}''',
            solution_code='''def calculate_pricing(df):
    """Calculate taxes, shipping, and discounts."""
    df['tax'] = df['price'] * 0.08
    df['shipping'] = df['price'] * 0.05
    df['total'] = df['price'] + df['tax'] + df['shipping']
    df['discount'] = df['total'].where(df['total'] <= 100, df['total'] * 0.1).fillna(0)
    df['final_price'] = df['total'] - df['discount']
    return df

def summarize_by_region(df):
    """Summarize sales totals by region."""
    return df.groupby('region')['final_price'].sum().to_dict()

def analyze_sales(df):
    """Main analysis function - orchestrates the workflow."""
    df = calculate_pricing(df)
    return summarize_by_region(df)''',
            learning_focus="Single Responsibility Principle and function decomposition",
            performance_improvement="Easier testing, debugging, and reuse"
        )
    }

def get_enhanced_bug_examples() -> Dict[str, ExamplePair]:
    """Get bug examples with both problematic and fixed versions."""
    return {
        "index_error": ExamplePair(
            name="index_error",
            category="bugs",
            problem_code='''def get_last_three(items):  # ISSUE: No error handling for short lists
    return [items[-1], items[-2], items[-3]]''',
            solution_code='''def get_last_three(items):
    """Get up to the last three items from a list."""
    if len(items) == 0:
        return []
    elif len(items) < 3:
        return items.copy()  # Return all available items
    else:
        return items[-3:]    # Return last three''',
            learning_focus="Defensive programming and edge case handling",
            performance_improvement="Prevents runtime crashes"
        ),
        
        "division_by_zero": ExamplePair(
            name="division_by_zero",
            category="bugs",
            problem_code='''def calculate_average(numbers):  # ISSUE: No check for empty list
    return sum(numbers) / len(numbers)''',
            solution_code='''def calculate_average(numbers):
    """Calculate average with proper error handling."""
    if not numbers:  # Handle empty list
        return 0  # or raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)''',
            learning_focus="Input validation and error prevention",
            performance_improvement="Prevents division by zero errors"
        ),
        
        "mutable_default": ExamplePair(
            name="mutable_default",
            category="bugs", 
            problem_code='''def add_item(item, item_list=[]):  # ISSUE: Mutable default argument
    item_list.append(item)
    return item_list''',
            solution_code='''def add_item(item, item_list=None):
    """Add item to list, creating new list if none provided."""
    if item_list is None:
        item_list = []  # Create fresh list each time
    item_list.append(item)
    return item_list''',
            learning_focus="Avoiding mutable default argument pitfall",
            performance_improvement="Prevents unexpected behavior and bugs"
        )
    }

class EnhancedExampleGenerator:
    """Enhanced example generator with problem/solution pairs and validation."""
    
    @staticmethod
    def get_all_example_pairs() -> Dict[str, ExamplePair]:
        """Get all example pairs from all categories."""
        all_pairs = {}
        all_pairs.update(get_enhanced_performance_examples())
        all_pairs.update(get_enhanced_readability_examples())
        all_pairs.update(get_enhanced_bug_examples())
        return all_pairs
    
    @staticmethod
    def get_random_example_pair(exclude_categories: list = None, exclude_code: str = None) -> Tuple[ExamplePair, str]:
        """
        Get a random example pair with exclusion logic.
        Returns: (ExamplePair object, "problem"|"solution")
        """
        print(f"DEBUG: get_random_example_pair called with exclude_code: {exclude_code[:30] if exclude_code else None}...")
        
        # Get all example pairs
        all_pairs = EnhancedExampleGenerator.get_all_example_pairs()
        
        # Filter out excluded categories
        if exclude_categories:
            all_pairs = {k: v for k, v in all_pairs.items() 
                        if v.category not in exclude_categories}
            print(f"DEBUG: Filtered out categories: {exclude_categories}")
        
        # Filter out excluded code using normalized comparison
        if exclude_code:
            exclude_normalized = normalize_code(exclude_code)
            print(f"DEBUG: Normalized exclude_code: {exclude_normalized[:50]}...")
            
            # Also normalize and exclude the main example
            main_example_normalized = normalize_code(get_example_code())
            
            filtered_pairs = {}
            for name, pair in all_pairs.items():
                problem_normalized = normalize_code(pair.problem_code)
                solution_normalized = normalize_code(pair.solution_code)
                
                # Check if either problem or solution matches excluded code
                if (problem_normalized != exclude_normalized and 
                    solution_normalized != exclude_normalized and
                    problem_normalized != main_example_normalized):
                    filtered_pairs[name] = pair
                else:
                    print(f"DEBUG: Excluded {name} (matched exclude pattern)")
            
            all_pairs = filtered_pairs
            print(f"DEBUG: Example pairs after exclusion: {len(all_pairs)}")
        
        # Ensure we have examples left
        if not all_pairs:
            print("DEBUG: No examples left after exclusion, using fallback")
            # Fallback with guaranteed issue
            fallback_pair = ExamplePair(
                name="fallback_manual_loop",
                category="performance",
                problem_code='''def calculate_statistics(data):
    results = []
    for i in range(len(data)):  # ISSUE: Manual indexing
        results.append(data[i] * 2)
    return results''',
                solution_code='''def calculate_statistics(data):
    # List comprehension - more Pythonic
    return [value * 2 for value in data]''',
                learning_focus="Manual indexing vs direct iteration",
                performance_improvement="More readable and efficient"
            )
            return fallback_pair, "problem"
        
        # Select random example pair
        selected_name = random.choice(list(all_pairs.keys()))
        selected_pair = all_pairs[selected_name]
        print(f"DEBUG: Selected {selected_name} from {selected_pair.category}")
        
        # ALWAYS return the problem version for learning
        return selected_pair, "problem"
    
    @staticmethod
    def validate_example_has_issues(example_pair: ExamplePair) -> Dict[str, bool]:
        """
        Validate that an example pair has detectable issues in problem vs solution.
        Returns dict of detected differences.
        """
        from core.coaching_helpers import CodeAnalysisHelper
        
        try:
            # Analyze both problem and solution
            problem_analysis = CodeAnalysisHelper.analyze_code_for_coaching(example_pair.problem_code)
            solution_analysis = CodeAnalysisHelper.analyze_code_for_coaching(example_pair.solution_code)
            
            # Check for significant differences
            differences = {}
            for key in problem_analysis:
                if key.startswith('has_'):
                    problem_has_issue = problem_analysis.get(key, False)
                    solution_has_issue = solution_analysis.get(key, False)
                    # Difference exists if problem has issue but solution doesn't
                    differences[key] = problem_has_issue and not solution_has_issue
            
            print(f"DEBUG: Validation for {example_pair.name}:")
            print(f"  Problem issues: {[k for k, v in problem_analysis.items() if k.startswith('has_') and v]}")
            print(f"  Solution issues: {[k for k, v in solution_analysis.items() if k.startswith('has_') and v]}")
            print(f"  Significant differences: {[k for k, v in differences.items() if v]}")
            
            return differences
            
        except ImportError:
            # Fallback if CodeAnalysisHelper not available
            print("DEBUG: CodeAnalysisHelper not available for validation")
            return {"validation": True}  # Assume valid
    
    @staticmethod
    def get_example_by_category(category: str) -> Tuple[str, str]:
        """Get a problem example by category. Returns (code, category)."""
        all_pairs = EnhancedExampleGenerator.get_all_example_pairs()
        
        # Filter by category
        category_pairs = {k: v for k, v in all_pairs.items() if v.category == category}
        
        if category_pairs:
            # Return the first example's problem code
            first_pair = list(category_pairs.values())[0]
            return first_pair.problem_code, category
        else:
            # Default to main example
            return get_example_code(), "performance"

# Legacy compatibility functions
def get_performance_examples() -> dict:
    """Legacy compatibility - return problem codes only."""
    pairs = get_enhanced_performance_examples()
    return {name: pair.problem_code for name, pair in pairs.items()}

def get_readability_examples() -> dict:
    """Legacy compatibility - return problem codes only.""" 
    pairs = get_enhanced_readability_examples()
    return {name: pair.problem_code for name, pair in pairs.items()}

def get_bug_examples() -> dict:
    """Legacy compatibility - return problem codes only."""
    pairs = get_enhanced_bug_examples()
    return {name: pair.problem_code for name, pair in pairs.items()}

class ExampleGenerator:
    """Legacy ExampleGenerator class for backwards compatibility."""
    
    @staticmethod
    def get_random_example(exclude_categories: list = None, exclude_code: str = None) -> Tuple[str, str]:
        """
        Legacy method - returns (problem_code, category) for backwards compatibility.
        """
        example_pair, version = EnhancedExampleGenerator.get_random_example_pair(
            exclude_categories=exclude_categories, 
            exclude_code=exclude_code
        )
        return example_pair.problem_code, example_pair.category
    
    @staticmethod 
    def get_example_by_category(category: str) -> str:
        """Legacy method - return problem code by category."""
        code, _ = EnhancedExampleGenerator.get_example_by_category(category)
        return code