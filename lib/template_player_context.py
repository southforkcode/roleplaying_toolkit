"""Template-based player creation context and handler."""

from typing import Optional, Tuple

from lib.template import Template
from lib.template_macros import MacroProcessor
from lib.player import Player


class TemplatePlayerCreationHandler:
    """Manages interactive player creation using a template."""

    def __init__(self, template: Template, game_manager, main_handler=None):
        """Initialize template-based player creation handler.

        Args:
            template: Template to use for player creation
            game_manager: GameManager instance
            main_handler: Reference to main command handler for delegating dice rolls
        """
        self.template = template
        self.game_manager = game_manager
        self.main_handler = main_handler
        self.player: Optional[Player] = None
        self.current_step_index = 0
        self.answers: dict = {}  # Store answers indexed by step ID

    def get_welcome_message(self) -> str:
        """Get welcome message for template.

        Returns:
            Welcome message
        """
        msg = f"Starting player creation using template '{self.template.name}'.\n"
        msg += f"Description: {self.template.description}\n"
        msg += f"Total steps: {self.template.step_count()}\n"
        msg += "Type 'help' for available commands.\n"
        msg += "\n"

        current_step = self.get_current_step()
        if current_step:
            msg += f"{current_step.prompt}"
            if current_step.help:
                msg += f"\n({current_step.help})"

        return msg

    def get_current_step(self):
        """Get current template step.

        Returns:
            TemplateStep or None if at end
        """
        return self.template.get_step(self.current_step_index)

    def handle(self, input_str: str) -> str:
        """Handle player input during template-based creation.

        Args:
            input_str: User input

        Returns:
            Response message
        """
        input_str = input_str.strip()

        if not input_str:
            return "Enter a command or type 'help' for available commands"

        # Handle built-in commands
        if input_str.lower() == "help":
            return self._handle_help()
        elif input_str.lower() == "status":
            return self._handle_status()
        elif input_str.lower() == "back":
            return self._handle_back()
        elif input_str.lower() == "cancel":
            return self._handle_cancel()
        elif input_str.lower() == "show":
            return self._handle_show()

        # Handle template step input
        return self._handle_step_input(input_str)

    def _handle_step_input(self, input_str: str) -> str:
        """Handle input for current template step.

        Args:
            input_str: User input

        Returns:
            Response message
        """
        current_step = self.get_current_step()

        if not current_step:
            return "Template creation complete!"

        # For review steps, just show them and advance
        if current_step.type == "review":
            self.current_step_index += 1
            return self._advance_to_next_step()

        # For confirmation steps
        if current_step.type == "confirmation":
            if input_str.lower() == "yes":
                return self._handle_confirmation_yes(current_step)
            elif input_str.lower() == "no":
                return self._handle_confirmation_no(current_step)
            else:
                return "Please answer 'yes' or 'no'"

        # For regular steps, process input
        return self._process_step_answer(current_step, input_str)

    def _process_step_answer(self, step, input_str: str) -> str:
        """Process and validate answer for a step.

        Args:
            step: Current template step
            input_str: User input

        Returns:
            Response message
        """
        # Check if input is a macro
        if step.macros_enabled:
            macro = MacroProcessor.parse_macro(input_str)
            if macro:
                macro_type, params = macro
                success, value, message = MacroProcessor.execute(
                    macro_type, params
                )
                if success:
                    # If user confirmed with macro result, advance
                    self.answers[step.id] = value
                    self._apply_step_answer(step, value)
                    self.current_step_index += 1
                    return f"{message}\n\n{self._advance_to_next_step()}"
                else:
                    return f"Error: {message}\nPlease try again."

        # Try to parse as regular input
        success, value, error = self._validate_and_parse_answer(step, input_str)

        if not success:
            return f"Invalid input: {error}"

        # Store answer and apply to player
        self.answers[step.id] = value
        self._apply_step_answer(step, value)

        # Advance to next step
        self.current_step_index += 1
        return self._advance_to_next_step()

    def _validate_and_parse_answer(self, step, answer_str: str) -> Tuple[bool, any, str]:
        """Validate and parse answer for a step.

        Args:
            step: Template step
            answer_str: Answer string

        Returns:
            Tuple of (is_valid, parsed_value, error_message)
        """
        # Handle text inputs
        if step.type == "text":
            is_valid, error = step.validation.validate(answer_str)
            if not is_valid:
                return False, None, error
            return True, answer_str, None

        # Handle ability scores
        if step.type == "ability":
            try:
                value = int(answer_str)
                is_valid, error = step.validation.validate(value)
                if not is_valid:
                    return False, None, error
                return True, value, None
            except ValueError:
                return False, None, "Please enter a valid number"

        # Handle choice
        if step.type == "choice":
            if step.choices and answer_str not in step.choices:
                choices_str = ", ".join(step.choices)
                return False, None, f"Must be one of: {choices_str}"
            return True, answer_str, None

        return False, None, f"Unknown step type: {step.type}"

    def _apply_step_answer(self, step, value: any) -> None:
        """Apply step answer to player object.

        Args:
            step: Template step
            value: Validated answer value
        """
        if not self.player:
            self.player = Player("Unnamed")

        if not step.field:
            # Meta-step, no field to populate
            return

        # Handle different field types
        if step.type == "text" and step.field == "name":
            self.player.name = value
        elif step.type == "ability":
            # Map ability shorthand (str -> strength)
            ability_map = {
                "str": "strength",
                "dex": "dexterity",
                "con": "constitution",
                "int": "intelligence",
                "wis": "wisdom",
                "cha": "charisma",
            }
            ability = ability_map.get(step.field, step.field)
            self.player.set_ability(ability, value)
        else:
            # Generic field assignment
            setattr(self.player, step.field, value)

    def _advance_to_next_step(self) -> str:
        """Move to next step and return its prompt.

        Returns:
            Next step prompt or completion message
        """
        current_step = self.get_current_step()

        if not current_step:
            return self._get_completion_message()

        msg = current_step.prompt
        if current_step.help:
            msg += f"\n({current_step.help})"

        return msg

    def _get_completion_message(self) -> str:
        """Get message when all steps are complete.

        Returns:
            Completion message
        """
        if self.player:
            return (
                f"Player creation complete! '{self.player.name}' is ready.\n"
                "Use 'save' to save the character, or 'cancel' to discard."
            )
        return "Template creation complete!"

    def _handle_confirmation_yes(self, step) -> str:
        """Handle 'yes' response to confirmation step.

        Args:
            step: Confirmation step

        Returns:
            Response message
        """
        self.answers[step.id] = True
        self.current_step_index += 1
        return self._advance_to_next_step()

    def _handle_confirmation_no(self, step) -> str:
        """Handle 'no' response to confirmation step.

        Args:
            step: Confirmation step

        Returns:
            Response message
        """
        self.answers[step.id] = False
        self.current_step_index += 1
        return self._advance_to_next_step()

    def _handle_back(self) -> str:
        """Go back to previous step.

        Returns:
            Previous step or error message
        """
        if self.current_step_index > 0:
            self.current_step_index -= 1
            return self._advance_to_next_step()
        return "Already at first step"

    def _handle_cancel(self) -> str:
        """Cancel player creation.

        Returns:
            Cancellation message
        """
        self.player = None
        self.answers = {}
        return "Player creation cancelled."

    def _handle_status(self) -> str:
        """Show current player status.

        Returns:
            Status message
        """
        if not self.player:
            return "No player created yet"

        lines = [f"Player: {self.player.name}"]

        # Show answered steps so far
        for i in range(min(self.current_step_index + 1, self.template.step_count())):
            step = self.template.get_step(i)
            if step and step.id in self.answers:
                lines.append(f"  {step.id}: {self.answers[step.id]}")

        return "\n".join(lines)

    def _handle_help(self) -> str:
        """Show help message.

        Returns:
            Help message
        """
        help_lines = [
            "Template Player Creation Commands:",
            "  <answer>        - Answer the current step",
            "  @roll d20       - Roll dice (if enabled for this step)",
            "  @roll-top 3 4d6 - Roll 4d6, keep top 3",
            "  @sum 10+5       - Calculate sum",
            "  status          - Show current player status",
            "  show            - Show current step details",
            "  back            - Go to previous step",
            "  cancel          - Cancel without saving",
            "  help            - Show this help message",
        ]
        return "\n".join(help_lines)

    def _handle_show(self) -> str:
        """Show current step details.

        Returns:
            Step details
        """
        current_step = self.get_current_step()
        if not current_step:
            return "No more steps"

        lines = [
            f"Step {self.current_step_index + 1} of {self.template.step_count()}",
            f"ID: {current_step.id}",
            f"Type: {current_step.type}",
            f"Prompt: {current_step.prompt}",
        ]

        if current_step.help:
            lines.append(f"Help: {current_step.help}")

        if current_step.choices:
            lines.append(f"Choices: {', '.join(current_step.choices)}")

        if current_step.macros_enabled:
            lines.append("Macros enabled: @roll, @roll-top, @sum")

        return "\n".join(lines)

    def save_player(self, game_manager, game_name: str) -> Tuple[bool, str]:
        """Save the player to the game.

        Args:
            game_manager: GameManager instance
            game_name: Name of game to save to

        Returns:
            Tuple of (success, message)
        """
        if not self.player or not self.player.name:
            return False, "Cannot save: no player created"

        try:
            from lib.player_manager import PlayerManager
            from pathlib import Path

            game_path = game_manager.get_game_path(game_name)
            player_manager = PlayerManager(game_path)

            success, message = player_manager.save_player(self.player)
            return success, message

        except Exception as e:
            return False, f"Error saving player: {e}"
