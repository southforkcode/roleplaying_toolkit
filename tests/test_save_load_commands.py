"""Tests for save/load command integration."""

import tempfile
import shutil
from pathlib import Path

from lib.command_handler import Command


def create_command(name: str, args: list = None) -> Command:
    """Helper to create Command objects for testing."""
    if args is None:
        args = []
    raw_input = name if not args else f"{name} {' '.join(args)}"
    return Command(name, args, raw_input)


class TestSaveLoadCommands:
    """Test cases for save/load command integration."""

    def setup_method(self):
        """Set up test environment."""
        # Create temporary directory for saves
        self.temp_dir = tempfile.mkdtemp()

        # We'll create a modified version for testing
        # This is simpler than trying to patch the existing handler
        from lib.command_handler import CommandHandler
        from lib.journey_system import JourneyManager
        from lib.game_manager import GameManager
        from lib.state_manager import StateManager
        from lib.custom_commands import (
            _roll_dice_command,
            _status_command,
            _save_command,
            _load_command,
            _saves_command,
            _journey_command,
            _progress_command,
            _stop_journey_command,
        )

        self.handler = CommandHandler()
        self.journey_manager = JourneyManager()
        # Create a game manager that uses our temp directory
        self.game_manager = GameManager(self.temp_dir)
        # Create a test game so save/load commands work
        self.game_manager.create_game("test_game")
        self.game_manager.set_current_game("test_game")

        # Register commands with our test instances
        self.handler.register_command("roll", _roll_dice_command)
        self.handler.register_command(
            "status", lambda cmd: _status_command(cmd, self.journey_manager)
        )
        self.handler.register_command(
            "save",
            lambda cmd: _save_command(cmd, self.journey_manager, self.game_manager),
        )
        self.handler.register_command(
            "load",
            lambda cmd: _load_command(cmd, self.journey_manager, self.game_manager),
        )
        self.handler.register_command(
            "saves", lambda cmd: _saves_command(cmd, self.game_manager)
        )
        self.handler.register_command(
            "journey", lambda cmd: _journey_command(cmd, self.journey_manager)
        )
        self.handler.register_command(
            "progress", lambda cmd: _progress_command(cmd, self.journey_manager)
        )
        self.handler.register_command(
            "stop", lambda cmd: _stop_journey_command(cmd, self.journey_manager)
        )

    def teardown_method(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.temp_dir)

    def test_save_command_default_name(self):
        """Test save command with default name."""
        command = create_command("save")
        result = self.handler.execute_command(command)

        assert result["success"] is True
        assert "quicksave" in result["message"]
        # Saves are now in the game's saves subdirectory
        assert Path(self.temp_dir, "game_test_game", "saves", "quicksave.yaml").exists()

    def test_save_command_custom_name(self):
        """Test save command with custom name."""
        command = create_command("save", ["my_save"])
        result = self.handler.execute_command(command)

        assert result["success"] is True
        assert "my_save" in result["message"]
        # Saves are now in the game's saves subdirectory
        assert Path(self.temp_dir, "game_test_game", "saves", "my_save.yaml").exists()

    def test_save_command_with_journeys(self):
        """Test save command with active journeys."""
        # Start some journeys
        journey_cmd = create_command("journey", ["Test Journey", "5", "2"])
        self.handler.execute_command(journey_cmd)

        progress_cmd = create_command("progress", ["2"])
        self.handler.execute_command(progress_cmd)

        # Save the state
        save_cmd = create_command("save", ["with_journeys"])
        result = self.handler.execute_command(save_cmd)

        assert result["success"] is True
        assert "with_journeys" in result["message"]

        # Verify file exists and contains journey data
        save_path = Path(self.temp_dir, "game_test_game", "saves", "with_journeys.yaml")
        assert save_path.exists()

        import yaml

        with open(save_path, "r") as f:
            data = yaml.safe_load(f)

        journeys = data["journey_manager"]["journeys"]
        assert len(journeys) == 1
        assert journeys[0]["name"] == "Test Journey"
        assert journeys[0]["progress"] == 2

    def test_load_command_missing_file(self):
        """Test load command with non-existent save."""
        command = create_command("load", ["nonexistent"])
        result = self.handler.execute_command(command)

        assert result["success"] is False
        assert "not found" in result["message"]

    def test_load_command_no_args(self):
        """Test load command without arguments."""
        command = create_command("load")
        result = self.handler.execute_command(command)

        assert result["success"] is False
        assert "Usage: load <save_name>" in result["message"]

    def test_save_and_load_roundtrip(self):
        """Test complete save/load roundtrip."""
        # Create some journeys
        journey1_cmd = create_command("journey", ["First Journey", "5", "2"])
        self.handler.execute_command(journey1_cmd)

        progress1_cmd = create_command("progress", ["2"])
        self.handler.execute_command(progress1_cmd)

        journey2_cmd = create_command("journey", ["Second Journey", "3", "1"])
        self.handler.execute_command(journey2_cmd)

        progress2_cmd = create_command("progress", ["1"])
        self.handler.execute_command(progress2_cmd)

        # Check initial status
        status_cmd = create_command("status")
        initial_status = self.handler.execute_command(status_cmd)

        # Save the state
        save_cmd = create_command("save", ["roundtrip_test"])
        save_result = self.handler.execute_command(save_cmd)
        assert save_result["success"] is True

        # Make some changes
        progress3_cmd = create_command("progress", ["1"])
        self.handler.execute_command(progress3_cmd)

        # Verify state changed
        modified_status = self.handler.execute_command(status_cmd)
        assert modified_status["message"] != initial_status["message"]

        # Load the saved state
        load_cmd = create_command("load", ["roundtrip_test"])
        load_result = self.handler.execute_command(load_cmd)
        assert load_result["success"] is True
        assert "roundtrip_test" in load_result["message"]

        # Verify state is restored
        restored_status = self.handler.execute_command(status_cmd)
        # The status should be similar to initial (though exact format may differ)
        assert "First Journey" in restored_status["message"]
        assert "Second Journey" in restored_status["message"]

    def test_saves_command_empty(self):
        """Test saves command with no saves."""
        command = create_command("saves")
        result = self.handler.execute_command(command)

        assert result["success"] is True
        assert "No saved games found" in result["message"]

    def test_saves_command_with_saves(self):
        """Test saves command with multiple saves."""
        # Create multiple saves
        save1_cmd = create_command("save", ["save1"])
        self.handler.execute_command(save1_cmd)

        save2_cmd = create_command("save", ["save2"])
        self.handler.execute_command(save2_cmd)

        save3_cmd = create_command("save", ["another_save"])
        self.handler.execute_command(save3_cmd)

        # List saves
        saves_cmd = create_command("saves")
        result = self.handler.execute_command(saves_cmd)

        assert result["success"] is True
        assert "Available saves:" in result["message"]
        assert "save1" in result["message"]
        assert "save2" in result["message"]
        assert "another_save" in result["message"]

    def test_saves_command_with_journey_info(self):
        """Test saves command shows journey information."""
        # Create journeys
        journey_cmd = create_command("journey", ["Test Journey", "5", "2"])
        self.handler.execute_command(journey_cmd)

        journey2_cmd = create_command("journey", ["Another Journey", "3", "1"])
        self.handler.execute_command(journey2_cmd)

        # Save state
        save_cmd = create_command("save", ["with_info"])
        self.handler.execute_command(save_cmd)

        # List saves
        saves_cmd = create_command("saves")
        result = self.handler.execute_command(saves_cmd)

        assert result["success"] is True
        assert "with_info" in result["message"]
        assert "2 journeys" in result["message"]

    def test_load_empty_save(self):
        """Test loading a save with no journeys."""
        # Save empty state
        save_cmd = create_command("save", ["empty"])
        self.handler.execute_command(save_cmd)

        # Add some journeys
        journey_cmd = create_command("journey", ["Test Journey", "5", "2"])
        self.handler.execute_command(journey_cmd)

        # Load empty state
        load_cmd = create_command("load", ["empty"])
        result = self.handler.execute_command(load_cmd)

        assert result["success"] is True
        assert "no active journeys" in result["message"]

        # Verify journeys are cleared
        status_cmd = create_command("status")
        status_result = self.handler.execute_command(status_cmd)
        assert "Test Journey" not in status_result["message"]

    def test_load_preserves_stack_order(self):
        """Test that loading preserves the journey stack order."""
        # Create journeys in specific order
        journey1_cmd = create_command("journey", ["Bottom Journey", "5", "1"])
        self.handler.execute_command(journey1_cmd)

        journey2_cmd = create_command("journey", ["Middle Journey", "3", "2"])
        self.handler.execute_command(journey2_cmd)

        journey3_cmd = create_command("journey", ["Top Journey", "2", "3"])
        self.handler.execute_command(journey3_cmd)

        # Save state
        save_cmd = create_command("save", ["stack_order"])
        self.handler.execute_command(save_cmd)

        # Clear journeys by stopping all
        stop_cmd = create_command("stop")
        self.handler.execute_command(stop_cmd)
        self.handler.execute_command(stop_cmd)
        self.handler.execute_command(stop_cmd)

        # Load state
        load_cmd = create_command("load", ["stack_order"])
        result = self.handler.execute_command(load_cmd)
        assert result["success"] is True

        # Check that Top Journey is current (should be mentioned first in status)
        status_cmd = create_command("status")
        status_result = self.handler.execute_command(status_cmd)
        status_lines = status_result["message"].split("\n")

        # Find the journey lines (after "Active Journeys:")
        journey_lines = []
        found_journeys_section = False
        for line in status_lines:
            if "Active Journeys:" in line:
                found_journeys_section = True
                continue
            if found_journeys_section and line.strip().startswith(("1.", "2.", "3.")):
                journey_lines.append(line.strip())

        # Top Journey should be first (current journey)
        assert len(journey_lines) == 3
        assert "Top Journey" in journey_lines[0]
        assert "Middle Journey" in journey_lines[1]
        assert "Bottom Journey" in journey_lines[2]

    def test_save_invalid_name_handled(self):
        """Test that save command handles invalid names gracefully."""
        # Try to save with invalid characters
        command = create_command("save", ["invalid/name"])
        result = self.handler.execute_command(command)

        # Should still succeed due to name sanitization
        assert result["success"] is True

        # But the actual save name should be sanitized
        saves_cmd = create_command("saves")
        saves_result = self.handler.execute_command(saves_cmd)
        assert "invalidname" in saves_result["message"].lower()
