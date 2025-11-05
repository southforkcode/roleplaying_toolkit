"""Tests for the journey command integration."""

import pytest
from lib.custom_commands import (
    _roll_dice_command,
    _status_command,
    _journey_command,
    _progress_command,
    _stop_journey_command,
    create_extended_command_handler,
)
from lib.journey_system import JourneyManager
from lib.command_handler import Command


class MockCommand:
    """Mock command for testing."""

    def __init__(self, args=None):
        self.args = args or []


class TestJourneyCommandIntegration:
    """Test cases for journey command integration."""

    def test_journey_start_valid(self):
        """Test starting a valid journey."""
        cmd = MockCommand(["Find treasure", "5", "2"])
        manager = JourneyManager()
        result = _journey_command(cmd, manager)

        assert result["success"]
        assert "Started journey: 'Find treasure'" in result["message"]
        assert "(5 steps, 2 difficulty)" in result["message"]
        assert not result["exit"]

        # Verify journey was added
        assert manager.has_active_journeys()
        journeys = manager.get_all_journeys()
        assert len(journeys) == 1
        assert journeys[0].name == "Find treasure"

    def test_progress_command_integration(self):
        """Test progress command integration."""
        cmd = MockCommand(["2"])
        manager = JourneyManager()
        manager.start_journey("Test Quest", 5, 2)

        result = _progress_command(cmd, manager)

        assert result["success"]
        assert "Progress on 'Test Quest': 2/5" in result["message"]
        assert not result["exit"]

    def test_stop_command_integration(self):
        """Test stop command integration."""
        cmd = MockCommand([])
        manager = JourneyManager()
        manager.start_journey("Test Quest", 5, 2)
        manager.make_progress(2)

        result = _stop_journey_command(cmd, manager)

        assert result["success"]
        assert "Stopped journey: 'Test Quest' (was 2/5)" in result["message"]
        assert not result["exit"]

    def test_status_with_journeys_integration(self):
        """Test status command showing journeys."""
        cmd = MockCommand([])
        manager = JourneyManager()
        manager.start_journey("Quest One", 5, 2)
        manager.start_journey("Quest Two", 3, 1)
        manager.make_progress(1)  # Progress on Quest Two

        result = _status_command(cmd, manager)

        assert result["success"]
        assert "Active Journeys:" in result["message"]
        assert "Quest Two (1/3)" in result["message"]
        assert "Quest One (0/5)" in result["message"]
        assert not result["exit"]

    def test_extended_handler_has_journey_commands(self):
        """Test that extended handler includes journey commands."""
        handler = create_extended_command_handler()
        commands = handler.get_available_commands()

        # Should have journey commands
        assert "journey" in commands
        assert "progress" in commands
        assert "stop" in commands

    def test_full_journey_workflow_via_handler(self):
        """Test complete journey workflow through command handler."""
        handler = create_extended_command_handler()

        # Start a journey
        result1 = handler.process_input('journey "Epic Quest" 3 3')
        assert result1["success"]
        assert "Started journey: 'Epic Quest'" in result1["message"]

        # Check status
        result2 = handler.process_input("status")
        assert result2["success"]
        assert "Epic Quest (0/3)" in result2["message"]

        # Make progress
        result3 = handler.process_input("progress 2")
        assert result3["success"]
        assert "Progress on 'Epic Quest': 2/3" in result3["message"]

        # Check status again
        result4 = handler.process_input("status")
        assert result4["success"]
        assert "Epic Quest (2/3)" in result4["message"]

        # Complete the journey
        result5 = handler.process_input("progress 1")
        assert result5["success"]
        assert "completed" in result5["message"].lower()

        # Check status after completion
        result6 = handler.process_input("status")
        assert result6["success"]
        assert "Active Journeys:" not in result6["message"]

    def test_multiple_journey_stack_via_handler(self):
        """Test journey stacking through command handler."""
        handler = create_extended_command_handler()

        # Start first journey
        result1 = handler.process_input('journey "Bottom Quest" 5 1')
        assert result1["success"]

        # Start second journey (should become current)
        result2 = handler.process_input('journey "Top Quest" 2 2')
        assert result2["success"]

        # Make progress (should be on top quest)
        result3 = handler.process_input("progress")
        assert result3["success"]
        assert "Top Quest" in result3["message"]

        # Stop current journey
        result4 = handler.process_input("stop")
        assert result4["success"]
        assert "Stopped journey: 'Top Quest'" in result4["message"]

        # Make progress (should now be on bottom quest)
        result5 = handler.process_input("progress")
        assert result5["success"]
        assert "Bottom Quest" in result5["message"]

    def test_journey_error_handling_via_handler(self):
        """Test journey error handling through command handler."""
        handler = create_extended_command_handler()

        # Try progress with no journey
        result1 = handler.process_input("progress")
        assert not result1["success"]
        assert "No active journeys" in result1["message"]

        # Try stop with no journey
        result2 = handler.process_input("stop")
        assert not result2["success"]
        assert "No active journeys" in result2["message"]

        # Try invalid journey parameters
        result3 = handler.process_input('journey "Bad Quest" 0 1')
        assert not result3["success"]
        assert "positive number" in result3["message"]

        result4 = handler.process_input('journey "Bad Quest" 5 -1')
        assert not result4["success"]
        assert "positive number" in result4["message"]
