"""Tests for TUI functionality."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nanocode.tui.app import OutputArea


class TestOutputArea:
    """Test OutputArea functionality."""

    def test_output_area_initialization(self):
        """Test OutputArea initialization."""
        area = OutputArea()
        assert area.GRUVBOX is not None
        assert area.GRUVBOX["fg"] == "#ebdbb2"
        assert area.GRUVBOX["green"] == "#98971a"

    def test_gruvbox_colors(self):
        """Test that Gruvbox colors are defined."""
        area = OutputArea()
        expected_colors = [
            "fg", "gray", "red", "green", "yellow", "blue",
            "purple", "aqua", "orange", "red_bright", "green_bright",
            "yellow_bright", "blue_bright", "purple_bright",
            "aqua_bright", "orange_bright"
        ]
        for color in expected_colors:
            assert color in area.GRUVBOX, f"Missing color: {color}"

    def test_render_markdown_method(self):
        """Test _render_markdown method exists."""
        area = OutputArea()
        md = area._render_markdown("# Hello")
        assert md is not None

    def test_add_line_basic(self):
        """Test add_line method exists and accepts text."""
        area = OutputArea()
        area.add_line("Hello world")

    def test_add_line_with_style(self):
        """Test add_line with different styles."""
        area = OutputArea()
        area.add_line("User message", "user")
        area.add_line("Assistant message", "assistant")
        area.add_line("Tool message", "tool")

    def test_add_line_with_markdown(self):
        """Test add_line with markdown content."""
        area = OutputArea()
        area.add_line("# Heading\n\nThis is **bold** text.")
        area.add_line("`inline code` and *italic*")

    def test_add_line_with_code_block(self):
        """Test add_line with code blocks."""
        area = OutputArea()
        area.add_line("```python\nprint('hello')\n```")

    def test_add_empty_line(self):
        """Test add_empty_line method."""
        area = OutputArea()
        area.add_empty_line()

    def test_clear_lines(self):
        """Test clear_lines method."""
        area = OutputArea()
        area.add_line("Test line")
        area.clear_lines()
        assert len(area._lines) == 0
