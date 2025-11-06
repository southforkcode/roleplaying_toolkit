"""Main entry point for the Roleplaying Toolkit."""

from lib.custom_commands import create_extended_command_handler


def main():
    """Run the main Roleplaying Toolkit application."""
    print("Welcome to the Roleplaying Toolkit!")
    print("Type 'help' for available commands or 'quit' to exit.")
    print("Try commands like: roll d20, status, save, load")

    command_handler = create_extended_command_handler()
    current_context = None  # Track the current context handler

    exit_flag = False

    while not exit_flag:
        try:
            # Get user input
            user_input = input("> ").strip()

            # If in a context, use the context handler; otherwise use main handler
            if current_context is not None:
                # Use the context's handle method
                result_message = current_context.handle(user_input)
                print(result_message)

                # Check if context has been cleared (player saved/exited)
                if (hasattr(current_context, 'context')
                        and current_context.context.player is None):
                    # Check if message indicates we should exit context
                    if ("Exited player creation" in result_message
                            or "Saved player" in result_message):
                        current_context = None
            else:
                # Process the command normally
                result = command_handler.process_input(user_input)

                # Display result message if there is one
                if result.get("message"):
                    print(result["message"])

                # Check if result indicates we're entering a context
                if result.get("context") is not None:
                    current_context = result["context"]

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
