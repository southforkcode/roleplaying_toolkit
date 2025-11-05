"""Unit tests for the command handler."""

import unittest
from unittest.mock import patch, call
from lib.command_handler import CommandHandler, Command


class TestCommand(unittest.TestCase):
    """Test cases for the Command class."""
    
    def test_command_creation(self):
        """Test Command object creation."""
        cmd = Command("test", ["arg1", "arg2"], "test arg1 arg2")
        
        self.assertEqual(cmd.name, "test")
        self.assertEqual(cmd.args, ["arg1", "arg2"])
        self.assertEqual(cmd.raw_input, "test arg1 arg2")
    
    def test_command_repr(self):
        """Test Command string representation."""
        cmd = Command("test", ["arg1"], "test arg1")
        expected = "Command(name='test', args=['arg1'])"
        
        self.assertEqual(repr(cmd), expected)


class TestCommandHandler(unittest.TestCase):
    """Test cases for the CommandHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = CommandHandler()
    
    def test_initialization(self):
        """Test CommandHandler initialization."""
        # Check that built-in commands are registered
        available_commands = self.handler.get_available_commands()
        self.assertIn("help", available_commands)
        self.assertIn("quit", available_commands)
        self.assertIn("exit", available_commands)
    
    def test_register_command(self):
        """Test command registration."""
        def test_handler(command):
            return {"success": True, "message": "test", "exit": False}
        
        self.handler.register_command("test", test_handler)
        available_commands = self.handler.get_available_commands()
        
        self.assertIn("test", available_commands)
    
    def test_parse_command_simple(self):
        """Test parsing simple commands."""
        cmd = self.handler.parse_command("help")
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "help")
        self.assertEqual(cmd.args, [])
        self.assertEqual(cmd.raw_input, "help")
    
    def test_parse_command_with_args(self):
        """Test parsing commands with arguments."""
        cmd = self.handler.parse_command("test arg1 arg2")
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "test")
        self.assertEqual(cmd.args, ["arg1", "arg2"])
        self.assertEqual(cmd.raw_input, "test arg1 arg2")
    
    def test_parse_command_with_quotes(self):
        """Test parsing commands with quoted arguments."""
        cmd = self.handler.parse_command('test "quoted arg" single')
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "test")
        self.assertEqual(cmd.args, ["quoted arg", "single"])
    
    def test_parse_command_empty_input(self):
        """Test parsing empty input."""
        cmd = self.handler.parse_command("")
        self.assertIsNone(cmd)
        
        cmd = self.handler.parse_command("   ")
        self.assertIsNone(cmd)
    
    def test_parse_command_unclosed_quotes(self):
        """Test parsing commands with unclosed quotes."""
        cmd = self.handler.parse_command('test "unclosed quote')
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "test")
        # Should fall back to simple split when shlex fails
        self.assertEqual(cmd.args, ['"unclosed', 'quote'])
    
    def test_parse_command_case_insensitive(self):
        """Test that command names are case insensitive."""
        cmd = self.handler.parse_command("HELP")
        
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd.name, "help")
    
    def test_execute_builtin_help_command(self):
        """Test executing the built-in help command."""
        cmd = Command("help", [], "help")
        result = self.handler.execute_command(cmd)
        
        self.assertTrue(result["success"])
        self.assertIn("Available commands:", result["message"])
        self.assertFalse(result["exit"])
    
    def test_execute_builtin_quit_command(self):
        """Test executing the built-in quit command."""
        cmd = Command("quit", [], "quit")
        result = self.handler.execute_command(cmd)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Goodbye!")
        self.assertTrue(result["exit"])
    
    def test_execute_builtin_exit_command(self):
        """Test executing the built-in exit command."""
        cmd = Command("exit", [], "exit")
        result = self.handler.execute_command(cmd)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Goodbye!")
        self.assertTrue(result["exit"])
    
    def test_execute_unknown_command(self):
        """Test executing an unknown command."""
        cmd = Command("unknown", [], "unknown")
        result = self.handler.execute_command(cmd)
        
        self.assertFalse(result["success"])
        self.assertIn("Unknown command: unknown", result["message"])
        self.assertFalse(result["exit"])
    
    def test_execute_custom_command(self):
        """Test executing a custom registered command."""
        def custom_handler(command):
            return {
                "success": True,
                "message": f"Custom command executed with args: {command.args}",
                "exit": False
            }
        
        self.handler.register_command("custom", custom_handler)
        cmd = Command("custom", ["arg1", "arg2"], "custom arg1 arg2")
        result = self.handler.execute_command(cmd)
        
        self.assertTrue(result["success"])
        self.assertIn("Custom command executed with args: ['arg1', 'arg2']", result["message"])
        self.assertFalse(result["exit"])
    
    def test_execute_command_with_exception(self):
        """Test executing a command that raises an exception."""
        def failing_handler(command):
            raise ValueError("Test error")
        
        self.handler.register_command("fail", failing_handler)
        cmd = Command("fail", [], "fail")
        result = self.handler.execute_command(cmd)
        
        self.assertFalse(result["success"])
        self.assertIn("Error executing command 'fail': Test error", result["message"])
        self.assertFalse(result["exit"])
    
    def test_process_input_valid_command(self):
        """Test processing valid input."""
        result = self.handler.process_input("help")
        
        self.assertTrue(result["success"])
        self.assertIn("Available commands:", result["message"])
        self.assertFalse(result["exit"])
    
    def test_process_input_empty(self):
        """Test processing empty input."""
        result = self.handler.process_input("")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "")
        self.assertFalse(result["exit"])
    
    def test_process_input_unknown_command(self):
        """Test processing unknown command."""
        result = self.handler.process_input("unknown")
        
        self.assertFalse(result["success"])
        self.assertIn("Unknown command: unknown", result["message"])
        self.assertFalse(result["exit"])
    
    def test_get_available_commands(self):
        """Test getting available commands."""
        commands = self.handler.get_available_commands()
        
        self.assertIsInstance(commands, list)
        self.assertIn("help", commands)
        self.assertIn("quit", commands)
        self.assertIn("exit", commands)
        # Should be sorted
        self.assertEqual(commands, sorted(commands))


class TestCommandLoopIntegration(unittest.TestCase):
    """Integration tests for command loop functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = CommandHandler()
    
    def test_complete_command_flow(self):
        """Test complete command processing flow."""
        # Test help command
        result = self.handler.process_input("help")
        self.assertTrue(result["success"])
        self.assertFalse(result["exit"])
        
        # Test quit command
        result = self.handler.process_input("quit")
        self.assertTrue(result["success"])
        self.assertTrue(result["exit"])
    
    def test_command_case_insensitivity(self):
        """Test that commands work regardless of case."""
        results = [
            self.handler.process_input("HELP"),
            self.handler.process_input("Help"),
            self.handler.process_input("hElP"),
            self.handler.process_input("help")
        ]
        
        for result in results:
            self.assertTrue(result["success"])
            self.assertIn("Available commands:", result["message"])
    
    def test_whitespace_handling(self):
        """Test handling of various whitespace scenarios."""
        # Leading/trailing whitespace
        result = self.handler.process_input("  help  ")
        self.assertTrue(result["success"])
        
        # Multiple spaces between command and args
        self.handler.register_command("test", lambda cmd: {
            "success": True, "message": f"args: {cmd.args}", "exit": False
        })
        result = self.handler.process_input("test   arg1    arg2")
        self.assertTrue(result["success"])
        self.assertIn("['arg1', 'arg2']", result["message"])


if __name__ == "__main__":
    unittest.main()