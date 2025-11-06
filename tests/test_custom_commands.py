"""Tests for custom command extensions."""

import unittest
import shutil
from pathlib import Path
from unittest.mock import patch
from lib.custom_commands import create_extended_command_handler
from lib.journal_manager import JournalManager
from lib.game_manager import GameManager


class TestCustomCommands(unittest.TestCase):
    """Test cases for custom command extensions."""

    def setUp(self):
        """Set up test fixtures."""
        # Clean up any saved games from previous tests
        saves_dir = Path("saves")
        
        # Remove game directories
        for game_dir in saves_dir.glob("game_*"):
            shutil.rmtree(game_dir, ignore_errors=True)
        
        # Remove save files (except journal which is per-game now)
        for save_file in saves_dir.glob("*.yaml"):
            if not save_file.name.startswith("game_"):
                try:
                    save_file.unlink()
                except OSError:
                    pass
        
        # Clean up .current_game state file
        current_file = saves_dir / ".current_game"
        if current_file.exists():
            current_file.unlink()
        
        self.handler = create_extended_command_handler()
        # Clear journal for each test to avoid cross-test pollution
        journal_manager = JournalManager()
        journal_manager.clear_journal()

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

    def test_new_game_command_creates_game(self):
        """Test that new <game_name> creates a new game."""
        result = self.handler.process_input("new my_adventure")
        self.assertTrue(result["success"])
        self.assertIn("loaded/created", result["message"])
        self.assertIn("my_adventure", result["message"])

    def test_new_game_command_invalid_name(self):
        """Test that new command rejects invalid game names."""
        result = self.handler.process_input("new invalid@name")
        self.assertFalse(result["success"])
        self.assertIn("can only contain", result["message"])

    def test_new_game_command_no_args(self):
        """Test that new command requires game name."""
        result = self.handler.process_input("new")
        self.assertFalse(result["success"])
        self.assertIn("Usage:", result["message"])

    def test_fate_two_options(self):
        """Test fate command with two options."""
        with patch("random.randint", return_value=25):
            result = self.handler.process_input("fate safe,encounter")

            self.assertTrue(result["success"])
            self.assertIn("Fate checked:", result["message"])
            self.assertIn("safe (50%)", result["message"])
            self.assertIn("encounter (50%)", result["message"])
            self.assertIn("d100 => 25", result["message"])
            self.assertIn("=> safe", result["message"])
            self.assertFalse(result["exit"])

    def test_fate_multiple_options(self):
        """Test fate command with more than two options."""
        with patch("random.randint", return_value=50):
            result = self.handler.process_input("fate option1,option2,option3")

            self.assertTrue(result["success"])
            self.assertIn("option1 (33%)", result["message"])
            self.assertIn("option2 (33%)", result["message"])
            self.assertIn("option3 (33%)", result["message"])
            self.assertIn("d100 => 50", result["message"])
            self.assertFalse(result["exit"])

    def test_fate_no_args(self):
        """Test fate command with no arguments."""
        result = self.handler.process_input("fate")

        self.assertFalse(result["success"])
        self.assertIn("Usage: fate", result["message"])
        self.assertIn("Example: fate safe,encounter", result["message"])

    def test_fate_single_option(self):
        """Test fate command with single option (should fail)."""
        result = self.handler.process_input("fate onlyoption")

        self.assertFalse(result["success"])
        self.assertIn("at least 2 options", result["message"])

    def test_fate_selection_high_roll(self):
        """Test that high d100 roll selects last option."""
        with patch("random.randint", return_value=99):
            result = self.handler.process_input("fate first,second,third")

            self.assertTrue(result["success"])
            self.assertIn("d100 => 99", result["message"])
            self.assertIn("=> third", result["message"])

    def test_fate_selection_low_roll(self):
        """Test that low d100 roll selects first option."""
        with patch("random.randint", return_value=1):
            result = self.handler.process_input("fate first,second,third")

            self.assertTrue(result["success"])
            self.assertIn("d100 => 1", result["message"])
            self.assertIn("=> first", result["message"])

    def test_fate_with_spaces(self):
        """Test fate command handles spaces around options."""
        with patch("random.randint", return_value=50):
            # The fate command expects options in a single argument separated by commas
            result = self.handler.process_input('fate "safe , encounter"')

            self.assertTrue(result["success"])
            self.assertIn("safe", result["message"])
            self.assertIn("encounter", result["message"])
            self.assertFalse(result["exit"])

    def test_journey_auto_logs_to_journal(self):
        """Test that starting a journey logs to journal."""
        # Start a journey
        self.handler.process_input('journey "Test Quest" 5 2')

        # Check journal has entry
        result = self.handler.process_input("journal")
        self.assertTrue(result["success"])
        self.assertIn("Test Quest", result["message"])
        self.assertIn("Started journey", result["message"])

    def test_journal_invalid_limit(self):
        """Test journal command with invalid limit."""
        result = self.handler.process_input("journal invalid")

        self.assertFalse(result["success"])
        self.assertIn("Usage: journal", result["message"])

    def test_progress_auto_logs_to_journal(self):
        """Test that progress is logged to journal."""
        from lib.journal_manager import JournalManager

        # Create a fresh journal to avoid test pollution
        journal_manager = JournalManager("saves/test_journal.yaml")
        journal_manager.clear_journal()

        # Use the extended handler's managers
        self.handler.process_input('journey "Quest" 5 2')
        self.handler.process_input("progress 2")

        # Check that progress was logged
        result = self.handler.process_input("journal")
        self.assertTrue(result["success"])
        # Look for the progress entry in journal output
        lines = result["message"].split("\n")
        has_progress_entry = any("Made 2 step" in line for line in lines)
        self.assertTrue(
            has_progress_entry,
            f"Did not find progress entry. Journal output: {result['message']}"
        )

    def test_stop_journey_auto_logs_to_journal(self):
        """Test that completing a journey logs to journal."""
        # Start a journey
        self.handler.process_input('journey "Test Quest" 5 2')

        # Complete the journey
        self.handler.process_input("stop")

        # Check journal has stop entry
        result = self.handler.process_input("journal")
        self.assertTrue(result["success"])
        self.assertIn("Completed journey", result["message"])

    def test_journal_with_limit(self):
        """Test journal command with custom limit."""
        # Add multiple entries
        for i in range(15):
            self.handler.process_input(f'journey "Quest {i}" {i + 1} 1')

        # Request only 5 entries
        result = self.handler.process_input("journal 5")

        self.assertTrue(result["success"])
        # Should have 5 entries (15 journeys total, but only showing 5)
        self.assertIn("Quest 14", result["message"])  # Most recent
        self.assertNotIn("Quest 9", result["message"])  # Outside limit

    def test_journal_invalid_limit(self):
        """Test journal command with invalid limit."""
        result = self.handler.process_input("journal invalid")

        self.assertFalse(result["success"])
        self.assertIn("Usage: journal", result["message"])

    def test_journal_negative_limit(self):
        """Test journal command with negative limit."""
        result = self.handler.process_input("journal -5")

        self.assertFalse(result["success"])
        self.assertIn("positive number", result["message"])

    def test_journal_persistence(self):
        """Test that journal entries are persisted between handler instances."""
        import os
        import tempfile

        # Create a temporary journal file
        with tempfile.TemporaryDirectory() as tmpdir:
            journal_path = os.path.join(tmpdir, "journal.yaml")

            # Create first handler and add entries
            from lib.journal_manager import JournalManager

            journal1 = JournalManager(journal_path)
            journal1.add_entry(
                "test_event", "Test entry 1", {"key": "value"}
            )

            # Create second handler with same file
            journal2 = JournalManager(journal_path)
            entries = journal2.get_entries(10)

            # Should have the entry from first handler
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]["description"], "Test entry 1")

    def test_new_game_clears_journal(self):
        """Test that creating a new game clears journal entries."""
        # Create first game and add journal entries
        self.handler.process_input("new game1")
        self.handler.process_input('journey "Quest One" 5 2')
        self.handler.process_input("progress 2")

        # Verify journal has entries
        result = self.handler.process_input("journal")
        self.assertTrue(result["success"])
        self.assertIn("Quest One", result["message"])

        # Create new game - should clear journal
        self.handler.process_input("new game2")

        # Verify journal is now empty
        result = self.handler.process_input("journal")
        self.assertTrue(result["success"])
        self.assertIn("empty", result["message"].lower())

    def test_list_games_empty(self):
        """Test list command when no games exist."""
        result = self.handler.process_input("list")
        self.assertTrue(result["success"])
        self.assertIn("No games", result["message"])

    def test_list_games_with_games(self):
        """Test list command with existing games."""
        self.handler.process_input("new game_one")
        self.handler.process_input("new game_two")
        self.handler.process_input("new game_three")

        result = self.handler.process_input("list")
        self.assertTrue(result["success"])
        self.assertIn("game_one", result["message"])
        self.assertIn("game_two", result["message"])
        self.assertIn("game_three", result["message"])
        self.assertIn("current", result["message"].lower())

    def test_select_game_command(self):
        """Test switching between games."""
        self.handler.process_input("new game_alpha")
        self.handler.process_input("new game_beta")

        result = self.handler.process_input("select game_alpha")
        self.assertTrue(result["success"])
        self.assertIn("game_alpha", result["message"])

    def test_select_game_nonexistent(self):
        """Test selecting non-existent game fails."""
        result = self.handler.process_input("select nonexistent_game")
        self.assertFalse(result["success"])
        self.assertIn("not found", result["message"])

    def test_select_game_no_args(self):
        """Test select command requires game name."""
        self.handler.process_input("new test_game")
        result = self.handler.process_input("select")
        self.assertFalse(result["success"])
        self.assertIn("Usage:", result["message"])

    def test_session_command(self):
        """Test session command shows game info."""
        self.handler.process_input("new test_game")
        result = self.handler.process_input("session")

        self.assertTrue(result["success"])
        self.assertIn("test_game", result["message"])
        self.assertIn("Created:", result["message"])
        self.assertIn("Sessions:", result["message"])
        self.assertIn("Unsaved", result["message"])

    def test_session_command_no_game(self):
        """Test session command with no game loaded."""
        result = self.handler.process_input("session")
        self.assertTrue(result["success"])
        self.assertIn("No game", result["message"])


if __name__ == "__main__":
    unittest.main()
