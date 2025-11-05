# Roleplaying Toolkit

A command-line toolkit for roleplaying games with an extensible command system.

## Features

- **Interactive Command Loop**: Text-based interface with command parsing
- **Extensible Command System**: Easy to add custom commands
- **Built-in Commands**: Help, quit/exit functionality
- **State Management**: Integration with game state system
- **Comprehensive Testing**: Full unit test coverage

## Usage

Run the main application:

```bash
python roleplaying_toolkit.py
```

### Available Commands

- `help` - Show available commands
- `quit` / `exit` - Exit the application
- `roll <dice> [advantage|disadvantage]` - Roll dice with optional advantage/disadvantage
  - Basic: `roll d20`, `roll 2d6`
  - Advantage: `roll d20 advantage`, `roll 2d6 adv`, `roll d12 a`
  - Disadvantage: `roll d20 disadvantage`, `roll 3d6 disadv`, `roll d8 d`
- `status` - Show current game status
- `save [name]` - Save game state (defaults to 'quicksave')
- `load <name>` - Load game state

## Architecture

### Command Handling (`lib/command_handler.py`)

The `CommandHandler` class provides:

- **Command Parsing**: Handles quoted arguments and proper tokenization
- **Command Registration**: Easy way to add custom commands
- **Error Handling**: Graceful handling of invalid commands and exceptions
- **Extensibility**: Simple interface for adding new functionality

### Extended Commands (`lib/custom_commands.py`)

The main application now includes extended functionality:

- **Dice Rolling**: `roll 2d6`, `roll d20` - Roll dice with proper validation
  - **Advantage/Disadvantage**: Support for advantage and disadvantage rolls
  - Advantage: Rolls twice and takes the higher result (`advantage`, `adv`, `a`)
  - Disadvantage: Rolls twice and takes the lower result (`disadvantage`, `disadv`, `d`)
  - Example: `roll d20 advantage` outputs `Rolled d20 (advantage): 18, 7 => 18`
- **Game Status**: `status` - Display current game state information  
- **Save/Load**: `save [name]`, `load <name>` - Game state persistence

## Features Detail

### Advantage and Disadvantage Rolling

The roll command supports D&D-style advantage and disadvantage mechanics:

**Advantage Rolling:**

- Roll two sets of dice and take the higher total
- Aliases: `advantage`, `adv`, `a`
- Single die: `roll d20 advantage` → `Rolled d20 (advantage): 18, 7 => 18`
- Multiple dice: `roll 3d6 adv` → `Rolled 3d6 (advantage): [1, 2, 3] = 6, [4, 5, 6] = 15 => [4, 5, 6] = 15`

**Disadvantage Rolling:**

- Roll two sets of dice and take the lower total  
- Aliases: `disadvantage`, `disadv`, `d`
- Single die: `roll d20 disadvantage` → `Rolled d20 (disadvantage): 7, 18 => 7`
- Multiple dice: `roll 2d6 d` → `Rolled 2d6 (disadvantage): [1, 2] = 3, [5, 6] = 11 => [1, 2] = 3`

## Development

### Development Workflow Guidelines

When implementing features or bug fixes, follow this structured approach:

#### 1. Issue Analysis & Planning

- **Read Referenced Issues**: Always start by thoroughly reading any GitHub issues referenced in the request
- **Understand Requirements**: Break down the request into specific, testable requirements
- **Design Planning**: Plan the code changes before implementation:
  - Identify which files need modification
  - Consider impact on existing functionality
  - Plan test cases and edge cases
  - Consider backward compatibility

#### 2. Environment Setup

##### Option A: Automated Setup (Recommended)

```bash
# The project includes automated Python environment configuration
# This approach allows testing/linting without manual approval prompts
# Simply run any pytest or flake8 command and the environment will be configured
python -m pytest tests/ -v  # Auto-configures environment and runs tests
python -m flake8 lib/ --max-line-length=120  # Auto-configures and lints
```

##### Option B: Manual Setup

```bash
# Manual environment setup (if needed)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Implementation Process

- **Feature Branch**: Create a descriptive feature branch
- **Code Changes**: Implement following established patterns and conventions
- **Code Quality**: Maintain consistent style and documentation
- **Incremental Testing**: Test frequently during development

#### 4. Testing & Quality Assurance

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

#### 5. Code Quality Checks

```bash
# Format code with black
python -m black lib/ tests/ --line-length=120

# Lint code with flake8
python -m flake8 lib/ tests/ --max-line-length=120 --exclude=__pycache__

# Check specific files
python -m flake8 lib/custom_commands.py --max-line-length=120
```

#### 6. Integration Testing

```bash
# Test the actual application
echo -e "help\nroll d20 advantage\nquit" | python roleplaying_toolkit.py
```

#### 7. Documentation Updates

- Update README.md with new features/changes
- Update docstrings for modified functions
- Include usage examples for new functionality

#### 8. Final Validation

- All tests must pass: `python -m pytest tests/ -v`
- Code must pass linting: `python -m flake8 lib/ tests/ --max-line-length=120`
- Application must run without errors
- New functionality must be documented

### Running Tests

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

### Test Coverage

The project includes comprehensive tests for:

- Command parsing and execution
- Error handling
- Main application integration
- Custom command extensions

## Project Structure

```text
roleplaying_toolkit/
├── roleplaying_toolkit.py      # Main application entry point
├── lib/
│   ├── statemgr.py            # State management system
│   ├── command_handler.py     # Core command handling logic
│   ├── custom_commands.py     # Example custom commands
│   └── states/                # Game states
└── tests/                     # Unit tests
    ├── test_command_handler.py
    ├── test_main_integration.py
    └── test_custom_commands.py
```
