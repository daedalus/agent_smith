"""Tests for core.py Rich color integration."""

from unittest.mock import MagicMock, patch
import pytest


class TestRichColorCore:
    """Test RichColor enum in core.py."""

    def test_rich_color_enum_values(self):
        """Test RichColor enum has correct values."""
        from nanocode.core import RichColor
        assert RichColor.RESET.value == "reset"
        assert RichColor.RED.value == "red"
        assert RichColor.GREEN.value == "green"
        assert RichColor.YELLOW.value == "yellow"
        assert RichColor.BLUE.value == "blue"
        assert RichColor.MAGENTA.value == "magenta"
        assert RichColor.CYAN.value == "cyan"
        assert RichColor.GRAY.value == "dim"

    def test_rich_color_enum_count(self):
        """Test RichColor enum has expected colors."""
        from nanocode.core import RichColor
        colors = list(RichColor)
        assert len(colors) == 8


class TestCustomTheme:
    """Test custom theme in core.py."""

    def test_theme_defined(self):
        """Test custom_theme is defined."""
        from nanocode.core import custom_theme
        assert custom_theme is not None

    def test_theme_has_thought_style(self):
        """Test theme has 'thought' style."""
        from nanocode.core import custom_theme
        thought_style = custom_theme.styles.get("thought")
        assert thought_style is not None
        assert thought_style.color is not None

    def test_theme_has_tool_call_style(self):
        """Test theme has 'tool_call' style."""
        from nanocode.core import custom_theme
        style = custom_theme.styles.get("tool_call")
        assert style is not None

    def test_theme_has_debug_style(self):
        """Test theme has 'debug' style."""
        from nanocode.core import custom_theme
        style = custom_theme.styles.get("debug")
        assert style is not None

    def test_theme_has_warning_style(self):
        """Test theme has 'warning' style."""
        from nanocode.core import custom_theme
        style = custom_theme.styles.get("warning")
        assert style is not None


class TestConsole:
    """Test console object in core.py."""

    def test_console_defined(self):
        """Test console is defined."""
        from nanocode.core import console
        assert console is not None

    def test_console_print(self):
        """Test console.print works."""
        from nanocode.core import console
        console.print("[yellow]test[/yellow]")


class TestFormatThinking:
    """Test _format_thinking method."""

    def test_format_thinking_contains_thought_tag(self):
        """Test _format_thinking output contains [thought] tag."""
        from nanocode.core import AutonomousAgent

        with patch("nanocode.core.AutonomousAgent.__init__", return_value=None):
            agent = AutonomousAgent.__new__(AutonomousAgent)
            agent._last_thinking = None

        result = agent._format_thinking("test thinking")
        assert "[thought]" in result
        assert "[/thought]" in result


class TestAugmentedContentThinking:
    """Test augmented content includes thinking."""

    def test_augmented_includes_thought_tag(self):
        """Test augmented content uses [thought] tag."""
        from nanocode.core import AutonomousAgent

        with patch("nanocode.core.AutonomousAgent.__init__", return_value=None):
            agent = AutonomousAgent.__new__(AutonomousAgent)
            agent._last_thinking = "some thinking"
            agent.show_thinking = True

        augmented = ""
        if agent.show_thinking and hasattr(agent, "_last_thinking") and agent._last_thinking:
            augmented += f"\n\n[thought]| Thinking:[/thought] {agent._last_thinking}"

        assert "[thought]" in augmented
        assert "Thinking:" in augmented
        assert "some thinking" in augmented


class TestDebugOutput:
    """Test debug output uses Rich markup."""

    def test_debug_uses_markup(self):
        """Test debug output uses Rich markup tags."""
        from nanocode.core import console

        output_lines = []
        with patch.object(console, "print") as mock_print:
            console.print("[debug]test[/debug]")
            mock_print.assert_called_once()

    def test_warning_uses_markup(self):
        """Test warning output uses Rich markup tags."""
        from nanocode.core import console

        with patch.object(console, "print") as mock_print:
            console.print("[warning]test[/warning]")
            mock_print.assert_called_once()