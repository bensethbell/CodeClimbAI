# templates/examples.py
"""
Enhanced example code snippets with clear docstrings and no spoiler comments.
FIXED VERSION: Each example has clear purpose and hidden optimization opportunities.
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
    """Get the main pandas optimization example with clear docstring."""
    return '''def add_metrics(df):
    """Calculate additional metrics for sales data.
    INPUT: DataFrame with 'price' and 'tax' columns
    OUTPUT: DataFrame with new 'total' column added
    """
    results = []
    for idx, row in df.iterrows():
        results.append(row["price"] * 0.2 + row["tax"])
    df["total"] = results
    return df'''

def get_enhanced_performance_examples() -> Dict[str, ExamplePair]:
    """Get performance examples with clear docstrings and no spoiler comments."""
    return {
        "pandas_iterrows": ExamplePair(
            name="pandas_iterrows",
            category="performance",
            problem_code='''def process_sales_data(df):
    """Apply regional sales adjustments to the dataset.
    INPUT: DataFrame with 'sales' and 'region' columns
    OUTPUT: DataFrame with 'adjusted_sales' column added
    """
    totals = []
    for idx, row in df.iterrows():
        if row['region'] == 'North':
            totals.append(row['sales'] * 1.1)
        else:
            totals.append(row['sales'])
    df['adjusted_sales'] = totals
    return df''',
            solution_code='''def process_sales_data(df):
    """Apply regional sales adjustments to the dataset.
    INPUT: DataFrame with 'sales' and 'region' columns
    OUTPUT: DataFrame with 'adjusted_sales' column added
    """
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
    """Find items that appear in both datasets.
    INPUT: Two lists of dictionaries with 'id' keys
    OUTPUT: List of items from data1 that have matching IDs in data2
    """
    duplicates = []
    for item1 in data1:
        for item2 in data2:
            if item1['id'] == item2['id']:
                duplicates.append(item1)
    return duplicates''',
            solution_code='''def find_duplicates(data1, data2):
    """Find items that appear in both datasets.
    INPUT: Two lists of dictionaries with 'id' keys
    OUTPUT: List of items from data1 that have matching IDs in data2
    """
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
    """Generate a formatted report from a list of items.
    INPUT: List of dictionaries with 'name' and 'price' keys
    OUTPUT: Multi-line string report
    """
    report = ""
    for item in items:
        report += f"Item: {item['name']}, Price: ${item['price']}\\n"
    return report''',
            solution_code='''def build_report(items):
    """Generate a formatted report from a list of items.
    INPUT: List of dictionaries with 'name' and 'price' keys
    OUTPUT: Multi-line string report
    """
    # Collect in list, then join - much more efficient
    lines = []
    for item in items:
        lines.append(f"Item: {item['name']}, Price: ${item['price']}")
    return "\\n".join(lines)''',
            learning_focus="Efficient string building techniques",
            performance_improvement="Linear vs quadratic string operations"
        ),
        
        "manual_indexing_with_concat": ExamplePair(
            name="manual_indexing_with_concat",
            category="performance",
            problem_code='''def format_data(items):
    """Convert a list of items to a comma-separated string.
    INPUT: List of any objects that can be converted to string
    OUTPUT: Single string with items separated by commas
    """
    result = ""
    for i in range(len(items)):
        result += str(items[i]) + ", "
    return result''',
            solution_code='''def format_data(items):
    """Convert a list of items to a comma-separated string.
    INPUT: List of any objects that can be converted to string
    OUTPUT: Single string with items separated by commas
    """
    # Both more Pythonic and efficient
    return ", ".join(str(item) for item in items)''',
            learning_focus="Direct iteration and efficient string joining",
            performance_improvement="More readable and much faster"
        ),
        
        "inefficient_search_with_loops": ExamplePair(
            name="inefficient_search_with_loops",
            category="performance",
            problem_code='''def find_matching_users(users, target_ids):
    """Find users whose IDs match the target list.
    INPUT: List of user dicts with 'id' key, list of target IDs
    OUTPUT: List of matching user dictionaries
    """
    matches = []
    for target_id in target_ids:
        for user in users:
            if user['id'] == target_id:
                matches.append(user)
    return matches''',
            solution_code='''def find_matching_users(users, target_ids):
    """Find users whose IDs match the target list.
    INPUT: List of user dicts with 'id' key, list of target IDs
    OUTPUT: List of matching user dictionaries
    """
    # Use dictionary for O(1) lookup instead of O(n²) nested loops
    user_dict = {user['id']: user for user in users}
    return [user_dict[target_id] for target_id in target_ids if target_id in user_dict]''',
            learning_focus="Data structure choice and avoiding nested loops",
            performance_improvement="O(n²) to O(n) complexity reduction"
        ),

        "inefficient_filtering": ExamplePair(
            name="inefficient_filtering",
            category="performance",
            problem_code='''def filter_expensive_items(products):
    """Get products that cost more than $100.
    INPUT: List of product dictionaries with 'price' key
    OUTPUT: List of products where price > 100
    """
    expensive = []
    for product in products:
        if product['price'] > 100:
            expensive.append(product)
    return expensive''',
            solution_code='''def filter_expensive_items(products):
    """Get products that cost more than $100.
    INPUT: List of product dictionaries with 'price' key
    OUTPUT: List of products where price > 100
    """
    # List comprehension - more Pythonic and efficient
    return [product for product in products if product['price'] > 100]''',
            learning_focus="List comprehensions vs manual loops",
            performance_improvement="More readable and typically faster"
        ),

        "inefficient_counting": ExamplePair(
            name="inefficient_counting",
            category="performance",
            problem_code='''def count_occurrences(items):
    """Count how many times each item appears in the list.
    INPUT: List of hashable items
    OUTPUT: Dictionary mapping items to their counts
    """
    counts = {}
    for item in items:
        if item in counts:
            counts[item] = counts[item] + 1
        else:
            counts[item] = 1
    return counts''',
            solution_code='''from collections import Counter

def count_occurrences(items):
    """Count how many times each item appears in the list.
    INPUT: List of hashable items
    OUTPUT: Dictionary mapping items to their counts
    """
    # Counter is optimized for this exact use case
    return Counter(items)''',
            learning_focus="Using specialized data structures",
            performance_improvement="Leverages C-level optimizations"
        ),

        "inefficient_aggregation_with_concat": ExamplePair(
            name="inefficient_aggregation_with_concat",
            category="performance",
            problem_code='''def summarize_numbers(numbers):
    """Create a running summary of number additions.
    INPUT: List of numbers
    OUTPUT: String showing running totals
    """
    total = 0
    summary = ""
    for num in numbers:
        total = total + num
        summary += f"Added {num}, total now {total}\\n"
    return summary''',
            solution_code='''def summarize_numbers(numbers):
    """Create a running summary of number additions.
    INPUT: List of numbers
    OUTPUT: String showing running totals
    """
    # Use built-in sum and efficient string building
    total = sum(numbers)
    lines = [f"Added {num}, total now {sum(numbers[:i+1])}" for i, num in enumerate(numbers)]
    return "\\n".join(lines)''',
            learning_focus="Built-in functions and efficient string operations",
            performance_improvement="Leverages optimizations and avoids quadratic string building"
        )
    }

def get_enhanced_readability_examples() -> Dict[str, ExamplePair]:
    """Get readability examples with clear docstrings and no spoiler comments."""
    return {
        "unclear_variables": ExamplePair(
            name="unclear_variables",
            category="readability",
            problem_code='''def calc(x, y, z):
    """Calculate final amount including fees and tax.
    INPUT: Base price, base fee, additional fee
    OUTPUT: Total amount including all charges
    """
    a = x * 0.1
    b = y + z
    c = a + b
    return c''',
            solution_code='''def calculate_total_with_tax(price, base_fee, additional_fee):
    """Calculate final amount including fees and tax.
    INPUT: Base price, base fee, additional fee
    OUTPUT: Total amount including all charges
    """
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
            problem_code='''def process_regions(df):
    """Calculate sales totals for each region.
    INPUT: DataFrame with 'region' and 'sales' columns
    OUTPUT: List of sales totals [north, south, east, west]
    """
    north_data = df[df['region'] == 'North']
    north_result = north_data['sales'].sum()
    south_data = df[df['region'] == 'South']
    south_result = south_data['sales'].sum()
    east_data = df[df['region'] == 'East']
    east_result = east_data['sales'].sum()
    west_data = df[df['region'] == 'West']
    west_result = west_data['sales'].sum()
    return [north_result, south_result, east_result, west_result]''',
            solution_code='''def process_regions(df):
    """Calculate sales totals for each region.
    INPUT: DataFrame with 'region' and 'sales' columns
    OUTPUT: Dictionary mapping region names to sales totals
    """
    # Even better: use pandas groupby
    return df.groupby('region')['sales'].sum().to_dict()''',
            learning_focus="DRY principle and pandas groupby",
            performance_improvement="Easier to maintain and extend"
        )
    }

def get_enhanced_bug_examples() -> Dict[str, ExamplePair]:
    """Get bug examples with clear docstrings and no spoiler comments."""
    return {
        "index_error": ExamplePair(
            name="index_error",
            category="bugs",
            problem_code='''def get_last_three(items):
    """Get the last three items from a list.
    INPUT: List of any items
    OUTPUT: List containing up to the last 3 items
    """
    result = []
    for i in range(3):
        result.append(items[len(items) - 3 + i])
    return result''',
            solution_code='''def get_last_three(items):
    """Get the last three items from a list.
    INPUT: List of any items
    OUTPUT: List containing up to the last 3 items
    """
    if len(items) == 0:
        return []
    elif len(items) < 3:
        return items.copy()  # Return all available items
    else:
        return items[-3:]    # Return last three''',
            learning_focus="Defensive programming and Pythonic slicing",
            performance_improvement="Prevents runtime crashes and cleaner code"
        ),
        
        "mutable_default": ExamplePair(
            name="mutable_default",
            category="bugs", 
            problem_code='''def add_item(item, item_list=[]):
    """Add an item to a list and return the updated list.
    INPUT: Item to add, optional existing list
    OUTPUT: New list containing all items
    """
    new_list = []
    for existing_item in item_list:
        new_list.append(existing_item)
    new_list.append(item)
    return new_list''',
            solution_code='''def add_item(item, item_list=None):
    """Add an item to a list and return the updated list.
    INPUT: Item to add, optional existing list
    OUTPUT: New list containing all items
    """
    if item_list is None:
        item_list = []  # Create fresh list each time
    result = item_list.copy()  # Efficient copying
    result.append(item)
    return result''',
            learning_focus="Avoiding mutable defaults and efficient copying",
            performance_improvement="Prevents unexpected behavior and cleaner code"
        ),

        "inefficient_file_processing": ExamplePair(
            name="inefficient_file_processing",
            category="bugs",
            problem_code='''def process_large_file(filename):
    """Read and clean lines from a text file.
    INPUT: Path to text file
    OUTPUT: List of cleaned lines (no newlines)
    """
    lines = []
    file = open(filename, 'r')
    for line in file:
        processed_line = ""
        for char in line:
            if char != '\\n':
                processed_line = processed_line + char
        lines.append(processed_line)
    file.close()
    return lines''',
            solution_code='''def process_large_file(filename):
    """Read and clean lines from a text file.
    INPUT: Path to text file
    OUTPUT: List of cleaned lines (no newlines)
    """
    try:
        with open(filename, 'r') as file:  # Context manager
            return [line.strip() for line in file]  # List comprehension
    except FileNotFoundError:
        return []  # Graceful error handling''',
            learning_focus="Context managers, list comprehensions, and error handling",
            performance_improvement="Much faster and prevents resource leaks"
        )
    }

# Rest of the file remains the same...
class EnhancedExampleGenerator:
    """Enhanced example generator with verified optimization opportunities."""
    
    @staticmethod
    def get_all_example_pairs() -> Dict[str, ExamplePair]:
        """Get all example pairs from all categories."""
        all_pairs = {}
        all_pairs.update(get_enhanced_performance_examples())
        all_pairs.update(get_enhanced_readability_examples())
        all_pairs.update(get_enhanced_bug_examples())
        return all_pairs
    
    @staticmethod
    def validate_example_has_issues(example_pair: ExamplePair) -> bool:
        """Validate that an example has clear optimization opportunities."""
        code = example_pair.problem_code
        
        # Check for clear performance issues
        has_iterrows = 'iterrows' in code.lower()
        has_string_concat = '+=' in code and any(s in code.lower() for s in ['str', '"', "'"])
        has_nested_loops = code.count('for ') > 1
        has_manual_indexing = 'range(len(' in code
        has_manual_iteration = 'for i in range' in code
        has_inefficient_patterns = any([
            'append(' in code and 'for' in code,  # Manual list building
            '.iloc[' in code,  # Pandas inefficiency
            'if item in' in code and 'for' in code,  # Inefficient searching
        ])
        
        # Must have at least one clear issue
        return any([
            has_iterrows, has_string_concat, has_nested_loops, 
            has_manual_indexing, has_manual_iteration, has_inefficient_patterns
        ])
    
    @staticmethod
    def get_random_example_pair(exclude_categories: list = None, exclude_code: str = None) -> Tuple[ExamplePair, str]:
        """Get a random example pair with exclusion logic and validation."""
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
                    # Validate the example has clear issues
                    if EnhancedExampleGenerator.validate_example_has_issues(pair):
                        filtered_pairs[name] = pair
                    else:
                        print(f"DEBUG: Excluded {name} (no clear optimization opportunities)")
                else:
                    print(f"DEBUG: Excluded {name} (matched exclude pattern)")
            
            all_pairs = filtered_pairs
            print(f"DEBUG: Example pairs after filtering: {len(all_pairs)}")
        
        # Ensure we have examples left
        if not all_pairs:
            print("DEBUG: No examples left after exclusion, using guaranteed fallback")
            # Fallback with guaranteed multiple issues
            fallback_pair = ExamplePair(
                name="fallback_multiple_issues",
                category="performance",
                problem_code='''def process_data(items):
    """Transform a list of items to uppercase strings.
    INPUT: List of items that can be converted to strings
    OUTPUT: List of uppercase string representations
    """
    results = []
    for i in range(len(items)):
        result = ""
        for char in str(items[i]):
            result = result + char.upper()
        results.append(result)
    return results''',
                solution_code='''def process_data(items):
    """Transform a list of items to uppercase strings.
    INPUT: List of items that can be converted to strings
    OUTPUT: List of uppercase string representations
    """
    # Multiple optimizations: direct iteration + list comprehension + str methods
    return [str(item).upper() for item in items]''',
                learning_focus="Multiple optimization opportunities",
                performance_improvement="Much more readable and efficient"
            )
            return fallback_pair, "problem"
        
        # Select random example pair
        selected_name = random.choice(list(all_pairs.keys()))
        selected_pair = all_pairs[selected_name]
        print(f"DEBUG: Selected {selected_name} from {selected_pair.category}")
        
        # ALWAYS return the problem version for learning
        return selected_pair, "problem"
    
    @staticmethod
    def get_example_by_category(category: str) -> Tuple[str, str]:
        """Get a problem example by category. Returns (code, category)."""
        all_pairs = EnhancedExampleGenerator.get_all_example_pairs()
        
        # Filter by category and validate
        category_pairs = {}
        for k, v in all_pairs.items():
            if v.category == category and EnhancedExampleGenerator.validate_example_has_issues(v):
                category_pairs[k] = v
        
        if category_pairs:
            # Return the first valid example's problem code
            first_pair = list(category_pairs.values())[0]
            return first_pair.problem_code, category
        else:
            # Default to main example which is guaranteed to have issues
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
        """Legacy method - returns (problem_code, category) for backwards compatibility."""
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