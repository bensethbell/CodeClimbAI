# utils/ - Utilities and Helper Functions

Support utilities for code execution, analysis, and session management.

## Files

### [`execution.py`](./execution.py)
Safe code execution with intelligent fake data generation.

#### Key Features
- **Smart Data Generation** - Analyzes code to create appropriate pandas DataFrames
- **Safe Execution Environment** - Isolated code execution with error handling
- **Column Pattern Recognition** - Detects data types from variable names
- **Comprehensive Error Reporting** - Detailed feedback for debugging

#### Usage
```python
from utils.execution import CodeExecutor

result = CodeExecutor.execute_code_safely(user_code)
if result['success']:
    print(f"Output: {result['output']}")
else:
    print(f"Error: {result['error']}")
```

### [`helpers.py`](./helpers.py)
Analysis and comparison utilities for code and sessions.

#### CodeDiffer
- **Simple diff calculation** between code versions
- **Significance threshold detection** for meaningful changes
- **Line-by-line change tracking**

#### FileUtils
- **Python syntax validation** without execution
- **Function name extraction** using AST parsing
- **Code metrics calculation** (complexity, line counts)

#### SessionUtils
- **Session serialization** for storage and persistence
- **Human-readable session summaries**
- **Learning progress tracking**

## Architecture Notes

### Safe Execution Design
The execution system creates isolated environments with controlled imports and fake data injection, enabling users to test code safely without requiring real datasets.

### Intelligent Data Generation
The system analyzes code patterns to generate contextually appropriate fake data:
- Price/cost columns get realistic monetary values
- Region/location columns get geographical categories  
- Date columns get proper datetime sequences
- Categorical columns get meaningful category sets

### Error Handling Philosophy
All utilities implement graceful degradation that preserves educational value even when technical issues occur, ensuring the learning experience continues despite edge cases.