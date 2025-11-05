"""Example of extending the command handler with custom commands."""

from lib.command_handler import CommandHandler
from lib.journey_system import JourneyManager
from lib.state_manager import StateManager
from lib.journal_manager import JournalManager


def create_extended_command_handler():
    """Create a command handler with additional custom commands."""
    handler = CommandHandler()

    # Initialize journey manager, state manager, and journal manager
    journey_manager = JourneyManager()
    state_manager = StateManager()
    journal_manager = JournalManager()

    # Register custom commands
    handler.register_command("roll", _roll_dice_command)
    handler.register_command(
        "status", lambda cmd: _status_command(cmd, journey_manager)
    )
    handler.register_command(
        "save", lambda cmd: _save_command(cmd, journey_manager, state_manager)
    )
    handler.register_command(
        "load", lambda cmd: _load_command(cmd, journey_manager, state_manager)
    )
    handler.register_command("saves", lambda cmd: _saves_command(cmd, state_manager))
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
    # Register new session command with confirmation flow
    handler.register_command(
        "new", lambda cmd: _new_command(cmd, journey_manager, handler)
    )
    # Register fate command for decision making
    handler.register_command("fate", _fate_command)
    # Register journal command to view entries
    handler.register_command(
        "journal", lambda cmd: _journal_command(cmd, journal_manager)
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


def _status_command(command, journey_manager):
    """Show current game status."""
    status_lines = [
        "Current Status:",
        "  Health: 100/100",
        "  Mana: 50/50",
        "  Level: 1",
        "  Location: Starting Town",
    ]

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


def _save_command(command, journey_manager, state_manager):
    """Save game state to YAML file."""
    save_name = command.args[0] if command.args else "quicksave"

    try:
        message = state_manager.save_state(journey_manager, save_name)
        return {"success": True, "message": message, "exit": False}
    except (ValueError, OSError) as e:
        return {"success": False, "message": f"Save failed: {e}", "exit": False}


def _load_command(command, journey_manager, state_manager):
    """Load game state from YAML file."""
    if not command.args:
        return {"success": False, "message": "Usage: load <save_name>", "exit": False}

    save_name = command.args[0]

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


def _saves_command(command, state_manager):
    """List available save files."""
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


def _new_command(command, journey_manager, handler):
    """Reset session state if user confirms by typing 'new' twice.

    Behavior:
    - If there are no active journeys, perform a no-op reset and inform the user.
    - If there are active journeys and this is the first 'new', ask for confirmation
      and set handler._pending_new = True.
    - If handler._pending_new is True and the user types 'new' again, clear all
      journeys and reset the confirmation flag.
    """
    # If no journeys are active, clear and return a message (no confirmation needed)
    if not journey_manager.has_active_journeys():
        # Ensure any pending flag is cleared
        if hasattr(handler, "_pending_new"):
            handler._pending_new = False
        return {
            "success": True,
            "message": "Session reset (no active journeys).",
            "exit": False,
        }

    # If confirmation pending and user typed 'new' again -> perform reset
    if hasattr(handler, "_pending_new") and handler._pending_new:
        journey_manager.stop_all_journeys()
        handler._pending_new = False
        return {
            "success": True,
            "message": "Session reset. All journeys cleared.",
            "exit": False,
        }

    # Otherwise, set pending confirmation and prompt the user
    if hasattr(handler, "_pending_new"):
        handler._pending_new = True

    return {
        "success": True,
        "message": "Type 'new' again to confirm resetting the session.",
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
