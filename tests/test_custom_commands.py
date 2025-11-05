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
        with patch("random.randint", return_value=15):
            result = self.handler.process_input("roll d20")

            self.assertTrue(result["success"])
            self.assertIn("Rolled d20: 15", result["message"])
            self.assertFalse(result["exit"])

    def test_roll_multiple_dice(self):
        """Test rolling multiple dice."""
        with patch("random.randint", side_effect=[3, 5]):
            result = self.handler.process_input("roll 2d6")

            self.assertTrue(result["success"])
            self.assertIn("Rolled 2d6: [3, 5] = 8", result["message"])
            self.assertFalse(result["exit"])

    def test_roll_no_args(self):
        """Test roll command with no arguments."""
        result = self.handler.process_input("roll")

        self.assertFalse(result["success"])
        self.assertIn("Usage: roll <dice> [advantage|disadvantage]", result["message"])
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

    def test_roll_single_die_advantage(self):
        """Test rolling single die with advantage."""
        with patch("random.randint", side_effect=[15, 8]):
            result = self.handler.process_input("roll d20 advantage")

            self.assertTrue(result["success"])
            self.assertIn("Rolled d20 (advantage): 15, 8 => 15", result["message"])
            self.assertFalse(result["exit"])

    def test_roll_single_die_advantage_short(self):
        """Test rolling single die with advantage using short form."""
        with patch("random.randint", side_effect=[12, 18]):
            result = self.handler.process_input("roll d20 adv")

            self.assertTrue(result["success"])
            self.assertIn("Rolled d20 (advantage): 18, 12 => 18", result["message"])
            self.assertFalse(result["exit"])

    def test_roll_single_die_advantage_shortest(self):
        """Test rolling single die with advantage using shortest form."""
        with patch("random.randint", side_effect=[10, 3]):
            result = self.handler.process_input("roll d20 a")

            self.assertTrue(result["success"])
            self.assertIn("Rolled d20 (advantage): 10, 3 => 10", result["message"])
            self.assertFalse(result["exit"])

    def test_roll_single_die_disadvantage(self):
        """Test rolling single die with disadvantage."""
        with patch("random.randint", side_effect=[15, 8]):
            result = self.handler.process_input("roll d20 disadvantage")

            self.assertTrue(result["success"])
            self.assertIn("Rolled d20 (disadvantage): 8, 15 => 8", result["message"])
            self.assertFalse(result["exit"])

    def test_roll_single_die_disadvantage_short(self):
        """Test rolling single die with disadvantage using short form."""
        with patch("random.randint", side_effect=[12, 18]):
            result = self.handler.process_input("roll d20 disadv")

            self.assertTrue(result["success"])
            self.assertIn("Rolled d20 (disadvantage): 12, 18 => 12", result["message"])
            self.assertFalse(result["exit"])

    def test_roll_single_die_disadvantage_shortest(self):
        """Test rolling single die with disadvantage using shortest form."""
        with patch("random.randint", side_effect=[10, 3]):
            result = self.handler.process_input("roll d20 d")

            self.assertTrue(result["success"])
            self.assertIn("Rolled d20 (disadvantage): 3, 10 => 3", result["message"])
            self.assertFalse(result["exit"])

    def test_roll_multiple_dice_advantage(self):
        """Test rolling multiple dice with advantage."""
        with patch("random.randint", side_effect=[3, 5, 2, 6]):  # First roll: 3,5 = 8, Second roll: 2,6 = 8
            result = self.handler.process_input("roll 2d6 advantage")

            self.assertTrue(result["success"])
            # Should pick the first roll when totals are equal and show both sets
            expected = "Rolled 2d6 (advantage): [3, 5] = 8, [2, 6] = 8 => [3, 5] = 8"
            self.assertIn(expected, result["message"])
            self.assertFalse(result["exit"])

    def test_roll_multiple_dice_advantage_different_totals(self):
        """Test rolling multiple dice with advantage and different totals."""
        with patch("random.randint", side_effect=[1, 2, 5, 6]):  # First roll: 1,2 = 3, Second roll: 5,6 = 11
            result = self.handler.process_input("roll 2d6 adv")

            self.assertTrue(result["success"])
            expected = "Rolled 2d6 (advantage): [1, 2] = 3, [5, 6] = 11 => [5, 6] = 11"
            self.assertIn(expected, result["message"])
            self.assertFalse(result["exit"])

    def test_roll_multiple_dice_disadvantage(self):
        """Test rolling multiple dice with disadvantage."""
        with patch("random.randint", side_effect=[1, 2, 5, 6]):  # First roll: 1,2 = 3, Second roll: 5,6 = 11
            result = self.handler.process_input("roll 2d6 disadvantage")

            self.assertTrue(result["success"])
            expected = "Rolled 2d6 (disadvantage): [1, 2] = 3, [5, 6] = 11 => [1, 2] = 3"
            self.assertIn(expected, result["message"])
            self.assertFalse(result["exit"])

    def test_roll_complex_dice_advantage(self):
        """Test rolling complex dice combinations with advantage."""
        with patch("random.randint", side_effect=[1, 2, 3, 4, 5, 6]):  # First: 1,2,3 = 6, Second: 4,5,6 = 15
            result = self.handler.process_input("roll 3d6 a")

            self.assertTrue(result["success"])
            expected = "Rolled 3d6 (advantage): [1, 2, 3] = 6, [4, 5, 6] = 15 => [4, 5, 6] = 15"
            self.assertIn(expected, result["message"])
            self.assertFalse(result["exit"])

    def test_roll_invalid_modifier(self):
        """Test roll command with invalid modifier."""
        result = self.handler.process_input("roll d20 invalid")

        self.assertFalse(result["success"])
        self.assertIn("Invalid modifier 'invalid'", result["message"])
        self.assertFalse(result["exit"])

    def test_roll_case_insensitive_modifiers(self):
        """Test that modifiers are case insensitive."""
        with patch("random.randint", side_effect=[15, 8]):
            result = self.handler.process_input("roll d20 ADVANTAGE")

            self.assertTrue(result["success"])
            self.assertIn("Rolled d20 (advantage): 15, 8 => 15", result["message"])
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
        """Test load command with save name (should fail if file doesn't exist)."""
        result = self.handler.process_input("load mysave")

        self.assertFalse(result["success"])  # Should fail since file doesn't exist
        self.assertIn("Load failed", result["message"])
        self.assertFalse(result["exit"])

    def test_load_command_no_name(self):
        """Test load command without save name."""
        result = self.handler.process_input("load")

        self.assertFalse(result["success"])
        self.assertIn("Usage: load <save_name>", result["message"])
        self.assertFalse(result["exit"])

    def test_new_command_confirm_resets(self):
        """Typing 'new' twice should reset the session state."""
        # Start a journey
        self.handler.process_input('journey "Temp Quest" 3 1')
        status_before = self.handler.process_input("status")
        self.assertIn("Temp Quest", status_before["message"])

        # First 'new' asks for confirmation
        first = self.handler.process_input("new")
        self.assertTrue(first["success"])
        self.assertIn("Type 'new' again to confirm", first["message"])

        # Second 'new' performs reset
        second = self.handler.process_input("new")
        self.assertTrue(second["success"])
        self.assertIn("Session reset", second["message"])

        # Status should not include the previous journey
        status_after = self.handler.process_input("status")
        self.assertNotIn("Temp Quest", status_after["message"]) 

    def test_new_command_cancelled_by_other(self):
        """Typing 'new' then another command should cancel confirmation."""
        # Start a journey
        self.handler.process_input('journey "Keep Quest" 4 2')

        # First 'new' asks for confirmation
        first = self.handler.process_input("new")
        self.assertIn("Type 'new' again to confirm", first["message"])

        # Now run a different command which should cancel pending confirmation
        other = self.handler.process_input("status")
        self.assertTrue(other["success"])

        # If we type 'new' now, it should ask for confirmation again (not reset immediately)
        again = self.handler.process_input("new")
        self.assertIn("Type 'new' again to confirm", again["message"])


if __name__ == "__main__":
    unittest.main()
