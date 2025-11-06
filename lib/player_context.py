"""Player creation context and handler for interactive player creation mode."""

import random
from typing import Optional
from lib.player import Player
from lib.ability_scores import ABILITY_SCORES
from lib.player_manager import PlayerManager


class PlayerCreationContext:
    """Context for managing interactive player creation."""

    def __init__(self, game_manager, game_name: str):
        """Initialize player creation context.

        Args:
            game_manager: GameManager instance
            game_name: Name of the game
        """
        self.game_manager = game_manager
        self.game_name = game_name
        self.player: Optional[Player] = None
        self.rolled_scores: list[int] = []  # Track rolled scores for user assignment

        # Get the game's directory and create player manager
        game_path = self.game_manager.get_game_path(game_name)
        self.player_manager = PlayerManager(game_path)

    def set_player_name(self, name: str) -> tuple[bool, str]:
        """Set the player name and create a new player.

        Args:
            name: Name of the player

        Returns:
            Tuple of (success, message)
        """
        name = name.strip()

        if not name:
            return False, "Player name cannot be empty"

        if self.player_manager.player_exists(name):
            return False, f"Player '{name}' already exists in this game"

        self.player = Player(name)
        return True, f"Created player '{name}'"

    def set_ability(self, ability: str, value: int) -> tuple[bool, str]:
        """Set an ability score for the current player.

        Args:
            ability: Name of the ability
            value: Value to set

        Returns:
            Tuple of (success, message)
        """
        if self.player is None:
            return False, "Cannot set ability: no active player"

        return self.player.set_ability(ability, value)

    def roll_abilities(self) -> tuple[bool, str]:
        """Roll random ability scores (4d6 drop lowest) but don't assign them.

        User must manually assign rolled scores using the 'set' command.

        Returns:
            Tuple of (success, message with rolled scores)
        """
        if self.player is None:
            return False, "Cannot roll abilities: no active player"

        rolled_scores = []
        for _ in range(6):
            # Roll 4d6 and drop the lowest
            rolls = sorted([random.randint(1, 6) for _ in range(4)])
            score = sum(rolls[1:])  # Drop lowest, sum the rest
            rolled_scores.append(score)

        # Store the scores for reference
        self.rolled_scores = sorted(rolled_scores, reverse=True)

        # Format message showing the rolled scores
        scores_str = ", ".join(str(s) for s in self.rolled_scores)
        assign_msg = "(Use 'set <ability> <value>' to assign these scores)"
        return True, f"Rolled abilities: {scores_str}\n{assign_msg}"

    def get_status(self) -> str:
        """Get current player creation status.

        Returns:
            Status string
        """
        if self.player is None:
            return "No active player in creation mode"

        lines = [f"Player: {self.player.name}"]

        # Add ability scores
        for ability, config in ABILITY_SCORES.items():
            score = self.player.get_ability(ability)
            lines.append(f"  {config['display']}: {score}")

        if self.player.race:
            lines.append(f"Race: {self.player.race}")
        if self.player.class_type:
            lines.append(f"Class: {self.player.class_type}")

        return "\n".join(lines)

    def save_player(self) -> tuple[bool, str]:
        """Save the current player to the game.

        Args:
            None

        Returns:
            Tuple of (success, message)
        """
        if self.player is None:
            return False, "Cannot save: no active player"

        success, message = self.player_manager.save_player(self.player)

        if success:
            self.player = None  # Clear the current player after saving

        return success, message


class PlayerCreationHandler:
    """Command handler for player creation mode."""

    def __init__(self, game_manager, game_name: str):
        """Initialize the player creation handler.

        Args:
            game_manager: GameManager instance
            game_name: Name of the game
        """
        self.context = PlayerCreationContext(game_manager, game_name)
        self.game_manager = game_manager
        self.game_name = game_name
        self.awaiting_name = True  # Track if we're waiting for a name input

    def handle(self, command: str) -> str:
        """Handle a player creation command.

        Args:
            command: Command string

        Returns:
            Response message
        """
        command = command.strip()
        if not command:
            return "Enter a command or type 'help' for available commands"

        # If we're waiting for a name and this doesn't look like a command,
        # treat it as a name
        if self.awaiting_name and not any(
            command.lower().startswith(c)
            for c in ["name", "set", "roll", "status", "save", "help", "exit"]
        ):
            success, message = self.context.set_player_name(command)
            if success:
                self.awaiting_name = False
            return message

        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "name":
            if not args:
                return "Usage: name <player_name>"
            success, message = self.context.set_player_name(args)
            if success:
                self.awaiting_name = False
            return message

        elif cmd == "set":
            # set <ability> <value>
            set_parts = args.split(maxsplit=1)
            if len(set_parts) < 2:
                return "Usage: set <ability> <value>"

            ability = set_parts[0].lower()
            try:
                value = int(set_parts[1])
            except ValueError:
                return f"Invalid value: '{set_parts[1]}' is not a number"

            success, message = self.context.set_ability(ability, value)
            return message

        elif cmd == "roll":
            success, message = self.context.roll_abilities()
            return message

        elif cmd == "status":
            return self.context.get_status()

        elif cmd == "save":
            success, message = self.context.save_player()
            return message

        elif cmd == "help":
            help_text = [
                "Player Creation Commands:",
                "  name <name>        - Set player name",
                "  set <ability> <#>  - Set ability score",
                "                       Abilities: str, dex, con, int, wis, cha",
                "  roll               - Roll random abilities (4d6 drop lowest)",
                "  status             - Show current player status",
                "  save               - Save player to game",
                "  help               - Show this help message",
                "  exit               - Exit player creation without saving",
            ]
            return "\n".join(help_text)

        elif cmd == "exit":
            self.context.player = None
            return "Exited player creation mode without saving"

        else:
            return f"Unknown command: '{cmd}'. Type 'help' for available commands"
