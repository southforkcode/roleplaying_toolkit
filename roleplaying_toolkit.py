from lib.statemgr import StateManager
from lib.custom_commands import create_extended_command_handler

def main():
    print("Welcome to the Roleplaying Toolkit!")
    print("Type 'help' for available commands or 'quit' to exit.")
    print("Try commands like: roll d20, status, save, load")

    state_manager = StateManager.get_instance()
    command_handler = create_extended_command_handler()

    exit_flag = False

    while not exit_flag:
        try:
            # Get user input
            user_input = input("> ").strip()
            
            # Process the command
            result = command_handler.process_input(user_input)
            
            # Display result message if there is one
            if result.get("message"):
                print(result["message"])
            
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
