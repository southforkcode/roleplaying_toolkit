"""Tests for player character model."""

import pytest
from lib.player import Player
from lib.ability_scores import ABILITY_SCORES


class TestPlayer:
    """Test player character model."""

    def test_player_creation(self):
        """Test creating a new player."""
        player = Player("Jackbar")
        assert player.name == "Jackbar"
        assert player.race is None
        assert player.class_type is None
        assert player.created_at is not None
        assert player.updated_at is not None

    def test_player_default_stats(self):
        """Test that new player has default stats."""
        player = Player("Jackbar")
        # All stats should start at default (10)
        for ability in ABILITY_SCORES:
            assert player.stats[ability] == 10

    def test_set_ability_valid(self):
        """Test setting a valid ability score."""
        player = Player("Jackbar")
        success, message = player.set_ability("strength", 14)
        assert success is True
        assert player.get_ability("strength") == 14
        assert "Set Jackbar strength to 14" in message

    def test_set_ability_invalid_name(self):
        """Test setting an invalid ability."""
        player = Player("Jackbar")
        success, message = player.set_ability("invalid", 14)
        assert success is False
        assert "Unknown ability" in message

    def test_set_ability_out_of_range(self):
        """Test setting an ability score outside valid range."""
        player = Player("Jackbar")

        # Too low
        success, message = player.set_ability("strength", 2)
        assert success is False
        assert "must be between" in message

        # Too high
        success, message = player.set_ability("strength", 21)
        assert success is False
        assert "must be between" in message

    def test_set_ability_case_insensitive(self):
        """Test that ability names are case insensitive."""
        player = Player("Jackbar")
        success, message = player.set_ability("STRENGTH", 14)
        assert success is True
        assert player.get_ability("strength") == 14

    def test_get_ability(self):
        """Test getting ability scores."""
        player = Player("Jackbar")
        player.set_ability("strength", 14)
        assert player.get_ability("strength") == 14
        assert player.get_ability("dexterity") == 10  # Default
        assert player.get_ability("invalid") is None

    def test_player_serialization(self):
        """Test converting player to/from dictionary."""
        player = Player("Jackbar")
        player.set_ability("strength", 14)
        player.set_ability("dexterity", 15)
        player.race = "Human"
        player.class_type = "Rogue"

        data = player.to_dict()
        assert data["name"] == "Jackbar"
        assert data["race"] == "Human"
        assert data["class"] == "Rogue"
        assert data["stats"]["strength"] == 14
        assert data["stats"]["dexterity"] == 15

    def test_player_deserialization(self):
        """Test creating player from dictionary."""
        data = {
            "name": "Elara",
            "race": "Elf",
            "class": "Ranger",
            "stats": {
                "strength": 12,
                "dexterity": 16,
                "constitution": 13,
                "intelligence": 10,
                "wisdom": 14,
                "charisma": 11,
            },
            "created_at": "2025-11-05T10:00:00",
            "updated_at": "2025-11-05T10:00:00",
        }

        player = Player.from_dict(data)
        assert player.name == "Elara"
        assert player.race == "Elf"
        assert player.class_type == "Ranger"
        assert player.get_ability("strength") == 12
        assert player.get_ability("dexterity") == 16

    def test_player_repr(self):
        """Test player string representation."""
        player = Player("Jackbar")
        assert "Jackbar" in repr(player)
        assert "no race" in repr(player)
        assert "no class" in repr(player)

        player.race = "Human"
        player.class_type = "Rogue"
        assert "Human" in repr(player)
        assert "Rogue" in repr(player)
