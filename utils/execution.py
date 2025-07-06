"""
Code execution utilities with fake data generation and error handling.
"""

import io
import sys
import traceback
import pandas as pd
import numpy as np
import re

class CodeExecutor:
    """Handles code execution with fake data generation and error handling."""
    
    @staticmethod
    def generate_fake_data_for_pandas():
        """Generate realistic fake data for pandas examples."""
        # Generate sample data to match the add_metrics function (hardcoded for main example)
        np.random.seed(42)  # Consistent fake data
        
        data = {
            'price': np.random.uniform(10.0, 500.0, 1000).round(2),
            'tax': np.random.uniform(0.5, 50.0, 1000).round(2),
            'product': np.random.choice(['Widget A', 'Widget B', 'Widget C'], 1000),
            'category': np.random.choice(['Electronics', 'Books', 'Clothing'], 1000)
        }
        
        return pd.DataFrame(data)
    
    @staticmethod
    def analyze_code_and_generate_data(code: str):
        """Analyze code to intelligently generate appropriate fake data."""
        # Default to the hardcoded example for known case
        if 'add_metrics' in code and 'price' in code and 'tax' in code:
            return CodeExecutor.generate_fake_data_for_pandas()
        
        # Extract column references from pandas code
        column_patterns = [
            r"df\[(['\"])([^'\"]+)\1\]",  # df['column'] or df["column"]
            r"df\.([a-zA-Z_][a-zA-Z0-9_]*)",  # df.column
            r"row\[(['\"])([^'\"]+)\1\]",  # row['column'] or row["column"]
        ]
        
        columns = set()
        for pattern in column_patterns:
            matches = re.findall(pattern, code)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    columns.add(match[1])  # Extract column name from quoted match
                elif isinstance(match, str):
                    columns.add(match)  # Direct column name match
        
        # Remove common non-column words
        exclude_words = {'index', 'iloc', 'loc', 'values', 'shape', 'columns', 'dtypes', 'head', 'tail'}
        columns = {col for col in columns if col not in exclude_words}
        
        if not columns:
            # Fallback: create generic dataset
            columns = {'value', 'category', 'amount'}
        
        # Generate appropriate data for each detected column
        np.random.seed(42)
        data = {}
        num_rows = 1000
        
        for col in columns:
            col_lower = col.lower()
            
            # Generate data based on column name patterns
            if any(word in col_lower for word in ['price', 'cost', 'amount', 'salary', 'revenue']):
                data[col] = np.random.uniform(10.0, 1000.0, num_rows).round(2)
            elif any(word in col_lower for word in ['tax', 'fee', 'discount']):
                data[col] = np.random.uniform(0.5, 50.0, num_rows).round(2)
            elif any(word in col_lower for word in ['age', 'year', 'count']):
                data[col] = np.random.randint(18, 80, num_rows)
            elif any(word in col_lower for word in ['score', 'rating', 'percentage']):
                data[col] = np.random.uniform(0, 100, num_rows).round(1)
            elif any(word in col_lower for word in ['region', 'location', 'area']):
                data[col] = np.random.choice(['North', 'South', 'East', 'West', 'Central'], num_rows)
            elif any(word in col_lower for word in ['category', 'type', 'class']):
                data[col] = np.random.choice(['Category A', 'Category B', 'Category C'], num_rows)
            elif any(word in col_lower for word in ['product', 'item', 'name']):
                data[col] = np.random.choice(['Product X', 'Product Y', 'Product Z'], num_rows)
            elif any(word in col_lower for word in ['date', 'time']):
                data[col] = pd.date_range('2023-01-01', periods=num_rows, freq='D')[:num_rows]
            elif any(word in col_lower for word in ['status', 'state']):
                data[col] = np.random.choice(['Active', 'Inactive', 'Pending'], num_rows)
            else:
                # Default: generate mixed numeric data
                data[col] = np.random.uniform(1.0, 100.0, num_rows).round(2)
        
        return pd.DataFrame(data)
    
    @staticmethod
    def execute_code_safely(code: str, generate_data: bool = True):
        """Execute code safely with intelligent fake data generation and return results or errors."""
        # Capture output
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # Generate fake data if needed
            fake_data = None
            if generate_data and ('pandas' in code or 'pd' in code or 'df' in code):
                fake_data = CodeExecutor.analyze_code_and_generate_data(code)
            
            # Create execution environment
            exec_globals = {
                '__builtins__': __builtins__,
                'pd': pd,
                'np': np,
                'df': fake_data  # Provide the fake dataframe
            }
            
            # Redirect output
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # Execute the code
            exec(code, exec_globals)
            
            # Get any output
            output = stdout_capture.getvalue()
            error_output = stderr_capture.getvalue()
            
            return {
                'success': True,
                'output': output,
                'error': error_output,
                'fake_data_info': f"Generated sample dataset with {len(fake_data)} rows and columns: {list(fake_data.columns)}" if fake_data is not None else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'fake_data_info': f"Generated sample dataset with {len(fake_data)} rows and columns: {list(fake_data.columns)}" if fake_data is not None else None
            }
        finally:
            # Restore output
            sys.stdout = old_stdout
            sys.stderr = old_stderr