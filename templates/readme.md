# templates/ - Learning Materials and Examples

Contains code examples and educational content used throughout the learning experience.

## Files

### [`examples.py`](./examples.py)
Enhanced example generation system with problem/solution pairs for different optimization categories.

#### Example Categories

**Performance Examples**
- Pandas vectorization vs iterrows()
- Nested loops and algorithmic complexity
- String concatenation optimization
- Data structure efficiency

**Readability Examples**  
- Variable naming and code clarity
- Function decomposition and organization
- DRY principle application

**Bug Prevention Examples**
- Edge case handling
- Input validation
- Common Python pitfalls

#### Key Features

- **Problem/Solution Pairs** - Each example includes both problematic and optimized versions
- **Smart Exclusion Logic** - Prevents showing the same example twice
- **Intelligent Data Generation** - Creates appropriate fake datasets for testing
- **Validation System** - Ensures examples have detectable optimization opportunities

#### Usage

```python
from templates.examples import get_example_code, ExampleGenerator

# Get the main pandas optimization example
main_example = get_example_code()

# Get a random example excluding previous ones
code, category = ExampleGenerator.get_random_example(exclude_code=previous_code)

# Get example by specific category
performance_code, _ = ExampleGenerator.get_example_by_category("performance")
```

## Example Structure

Each example is designed to:
1. **Demonstrate a specific optimization concept**
2. **Contain detectable performance or quality issues**
3. **Be realistic and representative of common coding patterns**
4. **Support the Socratic questioning methodology**