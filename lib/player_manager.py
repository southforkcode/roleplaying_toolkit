"""Manager for player characters within a game."""

import yaml
from pathlib import Path
from typing import List, Optional
from lib.player import Player


class PlayerManager:
    """Manages player characters for a specific game."""

    def __init__(self, game_path: str):
        """Initialize the player manager for a game.

        Args:
            game_path: Path to the game directory
        """
        self.game_path = Path(game_path)
        self.players_directory = self.game_path / "players"
        self.players_directory.mkdir(parents=True, exist_ok=True)

    def create_player(self, name: str) -> tuple[bool, str]:
        """Create a new player character.

        Args:
            name: Name of the player character

        Returns:
            Tuple of (success, message)
        """
        name = name.strip()

        if not name:
            return False, "Player name cannot be empty"

        if self.player_exists(name):
            return False, f"Player '{name}' already exists in this game"

        # Create and save the player
        player = Player(name)
        return self.save_player(player)

    def save_player(self, player: Player) -> tuple[bool, str]:
        """Save a player to YAML file.

        Args:
            player: Player instance to save

        Returns:
            Tuple of (success, message)
        """
        try:
            player_file = self.players_directory / f"{player.name}.yaml"
            with open(player_file, "w") as f:
                yaml.dump(player.to_dict(), f, default_flow_style=False, sort_keys=False)
            return True, f"Saved player {player.name}."
        except OSError as e:
            return False, f"Failed to save player: {e}"

    def load_player(self, name: str) -> Optional[Player]:
        """Load a player from YAML file.

        Args:
            name: Name of the player to load

        Returns:
            Player instance or None if not found
        """
        player_file = self.players_directory / f"{name}.yaml"

        if not player_file.exists():
            return None

        try:
            with open(player_file, "r") as f:
                data = yaml.safe_load(f)
            return Player.from_dict(data)
        except (OSError, yaml.YAMLError):
            return None

    def player_exists(self, name: str) -> bool:
        """Check if a player exists.

        Args:
            name: Name of the player

        Returns:
            True if player exists, False otherwise
        """
        player_file = self.players_directory / f"{name}.yaml"
        return player_file.exists()

    def get_all_players(self) -> List[Player]:
        """Get all players in the game.

        Returns:
            List of Player instances
        """
        players = []
        if not self.players_directory.exists():
            return players

        for player_file in self.players_directory.glob("*.yaml"):
            try:
                with open(player_file, "r") as f:
                    data = yaml.safe_load(f)
                players.append(Player.from_dict(data))
            except (OSError, yaml.YAMLError):
                pass

        return sorted(players, key=lambda p: p.name)

    def get_player(self, name: str) -> Optional[Player]:
        """Get a specific player by name.

        Args:
            name: Name of the player

        Returns:
            Player instance or None if not found
        """
        return self.load_player(name)

    def delete_player(self, name: str) -> tuple[bool, str]:
        """Delete a player.

        Args:
            name: Name of the player

        Returns:
            Tuple of (success, message)
        """
        player_file = self.players_directory / f"{name}.yaml"

        if not player_file.exists():
            return False, f"Player '{name}' not found"

        try:
            player_file.unlink()
            return True, f"Deleted player {name}."
        except OSError as e:
            return False, f"Failed to delete player: {e}"

    def get_player_count(self) -> int:
        """Get the number of players in the game.

        Returns:
            Number of players
        """
        return len(self.get_all_players())
