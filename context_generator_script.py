#!/usr/bin/env python3
"""
CodeClimbAI Context Generator Script - OPTIMIZED VERSION
Generates a comprehensive but non-redundant context document for Claude chat sessions.
FIXED: Eliminates duplicate file descriptions, redundant project instructions, and excessive content.

Usage: python generate_context.py [output_file]
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple


class CodeClimbAIContextGenerator:
    """Generates optimized, non-redundant context documents for CodeClimbAI project."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.output_lines = []
        
        # File extensions to include as code files
        self.code_extensions = {'.py', '.md', '.txt', '.yaml', '.yml', '.json', '.toml'}
        
        # Directories to exclude from scanning
        self.exclude_dirs = {
            '__pycache__', '.git', '.pytest_cache', '.venv', 'venv', 'env',
            'node_modules', '.streamlit', 'dist', 'build', '.mypy_cache',
            'pipreqs-env', 'site-packages', '.vscode', 'pip-env', 'conda-env'
        }
        
        # Files to exclude from scanning
        self.exclude_files = {
            '.gitignore', '.DS_Store', 'Thumbs.db', '.env', '.env.local',
            'requirements.txt', 'LICENSE.txt', 'SOURCES.txt', 'top_level.txt',
            'dependency_links.txt', 'installed-files.txt', 'pbr.json'
        }
        
        # OPTIMIZATION: Define essential files that need full content
        self.essential_files = {
            'app.py', 'adaptive_coach.py', 'session_manager.py', 
            'question_templates.py', 'examples.py', 'question_formatter.py',
            'coaching_models.py', 'models.py', 'handlers.py'
        }
    
    def discover_project_structure(self) -> Dict[str, List[Tuple[str, str, bool]]]:
        """
        OPTIMIZED: Discover project structure with essential file flagging.
        Returns: Dict mapping directory names to lists of (file_path, description, is_essential) tuples
        """
        structure = {}
        
        # Scan the project directory
        for root, dirs, files in os.walk(self.project_root):
            # Filter out excluded directories EARLY to avoid traversing them
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs and not d.endswith('.dist-info')]
            
            # Skip entire virtual environment and dependency directories
            rel_root = os.path.relpath(root, self.project_root)
            if any(excluded in rel_root for excluded in self.exclude_dirs):
                continue
            if 'site-packages' in rel_root or 'lib/python' in rel_root:
                continue
                
            if rel_root == '.':
                rel_root = 'root'
            
            # Process files in this directory
            file_list = []
            for file in sorted(files):
                if file in self.exclude_files:
                    continue
                    
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, self.project_root)
                
                # Check if it's a code file we want to include
                file_ext = Path(file).suffix.lower()
                if file_ext in self.code_extensions:
                    description = self.get_file_description(rel_file_path, file)
                    is_essential = file in self.essential_files
                    file_list.append((rel_file_path, description, is_essential))
            
            if file_list:
                structure[rel_root] = file_list
        
        return structure
    
    def get_file_description(self, file_path: str, filename: str) -> str:
        """Generate a description for a file based on its path and name."""
        
        # Special cases for known files
        descriptions = {
            'app.py': 'Main Streamlit application entry point',
            'config.py': 'Configuration settings (API keys, UI parameters)',
            '__init__.py': 'Package initialization and exports',
            'requirements.txt': 'Python dependencies',
            'LICENSE': 'Project license',
            'README.md': 'Project documentation',
            'readme.md': 'Module documentation'
        }
        
        if filename in descriptions:
            return descriptions[filename]
        
        # Generate description based on file path and name
        path_parts = Path(file_path).parts
        
        if 'core' in path_parts:
            if 'adaptive_coach' in filename:
                return 'Main coaching orchestration and session management'
            elif 'analyzer' in filename:
                return 'Code analysis and Claude API client'
            elif 'assistant' in filename:
                return 'Main code review assistant class'
            elif 'coaching' in filename:
                return 'Coaching system data models and helpers'
            elif 'session' in filename:
                return 'Session state and lifecycle management'
            elif 'question' in filename:
                return 'Question generation and formatting'
            elif 'prompt' in filename:
                return 'System prompts for Claude interactions'
            elif 'model' in filename:
                return 'Core data models'
            else:
                return 'Core business logic component'
        
        elif 'templates' in path_parts:
            if 'example' in filename:
                return 'Code examples and learning materials'
            else:
                return 'Template or example content'
        
        elif 'ui' in path_parts:
            if 'component' in filename:
                return 'UI component rendering'
            elif 'handler' in filename:
                return 'User input processing'
            elif 'panel' in filename:
                return 'UI panel rendering'
            elif 'message' in filename:
                return 'Chat message rendering'
            else:
                return 'User interface component'
        
        elif 'utils' in path_parts:
            if 'execution' in filename:
                return 'Safe code execution utilities'
            elif 'helper' in filename:
                return 'Helper utility functions'
            else:
                return 'Utility functions'
        
        elif 'test' in path_parts or filename.startswith('test_'):
            return 'Test file'
        
        else:
            # Generic description based on file type
            if filename.endswith('.py'):
                return 'Python module'
            elif filename.endswith('.md'):
                return 'Documentation'
            elif filename.endswith('.json'):
                return 'JSON configuration'
            elif filename.endswith(('.yaml', '.yml')):
                return 'YAML configuration'
            elif filename.endswith('.toml'):
                return 'TOML configuration'
            else:
                return 'Project file'
    
    def add_section(self, title: str, content: str = ""):
        """Add a section to the output document."""
        self.output_lines.append(f"\n# {title}\n")
        if content:
            self.output_lines.append(content)
    
    def add_subsection(self, title: str, content: str = ""):
        """Add a subsection to the output document."""
        self.output_lines.append(f"\n## {title}\n")
        if content:
            self.output_lines.append(content)
    
    def add_code_block(self, content: str, language: str = ""):
        """Add a code block to the output document."""
        self.output_lines.append(f"```{language}\n{content}\n```\n")
    
    def read_file_safely(self, file_path: Path) -> str:
        """Safely read a file with encoding fallback."""
        encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
            except Exception as e:
                return f"Error reading file: {str(e)}"
        
        return "Unable to read file: encoding not supported"
    
    def get_file_preview(self, content: str, file_path: str) -> str:
        """OPTIMIZATION: Generate smart preview for non-essential files."""
        filename = Path(file_path).name
        
        # For Python files, extract structure
        if filename.endswith('.py'):
            return self.extract_python_structure(content)
        
        # For large markdown files, show first section only
        elif filename.endswith('.md') and len(content) > 1500:
            lines = content.split('\n')
            preview_lines = []
            for i, line in enumerate(lines):
                preview_lines.append(line)
                if i > 20 and line.startswith('#') and i > 0:  # Stop at next section
                    break
            preview_lines.append("\n*[Content abbreviated for context efficiency]*")
            return '\n'.join(preview_lines)
        
        # For other files, return first 1000 chars if too long
        elif len(content) > 1000:
            return content[:1000] + "\n\n*[Content abbreviated for context efficiency]*"
        
        return content
    
    def extract_python_structure(self, content: str) -> str:
        """Extract key structure from Python files for preview."""
        lines = content.split('\n')
        structure_lines = []
        
        in_docstring = False
        docstring_chars = ['"""', "'''"]
        
        for line in lines:
            stripped = line.strip()
            
            # Track docstrings
            for char in docstring_chars:
                if char in stripped:
                    in_docstring = not in_docstring
            
            # Include imports, class/function definitions, and docstrings
            if (stripped.startswith(('import ', 'from ')) or
                stripped.startswith(('class ', 'def ', '@')) or
                stripped.startswith('"""') or stripped.endswith('"""') or
                in_docstring):
                structure_lines.append(line)
            # Include key constants and module-level variables
            elif (stripped and not stripped.startswith('#') and 
                  '=' in stripped and not stripped.startswith((' ', '\t'))):
                structure_lines.append(line)
        
        # Add preview note
        if len(structure_lines) < len(lines) - 5:  # Only if we actually abbreviated
            structure_lines.append("\n# *[Implementation details abbreviated for context efficiency]*")
        
        return '\n'.join(structure_lines)
    
    def generate_header(self):
        """Generate document header with metadata."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header = f"""# CodeClimbAI - Complete Context Document
**Generated:** {timestamp}
**Purpose:** Comprehensive context for Claude chat sessions
**Project:** Learn-as-You-Go Code Review Assistant with Adaptive Coaching

## Document Overview

This document contains the complete codebase, project structure, recent chat history, and all necessary context for understanding and working with the CodeClimbAI project. The project uses Socratic questioning and adaptive coaching to teach code optimization through discovery rather than direct instruction.

## Key Architecture Components

- **Adaptive Coaching System:** Main orchestration with interview-critical issue detection
- **Session Memory:** Learning continuity system that prevents question repetition
- **Socratic Learning Engine:** Multiple question types with progressive difficulty
- **Interview Focus:** Prioritizes performance issues that matter in coding interviews
- **Safe Execution:** Code execution with intelligent fake data generation
- **Modular Design:** Clean separation of concerns across core/, templates/, ui/, utils/

"""
        self.output_lines.append(header)
    
    def generate_optimized_project_structure(self, structure: Dict[str, List[Tuple[str, str, bool]]]):
        """OPTIMIZED: Generate project structure WITHOUT redundant content."""
        self.add_section("Project Structure")
        
        # Create ASCII tree structure
        tree_lines = ["```"]
        tree_lines.append("CodeClimbAI/")
        
        # Sort directories for consistent output
        sorted_dirs = sorted(structure.keys())
        
        # Track file counts and essentials
        total_files = 0
        essential_files = 0
        
        for dir_name in sorted_dirs:
            files = structure[dir_name]
            total_files += len(files)
            
            if dir_name == 'root':
                # Root level files
                for file_path, description, is_essential in files:
                    if is_essential:
                        essential_files += 1
                        tree_lines.append(f"├── {file_path:<30} # {description} [ESSENTIAL]")
                    else:
                        tree_lines.append(f"├── {file_path:<30} # {description}")
            else:
                # Directory
                tree_lines.append(f"├── {dir_name}/")
                for i, (file_path, description, is_essential) in enumerate(files):
                    filename = os.path.basename(file_path)
                    prefix = "└──" if i == len(files) - 1 else "├──"
                    if is_essential:
                        essential_files += 1
                        tree_lines.append(f"│   {prefix} {filename:<25} # {description} [ESSENTIAL]")
                    else:
                        tree_lines.append(f"│   {prefix} {filename:<25} # {description}")
        
        tree_lines.append("```")
        self.output_lines.extend(tree_lines)
        
        # Add optimized file count summary
        self.add_subsection("File Summary")
        summary = f"""**Total Files:** {total_files} discovered and included
**Essential Files:** {essential_files} (full content included)
**Other Files:** {total_files - essential_files} (structure/preview included)

**Note:** Essential files are core system components that receive full content inclusion. 
Other files show structure and key functions to optimize context document size.

"""
        self.output_lines.append(summary)
    
    def generate_optimized_code_section(self, structure: Dict[str, List[Tuple[str, str, bool]]]):
        """OPTIMIZED: Generate code section with smart content inclusion."""
        self.add_section("Complete Codebase")
        
        # Sort directories for consistent output
        sorted_dirs = sorted(structure.keys())
        
        for dir_name in sorted_dirs:
            display_name = "Root Level Files" if dir_name == 'root' else f"{dir_name.title()} Module"
            self.add_subsection(display_name)
            
            files = structure[dir_name]
            for file_path, description, is_essential in files:
                full_path = self.project_root / file_path
                
                # Add file header
                self.output_lines.append(f"### {file_path}\n")
                self.output_lines.append(f"**Description:** {description}\n")
                
                # Read and add file content (full or preview)
                if full_path.exists():
                    content = self.read_file_safely(full_path)
                    
                    # OPTIMIZATION: Use full content for essential files, preview for others
                    if is_essential:
                        final_content = content
                    else:
                        final_content = self.get_file_preview(content, file_path)
                    
                    # Determine language for syntax highlighting
                    ext = full_path.suffix.lower()
                    lang_map = {
                        '.py': 'python',
                        '.md': 'markdown',
                        '.json': 'json',
                        '.yaml': 'yaml',
                        '.yml': 'yaml',
                        '.toml': 'toml'
                    }
                    language = lang_map.get(ext, '')
                    
                    self.add_code_block(final_content, language)
                else:
                    self.output_lines.append("*File not found*\n")
    
    def generate_chat_history_section(self):
        """Generate chat history section as requested: 3 recent full + all previous summarized."""
        self.add_section("Recent Chat History")
        
        chatlogs_dir = self.project_root / "chatlogs"
        
        if not chatlogs_dir.exists():
            self.output_lines.append("*No chatlogs directory found*\n")
            return
        
        # Find all chatlog files
        chatlog_files = []
        for file in chatlogs_dir.glob("*.md"):
            chatlog_files.append(file)
        
        if not chatlog_files:
            self.output_lines.append("*No chatlog files found*\n")
            return
        
        # Sort by modification time (most recent first)
        chatlog_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Include full content for most recent 3 chatlogs (as requested)
        recent_logs = chatlog_files[:3]
        older_logs = chatlog_files[3:]
        
        self.add_subsection("Recent Chat Sessions (Full Content)")
        
        for i, log_file in enumerate(recent_logs, 1):
            self.output_lines.append(f"### Chat Session {i}: {log_file.name}\n")
            content = self.read_file_safely(log_file)
            self.add_code_block(content, "markdown")
        
        # Summarize older chatlogs (as requested)
        if older_logs:
            self.add_subsection("Previous Chat Sessions (Summaries)")
            
            for log_file in older_logs:
                self.output_lines.append(f"**{log_file.name}:**\n")
                
                # Extract summary from file
                content = self.read_file_safely(log_file)
                summary = self.extract_chatlog_summary(content, log_file.name)
                self.output_lines.append(f"{summary}\n")
    
    def extract_chatlog_summary(self, content: str, filename: str) -> str:
        """Extract a summary from a chatlog file."""
        lines = content.split('\n')
        
        # Try to find key information
        topics = []
        decisions = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Look for topic indicators
            if any(indicator in line_lower for indicator in [
                'working on', 'focusing on', 'implementing', 'fixing', 'debugging',
                'issue:', 'problem:', 'task:', 'goal:'
            ]):
                topics.append(line.strip())
            
            # Look for decision indicators  
            if any(indicator in line_lower for indicator in [
                'decided', 'agreed', 'resolved', 'completed', 'fixed',
                'solution:', 'result:', 'outcome:'
            ]):
                decisions.append(line.strip())
        
        # Create summary
        summary_parts = []
        
        if topics:
            summary_parts.append(f"Topics: {'; '.join(topics[:2])}")
        
        if decisions:
            summary_parts.append(f"Outcomes: {'; '.join(decisions[:2])}")
        
        if not summary_parts:
            # Fallback: use first few lines
            first_lines = [line.strip() for line in lines[:3] if line.strip()]
            if first_lines:
                summary_parts.append(f"Content: {' '.join(first_lines)[:100]}...")
        
        return ' | '.join(summary_parts) if summary_parts else "Chat session content available"
    
    def generate_context_document(self, output_file: str = None) -> str:
        """Generate the optimized, non-redundant context document."""
        print("🚀 Generating optimized CodeClimbAI context document...")
        
        # Discover project structure
        print("📁 Discovering project structure...")
        structure = self.discover_project_structure()
        
        # Generate document sections (OPTIMIZED: removed redundant project instructions)
        print("📝 Generating document sections...")
        self.generate_header()
        self.generate_optimized_project_structure(structure)
        self.generate_chat_history_section()  # As requested: 3 recent + all summarized
        self.generate_optimized_code_section(structure)
        
        # Combine all content
        full_content = '\n'.join(self.output_lines)
        
        # Write to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(full_content, encoding='utf-8')
            print(f"✅ Context document written to: {output_path}")
        
        return full_content


def main():
    """Main script entry point."""
    # Get output filename from command line or use default
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"codeclimbai_context_{timestamp}.md"
    
    # Generate context document
    try:
        generator = CodeClimbAIContextGenerator()
        content = generator.generate_context_document(output_file)
        
        print(f"📊 Document stats:")
        print(f"   - Lines: {len(content.splitlines()):,}")
        print(f"   - Characters: {len(content):,}")
        print(f"   - Size: {len(content.encode('utf-8')) / 1024:.1f} KB")
        print(f"✨ Optimized context document generation complete!")
        
    except Exception as e:
        print(f"❌ Error generating context document: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()