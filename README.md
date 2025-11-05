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
- `roll <dice>` - Roll dice (e.g., `roll d20`, `roll 2d6`)
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
- **Game Status**: `status` - Display current game state information  
- **Save/Load**: `save [name]`, `load <name>` - Game state persistence

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_command_handler.py -v
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
