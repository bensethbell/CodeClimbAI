"""
Learning continuity and session memory system for adaptive coaching.
ADD THIS to the coaching system to prevent question repetition and build on prior learning.
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from .coaching_models import (
    LearningQuestion, QuestionType, CoachingInteraction, AnswerStatus, CoachingMode
)

@dataclass
class QuestionMemory:
    """Stores information about a previously asked question."""
    question: LearningQuestion
    user_answer: str
    was_correct: bool
    timestamp: datetime
    code_context: str  # The code this question was about
    main_concept: str  # e.g., "pandas_iterrows", "nested_loops", "string_concat"
    
    def get_similarity_score(self, other_question: LearningQuestion, other_concept: str) -> float:
        """Calculate similarity between this and another question (0.0 to 1.0)."""
        
        # Same question type and concept = very similar
        if (self.question.question_type == other_question.question_type and 
            self.main_concept == other_concept):
            return 0.9
        
        # Same concept, different question type = moderately similar
        if self.main_concept == other_concept:
            return 0.7
        
        # Same question type, different concept = somewhat similar
        if self.question.question_type == other_question.question_type:
            return 0.4
        
        # Different concept and type = not similar
        return 0.1

@dataclass 
class LearningProgress:
    """Tracks what concepts the user has learned and their proficiency."""
    concept_scores: Dict[str, float] = field(default_factory=dict)  # concept -> score (0.0-1.0)
    mastered_concepts: set = field(default_factory=set)
    struggling_concepts: set = field(default_factory=set)
    
    def update_concept_score(self, concept: str, was_correct: bool):
        """Update the user's score for a concept based on their answer."""
        current_score = self.concept_scores.get(concept, 0.5)
        
        if was_correct:
            # Increase score (but don't exceed 1.0)
            new_score = min(1.0, current_score + 0.2)
        else:
            # Decrease score (but don't go below 0.0)
            new_score = max(0.0, current_score - 0.15)
        
        self.concept_scores[concept] = new_score
        
        # Update mastery status
        if new_score >= 0.8:
            self.mastered_concepts.add(concept)
            self.struggling_concepts.discard(concept)
        elif new_score <= 0.3:
            self.struggling_concepts.add(concept)
            self.mastered_concepts.discard(concept)
        else:
            # In between - remove from both sets
            self.mastered_concepts.discard(concept)
            self.struggling_concepts.discard(concept)
    
    def get_concept_status(self, concept: str) -> str:
        """Get the user's status with a concept: 'mastered', 'struggling', 'learning', 'new'."""
        if concept in self.mastered_concepts:
            return 'mastered'
        elif concept in self.struggling_concepts:
            return 'struggling'
        elif concept in self.concept_scores:
            return 'learning'
        else:
            return 'new'

class SessionMemory:
    """Manages session memory for learning continuity."""
    
    def __init__(self):
        self.question_history: List[QuestionMemory] = []
        self.learning_progress = LearningProgress()
        self.session_concepts: set = set()  # All concepts seen this session
    
    def add_question(self, question: LearningQuestion, code: str, concept: str):
        """Add a question to memory when it's asked."""
        question_memory = QuestionMemory(
            question=question,
            user_answer="",  # Will be filled when answered
            was_correct=False,  # Will be updated when answered
            timestamp=datetime.now(),
            code_context=code,
            main_concept=concept
        )
        self.question_history.append(question_memory)
        self.session_concepts.add(concept)
    
    def update_answer(self, user_answer: str, was_correct: bool):
        """Update the most recent question with the user's answer."""
        if self.question_history:
            latest = self.question_history[-1]
            latest.user_answer = user_answer
            latest.was_correct = was_correct
            
            # Update learning progress
            self.learning_progress.update_concept_score(latest.main_concept, was_correct)
    
    def get_similar_questions(self, new_question: LearningQuestion, concept: str, 
                            threshold: float = 0.6) -> List[QuestionMemory]:
        """Find previous questions that are similar to the new one."""
        similar = []
        for memory in self.question_history:
            similarity = memory.get_similarity_score(new_question, concept)
            if similarity >= threshold:
                similar.append(memory)
        return similar
    
    def has_recent_similar_question(self, new_question: LearningQuestion, concept: str, 
                                   recent_count: int = 3) -> Optional[QuestionMemory]:
        """Check if a similar question was asked recently."""
        recent_questions = self.question_history[-recent_count:] if len(self.question_history) >= recent_count else self.question_history
        
        for memory in reversed(recent_questions):  # Check most recent first
            similarity = memory.get_similarity_score(new_question, concept)
            if similarity >= 0.7:  # High similarity threshold for "recent"
                return memory
        return None
    
    def get_learning_summary(self) -> str:
        """Generate a summary of what the user has learned this session."""
        if not self.session_concepts:
            return "This is your first question in this session."
        
        summary_parts = []
        
        # Mastered concepts
        mastered = [c for c in self.session_concepts if c in self.learning_progress.mastered_concepts]
        if mastered:
            concept_names = [c.replace('_', ' ').title() for c in mastered]
            summary_parts.append(f"✅ **Concepts you've mastered:** {', '.join(concept_names)}")
        
        # Learning concepts
        learning = [c for c in self.session_concepts 
                   if c in self.learning_progress.concept_scores and 
                   c not in self.learning_progress.mastered_concepts and 
                   c not in self.learning_progress.struggling_concepts]
        if learning:
            concept_names = [c.replace('_', ' ').title() for c in learning]
            summary_parts.append(f"📚 **Concepts you're learning:** {', '.join(concept_names)}")
        
        # Struggling concepts
        struggling = [c for c in self.session_concepts if c in self.learning_progress.struggling_concepts]
        if struggling:
            concept_names = [c.replace('_', ' ').title() for c in struggling]
            summary_parts.append(f"🔄 **Concepts to revisit:** {', '.join(concept_names)}")
        
        return "\n".join(summary_parts) if summary_parts else "You're building your understanding step by step."


class EnhancedQuestionSelector:
    """Enhanced question selector with session memory and learning continuity."""
    
    @staticmethod
    def select_question_with_memory(code: str, coaching_state, session_memory: SessionMemory) -> LearningQuestion:
        """Select question considering session history and learning progression."""
        
        # Determine the main concept for this code
        main_concept = EnhancedQuestionSelector._determine_main_concept(code)
        
        # Generate potential questions for this concept
        potential_questions = EnhancedQuestionSelector._get_potential_questions(code, main_concept, coaching_state)
        
        # Check for recent similar questions
        for question in potential_questions:
            recent_similar = session_memory.has_recent_similar_question(question, main_concept)
            
            if recent_similar:
                # Found a similar recent question - create a connecting response instead
                return EnhancedQuestionSelector._create_connecting_question(
                    question, recent_similar, main_concept, session_memory
                )
        
        # No similar recent questions - select the best new question
        best_question = EnhancedQuestionSelector._select_progressive_question(
            potential_questions, main_concept, session_memory
        )
        
        # Add to memory
        session_memory.add_question(best_question, code, main_concept)
        
        return best_question
    
    @staticmethod
    def _determine_main_concept(code: str) -> str:
        """Determine the main optimization concept in the code."""
        code_lower = code.lower()
        
        if 'iterrows' in code_lower:
            return 'pandas_iterrows'
        elif '+=' in code and any(s in code_lower for s in ['str', '"', "'"]):
            return 'string_concatenation'
        elif code.count('for ') > 1:
            return 'nested_loops'
        elif 'range(len(' in code:
            return 'manual_indexing'
        elif 'append(' in code and 'for' in code:
            return 'manual_list_building'
        else:
            return 'general_optimization'
    
    @staticmethod
    def _get_potential_questions(code: str, concept: str, coaching_state) -> List[LearningQuestion]:
        """Get all potential questions for this code/concept."""
        from .question_templates import QuestionTemplates
        
        potential = []
        
        if concept == 'pandas_iterrows':
            potential.extend([
                QuestionTemplates.create_pandas_iterrows_mcq(code),
                QuestionTemplates.create_vectorization_toy_example(),
                QuestionTemplates.create_predict_output_tf(code)
            ])
        elif concept == 'string_concatenation':
            potential.extend([
                QuestionTemplates.create_string_concatenation_mcq(),
                QuestionTemplates.create_string_concatenation_toy_example()
            ])
        elif concept == 'nested_loops':
            potential.extend([
                QuestionTemplates.create_nested_loops_toy_example(),
                QuestionTemplates.create_what_if_scenario(code, "you had to process 10,000 items instead of 100")
            ])
        else:
            # Default questions
            potential.append(QuestionTemplates.create_predict_output_tf(code))
        
        return potential
    
    @staticmethod
    def _select_progressive_question(questions: List[LearningQuestion], concept: str, 
                                   session_memory: SessionMemory) -> LearningQuestion:
        """Select the best question based on learning progression."""
        concept_status = session_memory.learning_progress.get_concept_status(concept)
        
        # Prioritize question types based on user's progress with this concept
        if concept_status == 'new':
            # Start with MCQ for new concepts (concrete options help understanding)
            mcq_questions = [q for q in questions if q.question_type == QuestionType.MULTIPLE_CHOICE]
            if mcq_questions:
                return mcq_questions[0]
        
        elif concept_status == 'learning':
            # Use toy examples to deepen understanding
            toy_questions = [q for q in questions if q.question_type == QuestionType.TOY_EXAMPLE]
            if toy_questions:
                return toy_questions[0]
        
        elif concept_status == 'mastered':
            # Use what-if scenarios to challenge mastery
            whatif_questions = [q for q in questions if q.question_type == QuestionType.WHAT_IF]
            if whatif_questions:
                return whatif_questions[0]
        
        # Fallback to first available question
        return questions[0] if questions else QuestionTemplates.create_predict_output_tf("")
    
    @staticmethod
    def _create_connecting_question(new_question: LearningQuestion, recent_similar: QuestionMemory, 
                                  concept: str, session_memory: SessionMemory) -> LearningQuestion:
        """Create a question that connects to previous learning."""
        
        # Determine how to connect based on previous answer
        if recent_similar.was_correct:
            # User got previous question right - build on that success
            connecting_text = f"""🔗 **Building on Your Success!**

Earlier, you correctly understood {concept.replace('_', ' ')}. Now I see a similar pattern in this new code.

**Previous insight:** You learned that {EnhancedQuestionSelector._get_concept_insight(concept)}

**New challenge:** How would you apply that same insight to this code?

```python
{new_question.toy_code if hasattr(new_question, 'toy_code') and new_question.toy_code else "# [Code context]"}
```

Think about the connection between what you learned before and what you see now. What optimization approach would work here?"""
        
        else:
            # User struggled with previous question - provide reinforcement
            connecting_text = f"""🔄 **Let's Revisit This Concept**

I noticed we explored {concept.replace('_', ' ')} earlier, and it's appearing again in this new code. This is a great opportunity to strengthen your understanding!

**Key insight to remember:** {EnhancedQuestionSelector._get_concept_insight(concept)}

**Looking at this new example:**
```python
{new_question.toy_code if hasattr(new_question, 'toy_code') and new_question.toy_code else "# [Code context]"}
```

Can you spot the similarity to what we discussed before? How might the same optimization principle apply here?"""
        
        # Create a custom connecting question
        from .coaching_models import LearningQuestion, QuestionType
        import uuid
        
        connecting_question = LearningQuestion(
            question_id=str(uuid.uuid4()),
            question_type=QuestionType.WHAT_IF,
            title=f"Connecting Concepts: {concept.replace('_', ' ').title()}",
            question_text=connecting_text,
            correct_answer="Apply the same optimization principle",
            explanation=f"This reinforces your understanding of {concept.replace('_', ' ')} by applying it to a new context."
        )
        
        # Add to memory
        session_memory.add_question(connecting_question, "", concept)
        
        return connecting_question
    
    @staticmethod
    def _get_concept_insight(concept: str) -> str:
        """Get the key insight for a concept."""
        insights = {
            'pandas_iterrows': "vectorized operations are much faster than iterating row by row",
            'string_concatenation': "collecting strings in a list and joining them is more efficient than += in loops", 
            'nested_loops': "using sets or dictionaries for lookups can reduce O(n²) complexity to O(n)",
            'manual_indexing': "direct iteration is more Pythonic and often faster than manual indexing",
            'manual_list_building': "list comprehensions are cleaner and often faster than manual append loops"
        }
        return insights.get(concept, "optimization patterns can be applied consistently across similar problems")


# INTEGRATION: Enhanced coaching state to include session memory
@dataclass
class EnhancedCoachingState:
    """Enhanced coaching state with session memory."""
    # All existing fields from CoachingState
    current_interaction: Optional[CoachingInteraction] = None
    interaction_history: List[CoachingInteraction] = field(default_factory=list)
    total_questions_asked: int = 0
    correct_answers: int = 0
    learning_progress: Dict[str, Any] = field(default_factory=dict)
    main_issue: Optional[str] = None
    resolved_issues: set = field(default_factory=set)
    
    # NEW: Session memory for learning continuity
    session_memory: SessionMemory = field(default_factory=SessionMemory)
    
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
        """Complete the current interaction with user's answer and update session memory."""
        if self.current_interaction:
            self.current_interaction.user_answer = user_answer
            self.current_interaction.answer_status = status
            self.current_interaction.answered_at = datetime.now()
            
            # Update statistics
            if self.current_interaction.mode == CoachingMode.QUESTION:
                if status == AnswerStatus.CORRECT:
                    self.correct_answers += 1
                
                # Update session memory
                self.session_memory.update_answer(user_answer, status == AnswerStatus.CORRECT)
            
            # Move to history
            self.interaction_history.append(self.current_interaction)
            self.current_interaction = None
    
    def get_session_summary(self) -> str:
        """Get a summary of learning progress this session."""
        return self.session_memory.get_learning_summary()