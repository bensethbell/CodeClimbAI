# CodeClimbAI

**Try it live**: [codeclimb.streamlit.app](https://codeclimb.streamlit.app)

An AI-powered learning platform that teaches code optimization through Socratic questioning and adaptive coaching.

## Philosophy

CodeClimbAI teaches through discovery, not direct instruction. Instead of fixing your code, it guides you to identify and solve optimization problems yourself using research-backed pedagogical methods.

## Quick Start

1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Set your Anthropic API key in `.streamlit/secrets.toml`
4. Run: `streamlit run app.py`

## How It Works

1. Submit your code for analysis
2. Answer guided questions about potential improvements
3. Apply your discoveries and resubmit
4. Learn through structured reflection and concept reinforcement

## Architecture

```
CodeClimbAI/
├── app.py                 # Main application entry point
├── config.py             # Configuration settings
├── core/                 # Business logic and AI coaching
├── templates/            # Code examples and learning materials  
├── ui/                   # User interface components
└── utils/                # Utilities and helper functions
```

## Key Features

- **Socratic questioning** instead of direct solutions
- **Adaptive coaching** that responds to your learning patterns  
- **Interview-critical issue detection** for job preparation
- **Real code analysis** using your actual projects
- **Safe execution environment** with intelligent fake data generation

## Module Documentation

- [core/](./core/README.md) - AI coaching and business logic
- [templates/](./templates/README.md) - Learning materials and examples
- [ui/](./ui/README.md) - User interface components
- [utils/](./utils/README.md) - Utilities and execution tools

## Technical Stack

- **Frontend**: Streamlit
- **AI**: Claude (Anthropic)
- **Execution**: Safe Python code execution with pandas/numpy
- **Deployment**: Streamlit Cloud