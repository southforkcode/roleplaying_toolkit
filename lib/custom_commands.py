"""Example of extending the command handler with custom commands."""

from lib.command_handler import CommandHandler

def create_extended_command_handler():
    """Create a command handler with additional custom commands."""
    handler = CommandHandler()
    
    # Register custom commands
    handler.register_command("roll", _roll_dice_command)
    handler.register_command("status", _status_command)
    handler.register_command("save", _save_command)
    handler.register_command("load", _load_command)
    
    return handler

def _roll_dice_command(command):
    """Roll dice command - example: roll 2d6 or roll d20."""
    import random
    
    if not command.args:
        return {
            "success": False,
            "message": "Usage: roll <dice> (e.g., 'roll 2d6' or 'roll d20')",
            "exit": False
        }
    
    dice_notation = command.args[0].lower()
    
    try:
        if 'd' not in dice_notation:
            return {
                "success": False,
                "message": "Invalid dice notation. Use format like '2d6' or 'd20'",
                "exit": False
            }
        
        if dice_notation.startswith('d'):
            # Handle 'd20' format (single die)
            num_dice = 1
            sides = int(dice_notation[1:])
        else:
            # Handle '2d6' format (multiple dice)
            parts = dice_notation.split('d')
            num_dice = int(parts[0])
            sides = int(parts[1])
        
        if num_dice <= 0 or sides <= 0:
            raise ValueError("Dice count and sides must be positive")
        
        if num_dice > 100:
            return {
                "success": False,
                "message": "Too many dice! Maximum is 100 dice per roll.",
                "exit": False
            }
        
        # Roll the dice
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        total = sum(rolls)
        
        if num_dice == 1:
            message = f"Rolled {dice_notation}: {total}"
        else:
            message = f"Rolled {dice_notation}: {rolls} = {total}"
        
        return {
            "success": True,
            "message": message,
            "exit": False
        }
        
    except ValueError as e:
        return {
            "success": False,
            "message": f"Invalid dice notation '{dice_notation}': {str(e)}",
            "exit": False
        }

def _status_command(command):
    """Show current game status."""
    # This would integrate with the state manager in a real implementation
    return {
        "success": True,
        "message": "Current Status:\n  Health: 100/100\n  Mana: 50/50\n  Level: 1\n  Location: Starting Town",
        "exit": False
    }

def _save_command(command):
    """Save game state."""
    save_name = command.args[0] if command.args else "quicksave"
    
    # This would integrate with actual save/load functionality
    return {
        "success": True,
        "message": f"Game saved as '{save_name}'",
        "exit": False
    }

def _load_command(command):
    """Load game state."""
    if not command.args:
        return {
            "success": False,
            "message": "Usage: load <save_name>",
            "exit": False
        }
    
    save_name = command.args[0]
    
    # This would integrate with actual save/load functionality
    return {
        "success": True,
        "message": f"Game loaded from '{save_name}'",
        "exit": False
    }