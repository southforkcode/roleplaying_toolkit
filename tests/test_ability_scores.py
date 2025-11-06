"""Tests for ability scores system."""

import pytest
from lib.ability_scores import (
    ABILITY_SCORES,
    is_valid_ability,
    get_ability_short,
    get_ability_display,
    is_valid_score,
    get_ability_range,
    get_all_abilities,
)


class TestAbilityScores:
    """Test ability score validation and utilities."""

    def test_all_abilities_defined(self):
        """Test that all standard abilities are defined."""
        expected_abilities = {
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        }
        assert set(ABILITY_SCORES.keys()) == expected_abilities

    def test_is_valid_ability(self):
        """Test ability validation."""
        assert is_valid_ability("strength")
        assert is_valid_ability("STRENGTH")  # Case insensitive
        assert is_valid_ability("dexterity")
        assert not is_valid_ability("invalid_ability")
        assert not is_valid_ability("")

    def test_get_ability_short(self):
        """Test getting short form of abilities."""
        assert get_ability_short("strength") == "str"
        assert get_ability_short("dexterity") == "dex"
        assert get_ability_short("constitution") == "con"
        assert get_ability_short("intelligence") == "int"
        assert get_ability_short("wisdom") == "wis"
        assert get_ability_short("charisma") == "cha"

    def test_get_ability_display(self):
        """Test getting display name of abilities."""
        assert get_ability_display("strength") == "Strength"
        assert get_ability_display("dexterity") == "Dexterity"

    def test_is_valid_score(self):
        """Test score validation."""
        # Valid scores
        assert is_valid_score("strength", 10)
        assert is_valid_score("strength", 3)   # Minimum
        assert is_valid_score("strength", 20)  # Maximum

        # Invalid scores
        assert not is_valid_score("strength", 2)   # Below minimum
        assert not is_valid_score("strength", 21)  # Above maximum
        assert not is_valid_score("invalid", 10)   # Invalid ability

    def test_get_ability_range(self):
        """Test getting ability ranges."""
        min_val, max_val = get_ability_range("strength")
        assert min_val == 3
        assert max_val == 20

        # Invalid ability
        min_val, max_val = get_ability_range("invalid")
        assert min_val == 0
        assert max_val == 0

    def test_get_all_abilities(self):
        """Test getting list of all abilities."""
        abilities = get_all_abilities()
        assert len(abilities) == 6
        assert "strength" in abilities
        assert "dexterity" in abilities
        assert "constitution" in abilities
        assert "intelligence" in abilities
        assert "wisdom" in abilities
        assert "charisma" in abilities
