"""
Example code snippets and templates for the code review assistant.
FIXED: Random example selection with proper exclusion logic.
"""
print("👀 examples.py loaded!")
import random
import re

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
    """Get the main pandas optimization example."""
    return '''def add_metrics(df):
    results = []
    for idx, row in df.iterrows():
        results.append(row["price"] * 0.2 + row["tax"])
    df["total"] = results
    return df'''

def get_performance_examples() -> dict:
    """Get various performance optimization examples."""
    return {
        "pandas_inefficient": '''def process_sales_data(df):
    totals = []
    for idx, row in df.iterrows():
        if row['region'] == 'North':
            totals.append(row['sales'] * 1.1)
        else:
            totals.append(row['sales'])
    df['adjusted_sales'] = totals
    return df''',
        
        "nested_loops": '''def find_duplicates(data1, data2):
    duplicates = []
    for item1 in data1:
        for item2 in data2:
            if item1['id'] == item2['id']:
                duplicates.append(item1)
    return duplicates''',
        
        "string_concatenation": '''def build_report(items):
    report = ""
    for item in items:
        report = report + f"Item: {item['name']}, Price: ${item['price']}\n"
    return report''',
        
        "inefficient_filtering": '''def filter_expensive_items(products):
    expensive = []
    for product in products:
        if product['price'] > 100:
            expensive.append(product)
    return expensive'''
    }

def get_readability_examples() -> dict:
    """Get code readability improvement examples."""
    return {
        "unclear_variable_names": '''def calc(x, y, z):
    a = x * 0.1
    b = y + z
    c = a + b
    return c''',
        
        "no_comments": '''def process_data(df):
    df['new_col'] = df['price'] * 0.15 + df['base']
    df = df[df['new_col'] > 50]
    df['final'] = df['new_col'] * 0.8
    return df.groupby('category').sum()''',
        
        "long_function": '''def analyze_sales(df):
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
    return {'North': north_sales, 'South': south_sales, 'East': east_sales, 'West': west_sales}'''
    }

def get_bug_examples() -> dict:
    """Get examples with potential bugs."""
    return {
        "index_error": '''def get_last_three(items):
    return [items[-1], items[-2], items[-3]]''',
        
        "division_by_zero": '''def calculate_average(numbers):
    return sum(numbers) / len(numbers)''',
        
        "type_error": '''def concatenate_values(data):
    result = ""
    for item in data:
        result += item
    return result''',
        
        "mutable_default": '''def add_item(item, item_list=[]):
    item_list.append(item)
    return item_list'''
    }

def get_security_examples() -> dict:
    """Get examples with security concerns."""
    return {
        "sql_injection": '''def get_user_data(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return execute_query(query)''',
        
        "unsafe_eval": '''def calculate_expression(expr):
    return eval(expr)''',
        
        "path_traversal": '''def read_file(filename):
    with open(f"data/{filename}", 'r') as f:
        return f.read()'''
    }

class ExampleGenerator:
    """Generate contextual examples based on learning objectives."""
    
    @staticmethod
    def get_example_by_category(category: str) -> str:
        """Get an example by category."""
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
        """Get all examples in a category."""
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
        Get a random example with its category, excluding specific code.
        FIXED: Improved exclusion logic with code normalization and better debugging.
        """
        print(f"DEBUG: get_random_example called with exclude_code: {exclude_code[:30] if exclude_code else None}...")
        
        # Get all example categories
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
            print("DEBUG: No examples left after exclusion, creating fallback")
            # Create a unique fallback that's definitely different
            fallback_code = '''def calculate_statistics(data):
    total = sum(data)
    count = len(data)
    average = total / count if count > 0 else 0
    return {'total': total, 'count': count, 'average': average}'''
            return fallback_code, "performance"

        # Select random example
        selected = random.choice(all_examples)
        code, category, name = selected
        print(f"DEBUG: Selected {name} from {category}: {code[:30]}...")
        
        return code, category
        
    @staticmethod
    def get_progressive_examples() -> list:
        """Get examples in order of increasing difficulty."""
        return [
            ("Basic pandas optimization", get_example_code()),
            ("String concatenation", get_performance_examples()["string_concatenation"]),
            ("Nested loops", get_performance_examples()["nested_loops"]),
            ("Complex function refactoring", get_readability_examples()["long_function"])
        ]
    
    @staticmethod
    def get_example_description(code: str) -> str:
        """Get a description of what the example demonstrates."""
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
    """Get template code for different programming patterns."""
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