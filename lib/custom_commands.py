"""Example of extending the command handler with custom commands."""

from pathlib import Path
from lib.command_handler import CommandHandler
from lib.journey_system import JourneyManager
from lib.state_manager import StateManager
from lib.journal_manager import JournalManager
from lib.game_manager import GameManager
from lib.player_context import PlayerCreationHandler


def create_extended_command_handler():
    """Create a command handler with additional custom commands."""
    import yaml
    handler = CommandHandler()

    # Initialize managers
    game_manager = GameManager()
    journey_manager = JourneyManager()

    # Get current game and set up journal manager with game-specific path
    current_game = game_manager.get_current_game()
    if current_game:
        game_path = game_manager.get_game_path(current_game)
        # Initialize journal manager with current game's journal
        journal_path = game_path / "journal.yaml"
        journal_manager = JournalManager(str(journal_path))
        
        # Load the last saved game state (from quicksave) if available
        try:
            game_saves_dir = game_path / "saves"
            quicksave_path = game_saves_dir / "quicksave.yaml"
            if quicksave_path.exists():
                with open(quicksave_path, "r") as f:
                    state_data = yaml.safe_load(f)
                if state_data and isinstance(state_data, dict):
                    if "journey_manager" in state_data:
                        restored_manager = JourneyManager.from_dict(
                            state_data["journey_manager"]
                        )
                        # Replace journey manager's journeys with restored ones
                        journey_manager._journeys = restored_manager._journeys
        except (OSError, ValueError, KeyError, AttributeError):
            # If loading fails, continue with empty journey manager
            pass
    else:
        # No current game - use a placeholder journal that won't create root-level file
        # We'll set the proper path when a game is selected
        journal_manager = JournalManager("saves/.journal_placeholder")

    # Register custom commands
    handler.register_command("roll", _roll_dice_command)
    handler.register_command(
        "status", lambda cmd: _status_command(cmd, journey_manager, game_manager)
    )
    handler.register_command(
        "save", lambda cmd: _save_command(cmd, journey_manager, game_manager)
    )
    handler.register_command(
        "load", lambda cmd: _load_command(cmd, journey_manager, game_manager)
    )
    handler.register_command("saves", lambda cmd: _saves_command(cmd, game_manager))
    handler.register_command(
        "journey",
        lambda cmd: _journey_command(cmd, journey_manager, journal_manager),
    )
    handler.register_command(
        "progress",
        lambda cmd: _progress_command(cmd, journey_manager, journal_manager),
    )
    handler.register_command(
        "stop",
        lambda cmd: _stop_journey_command(cmd, journey_manager, journal_manager),
    )
    # Register new game command with confirmation flow
    handler.register_command(
        "new",
        lambda cmd: _new_game_command(
            cmd, game_manager, journey_manager, journal_manager, handler
        ),
    )
    # Register game management commands
    handler.register_command(
        "list", lambda cmd: _list_games_command(cmd, game_manager)
    )
    handler.register_command(
        "select", lambda cmd: _select_game_command(cmd, game_manager, journey_manager, journal_manager)
    )
    handler.register_command(
        "session", lambda cmd: _session_command(cmd, game_manager)
    )
    # Register fate command for decision making
    handler.register_command("fate", _fate_command)
    # Register journal command to view entries
    handler.register_command(
        "journal", lambda cmd: _journal_command(cmd, journal_manager)
    )
    # Register player creation command
    handler.register_command(
        "create_player",
        lambda cmd: _create_player_command(cmd, game_manager, handler),
    )

    return handler


def _roll_dice_command(command):
    """Roll dice command - example: roll 2d6 or roll d20 [advantage|disadvantage]."""
    import random

    if not command.args:
        return {
            "success": False,
            "message": "Usage: roll <dice> [advantage|disadvantage] (e.g., 'roll 2d6', 'roll d20 advantage')",
            "exit": False,
        }

    dice_notation = command.args[0].lower()

    # Check for advantage/disadvantage modifier
    advantage_mode = None
    if len(command.args) > 1:
        modifier = command.args[1].lower()
        if modifier in ["advantage", "adv", "a"]:
            advantage_mode = "advantage"
        elif modifier in ["disadvantage", "disadv", "d"]:
            advantage_mode = "disadvantage"
        else:
            return {
                "success": False,
                "message": (
                    f"Invalid modifier '{command.args[1]}'. "
                    "Use 'advantage', 'adv', 'a' or 'disadvantage', "
                    "'disadv', 'd'"
                ),
                "exit": False,
            }

    try:
        if "d" not in dice_notation:
            return {
                "success": False,
                "message": "Invalid dice notation. Use format like '2d6' or 'd20'",
                "exit": False,
            }

        if dice_notation.startswith("d"):
            # Handle 'd20' format (single die)
            num_dice = 1
            sides = int(dice_notation[1:])
        else:
            # Handle '2d6' format (multiple dice)
            parts = dice_notation.split("d")
            num_dice = int(parts[0])
            sides = int(parts[1])

        if num_dice <= 0 or sides <= 0:
            raise ValueError("Dice count and sides must be positive")

        if num_dice > 100:
            return {
                "success": False,
                "message": "Too many dice! Maximum is 100 dice per roll.",
                "exit": False,
            }

        if advantage_mode:
            # Roll two sets of dice for advantage/disadvantage
            rolls1 = [random.randint(1, sides) for _ in range(num_dice)]
            rolls2 = [random.randint(1, sides) for _ in range(num_dice)]
            total1 = sum(rolls1)
            total2 = sum(rolls2)

            if advantage_mode == "advantage":
                chosen_total = max(total1, total2)
            else:  # disadvantage
                chosen_total = min(total1, total2)

            if num_dice == 1:
                # Always display the rolls in descending order (highest first)
                rolls = sorted([total1, total2], reverse=True)
                message = (
                    f"Rolled {dice_notation} ({advantage_mode}): "
                    f"{rolls[0]}, {rolls[1]} => {chosen_total}"
                )
            else:
                # Determine which roll set is chosen and display accordingly
                if (advantage_mode == "advantage" and total1 >= total2) or (
                    advantage_mode == "disadvantage" and total1 <= total2
                ):
                    chosen_rolls, chosen_total_val = rolls1, total1
                    other_rolls, other_total_val = rolls2, total2
                else:
                    chosen_rolls, chosen_total_val = rolls2, total2
                    other_rolls, other_total_val = rolls1, total1

                message = (
                    f"Rolled {dice_notation} ({advantage_mode}): "
                    f"{chosen_rolls} = {chosen_total_val}, {other_rolls} = {other_total_val} => {chosen_total}"
                )
        else:
            # Normal roll
            rolls = [random.randint(1, sides) for _ in range(num_dice)]
            total = sum(rolls)

            if num_dice == 1:
                message = f"Rolled {dice_notation}: {total}"
            else:
                message = f"Rolled {dice_notation}: {rolls} = {total}"

        return {"success": True, "message": message, "exit": False}

    except ValueError as e:
        return {
            "success": False,
            "message": f"Invalid dice notation '{dice_notation}': {str(e)}",
            "exit": False,
        }


def _status_command(command, journey_manager, game_manager):
    """Show current game status."""
    from lib.player_manager import PlayerManager

    status_lines = [
        "Current Status:",
        "  Health: 100/100",
        "  Mana: 50/50",
        "  Level: 1",
        "  Location: Starting Town",
    ]

    # Add player information if game is selected
    current_game = game_manager.get_current_game()
    if current_game:
        game_path = game_manager.get_game_path(current_game)
        player_manager = PlayerManager(game_path)
        player_count = player_manager.get_player_count()

        if player_count > 0:
            status_lines.append(f"\nParty Members ({player_count}):")
            players = player_manager.get_all_players()
            for i, player in enumerate(players, 1):
                status_lines.append(f"  {i}. {player.name} (no class)")

    # Add journey information if there are active journeys
    if journey_manager.has_active_journeys():
        status_lines.append("\nActive Journeys:")
        journeys = journey_manager.get_all_journeys()
        for i, journey in enumerate(journeys, 1):
            status_lines.append(
                f"  {i}. {journey.name} ({journey.progress}/{journey.total_steps}) - {journey.difficulty}"
            )

    return {
        "success": True,
        "message": "\n".join(status_lines),
        "exit": False,
    }


def _save_command(command, journey_manager, game_manager):
    """Save game state to YAML file."""
    save_name = command.args[0] if command.args else "quicksave"

    # Get StateManager for current game
    current_game = game_manager.get_current_game()
    if not current_game:
        return {
            "success": False,
            "message": "No game selected. Use 'new' or 'select' to choose a game.",
            "exit": False,
        }

    game_path = game_manager.get_game_path(current_game)
    game_saves_dir = game_path / "saves"
    state_manager = StateManager(str(game_saves_dir))

    try:
        message = state_manager.save_state(journey_manager, save_name)
        return {"success": True, "message": message, "exit": False}
    except (ValueError, OSError) as e:
        return {"success": False, "message": f"Save failed: {e}", "exit": False}


def _load_command(command, journey_manager, game_manager):
    """Load game state from YAML file."""
    if not command.args:
        return {"success": False, "message": "Usage: load <save_name>", "exit": False}

    save_name = command.args[0]

    # Get StateManager for current game
    current_game = game_manager.get_current_game()
    if not current_game:
        return {
            "success": False,
            "message": "No game selected. Use 'new' or 'select' to choose a game.",
            "exit": False,
        }

    game_path = game_manager.get_game_path(current_game)
    game_saves_dir = game_path / "saves"
    state_manager = StateManager(str(game_saves_dir))

    try:
        # Load the new state
        new_journey_manager = state_manager.load_state(save_name)

        # Replace the current journey manager's state
        journey_manager._journeys = new_journey_manager._journeys

        # Get status for confirmation
        if journey_manager.has_active_journeys():
            status = journey_manager.get_status_summary()
            message = f"Game loaded from '{save_name}'\n\n{status}"
        else:
            message = f"Game loaded from '{save_name}' (no active journeys)"

        return {"success": True, "message": message, "exit": False}
    except (FileNotFoundError, ValueError, OSError) as e:
        return {"success": False, "message": f"Load failed: {e}", "exit": False}


def _saves_command(command, game_manager):
    """List available save files."""
    # Get StateManager for current game
    current_game = game_manager.get_current_game()
    if not current_game:
        return {
            "success": False,
            "message": "No game selected. Use 'new' or 'select' to choose a game.",
            "exit": False,
        }

    game_path = game_manager.get_game_path(current_game)
    game_saves_dir = game_path / "saves"
    state_manager = StateManager(str(game_saves_dir))

    try:
        saves = state_manager.list_saves()
        if not saves:
            return {"success": True, "message": "No saved games found.", "exit": False}

        message_lines = ["Available saves:"]
        for save_name in saves:
            try:
                info = state_manager.get_save_info(save_name)
                timestamp = info.get("timestamp", "unknown")
                journey_count = info.get("journey_count", 0)
                if timestamp != "unknown" and timestamp:
                    # Format timestamp to be more readable
                    try:
                        from datetime import datetime

                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass  # Keep original timestamp if parsing fails

                journey_text = (
                    f"{journey_count} journey{'s' if journey_count != 1 else ''}"
                )
                message_lines.append(f"  {save_name} - {timestamp} ({journey_text})")
            except:
                # If we can't get info, just show the name
                message_lines.append(f"  {save_name}")

        return {"success": True, "message": "\n".join(message_lines), "exit": False}
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to list saves: {e}",
            "exit": False,
        }


def _journey_command(command, journey_manager, journal_manager=None):
    """Start a new journey - example: journey "Find the lost treasure" 5 2."""
    if len(command.args) < 3:
        return {
            "success": False,
            "message": 'Usage: journey "name" <steps> <difficulty>\nExample: journey "Find the treasure" 5 2',
            "exit": False,
        }

    # Parse arguments
    name = command.args[0].strip("\"'")  # Remove quotes if present

    try:
        steps = int(command.args[1])
        if steps <= 0:
            raise ValueError("Steps must be a positive number")
    except ValueError:
        return {
            "success": False,
            "message": "Steps must be a positive number",
            "exit": False,
        }

    try:
        difficulty = int(command.args[2])
        if difficulty < 0:
            raise ValueError("Difficulty must be 0 or positive")
    except ValueError:
        return {
            "success": False,
            "message": "Difficulty must be 0 or a positive number",
            "exit": False,
        }

    try:
        journey_manager.start_journey(name, steps, difficulty)
        
        # Log to journal if available
        if journal_manager:
            journal_manager.add_entry(
                event_type="journey_start",
                description=f"Started journey: '{name}'",
                metadata={
                    "journey_name": name,
                    "total_steps": steps,
                    "difficulty": difficulty,
                },
            )
        
        return {
            "success": True,
            "message": f"Started journey: '{name}' ({steps} steps, {difficulty} difficulty)",
            "exit": False,
        }
    except ValueError as e:
        return {
            "success": False,
            "message": str(e),
            "exit": False,
        }


def _new_game_command(
    command, game_manager, journey_manager, journal_manager, handler
):
    """Start a new game.

    Behavior:
    - `new <game_name>` starts a new game
    - If current game has unsaved changes, prompt for confirmation
    - If confirmed: reset current game to new initial state
    - If not confirmed: ignore the request
    """
    # Handle case where no game name provided
    if not command.args or len(command.args) < 1:
        return {
            "success": False,
            "message": "Usage: new <game_name>\nExample: new dnd_friends_of_the_obelisk",
            "exit": False,
        }

    game_name = command.args[0]

    # Check if we need to confirm unsaved changes
    current_game = game_manager.get_current_game()
    game_info = (
        game_manager.get_game_info(current_game) if current_game else None
    )
    has_unsaved = (
        game_info and game_info.get("current_session_unsaved", False)
    )

    # If there are unsaved changes and this is not a confirmed request
    if has_unsaved and not hasattr(handler, "_pending_new_game"):
        handler._pending_new_game = True
        handler._pending_new_game_name = game_name
        return {
            "success": True,
            "message": "You might have unsaved changes to the current game. Continue? (yes/no)",
            "exit": False,
        }

    # Check for "yes" confirmation
    if hasattr(handler, "_pending_new_game") and handler._pending_new_game:
        if command.raw_input.strip().lower() != "yes":
            handler._pending_new_game = False
            return {
                "success": True,
                "message": "You did not confirm. Ignoring the request for a new game.",
                "exit": False,
            }
        # User confirmed, proceed with new game
        game_name = handler._pending_new_game_name
        handler._pending_new_game = False
        handler._pending_new_game_name = None

    # Try to create or load the game
    games = game_manager.list_games()
    if game_name in games:
        # Load existing game
        success, message = game_manager.load_game(game_name)
        if not success:
            return {"success": False, "message": message, "exit": False}
        # Mark game as saved (fresh load)
        game_manager.update_game_metadata(game_name, current_session_unsaved=False)
        # Clear journeys for new session but reload the game's journal
        journey_manager.stop_all_journeys()
        # Set journal path to game's journal
        game_path = game_manager.get_game_path(game_name)
        journal_path = game_path / "journal.yaml"
        journal_manager.set_journal_path(str(journal_path))
        # Load the game's quicksave if available
        import yaml
        try:
            quicksave_path = game_path / "saves" / "quicksave.yaml"
            if quicksave_path.exists():
                with open(quicksave_path, "r") as f:
                    state_data = yaml.safe_load(f)
                if state_data and isinstance(state_data, dict):
                    if "journey_manager" in state_data:
                        restored_manager = JourneyManager.from_dict(
                            state_data["journey_manager"]
                        )
                        # Replace journey manager's journeys with restored ones
                        journey_manager._journeys = restored_manager._journeys
        except (OSError, ValueError, KeyError, AttributeError):
            # If loading fails, continue with empty journey manager
            pass
    else:
        # Create new game
        success, message = game_manager.create_game(game_name)
        if not success:
            return {"success": False, "message": message, "exit": False}
        # Clear journeys and reset journal for new game
        journey_manager.stop_all_journeys()
        journal_manager.clear_journal()
        # Set journal path to game's journal
        game_path = game_manager.get_game_path(game_name)
        journal_path = game_path / "journal.yaml"
        journal_manager.set_journal_path(str(journal_path))

    return {
        "success": True,
        "message": f"Game '{game_name}' loaded/created. Ready to play!",
        "exit": False,
    }


def _list_games_command(command, game_manager):
    """List all available games.

    Usage: list
    """
    games = game_manager.list_games()

    if not games:
        return {
            "success": True,
            "message": "No games found. Create one with: new <game_name>",
            "exit": False,
        }

    current = game_manager.get_current_game()
    lines = ["Available games:"]

    for i, game_name in enumerate(games, 1):
        info = game_manager.get_game_info(game_name)
        if info:
            sessions = info.get("total_sessions", 0)
            current_marker = " (current)" if game_name == current else ""
            lines.append(
                f"  {i}. {game_name} - {sessions} sessions{current_marker}"
            )
        else:
            lines.append(f"  {i}. {game_name}")

    return {
        "success": True,
        "message": "\n".join(lines),
        "exit": False,
    }


def _select_game_command(command, game_manager, journey_manager, journal_manager):
    """Switch to a different game.

    Usage: select <game_name>
    Example: select dnd_friends
    """
    if not command.args or len(command.args) < 1:
        games = game_manager.list_games()
        if not games:
            return {
                "success": False,
                "message": "No games available. Create one with: new <game_name>",
                "exit": False,
            }
        games_list = ", ".join(games)
        return {
            "success": False,
            "message": f"Usage: select <game_name>\nAvailable: {games_list}",
            "exit": False,
        }

    game_name = command.args[0]
    success, message = game_manager.set_current_game(game_name)

    if not success:
        return {"success": False, "message": message, "exit": False}

    # Update journal path to the selected game's journal
    game_path = game_manager.get_game_path(game_name)
    journal_path = game_path / "journal.yaml"
    journal_manager.set_journal_path(str(journal_path))

    # Load the game's quicksave if available
    import yaml
    try:
        quicksave_path = game_path / "saves" / "quicksave.yaml"
        if quicksave_path.exists():
            with open(quicksave_path, "r") as f:
                state_data = yaml.safe_load(f)
            if state_data and isinstance(state_data, dict):
                if "journey_manager" in state_data:
                    restored_manager = JourneyManager.from_dict(
                        state_data["journey_manager"]
                    )
                    # Replace journey manager's journeys with restored ones
                    journey_manager._journeys = restored_manager._journeys
    except (OSError, ValueError, KeyError, AttributeError):
        # If loading fails, continue with empty journey manager
        pass

    return {
        "success": True,
        "message": f"Switched to game '{game_name}'",
        "exit": False,
    }


def _session_command(command, game_manager):
    """Show current game session information.

    Usage: session
    """
    current = game_manager.get_current_game()

    if not current:
        return {
            "success": True,
            "message": "No game loaded. Create one with: new <game_name>",
            "exit": False,
        }

    info = game_manager.get_game_info(current)

    if not info:
        return {
            "success": False,
            "message": f"Could not load info for game '{current}'",
            "exit": False,
        }

    unsaved_status = "Yes" if info.get("current_session_unsaved") else "No"
    sessions = info.get("total_sessions", 0)

    message = (
        f"Current Game: {info['name']}\n"
        f"  Created: {info.get('created_at', 'unknown')}\n"
        f"  Last Modified: {info.get('last_modified', 'unknown')}\n"
        f"  Total Sessions: {sessions}\n"
        f"  Unsaved Changes: {unsaved_status}"
    )

    return {
        "success": True,
        "message": message,
        "exit": False,
    }


def _progress_command(command, journey_manager, journal_manager=None):
    """Make progress on the current journey - example: progress 2."""
    if not journey_manager.has_active_journeys():
        return {
            "success": False,
            "message": 'No active journeys. Start one with: journey "name" <steps> <difficulty>',
            "exit": False,
        }

    # Default to 1 step if no argument provided
    steps = 1
    if command.args:
        try:
            steps = int(command.args[0])
            if steps <= 0:
                raise ValueError("Steps must be a positive number")
        except ValueError:
            return {
                "success": False,
                "message": "Steps must be a positive number",
                "exit": False,
            }

    try:
        # Get current journey before making progress (it might be removed if completed)
        current_journey = journey_manager.current_journey
        journey_name = current_journey.name if current_journey else "Unknown"
        
        result = journey_manager.make_progress(steps)
        
        # Log to journal if available
        if journal_manager and current_journey:
            journal_manager.add_entry(
                event_type="journey_progress",
                description=f"Made {steps} step(s) on '{journey_name}'",
                metadata={
                    "journey_name": journey_name,
                    "progress_amount": steps,
                    "current_progress": current_journey.progress,
                    "total_steps": current_journey.total_steps,
                },
            )
        
        return {
            "success": True,
            "message": result,
            "exit": False,
        }
    except ValueError as e:
        return {
            "success": False,
            "message": str(e),
            "exit": False,
        }


def _stop_journey_command(command, journey_manager, journal_manager=None):
    """Stop the current journey."""
    if not journey_manager.has_active_journeys():
        return {
            "success": False,
            "message": "No active journeys to stop",
            "exit": False,
        }

    try:
        stopped_journey = journey_manager.stop_current_journey()
        
        # Log to journal if available
        if journal_manager:
            journal_manager.add_entry(
                event_type="journey_stop",
                description=f"Completed journey: '{stopped_journey.name}'",
                metadata={
                    "journey_name": stopped_journey.name,
                    "final_progress": stopped_journey.progress,
                    "total_steps": stopped_journey.total_steps,
                    "difficulty": stopped_journey.difficulty,
                },
            )

        return {
            "success": True,
            "message": (
                f"Stopped journey: '{stopped_journey.name}' "
                f"(was {stopped_journey.progress}/{stopped_journey.total_steps})"
            ),
            "exit": False,
        }
    except ValueError as e:
        return {
            "success": False,
            "message": str(e),
            "exit": False,
        }


def _fate_command(command):
    """Fate command for on-the-fly decision making.

    Usage: fate option1,option2[,option3...]

    Example: fate safe,encounter
    Rolls a d100 and selects one of the options with equal probability.
    """
    import random

    if not command.args:
        return {
            "success": False,
            "message": (
                "Usage: fate <option1>,<option2>[,<option3>...]\n"
                "Example: fate safe,encounter"
            ),
            "exit": False,
        }

    # Parse the options - they are comma-separated
    options_str = command.args[0]
    options = [opt.strip() for opt in options_str.split(",")]

    # Validate we have at least 2 options
    if len(options) < 2:
        return {
            "success": False,
            "message": (
                "Fate requires at least 2 options separated by commas\n"
                "Example: fate safe,encounter"
            ),
            "exit": False,
        }

    # Remove empty strings from options
    options = [opt for opt in options if opt]

    if len(options) < 2:
        return {
            "success": False,
            "message": (
                "Fate requires at least 2 options separated by commas\n"
                "Example: fate safe,encounter"
            ),
            "exit": False,
        }

    # Roll d100 to select an option
    d100_roll = random.randint(1, 100)

    # Calculate probability per option and which one was selected
    probability_per_option = 100 / len(options)
    selected_index = min(
        int((d100_roll - 1) / probability_per_option), len(options) - 1
    )
    selected_option = options[selected_index]

    # Format the probability display for each option
    probability_str = f"{probability_per_option:.0f}%"
    probabilities = ", ".join([f"{opt} ({probability_str})" for opt in options])

    message = (
        f"Fate checked: {probabilities} => d100 => {d100_roll} => "
        f"{selected_option}"
    )

    return {
        "success": True,
        "message": message,
        "exit": False,
    }


def _journal_command(command, journal_manager):
    """Display the journal entries."""
    # Parse optional limit argument
    limit = 10
    if command.args:
        try:
            limit = int(command.args[0])
            if limit <= 0:
                return {
                    "success": False,
                    "message": "Limit must be a positive number",
                    "exit": False,
                }
        except ValueError:
            return {
                "success": False,
                "message": "Usage: journal [limit]\nExample: journal 10 (shows last 10 entries, default)",
                "exit": False,
            }

    entries = journal_manager.get_entries(limit)

    if not entries:
        return {
            "success": True,
            "message": "Journal is empty. Start a journey to record events!",
            "exit": False,
        }

    # Format the output
    output_lines = ["Journal Entries:\n"]
    for i, entry in enumerate(entries, 1):
        timestamp = entry.get("timestamp", "Unknown")
        description = entry.get("description", "")
        output_lines.append(f"{i}. [{timestamp}] {description}")

    message = "\n".join(output_lines)

    return {
        "success": True,
        "message": message,
        "exit": False,
    }


def _create_player_command(command, game_manager, handler):
    """Create a new player character in the current game."""
    current_game = game_manager.get_current_game()

    if not current_game:
        return {
            "success": False,
            "message": "No game selected. Use 'select <game_name>' to select a game first.",
            "exit": False,
        }

    # Initialize player creation handler
    player_handler = PlayerCreationHandler(game_manager, current_game)

    # Show welcome message
    welcome_message = (
        f"Starting player creation for game '{current_game}'.\n"
        "Type 'help' for available commands.\n\n"
        "Enter player name: "
    )

    return {
        "success": True,
        "message": welcome_message,
        "exit": False,
        "context": player_handler,  # Store context for next iteration
        "mode": "player_creation",  # Signal we're entering player creation mode
    }
