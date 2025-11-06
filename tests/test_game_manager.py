"""Tests for game manager functionality."""

import unittest
import tempfile
import shutil
from pathlib import Path

from lib.game_manager import GameManager


class TestGameManager(unittest.TestCase):
    """Test cases for GameManager class."""

    def setUp(self):
        """Create temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.game_manager = GameManager(self.test_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_game_manager_initialization(self):
        """Test game manager initializes with empty saves directory."""
        games = self.game_manager.list_games()
        self.assertEqual(games, [])
        self.assertIsNone(self.game_manager.get_current_game())

    def test_create_game_success(self):
        """Test creating a new game successfully."""
        success, message = self.game_manager.create_game("quest_one")
        self.assertTrue(success)
        self.assertIn("created successfully", message)
        self.assertEqual(self.game_manager.get_current_game(), "quest_one")

    def test_create_game_creates_files(self):
        """Test that creating a game creates required files."""
        self.game_manager.create_game("test_game")
        game_path = Path(self.test_dir) / "game_test_game"

        self.assertTrue((game_path / "game.yaml").exists())
        self.assertTrue((game_path / "journal.yaml").exists())
        self.assertTrue((game_path / "state.yaml").exists())

    def test_create_game_duplicate(self):
        """Test creating a game with existing name fails."""
        self.game_manager.create_game("duplicate")
        success, message = self.game_manager.create_game("duplicate")

        self.assertFalse(success)
        self.assertIn("already exists", message)

    def test_create_game_empty_name(self):
        """Test creating a game with empty name fails."""
        success, message = self.game_manager.create_game("")
        self.assertFalse(success)
        self.assertIn("cannot be empty", message)

    def test_create_game_invalid_characters(self):
        """Test game name validation rejects invalid characters."""
        invalid_names = [
            "quest-one/path",
            "quest@one",
            "quest one",  # spaces not allowed
            "quest.one",
            "quest<one>",
        ]

        for name in invalid_names:
            success, message = self.game_manager.create_game(name)
            self.assertFalse(success, f"Should reject '{name}'")
            self.assertIn("can only contain", message)

    def test_create_game_valid_names(self):
        """Test game name validation accepts valid characters."""
        valid_names = ["quest_one", "quest-one", "QuestOne", "q1", "QUEST_123"]

        for i, name in enumerate(valid_names):
            self.game_manager.create_game(f"{name}_{i}")
            self.assertIn(f"{name}_{i}", self.game_manager.list_games())

    def test_list_games(self):
        """Test listing all games."""
        self.game_manager.create_game("game1")
        self.game_manager.create_game("game2")
        self.game_manager.create_game("game3")

        games = self.game_manager.list_games()
        self.assertEqual(len(games), 3)
        self.assertEqual(games, ["game1", "game2", "game3"])  # Sorted

    def test_list_games_sorted(self):
        """Test that list_games returns sorted names."""
        self.game_manager.create_game("zebra")
        self.game_manager.create_game("alpha")
        self.game_manager.create_game("beta")

        games = self.game_manager.list_games()
        self.assertEqual(games, ["alpha", "beta", "zebra"])

    def test_get_game_info(self):
        """Test retrieving game metadata."""
        self.game_manager.create_game("test_game")
        info = self.game_manager.get_game_info("test_game")

        self.assertIsNotNone(info)
        self.assertEqual(info["name"], "test_game")
        self.assertIn("created_at", info)
        self.assertIn("last_modified", info)
        self.assertIn("total_sessions", info)
        self.assertIn("current_session_unsaved", info)

    def test_get_game_info_nonexistent(self):
        """Test getting info for non-existent game returns None."""
        info = self.game_manager.get_game_info("nonexistent")
        self.assertIsNone(info)

    def test_load_game(self):
        """Test loading an existing game."""
        self.game_manager.create_game("game1")
        self.game_manager.create_game("game2")

        success, message = self.game_manager.load_game("game1")
        self.assertTrue(success)
        self.assertEqual(self.game_manager.get_current_game(), "game1")

    def test_load_game_nonexistent(self):
        """Test loading non-existent game fails."""
        success, message = self.game_manager.load_game("nonexistent")
        self.assertFalse(success)
        self.assertIn("not found", message)

    def test_delete_game(self):
        """Test deleting a game."""
        self.game_manager.create_game("to_delete")
        self.game_manager.create_game("to_keep")

        success, message = self.game_manager.delete_game("to_delete")
        self.assertTrue(success)

        games = self.game_manager.list_games()
        self.assertNotIn("to_delete", games)
        self.assertIn("to_keep", games)

    def test_delete_game_updates_current(self):
        """Test deleting current game switches to another."""
        self.game_manager.create_game("game1")
        self.game_manager.create_game("game2")
        self.game_manager.load_game("game1")

        self.game_manager.delete_game("game1")
        self.assertEqual(self.game_manager.get_current_game(), "game2")

    def test_delete_game_nonexistent(self):
        """Test deleting non-existent game fails."""
        success, message = self.game_manager.delete_game("nonexistent")
        self.assertFalse(success)
        self.assertIn("not found", message)

    def test_get_game_path(self):
        """Test getting game path."""
        self.game_manager.create_game("test_game")
        path = self.game_manager.get_game_path("test_game")

        self.assertTrue(path.exists())
        self.assertTrue(path.is_dir())
        self.assertIn("game_test_game", str(path))

    def test_get_game_path_current_game(self):
        """Test getting path for current game."""
        self.game_manager.create_game("current_game")
        path = self.game_manager.get_game_path()

        self.assertTrue(path.exists())
        self.assertIn("game_current_game", str(path))

    def test_get_game_path_no_current_game(self):
        """Test getting path with no current game raises error."""
        with self.assertRaises(ValueError):
            self.game_manager.get_game_path()

    def test_update_game_metadata(self):
        """Test updating game metadata."""
        self.game_manager.create_game("test_game")

        success, message = self.game_manager.update_game_metadata(
            "test_game", total_sessions=5, current_session_unsaved=True
        )
        self.assertTrue(success)

        info = self.game_manager.get_game_info("test_game")
        self.assertEqual(info["total_sessions"], 5)
        self.assertTrue(info["current_session_unsaved"])

    def test_update_game_metadata_immutable_fields(self):
        """Test that created_at and name cannot be modified."""
        self.game_manager.create_game("test_game")
        info_before = self.game_manager.get_game_info("test_game")

        self.game_manager.update_game_metadata(
            "test_game", name="new_name", created_at="2000-01-01"
        )

        info_after = self.game_manager.get_game_info("test_game")
        self.assertEqual(info_after["name"], info_before["name"])
        self.assertEqual(info_after["created_at"], info_before["created_at"])

    def test_current_game_persistence(self):
        """Test that current game is persisted between instances."""
        self.game_manager.create_game("persistent_game")
        self.game_manager.load_game("persistent_game")

        # Create new manager instance
        new_manager = GameManager(self.test_dir)
        self.assertEqual(new_manager.get_current_game(), "persistent_game")

    def test_game_name_length_limit(self):
        """Test game name length validation."""
        long_name = "a" * 51
        success, message = self.game_manager.create_game(long_name)
        self.assertFalse(success)
        self.assertIn("50 characters", message)

    def test_validate_game_name_static(self):
        """Test static validation method."""
        valid, error = GameManager._validate_game_name("valid_name")
        self.assertTrue(valid)
        self.assertEqual(error, "")

        valid, error = GameManager._validate_game_name("invalid name")
        self.assertFalse(valid)
        self.assertNotEqual(error, "")

    def test_current_game_yaml_metadata_creation(self):
        """Test that current_game.yaml is created with metadata (issue #16)."""
        self.game_manager.create_game("test_game")
        
        # Check that current_game.yaml exists
        metadata_file = Path(self.test_dir) / "current_game.yaml"
        self.assertTrue(metadata_file.exists())
        
        # Check metadata contents
        import yaml
        with open(metadata_file, "r") as f:
            metadata = yaml.safe_load(f)
        
        self.assertIn("game_name", metadata)
        self.assertEqual(metadata["game_name"], "test_game")
        self.assertIn("last_accessed", metadata)

    def test_current_game_yaml_updated_on_load(self):
        """Test that current_game.yaml is updated when loading a game (use case 4)."""
        self.game_manager.create_game("game1")
        self.game_manager.create_game("game2")
        
        # Load game1
        self.game_manager.load_game("game1")
        
        # Check metadata file
        import yaml
        metadata_file = Path(self.test_dir) / "current_game.yaml"
        with open(metadata_file, "r") as f:
            metadata = yaml.safe_load(f)
        
        self.assertEqual(metadata["game_name"], "game1")

    def test_startup_no_games(self):
        """Test startup behavior with no saved games (use case 1)."""
        manager = GameManager(self.test_dir)
        # No games should result in None current game
        self.assertIsNone(manager.get_current_game())

    def test_startup_with_games_no_metadata(self):
        """Test startup with existing games but no current_game.yaml (use case 2)."""
        # Create a game folder manually without using GameManager
        game_dir = Path(self.test_dir) / "game_existing"
        game_dir.mkdir()
        
        # Create new manager - should not set current game
        manager = GameManager(self.test_dir)
        self.assertIsNone(manager.get_current_game())

    def test_startup_with_valid_metadata(self):
        """Test startup with valid current_game.yaml pointing to existing game (use case 3)."""
        self.game_manager.create_game("game1")
        self.game_manager.create_game("game2")
        
        # Load game1
        self.game_manager.load_game("game1")
        
        # Create new manager instance
        manager = GameManager(self.test_dir)
        self.assertEqual(manager.get_current_game(), "game1")

    def test_startup_with_invalid_metadata(self):
        """Test startup with current_game.yaml pointing to deleted game (use case 4)."""
        self.game_manager.create_game("game1")
        self.game_manager.load_game("game1")
        
        # Delete the game manually
        game_dir = Path(self.test_dir) / "game_game1"
        shutil.rmtree(game_dir)
        
        # Create new manager instance - should not set current game
        manager = GameManager(self.test_dir)
        self.assertIsNone(manager.get_current_game())

    def test_delete_game_clears_metadata_if_current(self):
        """Test that deleting current game clears current_game.yaml."""
        self.game_manager.create_game("game1")
        self.game_manager.load_game("game1")
        
        # Verify metadata is set
        metadata_file = Path(self.test_dir) / "current_game.yaml"
        self.assertTrue(metadata_file.exists())
        
        # Delete the game
        self.game_manager.delete_game("game1")
        
        # Create new manager - should have no current game
        manager = GameManager(self.test_dir)
        self.assertIsNone(manager.get_current_game())


if __name__ == "__main__":
    unittest.main()
