# core/ - Business Logic and AI Coaching

The core module contains the intelligent coaching system that powers CodeClimbAI's adaptive learning approach.

## Key Components

### Adaptive Coaching System
- [`adaptive_coach.py`](./adaptive_coach.py) - Main coaching logic with Socratic questioning
- [`coaching_models.py`](./coaching_models.py) - Data models for coaching interactions
- [`question_templates.py`](./question_templates.py) - Structured learning questions
- [`question_formatter.py`](./question_formatter.py) - Question rendering and formatting

### AI and Analysis
- [`analyzer.py`](./analyzer.py) - Code analysis and Claude API client
- [`assistant.py`](./assistant.py) - Main code review assistant class
- [`prompts.py`](./prompts.py) - System prompts for Claude interactions

### Session Management
- [`models.py`](./models.py) - Core data models (sessions, messages)
- [`session_manager.py`](./session_manager.py) - Session state and lifecycle management

## Architecture Overview

The coaching system implements a sophisticated learning loop:

1. **Code Analysis** - Identifies optimization opportunities and learning targets
2. **Question Selection** - Chooses appropriate Socratic questions based on user progress  
3. **Adaptive Response** - Generates coaching responses calibrated to user understanding
4. **Progress Tracking** - Maintains learning state across interactions

## Key Features

### Interview-Critical Detection
The system prioritizes issues that matter most in coding interviews:
- Performance bottlenecks (O(n²) algorithms, inefficient pandas operations)
- Algorithm optimization opportunities
- Code quality improvements

### Multi-Modal Learning
- Multiple choice questions for concept checking
- Toy examples demonstrating principles
- "What-if" scenarios for deeper understanding
- Progressive hint systems

### Adaptive Intelligence
- Success rate tracking for personalized difficulty
- Pattern recognition of user coding habits  
- Context-aware coaching that builds on previous interactions