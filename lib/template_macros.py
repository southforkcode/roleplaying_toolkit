"""Macro system for template-based player creation."""

import random
import re
from typing import Optional, Tuple, Union


class MacroProcessor:
    """Processes and executes macros in template inputs."""

    # Macro patterns
    ROLL_TOP_PATTERN = re.compile(
        r"@roll-top\s+(\d+)\s+(\d+)d(\d+)(?:\+(\d+))?(?:\-(\d+))?", re.IGNORECASE
    )
    ROLL_PATTERN = re.compile(
        r"@roll\s+(\d+)?d(\d+)(?:\+(\d+))?(?:\-(\d+))?", re.IGNORECASE
    )
    SUM_PATTERN = re.compile(r"@sum\s+([\d\s\+\-]+)", re.IGNORECASE)

    @staticmethod
    def parse_macro(input_str: str) -> Optional[Tuple[str, dict]]:
        """Parse a macro from input string.

        Args:
            input_str: User input that may contain a macro

        Returns:
            Tuple of (macro_type, parameters) or None if no macro found

        Macro Types:
            - 'roll_top': {'num_dice': int, 'dice_size': int, 'keep': int, 'modifier': int}
            - 'roll': {'num_dice': int, 'dice_size': int, 'modifier': int}
            - 'sum': {'values': str}
        """
        input_str = input_str.strip()

        # Check for roll-top macro
        match = MacroProcessor.ROLL_TOP_PATTERN.match(input_str)
        if match:
            keep = int(match.group(1))
            num_dice = int(match.group(2))
            dice_size = int(match.group(3))
            plus_mod = int(match.group(4)) if match.group(4) else 0
            minus_mod = int(match.group(5)) if match.group(5) else 0
            modifier = plus_mod - minus_mod

            return "roll_top", {
                "keep": keep,
                "num_dice": num_dice,
                "dice_size": dice_size,
                "modifier": modifier,
            }

        # Check for roll macro
        match = MacroProcessor.ROLL_PATTERN.match(input_str)
        if match:
            num_dice = int(match.group(1)) if match.group(1) else 1
            dice_size = int(match.group(2))
            plus_mod = int(match.group(3)) if match.group(3) else 0
            minus_mod = int(match.group(4)) if match.group(4) else 0
            modifier = plus_mod - minus_mod

            return "roll", {
                "num_dice": num_dice,
                "dice_size": dice_size,
                "modifier": modifier,
            }

        # Check for sum macro
        match = MacroProcessor.SUM_PATTERN.match(input_str)
        if match:
            return "sum", {"values_str": match.group(1)}

        return None

    @staticmethod
    def execute(
        macro_type: str, params: dict
    ) -> Tuple[bool, Union[int, str], str]:
        """Execute a macro.

        Args:
            macro_type: Type of macro to execute
            params: Macro parameters

        Returns:
            Tuple of (success, result_value, message)
                result_value: int if successful, str with error if failed
                message: Human-readable message describing the result
        """
        if macro_type == "roll_top":
            return MacroProcessor._execute_roll_top(params)
        elif macro_type == "roll":
            return MacroProcessor._execute_roll(params)
        elif macro_type == "sum":
            return MacroProcessor._execute_sum(params)
        else:
            return False, "Unknown macro type", f"Unknown macro type: {macro_type}"

    @staticmethod
    def _execute_roll_top(params: dict) -> Tuple[bool, Union[int, str], str]:
        """Execute @roll-top macro.

        Example: @roll-top 3 4d6 (roll 4d6, keep top 3)
        """
        keep = params.get("keep", 0)
        num_dice = params.get("num_dice", 1)
        dice_size = params.get("dice_size", 20)
        modifier = params.get("modifier", 0)

        # Validate parameters
        if keep <= 0 or keep > num_dice:
            return (
                False,
                "Invalid parameters",
                f"Must keep between 1 and {num_dice} dice",
            )

        if num_dice > 100:
            return False, "Too many dice", "Cannot roll more than 100 dice"

        # Roll the dice
        rolls = [random.randint(1, dice_size) for _ in range(num_dice)]
        rolls_sorted = sorted(rolls, reverse=True)
        kept_rolls = rolls_sorted[:keep]
        total = sum(kept_rolls) + modifier

        # Format message
        rolls_str = ", ".join(str(r) for r in rolls)
        kept_str = ", ".join(str(r) for r in kept_rolls)
        if modifier > 0:
            modifier_str = f" + {modifier}"
        elif modifier < 0:
            modifier_str = f" - {abs(modifier)}"
        else:
            modifier_str = ""
        message = (
            f"Rolled {num_dice}d{dice_size} (keep top {keep}): "
            f"[{rolls_str}] → [{kept_str}] = {sum(kept_rolls)}{modifier_str} = {total}"
        )

        return True, total, message

    @staticmethod
    def _execute_roll(params: dict) -> Tuple[bool, Union[int, str], str]:
        """Execute @roll macro.

        Example: @roll d20 (roll 1d20)
        Example: @roll 2d6+3 (roll 2d6 and add 3)
        """
        num_dice = params.get("num_dice", 1)
        dice_size = params.get("dice_size", 20)
        modifier = params.get("modifier", 0)

        # Validate parameters
        if num_dice > 100:
            return False, "Too many dice", "Cannot roll more than 100 dice"

        if dice_size > 1000:
            return False, "Invalid dice size", "Dice size must be <= 1000"

        # Roll the dice
        rolls = [random.randint(1, dice_size) for _ in range(num_dice)]
        total = sum(rolls) + modifier

        # Format message
        if num_dice == 1:
            rolls_str = str(rolls[0])
        else:
            rolls_str = ", ".join(str(r) for r in rolls)

        if modifier > 0:
            modifier_str = f" + {modifier}"
        elif modifier < 0:
            modifier_str = f" - {abs(modifier)}"
        else:
            modifier_str = ""
        message = (
            f"Rolled {num_dice}d{dice_size}: [{rolls_str}] = {sum(rolls)}"
            f"{modifier_str} = {total}"
        )

        return True, total, message

    @staticmethod
    def _execute_sum(params: dict) -> Tuple[bool, Union[int, str], str]:
        """Execute @sum macro.

        Example: @sum 14 2 3 (sum 14+2+3)
        """
        values_str = params.get("values_str", "")

        # Parse the values
        try:
            # Replace operators and parse
            values_str = values_str.strip()
            total = eval(values_str, {"__builtins__": {}}, {})

            if not isinstance(total, (int, float)):
                return False, "Invalid sum", "Sum must result in a number"

            total = int(total)
            message = f"Sum: {values_str} = {total}"
            return True, total, message

        except Exception as e:
            return False, "Invalid sum", f"Cannot calculate sum: {e}"

    @staticmethod
    def process_input(input_str: str) -> Tuple[bool, Union[int, str], str]:
        """Process user input, executing macro if present.

        Args:
            input_str: User input that may contain a macro

        Returns:
            Tuple of (success, result_value, message)
                If macro found and executed: (True/False, value, message)
                If no macro: (False, input_str, error message saying no macro)

        Use this when you want to only process macros, or detect if a macro exists.
        """
        macro = MacroProcessor.parse_macro(input_str)

        if macro is None:
            # Not a macro
            return False, input_str, "No macro detected"

        macro_type, params = macro
        return MacroProcessor.execute(macro_type, params)
