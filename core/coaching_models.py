"""
Data models for the adaptive coaching system.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class CoachingMode(Enum):
    """Types of coaching interventions."""
    NUDGE = "nudge"  # Direct guidance to fix something
    QUESTION = "question"  # Active learning question

class QuestionType(Enum):
    """Types of learning questions."""
    MULTIPLE_CHOICE = "mcq"
    TRUE_FALSE = "tf"
    WHAT_IF = "what_if"
    SPOT_BUG = "spot_bug"
    PREDICT_OUTPUT = "predict_output"
    TOY_EXAMPLE = "toy_example"

class AnswerStatus(Enum):
    """Status of user's answer to a question."""
    PENDING = "pending"
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"
    SKIPPED = "skipped"

@dataclass
class QuestionOption:
    """A single option for multiple choice questions."""
    text: str
    is_correct: bool
    explanation: str = ""

@dataclass
class LearningQuestion:
    """Represents an active learning question."""
    question_id: str
    question_type: QuestionType
    title: str
    question_text: str
    correct_answer: str
    options: List[QuestionOption] = field(default_factory=list)  # For MCQ
    explanation: str = ""
    toy_code: Optional[str] = None  # For toy example questions
    created_at: datetime = field(default_factory=datetime.now)
    
    def is_multiple_choice(self) -> bool:
        """Check if this is a multiple choice question."""
        return self.question_type == QuestionType.MULTIPLE_CHOICE
    
    def get_correct_options(self) -> List[QuestionOption]:
        """Get all correct options for MCQ."""
        return [opt for opt in self.options if opt.is_correct]

@dataclass
class CoachingInteraction:
    """Tracks a single coaching interaction with the user."""
    interaction_id: str
    mode: CoachingMode
    content: str  # The nudge text or question
    question: Optional[LearningQuestion] = None
    user_answer: Optional[str] = None
    answer_status: AnswerStatus = AnswerStatus.PENDING
    feedback_given: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    answered_at: Optional[datetime] = None

@dataclass
class CoachingState:
    """Tracks the overall coaching state for a user session."""
    current_interaction: Optional[CoachingInteraction] = None
    interaction_history: List[CoachingInteraction] = field(default_factory=list)
    total_questions_asked: int = 0
    correct_answers: int = 0
    learning_progress: Dict[str, Any] = field(default_factory=dict)
    main_issue: Optional[str] = None  # Track the main issue for the session
    resolved_issues: set = field(default_factory=set)  # Track resolved issues
        
    def get_success_rate(self) -> float:
        """Calculate the user's success rate on questions."""
        if self.total_questions_asked == 0:
            return 0.0
        return self.correct_answers / self.total_questions_asked
    
    def is_waiting_for_answer(self) -> bool:
        """Check if we're waiting for user to answer a question."""
        return (self.current_interaction is not None and 
                self.current_interaction.mode == CoachingMode.QUESTION and
                self.current_interaction.answer_status == AnswerStatus.PENDING)
    
    def complete_current_interaction(self, user_answer: str, status: AnswerStatus):
        """Complete the current interaction with user's answer."""
        if self.current_interaction:
            self.current_interaction.user_answer = user_answer
            self.current_interaction.answer_status = status
            self.current_interaction.answered_at = datetime.now()
            
            # Update statistics
            if self.current_interaction.mode == CoachingMode.QUESTION:
                if status == AnswerStatus.CORRECT:
                    self.correct_answers += 1
            
            # Move to history
            self.interaction_history.append(self.current_interaction)
            self.current_interaction = None
            
    def __post_init__(self):
        print("DEBUG: CoachingState initialized:", self)