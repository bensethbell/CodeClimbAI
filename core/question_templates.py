"""
Question templates for adaptive coaching system.
FINAL FIX: Removed backticks from question text to prevent code block styling.
"""

from typing import List, Dict, Any
from .coaching_models import LearningQuestion, QuestionType, QuestionOption
import uuid

class QuestionTemplates:
    """Collection of reusable question templates for different code patterns."""
    
    @staticmethod
    def create_pandas_iterrows_mcq(user_code: str) -> LearningQuestion:
        """Create MCQ about pandas iterrows performance - FIXED: No backticks."""
        return LearningQuestion(
            question_id=str(uuid.uuid4()),
            question_type=QuestionType.MULTIPLE_CHOICE,
            title="Pandas Performance Question",
            question_text="Looking at your code with df.iterrows(), which statement is most accurate about its performance?",
            correct_answer="B",
            options=[
                QuestionOption(
                    text="A) iterrows() is the fastest way to process pandas DataFrames",
                    is_correct=False,
                    explanation="Actually, iterrows() is one of the slowest methods for DataFrame processing."
                ),
                QuestionOption(
                    text="B) iterrows() is convenient but slow; vectorized operations are much faster",
                    is_correct=True,
                    explanation="Correct! iterrows() is convenient but very slow. Pandas vectorized operations are typically 10-100x faster."
                ),
                QuestionOption(
                    text="C) iterrows() performance is similar to vectorized operations",
                    is_correct=False,
                    explanation="This is incorrect. iterrows() is significantly slower than vectorized operations."
                ),
                QuestionOption(
                    text="D) iterrows() should always be used for data processing",
                    is_correct=False,
                    explanation="This is not recommended. Use vectorized operations when possible for better performance."
                )
            ],
            explanation="iterrows() creates Python objects for each row, making it slow. Vectorized operations work on entire arrays at once."
        )
    
    @staticmethod
    def create_vectorization_toy_example() -> LearningQuestion:
        """Create a toy example showing vectorization benefits with different problem."""
        toy_code = '''# Problem: Calculate total scores for 10,000 students
# Each student has exam_score and homework_score

# Approach A - Loop through each student:
total_scores = []
for student_id in range(len(students_df)):
    exam = students_df.iloc[student_id]["exam_score"]
    homework = students_df.iloc[student_id]["homework_score"] 
    total_scores.append(exam + homework)

# Approach B - Work with entire columns:
total_scores = students_df["exam_score"] + students_df["homework_score"]'''
        
        return LearningQuestion(
            question_id=str(uuid.uuid4()),
            question_type=QuestionType.TOY_EXAMPLE,
            title="Vectorization Example",
            question_text="For calculating 10,000 student total scores, which approach would be significantly faster?",
            correct_answer="Approach B",
            toy_code=toy_code,
            explanation="Approach B (vectorization) is much faster because it operates on entire arrays at once, while Approach A processes one student at a time."
        )
    
    @staticmethod
    def create_predict_output_tf(code_snippet: str) -> LearningQuestion:
        """Create a True/False question about code output."""
        return LearningQuestion(
            question_id=str(uuid.uuid4()),
            question_type=QuestionType.TRUE_FALSE,
            title="Code Prediction",
            question_text=f"True or False: This code will successfully add a 'total' column to the DataFrame?\n\n**Python:**\n    {chr(10).join('    ' + line for line in code_snippet.split(chr(10)))}",
            correct_answer="True",
            explanation="Yes, this code will work, but it's inefficient. The loop approach will successfully create the 'total' column."
        )
    
    @staticmethod
    def create_spot_the_bug_question(buggy_code: str, bug_description: str) -> LearningQuestion:
        """Create a spot-the-bug question."""
        return LearningQuestion(
            question_id=str(uuid.uuid4()),
            question_type=QuestionType.SPOT_BUG,
            title="Spot the Bug",
            question_text=f"What's the main issue with this code?\n\n**Python:**\n    {chr(10).join('    ' + line for line in buggy_code.split(chr(10)))}",
            correct_answer=bug_description,
            explanation=f"The main issue is: {bug_description}"
        )
    
    @staticmethod
    def create_what_if_scenario(base_code: str, scenario: str) -> LearningQuestion:
        """Create a what-if scenario question."""
        return LearningQuestion(
            question_id=str(uuid.uuid4()),
            question_type=QuestionType.WHAT_IF,
            title="What If Scenario",
            question_text=f"What would happen if {scenario}?\n\nBase code:\n**Python:**\n    {chr(10).join('    ' + line for line in base_code.split(chr(10)))}",
            correct_answer="depends on scenario",
            explanation="Consider how the change affects performance, correctness, and maintainability."
        )
    
    @staticmethod
    def create_string_concatenation_toy_example() -> LearningQuestion:
        """Create a toy example for string concatenation performance."""
        toy_code = '''# Building a large log file from 5000 entries

# Method 1:
log_content = ""
for entry in log_entries:
    log_content = log_content + entry + "\\n"

# Method 2: 
log_parts = []
for entry in log_entries:
    log_parts.append(entry + "\\n")
log_content = "".join(log_parts)'''
        
        return LearningQuestion(
            question_id=str(uuid.uuid4()),
            question_type=QuestionType.TOY_EXAMPLE,
            title="String Building Performance",
            question_text="For building a large log file from thousands of entries, which method would be much more efficient?",
            correct_answer="Method 2",
            toy_code=toy_code,
            explanation="Method 2 is much more efficient because it collects parts in a list then joins once, while Method 1 creates a new string object every iteration."
        )
    @staticmethod
    def create_string_concatenation_mcq() -> LearningQuestion:
        """Create MCQ about string concatenation performance."""
        return LearningQuestion(
            question_id=str(uuid.uuid4()),
            question_type=QuestionType.MULTIPLE_CHOICE,
            title="String Concatenation Performance",
            question_text="Which is the most efficient way to build a large string from many pieces?",
            correct_answer="C",
            options=[
                QuestionOption(
                    text="A) Using += in a loop: result = result + piece",
                    is_correct=False,
                    explanation="This creates a new string object each time, making it O(n²) complexity."
                ),
                QuestionOption(
                    text="B) Using string formatting in a loop",
                    is_correct=False,
                    explanation="Still inefficient for large numbers of concatenations."
                ),
                QuestionOption(
                    text="C) Collecting in a list and using ''.join(list)",
                    is_correct=True,
                    explanation="Correct! This approach is O(n) and much more efficient for large strings."
                ),
                QuestionOption(
                    text="D) All methods have similar performance",
                    is_correct=False,
                    explanation="Performance differences can be dramatic, especially with many concatenations."
                )
            ]
        )
    
    @staticmethod
    def create_nested_loops_toy_example() -> LearningQuestion:
        """Create a toy example for nested loops optimization."""
        toy_code = '''# Finding common customers between two stores (each has 1000+ customers)

# Approach A:
common_customers = []
for customer_a in store_a_customers:
    for customer_b in store_b_customers:
        if customer_a["email"] == customer_b["email"]:
            common_customers.append(customer_a)

# Approach B:
store_b_emails = set(c["email"] for c in store_b_customers)
common_customers = [c for c in store_a_customers if c["email"] in store_b_emails]'''
        
        return LearningQuestion(
            question_id=str(uuid.uuid4()),
            question_type=QuestionType.TOY_EXAMPLE,
            title="Nested Loops vs Set Lookup",
            question_text="For finding common customers between two large customer lists, which approach would be dramatically faster?",
            correct_answer="Approach B",
            toy_code=toy_code,
            explanation="Approach B is much faster because set lookup is O(1) while nested loops create O(n²) complexity."
        )

class QuestionSelector:
    """Selects the best question based on code analysis and user progress."""
    
    @staticmethod
    def select_question_for_code(code: str, coaching_state: Any) -> LearningQuestion:
        """Select the most appropriate question based on code patterns."""
        code_lower = code.lower()
        
        # Check for pandas iterrows pattern
        if 'iterrows' in code_lower:
            # Prioritize MCQ and targeted questions over toy examples
            if coaching_state.total_questions_asked < 1:
                return QuestionTemplates.create_pandas_iterrows_mcq(code)
            elif coaching_state.total_questions_asked < 3:
                return QuestionTemplates.create_predict_output_tf(code)
            else:
                # Only use toy example after other question types
                return QuestionTemplates.create_vectorization_toy_example()
        
        # Check for string concatenation pattern
        elif '+=' in code and any(s in code_lower for s in ['str', '"', "'"]):
            if coaching_state.total_questions_asked < 2:
                return QuestionTemplates.create_string_concatenation_mcq()
            else:
                return QuestionTemplates.create_string_concatenation_toy_example()
        
        # Check for nested loops
        elif code.count('for ') > 1:
            if coaching_state.total_questions_asked < 2:
                return QuestionTemplates.create_what_if_scenario(
                    code, "you had to process 10,000 items instead of 100"
                )
            else:
                return QuestionTemplates.create_nested_loops_toy_example()
        
        # Check for potential bugs
        elif 'def ' in code and 'return' not in code:
            return QuestionTemplates.create_spot_the_bug_question(
                code, "Function doesn't return a value"
            )
        
        # Default fallback - create a general prediction question
        else:
            return QuestionTemplates.create_predict_output_tf(code)
    
    @staticmethod
    def should_ask_question(coaching_state: Any, code_analysis: Dict[str, Any]) -> bool:
        """Decide whether to ask a question or give a nudge."""
        # Early in the session, favor questions for engagement
        if coaching_state.total_questions_asked < 3:
            return True
        
        # If user is doing well, continue with questions
        if coaching_state.get_success_rate() > 0.7:
            return True
        
        # If struggling, give more direct nudges
        if coaching_state.get_success_rate() < 0.4:
            return False
        
        # Otherwise, balance questions and nudges
        return coaching_state.total_questions_asked % 2 == 0