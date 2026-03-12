"""Tests for InteractiveCLI command processing."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add the agent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_smith.cli import InteractiveCLI, ConsoleUI


class TestInteractiveCLI:
    """Test InteractiveCLI command processing."""

    def test_cli_initialization(self):
        """Test that CLI can be initialized."""
        mock_agent = Mock()
        cli = InteractiveCLI(mock_agent)
        assert cli.agent == mock_agent
        assert cli.ui is not None
        assert cli.history is not None

    def test_print_history(self):
        """Test _print_history method."""
        mock_agent = Mock()
        cli = InteractiveCLI(mock_agent)
        cli.history.add("command 1", "output 1")
        cli.history.add("command 2", "output 2")

        # Capture print output
        import io
        import sys

        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        try:
            cli._print_history()
            output = buffer.getvalue()
            assert "Command History:" in output
            assert "command 1" in output
            assert "command 2" in output
        finally:
            sys.stdout = old_stdout

    def test_print_tools(self):
        """Test _print_tools method."""
        mock_agent = Mock()
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"
        mock_agent.tool_registry.list_tools.return_value = [mock_tool]

        cli = InteractiveCLI(mock_agent)

        # Capture print output
        import io
        import sys

        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        try:
            cli._print_tools()
            output = buffer.getvalue()
            assert "Available Tools:" in output
            assert "test_tool" in output
            assert "A test tool" in output
        finally:
            sys.stdout = old_stdout

    def test_list_checkpoints_with_checkpoints(self):
        """Test _list_checkpoints method when checkpoints exist."""
        mock_agent = Mock()
        cli = InteractiveCLI(mock_agent)

        # Capture print output
        import io
        import sys

        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        try:
            with patch("os.path.exists", return_value=True):
                with patch("os.listdir", return_value=["checkpoint_1.json", "checkpoint_2.json"]):
                    cli._list_checkpoints()
                    output = buffer.getvalue()
                    assert "Saved Checkpoints:" in output
                    assert "checkpoint_1.json" in output
                    assert "checkpoint_2.json" in output
        finally:
            sys.stdout = old_stdout

    def test_list_checkpoints_without_checkpoints(self):
        """Test _list_checkpoints method when no checkpoints exist."""
        mock_agent = Mock()
        cli = InteractiveCLI(mock_agent)

        # Capture print output
        import io
        import sys

        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        try:
            with patch("os.path.exists", return_value=False):
                cli._list_checkpoints()
                output = buffer.getvalue()
                assert "No checkpoints found" in output
        finally:
            sys.stdout = old_stdout

    def test_console_ui_print_help(self):
        """Test that ConsoleUI print_help shows slash commands."""
        ui = ConsoleUI()

        # Capture print output
        import io
        import sys

        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        try:
            ui.print_help()
            output = buffer.getvalue()
            assert "/help" in output
            assert "/exit" in output
            assert "/clear" in output
            assert "/history" in output
            assert "/tools" in output
            assert "/provider" in output
            assert "/plan" in output
            assert "/resume" in output
            assert "/checkpoint" in output
        finally:
            sys.stdout = old_stdout
