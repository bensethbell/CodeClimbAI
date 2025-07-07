"""
Example code snippets and templates for the code review assistant.
COMPLETE VERSION: All original functionality preserved + enhancements.
"""
print("👀 examples.py loaded!")
import random
import re

def normalize_code(code: str) -> str:
    """PRESERVED: Normalize code for comparison by removing extra whitespace and comments."""
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
    """PRESERVED: Get the main pandas optimization example."""
    return '''def add_metrics(df):
    results = []
    for idx, row in df.iterrows():
        results.append(row["price"] * 0.2 + row["tax"])
    df["total"] = results
    return df'''

def get_performance_examples() -> dict:
    """ENHANCED: Get various performance optimization examples - ALL have clear issues."""
    return {
        "pandas_inefficient": '''def process_sales_data(df):
    totals = []
    for idx, row in df.iterrows():  # ISSUE: Uses iterrows()
        if row['region'] == 'North':
            totals.append(row['sales'] * 1.1)
        else:
            totals.append(row['sales'])
    df['adjusted_sales'] = totals
    return df''',
        
        "nested_loops": '''def find_duplicates(data1, data2):
    duplicates = []
    for item1 in data1:  # ISSUE: Nested loops O(n²)
        for item2 in data2:
            if item1['id'] == item2['id']:
                duplicates.append(item1)
    return duplicates''',
        
        "string_concatenation": '''def build_report(items):
    report = ""
    for item in items:  # ISSUE: String concatenation in loop
        report = report + f"Item: {item['name']}, Price: ${item['price']}\\n"
    return report''',
        
        "inefficient_filtering": '''def filter_expensive_items(products):
    expensive = []
    for product in products:  # ISSUE: Manual filtering instead of list comprehension
        if product['price'] > 100:
            expensive.append(product)
    return expensive''',
        
        "manual_loop_sum": '''def calculate_total(numbers):
    total = 0
    for i in range(len(numbers)):  # ISSUE: Manual indexing instead of direct iteration
        total = total + numbers[i]
    return total''',
        
        "inefficient_search": '''def find_user_by_id(users, target_id):
    for user in users:  # ISSUE: Linear search in list, could use dict
        if user['id'] == target_id:
            return user
    return None'''
    }

def get_readability_examples() -> dict:
    """ENHANCED: Get code readability improvement examples - ALL have clear issues."""
    return {
        "unclear_variable_names": '''def calc(x, y, z):  # ISSUE: Unclear variable names
    a = x * 0.1  # ISSUE: Single letter variables
    b = y + z
    c = a + b
    return c''',
        
        "no_comments": '''def process_data(df):  # ISSUE: No comments explaining complex logic
    df['new_col'] = df['price'] * 0.15 + df['base']
    df = df[df['new_col'] > 50]
    df['final'] = df['new_col'] * 0.8
    return df.groupby('category').sum()''',
        
        "long_function": '''def analyze_sales(df):  # ISSUE: Function doing too many things
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
        
        "repetitive_code": '''def process_regions(df):  # ISSUE: Repetitive code patterns
    north_data = df[df['region'] == 'North']
    north_result = north_data['sales'].sum()
    south_data = df[df['region'] == 'South']  # REPETITIVE
    south_result = south_data['sales'].sum()
    east_data = df[df['region'] == 'East']    # REPETITIVE
    east_result = east_data['sales'].sum()
    west_data = df[df['region'] == 'West']    # REPETITIVE
    west_result = west_data['sales'].sum()
    return [north_result, south_result, east_result, west_result]'''
    }

def get_bug_examples() -> dict:
    """ENHANCED: Get examples with potential bugs - ALL have clear issues."""
    return {
        "index_error": '''def get_last_three(items):  # ISSUE: No error handling for short lists
    return [items[-1], items[-2], items[-3]]''',
        
        "division_by_zero": '''def calculate_average(numbers):  # ISSUE: No check for empty list
    return sum(numbers) / len(numbers)''',
        
        "type_error": '''def concatenate_values(data):  # ISSUE: No type checking
    result = ""
    for item in data:
        result += item  # Will fail if item is not string
    return result''',
        
        "mutable_default": '''def add_item(item, item_list=[]):  # ISSUE: Mutable default argument
    item_list.append(item)
    return item_list''',
        
        "file_handling": '''def read_config(filename):  # ISSUE: No error handling for file operations
    file = open(filename, 'r')
    content = file.read()
    return content'''
    }

def get_security_examples() -> dict:
    """ENHANCED: Get examples with security concerns - ALL have clear issues."""
    return {
        "sql_injection": '''def get_user_data(username):  # ISSUE: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return execute_query(query)''',
        
        "unsafe_eval": '''def calculate_expression(expr):  # ISSUE: Dangerous use of eval
    return eval(expr)''',
        
        "path_traversal": '''def read_file(filename):  # ISSUE: Path traversal vulnerability
    with open(f"data/{filename}", 'r') as f:
        return f.read()''',
        
        "hardcoded_secrets": '''def connect_to_db():  # ISSUE: Hardcoded credentials
    username = "admin"
    password = "password123"
    return connect(username, password)'''
    }

class ExampleGenerator:
    """ENHANCED: Generate contextual examples based on learning objectives."""
    
    @staticmethod
    def get_example_by_category(category: str) -> str:
        """PRESERVED: Get an example by category."""
        examples = {
            'performance': get_performance_examples(),
            'readability': get_readability_examples(),
            'bugs': get_bug_examples(),
            'security': get_security_examples()
        }
        
        if category in examples:
            # Return the first example from the category
            return list(examples[category].values())[0]
        else:
            # Default to main example
            return get_example_code()
    
    @staticmethod
    def get_all_examples_by_category(category: str) -> dict:
        """PRESERVED: Get all examples in a category."""
        categories = {
            'performance': get_performance_examples(),
            'readability': get_readability_examples(),
            'bugs': get_bug_examples(),
            'security': get_security_examples()
        }
        
        return categories.get(category, {})
    
    @staticmethod
    def get_random_example(exclude_categories: list = None, exclude_code: str = None) -> tuple[str, str]:
        """
        ENHANCED: Get a random example with GUARANTEED optimization issues.
        PRESERVED: All original exclusion logic and functionality.
        """
        print(f"DEBUG: get_random_example called with exclude_code: {exclude_code[:30] if exclude_code else None}...")
        
        # Get all example categories with ENHANCED examples
        examples = {
            "performance": get_performance_examples(),
            "readability": get_readability_examples(),
            "bugs": get_bug_examples(),
            "security": get_security_examples()
        }
        
        # Filter out excluded categories
        if exclude_categories:
            examples = {k: v for k, v in examples.items() if k not in exclude_categories}
            print(f"DEBUG: Filtered out categories: {exclude_categories}")

        # Build list of all examples with categories
        all_examples = []
        for category, codes in examples.items():
            for code_name, code in codes.items():
                all_examples.append((code, category, code_name))
        
        print(f"DEBUG: Total examples available: {len(all_examples)}")
        
        # Filter out excluded code using normalized comparison
        if exclude_code:
            exclude_normalized = normalize_code(exclude_code)
            print(f"DEBUG: Normalized exclude_code: {exclude_normalized[:50]}...")
            
            # Also normalize and exclude the main example
            main_example_normalized = normalize_code(get_example_code())
            
            filtered_examples = []
            for code, category, name in all_examples:
                code_normalized = normalize_code(code)
                
                # Check if this code matches either excluded code
                if (code_normalized != exclude_normalized and 
                    code_normalized != main_example_normalized):
                    filtered_examples.append((code, category, name))
                else:
                    print(f"DEBUG: Excluded {name} from {category} (matched exclude pattern)")
            
            all_examples = filtered_examples
            print(f"DEBUG: Examples after exclusion: {len(all_examples)}")

        # Ensure we have examples left
        if not all_examples:
            print("DEBUG: No examples left after exclusion, using fallback with guaranteed issue")
            # ENHANCED: Fallback with guaranteed detectable issue
            fallback_code = '''def calculate_statistics(data):
    results = []
    for i in range(len(data)):  # ISSUE: Manual indexing instead of direct iteration
        results.append(data[i] * 2)
    return results'''
            return fallback_code, "performance"

        # Select random example
        selected = random.choice(all_examples)
        code, category, name = selected
        print(f"DEBUG: Selected {name} from {category}: {code[:30]}...")
        
        return code, category
        
    @staticmethod
    def get_progressive_examples() -> list:
        """PRESERVED: Get examples in order of increasing difficulty."""
        return [
            ("Basic pandas optimization", get_example_code()),
            ("String concatenation", get_performance_examples()["string_concatenation"]),
            ("Nested loops", get_performance_examples()["nested_loops"]),
            ("Complex function refactoring", get_readability_examples()["long_function"])
        ]
    
    @staticmethod
    def get_example_description(code: str) -> str:
        """PRESERVED: Get a description of what the example demonstrates."""
        descriptions = {
            "add_metrics": "Pandas iterrows() optimization - demonstrates inefficient row-by-row processing",
            "process_sales_data": "Pandas conditional processing with iterrows() - shows inefficient filtering",
            "find_duplicates": "Nested loop optimization - O(n²) algorithm that can be improved",
            "build_report": "String concatenation optimization - inefficient string building",
            "filter_expensive_items": "List comprehension opportunity - manual filtering vs built-in methods",
            "calc": "Variable naming and documentation - unclear function purpose",
            "process_data": "Code documentation - complex operations without explanation",
            "analyze_sales": "Function decomposition - overly long function doing multiple things",
            "get_last_three": "Error handling - potential IndexError with short lists",
            "calculate_average": "Division by zero - missing empty list check",
            "concatenate_values": "Type safety - potential TypeError with mixed data types",
            "add_item": "Mutable default arguments - classic Python gotcha",
            "get_user_data": "SQL injection vulnerability - unsafe string formatting",
            "calculate_expression": "Code injection - dangerous use of eval()",
            "read_file": "Path traversal - unsafe file path handling"
        }
        
        # Try to match code content to descriptions
        for key, desc in descriptions.items():
            if key in code:
                return desc
        
        return "Code optimization opportunity - multiple improvement areas available"

def get_starter_templates() -> dict:
    """PRESERVED: Get template code for different programming patterns."""
    return {
        "data_processing": '''import pandas as pd

def process_data(df):
    # TODO: Add your data processing logic here
    pass

# Example usage:
# df = pd.read_csv('data.csv')
# result = process_data(df)''',
        
        "algorithm": '''def solve_problem(input_data):
    # TODO: Implement your algorithm here
    pass

# Example usage:
# result = solve_problem([1, 2, 3, 4, 5])''',
        
        "class_template": '''class DataProcessor:
    def __init__(self):
        # TODO: Initialize your class
        pass
    
    def process(self, data):
        # TODO: Add processing logic
        pass''',
        
        "web_scraping": '''import requests
from bs4 import BeautifulSoup

def scrape_data(url):
    # TODO: Add web scraping logic
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Add your parsing logic here
    pass''',
        
        "file_processing": '''def process_file(filename):
    # TODO: Add file processing logic
    with open(filename, 'r') as file:
        # Add your file processing here
        pass'''
    }

# ENHANCED: Verification function to ensure all examples have detectable issues
def verify_all_examples_have_issues():
    """ENHANCED: Verify that all examples have detectable optimization issues."""
    # This would require importing CodeAnalysisHelper, but we'll include it for completeness
    try:
        from core.coaching_helpers import CodeAnalysisHelper
        
        all_examples = {}
        all_examples.update(get_performance_examples())
        all_examples.update(get_readability_examples()) 
        all_examples.update(get_bug_examples())
        all_examples.update(get_security_examples())
        
        issues_found = {}
        for name, code in all_examples.items():
            analysis = CodeAnalysisHelper.analyze_code_for_coaching(code)
            issues_found[name] = analysis.get('has_any_issue', False)
        
        return issues_found
    except ImportError:
        # Return placeholder result if CodeAnalysisHelper not available
        return {"verification": "requires_coaching_helpers_import"}