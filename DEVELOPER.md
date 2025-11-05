# Developer Documentation

This document provides comprehensive guidance for developers working on the Roleplaying Toolkit project.

## Development Workflow Guidelines

When implementing features or bug fixes, follow this structured approach:

### 1. Issue Analysis & Planning

- **Read Referenced Issues**: Always start by thoroughly reading any GitHub issues referenced in the request
- **Comment on Issues**: Add a comment to each GitHub issue with your approach before starting implementation:
  - Describe the design or bug fix strategy you'll use
  - Outline the files you plan to modify
  - Identify any potential edge cases
  - Ask for feedback if needed
- **Understand Requirements**: Break down the request into specific, testable requirements
- **Design Planning**: Plan the code changes before implementation:
  - Identify which files need modification
  - Consider impact on existing functionality
  - Plan test cases and edge cases
  - Consider backward compatibility

### 2. Environment Setup

#### Option A: Automated Setup (Recommended)

```bash
# The project includes automated Python environment configuration
# This approach allows testing/linting without manual approval prompts
# Simply run any pytest or flake8 command and the environment will be configured
python -m pytest tests/ -v  # Auto-configures environment and runs tests
python -m flake8 lib/ --max-line-length=120  # Auto-configures and lints
```

#### Option B: Manual Setup

```bash
# Manual environment setup (if needed)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Implementation Process

- **Feature Branch**: Create a descriptive feature branch
- **Code Changes**: Implement following established patterns and conventions
- **Code Quality**: Maintain consistent style and documentation
- **Incremental Testing**: Test frequently during development

### 4. Testing & Quality Assurance

```bash
# Run all tests (comprehensive)
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_custom_commands.py -v
python -m pytest tests/test_command_handler.py -v

# Run tests with coverage
python -m pytest tests/ --cov=lib --cov-report=term-missing

# Test specific functionality
python -m pytest tests/ -k "advantage" -v
```

### 5. Code Quality Checks

```bash
# Format code with black
python -m black lib/ tests/ --line-length=120

# Lint code with flake8
python -m flake8 lib/ tests/ --max-line-length=120 --exclude=__pycache__

# Check specific files
python -m flake8 lib/custom_commands.py --max-line-length=120
```

### 6. Integration Testing

```bash
# Test the actual application
echo -e "help\nroll d20 advantage\nquit" | python roleplaying_toolkit.py
```

### 7. Documentation Updates

- Update README.md with new features/changes
- Update docstrings for modified functions
- Include usage examples for new functionality

### 8. Final Validation

- All tests must pass: `python -m pytest tests/ -v`
- Code must pass linting: `python -m flake8 lib/ tests/ --max-line-length=120`
- Application must run without errors
- New functionality must be documented

## Architecture

### Command Handling (`lib/command_handler.py`)

The `CommandHandler` class provides:

- **Command Parsing**: Handles quoted arguments and proper tokenization
- **Command Registration**: Easy way to add custom commands
- **Error Handling**: Graceful handling of invalid commands and exceptions
- **Extensibility**: Simple interface for adding new functionality

### Extended Commands (`lib/custom_commands.py`)

The main application includes extended functionality:

- **Dice Rolling**: `roll 2d6`, `roll d20` - Roll dice with proper validation
- **Advantage/Disadvantage**: Support for advantage and disadvantage rolls
- **Game Status**: `status` - Display current game state information  
- **Save/Load**: `save [name]`, `load <name>` - Game state persistence
- **Journey System**: Commands for managing long-term quests and journeys
- **Session Management**: Commands for resetting and managing game sessions

### Adding Custom Commands

1. Create a command handler function:

```python
def my_command_handler(command):
    return {
        "success": True,
        "message": "Command executed!",
        "exit": False
    }
```

1. Register it with the command handler:

```python
command_handler.register_command("mycommand", my_command_handler)
```

### State Management (`lib/state_manager.py`)

The StateManager class handles:

- **YAML Persistence**: Human-readable save files
- **Named Saves**: Multiple save slots with automatic sanitization
- **Version Tracking**: Future-proof compatibility
- **Error Handling**: Graceful handling of missing/corrupt files

### Journey System (`lib/journey_system.py`)

The journey system provides:

- **Journey Class**: Individual journey tracking with progress
- **JourneyManager**: Stack-based journey management
- **Serialization**: Full state persistence support

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_command_handler.py -v

# Run tests matching pattern
python -m pytest tests/ -k "advantage" -v

# Run with coverage report
python -m pytest tests/ --cov=lib --cov-report=term-missing
```

## Test Coverage

The project includes comprehensive tests for:

- Command parsing and execution
- Error handling
- Main application integration
- Custom command extensions
- Journey system functionality
- Save/load state management
- Session reset mechanisms

## Project Structure

```text
roleplaying_toolkit/
├── roleplaying_toolkit.py      # Main application entry point
├── lib/
│   ├── command_handler.py     # Core command handling logic
│   ├── custom_commands.py     # Extended command implementations
│   ├── journey_system.py      # Journey tracking and management
│   ├── state_manager.py       # Save/load state persistence
│   └── statemgr.py           # Legacy state management
├── tests/                     # Comprehensive unit tests
│   ├── test_command_handler.py
│   ├── test_custom_commands.py
│   ├── test_journey_system.py
│   ├── test_journey_commands.py
│   ├── test_state_manager.py
│   ├── test_save_load_commands.py
│   └── test_main_integration.py
├── saves/                     # Save game files (gitignored)
├── README.md                  # User documentation
├── DEVELOPER.md              # This file - developer documentation
└── pyproject.toml            # Project configuration
```

## Code Quality Standards

- **Line Length**: Maximum 120 characters (configured in flake8)
- **Formatting**: Use black for consistent code formatting
- **Docstrings**: All public functions should have descriptive docstrings
- **Type Hints**: Use type hints where appropriate for better code clarity
- **Error Handling**: Implement proper error handling with informative messages
- **Testing**: All new functionality must include comprehensive tests

## Git Workflow

1. **Feature Branches**: Create descriptive feature branches for all changes
2. **Commit Messages**: Use clear, descriptive commit messages
3. **Pull Requests**: All changes go through pull request review
4. **Testing**: All tests must pass before merging
5. **Documentation**: Update relevant documentation with changes
