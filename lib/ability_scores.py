"""Ability score definitions for player characters."""

# Standard D&D 5e ability scores with typical ranges
ABILITY_SCORES = {
    "strength": {
        "short": "str",
        "display": "Strength",
        "min": 3,
        "max": 20,
        "default": 10,
    },
    "dexterity": {
        "short": "dex",
        "display": "Dexterity",
        "min": 3,
        "max": 20,
        "default": 10,
    },
    "constitution": {
        "short": "con",
        "display": "Constitution",
        "min": 3,
        "max": 20,
        "default": 10,
    },
    "intelligence": {
        "short": "int",
        "display": "Intelligence",
        "min": 3,
        "max": 20,
        "default": 10,
    },
    "wisdom": {
        "short": "wis",
        "display": "Wisdom",
        "min": 3,
        "max": 20,
        "default": 10,
    },
    "charisma": {
        "short": "cha",
        "display": "Charisma",
        "min": 3,
        "max": 20,
        "default": 10,
    },
}


def is_valid_ability(ability_name: str) -> bool:
    """Check if an ability score name is valid."""
    return ability_name.lower() in ABILITY_SCORES


def get_ability_short(ability_name: str) -> str:
    """Get the short form of an ability name."""
    return ABILITY_SCORES.get(ability_name.lower(), {}).get("short", "")


def get_ability_display(ability_name: str) -> str:
    """Get the display name of an ability."""
    return ABILITY_SCORES.get(ability_name.lower(), {}).get("display", "")


def is_valid_score(ability_name: str, score: int) -> bool:
    """Check if a score is valid for an ability."""
    ability = ABILITY_SCORES.get(ability_name.lower())
    if not ability:
        return False
    return ability["min"] <= score <= ability["max"]


def get_ability_range(ability_name: str) -> tuple[int, int]:
    """Get min and max values for an ability."""
    ability = ABILITY_SCORES.get(ability_name.lower())
    if not ability:
        return (0, 0)
    return (ability["min"], ability["max"])


def get_all_abilities() -> list[str]:
    """Get list of all valid ability names."""
    return list(ABILITY_SCORES.keys())
