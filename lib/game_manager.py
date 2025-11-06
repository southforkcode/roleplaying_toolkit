"""Game management system for handling multiple game saves."""

import yaml
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class GameManager:
    """Manages game lifecycle, metadata, and save points."""

    def __init__(self, saves_directory: str = "saves"):
        """Initialize the game manager.

        Args:
            saves_directory: Root directory for all games (default: "saves")
        """
        self.saves_directory = Path(saves_directory)
        self.saves_directory.mkdir(exist_ok=True)
        self._current_game: Optional[str] = None
        self._load_current_game()

    def _load_current_game(self) -> None:
        """Load the last played game or None if no games exist.

        Implements issue #16 use cases:
        1. No games: current_game = None
        2. Games exist, no current_game.yaml: current_game = None (will prompt user)
        3. current_game.yaml exists and points to valid game: load that game
        4. current_game.yaml points to deleted game: treat as case 2
        """
        games = self.list_games()
        if not games:
            self._current_game = None
            return

        # Try to load from current_game.yaml metadata file
        metadata_file = self.saves_directory / "current_game.yaml"
        if metadata_file.exists():
            try:
                with open(metadata_file, "r") as f:
                    data = yaml.safe_load(f)
                    if data and isinstance(data, dict):
                        current = data.get("game_name")
                        if current in games:
                            self._current_game = current
                            return
            except (OSError, yaml.YAMLError):
                pass

        # If no valid current_game.yaml or it points to deleted game,
        # don't set current game (None means prompt user for new game)
        self._current_game = None

    def _save_current_game(self) -> None:
        """Save the current game to current_game.yaml metadata file."""
        metadata_file = self.saves_directory / "current_game.yaml"
        try:
            metadata = {
                "game_name": self._current_game or "",
                "last_accessed": datetime.now().isoformat()
            }
            with open(metadata_file, "w") as f:
                yaml.dump(metadata, f, default_flow_style=False, sort_keys=False)
        except OSError:
            pass

    @staticmethod
    def _validate_game_name(name: str) -> tuple[bool, str]:
        """Validate game name for filesystem safety.

        Args:
            name: Game name to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Game name cannot be empty"

        # Remove leading/trailing whitespace
        name = name.strip()

        # Check for invalid characters (filesystem safe)
        if not re.match(r"^[a-zA-Z0-9_\-]+$", name):
            return (
                False,
                "Game name can only contain letters, numbers, underscores, and hyphens",
            )

        if len(name) > 50:
            return False, "Game name must be 50 characters or less"

        return True, ""

    def create_game(self, game_name: str) -> tuple[bool, str]:
        """Create a new game with initialization files.

        Args:
            game_name: Name of the new game

        Returns:
            Tuple of (success, message)
        """
        is_valid, error = self._validate_game_name(game_name)
        if not is_valid:
            return False, error

        game_dir = self.saves_directory / f"game_{game_name}"

        # Check if game already exists
        if game_dir.exists():
            return False, f"Game '{game_name}' already exists"

        try:
            # Create game directory
            game_dir.mkdir(parents=True, exist_ok=True)

            # Create game.yaml with metadata
            game_metadata = {
                "name": game_name,
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "total_sessions": 0,
                "current_session_unsaved": False,
            }
            game_file = game_dir / "game.yaml"
            with open(game_file, "w") as f:
                yaml.dump(game_metadata, f, default_flow_style=False, sort_keys=False)

            # Create empty journal.yaml
            journal_file = game_dir / "journal.yaml"
            with open(journal_file, "w") as f:
                yaml.dump({"entries": []}, f, default_flow_style=False, sort_keys=False)

            # Create empty state.yaml
            state_file = game_dir / "state.yaml"
            with open(state_file, "w") as f:
                yaml.dump({}, f, default_flow_style=False, sort_keys=False)

            self._current_game = game_name
            self._save_current_game()

            return True, f"Game '{game_name}' created successfully"

        except OSError as e:
            return False, f"Failed to create game: {e}"

    def delete_game(self, game_name: str) -> tuple[bool, str]:
        """Delete a game and all its files.

        Args:
            game_name: Name of the game to delete

        Returns:
            Tuple of (success, message)
        """
        is_valid, error = self._validate_game_name(game_name)
        if not is_valid:
            return False, error

        game_dir = self.saves_directory / f"game_{game_name}"

        if not game_dir.exists():
            return False, f"Game '{game_name}' not found"

        try:
            # Remove all files in game directory
            import shutil

            shutil.rmtree(game_dir)

            # If this was the current game, switch to another
            if self._current_game == game_name:
                games = self.list_games()
                if games:
                    self._current_game = games[0]
                else:
                    self._current_game = None
                self._save_current_game()

            return True, f"Game '{game_name}' deleted"

        except OSError as e:
            return False, f"Failed to delete game: {e}"

    def list_games(self) -> List[str]:
        """List all available games.

        Returns:
            List of game names (sorted)
        """
        games = []
        for game_dir in self.saves_directory.iterdir():
            if game_dir.is_dir() and game_dir.name.startswith("game_"):
                game_name = game_dir.name[5:]  # Remove "game_" prefix
                games.append(game_name)
        return sorted(games)

    def get_game_info(self, game_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a game.

        Args:
            game_name: Name of the game

        Returns:
            Dictionary with game info or None if not found
        """
        is_valid, _ = self._validate_game_name(game_name)
        if not is_valid:
            return None

        game_dir = self.saves_directory / f"game_{game_name}"
        game_file = game_dir / "game.yaml"

        if not game_file.exists():
            return None

        try:
            with open(game_file, "r") as f:
                metadata = yaml.safe_load(f)
                if metadata is None:
                    return None
                return metadata
        except (OSError, yaml.YAMLError):
            return None

    def load_game(self, game_name: str) -> tuple[bool, str]:
        """Load an existing game and set it as current.

        Args:
            game_name: Name of the game to load

        Returns:
            Tuple of (success, message)
        """
        is_valid, error = self._validate_game_name(game_name)
        if not is_valid:
            return False, error

        game_dir = self.saves_directory / f"game_{game_name}"

        if not game_dir.exists():
            return False, f"Game '{game_name}' not found"

        # Verify required files
        required_files = ["game.yaml", "journal.yaml", "state.yaml"]
        for filename in required_files:
            if not (game_dir / filename).exists():
                return False, f"Game '{game_name}' is corrupted (missing {filename})"

        self._current_game = game_name
        self._save_current_game()
        return True, f"Loaded game '{game_name}'"

    def get_current_game(self) -> Optional[str]:
        """Get the name of the current game.

        Returns:
            Current game name or None if no game loaded
        """
        return self._current_game

    def set_current_game(self, game_name: str) -> tuple[bool, str]:
        """Set the current game without loading files.

        Args:
            game_name: Name of the game to set as current

        Returns:
            Tuple of (success, message)
        """
        is_valid, error = self._validate_game_name(game_name)
        if not is_valid:
            return False, error

        game_dir = self.saves_directory / f"game_{game_name}"
        if not game_dir.exists():
            return False, f"Game '{game_name}' not found"

        self._current_game = game_name
        self._save_current_game()
        return True, ""

    def get_game_path(self, game_name: Optional[str] = None) -> Path:
        """Get the directory path for a game.

        Args:
            game_name: Name of the game (defaults to current game)

        Returns:
            Path to game directory
        """
        name = game_name or self._current_game
        if not name:
            raise ValueError("No game specified and no current game loaded")

        return self.saves_directory / f"game_{name}"

    def update_game_metadata(
        self, game_name: str, **kwargs
    ) -> tuple[bool, str]:
        """Update game metadata fields.

        Args:
            game_name: Name of the game
            **kwargs: Metadata fields to update

        Returns:
            Tuple of (success, message)
        """
        is_valid, error = self._validate_game_name(game_name)
        if not is_valid:
            return False, error

        game_file = self.get_game_path(game_name) / "game.yaml"

        if not game_file.exists():
            return False, f"Game '{game_name}' not found"

        try:
            with open(game_file, "r") as f:
                metadata = yaml.safe_load(f) or {}

            # Update fields
            for key, value in kwargs.items():
                if key not in ["name", "created_at"]:  # Prevent modification
                    metadata[key] = value

            # Always update last_modified
            metadata["last_modified"] = datetime.now().isoformat()

            # Write back
            with open(game_file, "w") as f:
                yaml.dump(
                    metadata, f, default_flow_style=False, sort_keys=False
                )

            return True, ""

        except (OSError, yaml.YAMLError) as e:
            return False, f"Failed to update metadata: {e}"
