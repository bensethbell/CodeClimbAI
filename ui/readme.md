# ui/ - User Interface Components

Educational-focused interface components optimized for learning and cognitive focus.

## Files

### [`components.py`](./components.py)
Core UI components and managers for rendering the application interface.

- **UIManager** - Main interface coordination
- **UIComponents** - Individual component rendering
- **Message formatting** - Clean text processing without code blocks

### [`panels.py`](./panels.py)
Main application panels for the three-column layout.

- **Code Input Panel** - Editor with example loading functionality
- **Chat Panel** - Conversation interface with coaching interactions
- **Session Management** - Action buttons and learning controls

### [`messages.py`](./messages.py)
Message rendering system optimized for educational content.

- **Chat message formatting** with role-based styling
- **MCQ rendering** with proper option formatting
- **Clean content processing** without distracting code syntax highlighting

### [`handlers.py`](./handlers.py)
Input processing and command handling for user interactions.

- **Special command processing** (test, example, hints)
- **Adaptive coaching integration** for answering questions
- **Session state management** during user interactions

## Design Philosophy

### Cognitive Load Management
- Clean, distraction-free main interface
- Progressive disclosure of complexity
- Collapsible instructions to prevent overwhelm

### Educational Focus
- Chat-based learning conversation
- MCQ formatting optimized for comprehension
- Visual hierarchy that guides attention to learning elements

### Professional Learning Environment
- Streamlit Cloud deployment optimization
- Responsive design for different screen sizes
- Robust error handling that preserves educational flow

## Key Features

### Adaptive Welcome System
- First-time user detection with educational onboarding
- Philosophy explanation integrated into user flow
- Smart state management for returning users

### Learning-Optimized Chat
- Reverse chronological message order (newest first)
- Role-based message styling for clear conversation flow
- Compact formatting that maximizes content visibility