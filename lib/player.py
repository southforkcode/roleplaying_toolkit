"""Player character model for the roleplaying toolkit."""

from datetime import datetime
from typing import Optional, Dict, Any
from lib.ability_scores import ABILITY_SCORES


class Player:
    """Represents a player character with stats and metadata."""

    def __init__(self, name: str):
        """Initialize a new player character.

        Args:
            name: Name of the player character
        """
        self.name = name
        self.race: Optional[str] = None
        self.class_type: Optional[str] = None
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

        # Initialize all ability scores to default (10)
        self.stats: Dict[str, int] = {}
        for ability in ABILITY_SCORES:
            self.stats[ability] = ABILITY_SCORES[ability]["default"]

    def set_ability(self, ability_name: str, value: int) -> tuple[bool, str]:
        """Set an ability score to a specific value.

        Args:
            ability_name: Name of the ability (e.g., 'strength')
            value: New value for the ability

        Returns:
            Tuple of (success, message)
        """
        ability_name = ability_name.lower()

        if ability_name not in ABILITY_SCORES:
            return False, f"Unknown ability: {ability_name}"

        ability = ABILITY_SCORES[ability_name]
        if not (ability["min"] <= value <= ability["max"]):
            return (
                False,
                f"{ability_name} must be between {ability['min']} and {ability['max']}",
            )

        self.stats[ability_name] = value
        self.updated_at = datetime.now().isoformat()
        return True, f"Set {self.name} {ability_name} to {value}."

    def get_ability(self, ability_name: str) -> Optional[int]:
        """Get an ability score value.

        Args:
            ability_name: Name of the ability

        Returns:
            Ability score or None if invalid
        """
        return self.stats.get(ability_name.lower())

    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for serialization.

        Returns:
            Dictionary representation of the player
        """
        return {
            "name": self.name,
            "race": self.race,
            "class": self.class_type,
            "stats": dict(self.stats),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Player":
        """Create a player from dictionary data.

        Args:
            data: Dictionary with player data

        Returns:
            Player instance
        """
        player = Player(data["name"])
        player.race = data.get("race")
        player.class_type = data.get("class")
        player.created_at = data.get("created_at", player.created_at)
        player.updated_at = data.get("updated_at", player.updated_at)

        # Restore stats
        if "stats" in data:
            player.stats.update(data["stats"])

        return player

    def __repr__(self) -> str:
        """String representation of the player."""
        race_str = self.race or "no race"
        class_str = self.class_type or "no class"
        return f"{self.name} ({race_str}) ({class_str})"
