"""Tests for custom command extensions."""

import unittest
from unittest.mock import patch
from lib.custom_commands import create_extended_command_handler


class TestCustomCommands(unittest.TestCase):
    """Test cases for custom command extensions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.handler = create_extended_command_handler()
    
    def test_extended_handler_has_custom_commands(self):
        """Test that extended handler includes custom commands."""
        commands = self.handler.get_available_commands()
        
        # Should have built-in commands
        self.assertIn("help", commands)
        self.assertIn("quit", commands)
        self.assertIn("exit", commands)
        
        # Should have custom commands
        self.assertIn("roll", commands)
        self.assertIn("status", commands)
        self.assertIn("save", commands)
        self.assertIn("load", commands)
    
    def test_roll_single_die(self):
        """Test rolling a single die."""
        with patch('random.randint', return_value=15):
            result = self.handler.process_input("roll d20")
            
            self.assertTrue(result["success"])
            self.assertIn("Rolled d20: 15", result["message"])
            self.assertFalse(result["exit"])
    
    def test_roll_multiple_dice(self):
        """Test rolling multiple dice."""
        with patch('random.randint', side_effect=[3, 5]):
            result = self.handler.process_input("roll 2d6")
            
            self.assertTrue(result["success"])
            self.assertIn("Rolled 2d6: [3, 5] = 8", result["message"])
            self.assertFalse(result["exit"])
    
    def test_roll_no_args(self):
        """Test roll command with no arguments."""
        result = self.handler.process_input("roll")
        
        self.assertFalse(result["success"])
        self.assertIn("Usage: roll <dice>", result["message"])
        self.assertFalse(result["exit"])
    
    def test_roll_invalid_format(self):
        """Test roll command with invalid format."""
        result = self.handler.process_input("roll invalid")
        
        self.assertFalse(result["success"])
        self.assertIn("Invalid dice notation", result["message"])
        self.assertFalse(result["exit"])
    
    def test_roll_too_many_dice(self):
        """Test roll command with too many dice."""
        result = self.handler.process_input("roll 101d6")
        
        self.assertFalse(result["success"])
        self.assertIn("Too many dice", result["message"])
        self.assertFalse(result["exit"])
    
    def test_roll_negative_values(self):
        """Test roll command with negative values."""
        result = self.handler.process_input("roll -1d6")
        
        self.assertFalse(result["success"])
        self.assertIn("Invalid dice notation", result["message"])
        self.assertFalse(result["exit"])
    
    def test_status_command(self):
        """Test status command."""
        result = self.handler.process_input("status")
        
        self.assertTrue(result["success"])
        self.assertIn("Current Status:", result["message"])
        self.assertIn("Health:", result["message"])
        self.assertIn("Mana:", result["message"])
        self.assertFalse(result["exit"])
    
    def test_save_command_with_name(self):
        """Test save command with explicit name."""
        result = self.handler.process_input("save mysave")
        
        self.assertTrue(result["success"])
        self.assertIn("Game saved as 'mysave'", result["message"])
        self.assertFalse(result["exit"])
    
    def test_save_command_default_name(self):
        """Test save command with default name."""
        result = self.handler.process_input("save")
        
        self.assertTrue(result["success"])
        self.assertIn("Game saved as 'quicksave'", result["message"])
        self.assertFalse(result["exit"])
    
    def test_load_command_with_name(self):
        """Test load command with save name."""
        result = self.handler.process_input("load mysave")
        
        self.assertTrue(result["success"])
        self.assertIn("Game loaded from 'mysave'", result["message"])
        self.assertFalse(result["exit"])
    
    def test_load_command_no_name(self):
        """Test load command without save name."""
        result = self.handler.process_input("load")
        
        self.assertFalse(result["success"])
        self.assertIn("Usage: load <save_name>", result["message"])
        self.assertFalse(result["exit"])


if __name__ == "__main__":
    unittest.main()