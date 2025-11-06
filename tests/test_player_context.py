"""Tests for player creation context handler."""

import pytest
import tempfile
from pathlib import Path
from lib.player_context import PlayerCreationContext, PlayerCreationHandler
from lib.game_manager import GameManager


class TestPlayerCreationContext:
    """Test player creation context."""

    @pytest.fixture
    def game_manager(self):
        """Create a temporary game for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            saves_dir = Path(tmpdir) / "saves"
            saves_dir.mkdir()
            gm = GameManager(str(saves_dir))
            gm.create_game("test_game")
            yield gm

    def test_context_initialization(self, game_manager):
        """Test creating a player creation context."""
        context = PlayerCreationContext(game_manager, "test_game")
        assert context.game_manager == game_manager
        assert context.game_name == "test_game"
        assert context.player is None

    def test_set_player_name(self, game_manager):
        """Test setting player name."""
        context = PlayerCreationContext(game_manager, "test_game")
        success, message = context.set_player_name("Jackbar")
        assert success is True
        assert context.player is not None
        assert context.player.name == "Jackbar"
        assert "Created player" in message

    def test_set_duplicate_player_name(self, game_manager):
        """Test setting duplicate player name."""
        context = PlayerCreationContext(game_manager, "test_game")
        context.set_player_name("Jackbar")
        context.save_player()  # Save the first player

        # Try to set same name again in a new context
        context2 = PlayerCreationContext(game_manager, "test_game")
        success, message = context2.set_player_name("Jackbar")
        assert success is False
        assert "already exists" in message

    def test_set_ability(self, game_manager):
        """Test setting an ability score."""
        context = PlayerCreationContext(game_manager, "test_game")
        context.set_player_name("Jackbar")

        success, message = context.set_ability("strength", 14)
        assert success is True
        assert context.player.get_ability("strength") == 14

    def test_set_ability_no_player(self, game_manager):
        """Test setting ability when no player exists."""
        context = PlayerCreationContext(game_manager, "test_game")
        success, message = context.set_ability("strength", 14)
        assert success is False
        assert "no active player" in message

    def test_roll_abilities(self, game_manager):
        """Test rolling random ability scores (without assigning them)."""
        context = PlayerCreationContext(game_manager, "test_game")
        context.set_player_name("Jackbar")

        success, message = context.roll_abilities()
        assert success is True
        assert "Rolled abilities" in message

        # Rolled scores should be stored but NOT automatically assigned to player
        assert len(context.rolled_scores) == 6
        # All rolled scores should be between 3 and 20
        for score in context.rolled_scores:
            assert 3 <= score <= 20

        # Player abilities should NOT be assigned (should be None)
        for ability in ["strength", "dexterity", "constitution",
                        "intelligence", "wisdom", "charisma"]:
            score = context.player.get_ability(ability)
            assert score is None  # Should still be unset

    def test_roll_abilities_no_player(self, game_manager):
        """Test rolling abilities when no player exists."""
        context = PlayerCreationContext(game_manager, "test_game")
        success, message = context.roll_abilities()
        assert success is False
        assert "no active player" in message

    def test_get_status(self, game_manager):
        """Test getting player status."""
        context = PlayerCreationContext(game_manager, "test_game")
        context.set_player_name("Jackbar")
        context.set_ability("strength", 14)

        status = context.get_status()
        assert "Jackbar" in status
        assert "strength" in status.lower()
        assert "14" in status

    def test_get_status_no_player(self, game_manager):
        """Test getting status when no player exists."""
        context = PlayerCreationContext(game_manager, "test_game")
        status = context.get_status()
        assert "no active player" in status.lower()

    def test_save_player(self, game_manager):
        """Test saving player."""
        context = PlayerCreationContext(game_manager, "test_game")
        context.set_player_name("Jackbar")
        context.set_ability("strength", 14)

        success, message = context.save_player()
        assert success is True
        assert "Saved" in message
        assert context.player is None  # Player cleared after save

    def test_save_player_no_player(self, game_manager):
        """Test saving when no player exists."""
        context = PlayerCreationContext(game_manager, "test_game")
        success, message = context.save_player()
        assert success is False
        assert "no active player" in message


class TestPlayerCreationHandler:
    """Test player creation command handler."""

    @pytest.fixture
    def game_manager(self):
        """Create a temporary game for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            saves_dir = Path(tmpdir) / "saves"
            saves_dir.mkdir()
            gm = GameManager(str(saves_dir))
            gm.create_game("test_game")
            yield gm

    def test_handler_initialization(self, game_manager):
        """Test creating a player creation handler."""
        handler = PlayerCreationHandler(game_manager, "test_game")
        assert handler.context is not None

    def test_handle_name_command(self, game_manager):
        """Test handling name command."""
        handler = PlayerCreationHandler(game_manager, "test_game")
        response = handler.handle("name Jackbar")
        assert "Created player" in response
        assert handler.context.player is not None

    def test_handle_set_command(self, game_manager):
        """Test handling set ability command."""
        handler = PlayerCreationHandler(game_manager, "test_game")
        handler.handle("name Jackbar")
        response = handler.handle("set strength 14")
        assert "Set" in response or "strength" in response
        assert handler.context.player.get_ability("strength") == 14

    def test_handle_roll_command(self, game_manager):
        """Test handling roll command requires dice notation."""
        handler = PlayerCreationHandler(game_manager, "test_game")
        handler.handle("name Jackbar")
        # roll without arguments should return usage error
        response = handler.handle("roll")
        assert "Usage:" in response or "dice_notation" in response
        # Verify abilities are NOT assigned
        assert handler.context.player.get_ability("strength") is None

    def test_handle_status_command(self, game_manager):
        """Test handling status command."""
        handler = PlayerCreationHandler(game_manager, "test_game")
        handler.handle("name Jackbar")
        handler.handle("set strength 14")
        response = handler.handle("status")
        assert "Jackbar" in response
        assert "14" in response

    def test_handle_save_command(self, game_manager):
        """Test handling save command."""
        handler = PlayerCreationHandler(game_manager, "test_game")
        handler.handle("name Jackbar")
        handler.handle("set strength 14")
        response = handler.handle("save")
        assert "Saved" in response

    def test_handle_invalid_command(self, game_manager):
        """Test handling invalid command."""
        handler = PlayerCreationHandler(game_manager, "test_game")
        response = handler.handle("invalid_command")
        assert "Unknown command" in response or "invalid" in response.lower()

    def test_handle_plain_name_input(self, game_manager):
        """Test handling plain name input without 'name' command prefix."""
        handler = PlayerCreationHandler(game_manager, "test_game")
        # Just type a name directly
        response = handler.handle("Aragorn")
        assert "Created player" in response
        assert handler.context.player is not None
        assert handler.context.player.name == "Aragorn"
        assert handler.awaiting_name is False

    def test_handle_help_command(self, game_manager):
        """Test handling help command."""
        handler = PlayerCreationHandler(game_manager, "test_game")
        response = handler.handle("help")
        assert "name" in response
        assert "set" in response
        assert "save" in response
