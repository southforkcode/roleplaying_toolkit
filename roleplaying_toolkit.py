"""Main entry point for the Roleplaying Toolkit."""

from lib.custom_commands import create_extended_command_handler


def main():
    """Run the main Roleplaying Toolkit application."""
    print("Welcome to the Roleplaying Toolkit!")
    print("Type 'help' for available commands or 'quit' to exit.")
    print("Try commands like: roll d20, status, save, load")

    command_handler = create_extended_command_handler()
    current_context = None  # Track the current context handler
    context_name = None  # Track the name of the current context
    context_mode = None  # Track the mode (player_creation, template_player_creation, etc)

    exit_flag = False

    while not exit_flag:
        try:
            # Get user input with appropriate prompt
            if current_context is not None:
                prompt = f"{context_name}> "
            else:
                prompt = "> "

            user_input = input(prompt).strip()

            # If in a context, use the context handler; otherwise use main handler
            if current_context is not None:
                # Handle special 'save' command for template-based creation
                if (user_input.lower() == "save" 
                        and context_mode == "template_player_creation"):
                    # Save template-created player
                    from lib.game_manager import GameManager
                    game_manager = GameManager()
                    current_game = game_manager.get_current_game()
                    success, message = current_context.save_player(
                        game_manager, current_game
                    )
                    if success:
                        print(f"{context_name}: {message}")
                        current_context = None
                        context_name = None
                        context_mode = None
                    else:
                        print(f"{context_name}: {message}")
                    continue

                # Use the context's handle method
                result_message = current_context.handle(user_input)

                # Prefix the response with context name
                if result_message:
                    formatted_message = f"{context_name}: {result_message}"
                    print(formatted_message)

                # Check if context has been cleared (player saved/exited)
                if (hasattr(current_context, 'context')
                        and current_context.context.player is None):
                    # Check if message indicates we should exit context
                    if ("Exited player creation" in result_message
                            or "Saved player" in result_message):
                        current_context = None
                        context_name = None
                        context_mode = None

                # Check for cancellation in template mode
                if (context_mode == "template_player_creation" 
                        and "cancelled" in result_message.lower()):
                    current_context = None
                    context_name = None
                    context_mode = None
            else:
                # Process the command normally
                result = command_handler.process_input(user_input)

                # Display result message if there is one
                if result.get("message"):
                    print(result["message"])

                # Check if result indicates we're entering a context
                if result.get("context") is not None:
                    current_context = result["context"]
                    context_mode = result.get("mode", "unknown")
                    
                    # Determine context name based on mode
                    if context_mode == "template_player_creation":
                        template_name = getattr(current_context, 'template', None)
                        if template_name and hasattr(template_name, 'name'):
                            context_name = f"create_player:{template_name.name}"
                        else:
                            context_name = "create_player:template"
                    elif context_mode == "player_creation":
                        context_name = "create_player"
                    else:
                        context_name = "context"

                # Check if we should exit
                if result.get("exit", False):
                    exit_flag = True

        except KeyboardInterrupt:
            print("\nExiting...")
            exit_flag = True
        except EOFError:
            print("\nExiting...")
            exit_flag = True


if __name__ == "__main__":
    main()
