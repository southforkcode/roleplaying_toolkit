"""Command handler for parsing and executing user commands."""

import shlex
from typing import Dict, List, Callable, Optional, Any


class Command:
    """Represents a parsed command with arguments."""

    def __init__(self, name: str, args: List[str], raw_input: str):
        self.name = name
        self.args = args
        self.raw_input = raw_input

    def __repr__(self):
        return f"Command(name='{self.name}', args={self.args})"


class CommandHandler:
    """Handles command parsing and execution."""

    def __init__(self):
        self._commands: Dict[str, Callable] = {}
        # Flag used to confirm destructive operations like resetting the
        # session when the user types 'new' once and must confirm by
        # typing 'new' again. Cleared automatically when any other
        # command is entered.
        self._pending_new: bool = False

        self._register_builtin_commands()

    def _register_builtin_commands(self):
        """Register built-in commands."""
        self.register_command("help", self._help_command)
        self.register_command("quit", self._quit_command)
        self.register_command("exit", self._quit_command)

    def register_command(self, name: str, handler: Callable) -> None:
        """Register a command handler.

        Args:
            name: Command name
            handler: Function to handle the command
        """
        self._commands[name.lower()] = handler

    def parse_command(self, user_input: str) -> Optional[Command]:
        """Parse user input into a Command object.

        Args:
            user_input: Raw user input string

        Returns:
            Command object or None if input is empty/invalid
        """
        if not user_input.strip():
            return None

        try:
            # Use shlex to properly handle quoted arguments
            tokens = shlex.split(user_input.strip())
        except ValueError:
            # Handle unclosed quotes gracefully
            tokens = user_input.strip().split()

        if not tokens:
            return None

        command_name = tokens[0].lower()
        args = tokens[1:] if len(tokens) > 1 else []

        return Command(command_name, args, user_input.strip())

    def execute_command(self, command: Command) -> Dict[str, Any]:
        """Execute a parsed command.

        Args:
            command: Command object to execute

        Returns:
            Dictionary with execution results including:
            - success: bool indicating if command succeeded
            - message: str with result message
            - exit: bool indicating if application should exit
        """
        if command.name not in self._commands:
            return {
                "success": False,
                "message": f"Unknown command: {command.name}. Type 'help' for available commands.",
                "exit": False,
            }

        try:
            handler = self._commands[command.name]
            return handler(command)
        except Exception as e:
            return {"success": False, "message": f"Error executing command '{command.name}': {str(e)}", "exit": False}

    def process_input(self, user_input: str) -> Dict[str, Any]:
        """Process raw user input - parse and execute command.

        Args:
            user_input: Raw user input string

        Returns:
            Dictionary with execution results
        """
        command = self.parse_command(user_input)

        if command is None:
            return {"success": True, "message": "", "exit": False}

        # If the parsed command is not the 'new' confirmation token, clear
        # any pending 'new' confirmation so that typing anything other than
        # 'new' after the first 'new' cancels the reset.
        if hasattr(self, "_pending_new") and command.name != "new":
            self._pending_new = False

        return self.execute_command(command)

    def get_available_commands(self) -> List[str]:
        """Get list of available command names."""
        return sorted(self._commands.keys())

    def _help_command(self, command: Command) -> Dict[str, Any]:
        """Built-in help command handler."""
        available_commands = self.get_available_commands()
        message = "Available commands:\n" + "\n".join(f"  {cmd}" for cmd in available_commands)

        return {"success": True, "message": message, "exit": False}

    def _quit_command(self, command: Command) -> Dict[str, Any]:
        """Built-in quit/exit command handler."""
        return {"success": True, "message": "Goodbye!", "exit": True}
