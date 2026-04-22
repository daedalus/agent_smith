"""Tests for TUI message actions."""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestMessageActionScreen:
    """Test MessageActionScreen modal."""

    def test_screen_initialization(self):
        """Test that screen initializes with message text."""
        from nanocode.tui.app import MessageActionScreen

        screen = MessageActionScreen("test message", 0)
        assert screen._message_text == "test message"
        assert screen._message_index == 0

    def test_screen_buttons(self):
        """Test that screen has Fork, Copy, Revert, Cancel buttons."""
        from nanocode.tui.app import MessageActionScreen

        screen = MessageActionScreen("test", 0)

        # Simulate button presses
        class MockEvent:
            button = Mock()

        # Test Fork action
        MockEvent.button.id = "btn-fork"
        result = None

        def capture_dismiss(val):
            nonlocal result
            result = val

        screen.dismiss = capture_dismiss
        screen.on_button_pressed(MockEvent())
        assert result == ("fork", "test", 0)

    def test_copy_action(self):
        """Test Copy button returns correct result."""
        from nanocode.tui.app import MessageActionScreen

        screen = MessageActionScreen("test message", 5)
        result = None

        def capture_dismiss(val):
            nonlocal result
            result = val

        screen.dismiss = capture_dismiss

        # Create mock event with button attribute
        event = Mock()
        event.button = Mock()
        event.button.id = "btn-copy"
        screen.on_button_pressed(event)
        assert result == ("copy", "test message", 5)

    def test_revert_action(self):
        """Test Revert button returns correct result."""
        from nanocode.tui.app import MessageActionScreen

        screen = MessageActionScreen("revert this", 2)
        result = None

        def capture_dismiss(val):
            nonlocal result
            result = val

        screen.dismiss = capture_dismiss

        event = Mock()
        event.button = Mock()
        event.button.id = "btn-revert"
        screen.on_button_pressed(event)
        assert result == ("revert", "revert this", 2)

    def test_cancel_action(self):
        """Test Cancel button returns None."""
        from nanocode.tui.app import MessageActionScreen

        screen = MessageActionScreen("test", 0)
        result = "not none"

        def capture_dismiss(val):
            nonlocal result
            result = val

        screen.dismiss = capture_dismiss

        event = Mock()
        event.button = Mock()
        event.button.id = "btn-cancel"
        screen.on_button_pressed(event)
        assert result is None


class TestMessageActionBindings:
    """Test keyboard bindings for message actions."""

    def test_ctrl_m_binding_exists(self):
        """Test Ctrl+M binding is defined."""
        from nanocode.tui.app import NanoCodeTUI

        bindings = NanoCodeTUI.BINDINGS
        ctrl_m_binding = [b for b in bindings if b.key == "ctrl+m"]
        assert len(ctrl_m_binding) == 1
        assert ctrl_m_binding[0].action == "message_actions"