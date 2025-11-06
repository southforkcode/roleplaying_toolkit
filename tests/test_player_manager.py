"""Tests for player manager persistence layer."""

import pytest
import tempfile
import os
from pathlib import Path
from lib.player_manager import PlayerManager


class TestPlayerManager:
    """Test player manager persistence."""

    @pytest.fixture
    def temp_game_dir(self):
        """Create a temporary game directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_player_manager_initialization(self, temp_game_dir):
        """Test creating a player manager."""
        pm = PlayerManager(temp_game_dir)
        assert str(pm.game_path) == temp_game_dir
        players_dir = Path(temp_game_dir) / "players"
        assert players_dir.exists()

    def test_create_player(self, temp_game_dir):
        """Test creating a new player."""
        pm = PlayerManager(temp_game_dir)
        success, message = pm.create_player("Jackbar")
        assert success is True
        assert "Saved player" in message
        assert pm.player_exists("Jackbar")

    def test_create_duplicate_player(self, temp_game_dir):
        """Test that duplicate player names are prevented."""
        pm = PlayerManager(temp_game_dir)
        pm.create_player("Jackbar")
        success, message = pm.create_player("Jackbar")
        assert success is False
        assert "already exists" in message

    def test_save_and_load_player(self, temp_game_dir):
        """Test saving and loading a player."""
        pm = PlayerManager(temp_game_dir)
        pm.create_player("Jackbar")

        # Get the player and modify it
        player = pm.get_player("Jackbar")
        player.set_ability("strength", 14)
        player.set_ability("dexterity", 15)
        player.race = "Human"
        player.class_type = "Rogue"

        # Save it
        success, message = pm.save_player(player)
        assert success is True
        assert "Saved player" in message

        # Load it back
        loaded = pm.load_player("Jackbar")
        assert loaded is not None
        assert loaded.name == "Jackbar"
        assert loaded.get_ability("strength") == 14
        assert loaded.get_ability("dexterity") == 15
        assert loaded.race == "Human"
        assert loaded.class_type == "Rogue"

    def test_get_player_not_found(self, temp_game_dir):
        """Test getting a non-existent player."""
        pm = PlayerManager(temp_game_dir)
        player = pm.get_player("NonExistent")
        assert player is None

    def test_get_all_players(self, temp_game_dir):
        """Test getting all players."""
        pm = PlayerManager(temp_game_dir)
        pm.create_player("Jackbar")
        pm.create_player("Elara")
        pm.create_player("Thorin")

        all_players = pm.get_all_players()
        assert len(all_players) == 3
        player_names = {p.name for p in all_players}
        assert player_names == {"Jackbar", "Elara", "Thorin"}

    def test_delete_player(self, temp_game_dir):
        """Test deleting a player."""
        pm = PlayerManager(temp_game_dir)
        pm.create_player("Jackbar")
        assert pm.player_exists("Jackbar")

        success, message = pm.delete_player("Jackbar")
        assert success is True
        assert "Deleted player" in message
        assert not pm.player_exists("Jackbar")

    def test_delete_nonexistent_player(self, temp_game_dir):
        """Test deleting a non-existent player."""
        pm = PlayerManager(temp_game_dir)
        success, message = pm.delete_player("NonExistent")
        assert success is False
        assert "not found" in message

    def test_get_player_count(self, temp_game_dir):
        """Test getting player count."""
        pm = PlayerManager(temp_game_dir)
        assert pm.get_player_count() == 0

        pm.create_player("Jackbar")
        assert pm.get_player_count() == 1

        pm.create_player("Elara")
        assert pm.get_player_count() == 2

        pm.delete_player("Jackbar")
        assert pm.get_player_count() == 1

    def test_player_file_location(self, temp_game_dir):
        """Test that player files are saved in correct location."""
        pm = PlayerManager(temp_game_dir)
        pm.create_player("Jackbar")

        player = pm.get_player("Jackbar")
        player.set_ability("strength", 14)
        pm.save_player(player)

        # Check that YAML file exists
        player_file = Path(temp_game_dir) / "players" / "Jackbar.yaml"
        assert player_file.exists()

        # Check that file contains player data
        content = player_file.read_text()
        assert "name: Jackbar" in content
        assert "strength: 14" in content

    def test_player_isolation_between_managers(self):
        """Test that different game paths have separate players."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                pm1 = PlayerManager(tmpdir1)
                pm2 = PlayerManager(tmpdir2)

                pm1.create_player("Jackbar")
                pm2.create_player("Elara")

                assert pm1.player_exists("Jackbar")
                assert not pm1.player_exists("Elara")
                assert pm2.player_exists("Elara")
                assert not pm2.player_exists("Jackbar")
