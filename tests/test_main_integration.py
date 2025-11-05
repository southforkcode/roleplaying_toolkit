"""Integration tests for the main command loop."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

# Add the project root to the path so we can import roleplaying_toolkit
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import roleplaying_toolkit


class TestMainCommandLoop(unittest.TestCase):
    """Test cases for the main command loop integration."""
    
    @patch('builtins.input')
    @patch('roleplaying_toolkit.StateManager')
    def test_main_help_then_quit(self, mock_state_manager, mock_input):
        """Test main function with help command followed by quit."""
        # Mock the StateManager
        mock_instance = MagicMock()
        mock_state_manager.get_instance.return_value = mock_instance
        
        # Simulate user input: help, then quit
        mock_input.side_effect = ['help', 'quit']
        
        # Capture output
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            roleplaying_toolkit.main()
        
        output = captured_output.getvalue()
        
        # Check that welcome message is displayed
        self.assertIn("Welcome to the Roleplaying Toolkit!", output)
        
        # Check that help output is displayed
        self.assertIn("Available commands:", output)
        
        # Check that goodbye message is displayed
        self.assertIn("Goodbye!", output)
        
        # Verify StateManager was initialized
        mock_state_manager.get_instance.assert_called_once()
    
    @patch('builtins.input')
    @patch('roleplaying_toolkit.StateManager')
    def test_main_unknown_command(self, mock_state_manager, mock_input):
        """Test main function with unknown command followed by quit."""
        # Mock the StateManager
        mock_instance = MagicMock()
        mock_state_manager.get_instance.return_value = mock_instance
        
        # Simulate user input: unknown command, then quit
        mock_input.side_effect = ['unknown_command', 'quit']
        
        # Capture output
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            roleplaying_toolkit.main()
        
        output = captured_output.getvalue()
        
        # Check that error message is displayed
        self.assertIn("Unknown command: unknown_command", output)
        
        # Check that goodbye message is displayed
        self.assertIn("Goodbye!", output)
    
    @patch('builtins.input')
    @patch('roleplaying_toolkit.StateManager')
    def test_main_empty_input(self, mock_state_manager, mock_input):
        """Test main function with empty input followed by quit."""
        # Mock the StateManager
        mock_instance = MagicMock()
        mock_state_manager.get_instance.return_value = mock_instance
        
        # Simulate user input: empty string, then quit
        mock_input.side_effect = ['', '   ', 'quit']
        
        # Capture output
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            roleplaying_toolkit.main()
        
        output = captured_output.getvalue()
        
        # Check that welcome message is displayed
        self.assertIn("Welcome to the Roleplaying Toolkit!", output)
        
        # Check that goodbye message is displayed
        self.assertIn("Goodbye!", output)
        
        # Should not contain error messages for empty input
        self.assertNotIn("Unknown command:", output)
    
    @patch('builtins.input')
    @patch('roleplaying_toolkit.StateManager')
    def test_main_keyboard_interrupt(self, mock_state_manager, mock_input):
        """Test main function handles KeyboardInterrupt gracefully."""
        # Mock the StateManager
        mock_instance = MagicMock()
        mock_state_manager.get_instance.return_value = mock_instance
        
        # Simulate KeyboardInterrupt (Ctrl+C)
        mock_input.side_effect = KeyboardInterrupt()
        
        # Capture output
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            roleplaying_toolkit.main()
        
        output = captured_output.getvalue()
        
        # Check that exit message is displayed
        self.assertIn("Exiting...", output)
    
    @patch('builtins.input')
    @patch('roleplaying_toolkit.StateManager')
    def test_main_eof_error(self, mock_state_manager, mock_input):
        """Test main function handles EOFError gracefully."""
        # Mock the StateManager
        mock_instance = MagicMock()
        mock_state_manager.get_instance.return_value = mock_instance
        
        # Simulate EOFError (Ctrl+D)
        mock_input.side_effect = EOFError()
        
        # Capture output
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            roleplaying_toolkit.main()
        
        output = captured_output.getvalue()
        
        # Check that exit message is displayed
        self.assertIn("Exiting...", output)
    
    @patch('builtins.input')
    @patch('roleplaying_toolkit.StateManager')
    def test_main_multiple_commands(self, mock_state_manager, mock_input):
        """Test main function with multiple commands."""
        # Mock the StateManager
        mock_instance = MagicMock()
        mock_state_manager.get_instance.return_value = mock_instance
        
        # Simulate multiple commands
        mock_input.side_effect = ['help', 'unknown', '', 'exit']
        
        # Capture output
        captured_output = io.StringIO()
        
        with redirect_stdout(captured_output):
            roleplaying_toolkit.main()
        
        output = captured_output.getvalue()
        
        # Check various outputs
        self.assertIn("Welcome to the Roleplaying Toolkit!", output)
        self.assertIn("Available commands:", output)
        self.assertIn("Unknown command: unknown", output)
        self.assertIn("Goodbye!", output)
        
        # Verify input was called 4 times
        self.assertEqual(mock_input.call_count, 4)


if __name__ == "__main__":
    unittest.main()