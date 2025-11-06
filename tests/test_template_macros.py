"""Tests for macro system."""

import pytest
from lib.template_macros import MacroProcessor


class TestMacroParser:
    """Test macro parsing."""

    def test_parse_roll_top_basic(self):
        """Test parsing basic @roll-top macro."""
        macro = MacroProcessor.parse_macro("@roll-top 3 4d6")
        assert macro is not None
        macro_type, params = macro
        assert macro_type == "roll_top"
        assert params["keep"] == 3
        assert params["num_dice"] == 4
        assert params["dice_size"] == 6
        assert params["modifier"] == 0

    def test_parse_roll_top_with_modifier(self):
        """Test parsing @roll-top with modifier."""
        macro = MacroProcessor.parse_macro("@roll-top 3 4d6+2")
        assert macro is not None
        macro_type, params = macro
        assert params["keep"] == 3
        assert params["modifier"] == 2

    def test_parse_roll_top_with_negative_modifier(self):
        """Test parsing @roll-top with negative modifier."""
        macro = MacroProcessor.parse_macro("@roll-top 2 3d6-1")
        assert macro is not None
        macro_type, params = macro
        assert params["keep"] == 2
        assert params["modifier"] == -1

    def test_parse_roll_basic(self):
        """Test parsing basic @roll macro."""
        macro = MacroProcessor.parse_macro("@roll d20")
        assert macro is not None
        macro_type, params = macro
        assert macro_type == "roll"
        assert params["num_dice"] == 1
        assert params["dice_size"] == 20
        assert params["modifier"] == 0

    def test_parse_roll_multiple_dice(self):
        """Test parsing @roll with multiple dice."""
        macro = MacroProcessor.parse_macro("@roll 2d6")
        assert macro is not None
        macro_type, params = macro
        assert params["num_dice"] == 2
        assert params["dice_size"] == 6

    def test_parse_roll_with_modifier(self):
        """Test parsing @roll with modifier."""
        macro = MacroProcessor.parse_macro("@roll d20+5")
        assert macro is not None
        macro_type, params = macro
        assert params["modifier"] == 5

    def test_parse_roll_with_negative_modifier(self):
        """Test parsing @roll with negative modifier."""
        macro = MacroProcessor.parse_macro("@roll 2d8-2")
        assert macro is not None
        macro_type, params = macro
        assert params["modifier"] == -2

    def test_parse_sum(self):
        """Test parsing @sum macro."""
        macro = MacroProcessor.parse_macro("@sum 14 2 3")
        assert macro is not None
        macro_type, params = macro
        assert macro_type == "sum"
        assert "14" in params["values_str"]

    def test_parse_sum_with_operators(self):
        """Test parsing @sum with operators."""
        macro = MacroProcessor.parse_macro("@sum 10+5-2")
        assert macro is not None
        macro_type, params = macro
        assert macro_type == "sum"

    def test_parse_no_macro(self):
        """Test parsing non-macro input."""
        macro = MacroProcessor.parse_macro("just a regular string")
        assert macro is None

    def test_parse_macro_case_insensitive(self):
        """Test that macros are case insensitive."""
        macro = MacroProcessor.parse_macro("@ROLL D20")
        assert macro is not None
        macro_type, params = macro
        assert macro_type == "roll"


class TestRollTopExecution:
    """Test @roll-top macro execution."""

    def test_roll_top_basic(self):
        """Test basic @roll-top execution."""
        success, value, message = MacroProcessor.execute(
            "roll_top", {"keep": 3, "num_dice": 4, "dice_size": 6, "modifier": 0}
        )
        assert success is True
        assert isinstance(value, int)
        assert 3 <= value <= 18  # Min: 1+1+1, Max: 6+6+6
        assert "Rolled" in message
        assert "keep top" in message

    def test_roll_top_with_modifier(self):
        """Test @roll-top with modifier."""
        success, value, message = MacroProcessor.execute(
            "roll_top", {"keep": 3, "num_dice": 4, "dice_size": 6, "modifier": 2}
        )
        assert success is True
        assert isinstance(value, int)
        assert 5 <= value <= 20  # Min + 2, Max + 2
        assert "+" in message or " = " in message

    def test_roll_top_with_negative_modifier(self):
        """Test @roll-top with negative modifier."""
        success, value, message = MacroProcessor.execute(
            "roll_top", {"keep": 3, "num_dice": 4, "dice_size": 6, "modifier": -1}
        )
        assert success is True
        assert isinstance(value, int)
        assert 2 <= value <= 17  # Min - 1, Max - 1

    def test_roll_top_invalid_keep(self):
        """Test @roll-top with invalid keep value."""
        success, value, message = MacroProcessor.execute(
            "roll_top", {"keep": 5, "num_dice": 4, "dice_size": 6, "modifier": 0}
        )
        assert success is False
        assert "keep" in message.lower()

    def test_roll_top_keep_zero(self):
        """Test @roll-top with keep=0."""
        success, value, message = MacroProcessor.execute(
            "roll_top", {"keep": 0, "num_dice": 4, "dice_size": 6, "modifier": 0}
        )
        assert success is False

    def test_roll_top_too_many_dice(self):
        """Test @roll-top with too many dice."""
        success, value, message = MacroProcessor.execute(
            "roll_top", {"keep": 50, "num_dice": 101, "dice_size": 6, "modifier": 0}
        )
        assert success is False
        assert "100" in message


class TestRollExecution:
    """Test @roll macro execution."""

    def test_roll_d20(self):
        """Test rolling d20."""
        success, value, message = MacroProcessor.execute(
            "roll", {"num_dice": 1, "dice_size": 20, "modifier": 0}
        )
        assert success is True
        assert isinstance(value, int)
        assert 1 <= value <= 20
        assert "Rolled 1d20" in message

    def test_roll_2d6(self):
        """Test rolling 2d6."""
        success, value, message = MacroProcessor.execute(
            "roll", {"num_dice": 2, "dice_size": 6, "modifier": 0}
        )
        assert success is True
        assert isinstance(value, int)
        assert 2 <= value <= 12
        assert "Rolled 2d6" in message

    def test_roll_with_modifier(self):
        """Test roll with modifier."""
        success, value, message = MacroProcessor.execute(
            "roll", {"num_dice": 1, "dice_size": 20, "modifier": 5}
        )
        assert success is True
        assert isinstance(value, int)
        assert 6 <= value <= 25

    def test_roll_with_negative_modifier(self):
        """Test roll with negative modifier."""
        success, value, message = MacroProcessor.execute(
            "roll", {"num_dice": 1, "dice_size": 20, "modifier": -3}
        )
        assert success is True
        assert isinstance(value, int)
        assert -2 <= value <= 17

    def test_roll_too_many_dice(self):
        """Test roll with too many dice."""
        success, value, message = MacroProcessor.execute(
            "roll", {"num_dice": 101, "dice_size": 6, "modifier": 0}
        )
        assert success is False

    def test_roll_invalid_dice_size(self):
        """Test roll with invalid dice size."""
        success, value, message = MacroProcessor.execute(
            "roll", {"num_dice": 1, "dice_size": 1001, "modifier": 0}
        )
        assert success is False


class TestSumExecution:
    """Test @sum macro execution."""

    def test_sum_simple(self):
        """Test simple sum."""
        success, value, message = MacroProcessor.execute("sum", {"values_str": "14"})
        assert success is True
        assert value == 14

    def test_sum_multiple_values(self):
        """Test summing multiple values."""
        success, value, message = MacroProcessor.execute(
            "sum", {"values_str": "14 + 2 + 3"}
        )
        assert success is True
        assert value == 19

    def test_sum_with_subtraction(self):
        """Test sum with subtraction."""
        success, value, message = MacroProcessor.execute(
            "sum", {"values_str": "20 - 5"}
        )
        assert success is True
        assert value == 15

    def test_sum_complex(self):
        """Test complex sum."""
        success, value, message = MacroProcessor.execute(
            "sum", {"values_str": "10 + 5 - 2 + 3"}
        )
        assert success is True
        assert value == 16

    def test_sum_invalid(self):
        """Test sum with invalid expression."""
        success, value, message = MacroProcessor.execute(
            "sum", {"values_str": "abc + def"}
        )
        assert success is False


class TestMacroIntegration:
    """Test macro processing end-to-end."""

    def test_process_roll_top_input(self):
        """Test processing @roll-top input."""
        success, value, message = MacroProcessor.process_input("@roll-top 3 4d6")
        assert success is True
        assert isinstance(value, int)
        assert 3 <= value <= 18

    def test_process_roll_input(self):
        """Test processing @roll input."""
        success, value, message = MacroProcessor.process_input("@roll d20")
        assert success is True
        assert isinstance(value, int)
        assert 1 <= value <= 20

    def test_process_sum_input(self):
        """Test processing @sum input."""
        success, value, message = MacroProcessor.process_input("@sum 10 + 5")
        assert success is True
        assert value == 15

    def test_process_no_macro_input(self):
        """Test processing non-macro input."""
        success, value, message = MacroProcessor.process_input("just text")
        assert success is False
        assert value == "just text"
        assert "no macro" in message.lower()

    def test_process_numeric_input(self):
        """Test processing numeric input (no macro)."""
        success, value, message = MacroProcessor.process_input("15")
        assert success is False
        assert value == "15"

    def test_process_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        success1, value1, _ = MacroProcessor.process_input("@roll d20")
        success2, value2, _ = MacroProcessor.process_input("  @roll d20  ")
        assert success1 == success2
        # Both should succeed (values may differ due to randomness)
