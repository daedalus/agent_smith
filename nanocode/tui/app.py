"""NanoCode TUI App - A Textual-based terminal UI."""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, RichLog, Button
from textual.binding import Binding

import asyncio


class OutputLog(RichLog):
    """Log viewer for agent output."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auto_scroll = True
    
    def add_message(self, role: str, content: str, style: str = ""):
        """Add a message to the log."""
        role_styles = {
            "user": "cyan",
            "assistant": "blue bold",
            "system": "yellow",
            "tool": "magenta",
            "error": "red bold",
            "success": "green",
        }
        color = role_styles.get(role, "white")
        self.write(f"[{color}][{role.upper()}][/] {content}")


class NanoCodeApp(App):
    """Main TUI application for NanoCode."""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #main-container {
        height: 100%;
    }
    
    #output-log {
        height: 1fr;
        border: solid $primary;
        margin: 1;
    }
    
    #input-container {
        height: auto;
        padding: 1;
    }
    
    #input {
        height: auto;
    }
    
    #send-btn {
        height: auto;
    }
    
    #status-bar {
        height: auto;
        background: $surface-darken-1;
        padding: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("enter", "submit", "Send"),
        Binding("ctrl+l", "clear_output", "Clear Output"),
        Binding("escape", "quit", "Quit", show=True),
    ]
    
    def __init__(self, agent=None, show_thinking: bool = True):
        super().__init__()
        self.agent = agent
        self.show_thinking = show_thinking
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main-container"):
            yield OutputLog(id="output-log")
            with Horizontal(id="input-container"):
                yield Input(placeholder="Enter your task...", id="input")
                yield Button("Send", id="send-btn", variant="primary")
        yield Static("", id="status-bar")
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize on mount."""
        self.query_one("#input", Input).focus()
        self._show_welcome()
        
        if self.agent:
            self._setup_permission_callback()
    
    def _show_welcome(self):
        """Show welcome message."""
        log = self.query_one("#output-log", OutputLog)
        log.add_message("system", "╔═══════════════════════════════════════════════════════════╗")
        log.add_message("system", "║              NanoCode TUI - Ready                        ║")
        log.add_message("system", "║  Type your task or 'help' for commands                     ║")
        log.add_message("system", "╚═══════════════════════════════════════════════════════════╝")
    
    def _setup_permission_callback(self):
        """Set up permission callback for the agent."""
        from nanocode.agents.permission import (
            PermissionReply,
            PermissionReplyType,
            PermissionRequest,
        )
        
        async def permission_callback(request: PermissionRequest) -> PermissionReply:
            self._show_permission_dialog(request)
            return PermissionReply(request_id=request.id, reply=PermissionReplyType.ALWAYS)
        
        self.agent.permission_handler.set_callback(permission_callback)
    
    def _show_permission_dialog(self, request):
        """Show permission request dialog."""
        log = self.query_one("#output-log", OutputLog)
        log.add_message("system", f"┌─[PERMISSION REQUEST]")
        log.add_message("system", f"  Agent: {request.agent_name}")
        log.add_message("system", f"  Tool: {request.tool_name}")
        if request.arguments:
            for k, v in request.arguments.items():
                v_str = str(v)
                if len(v_str) > 50:
                    v_str = v_str[:50] + "..."
                log.add_message("system", f"    {k}: {v_str}")
        log.add_message("system", f"  ➜ Allow? (y/n/a=always)")
    
    def action_submit(self):
        """Handle send action."""
        input_widget = self.query_one("#input", Input)
        text = input_widget.value.strip()
        if text:
            input_widget.value = ""
            self._process_input(text)
    
    def action_clear_output(self):
        """Clear output log."""
        log = self.query_one("#output-log", OutputLog)
        log.clear()
    
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        pass
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        text = event.value.strip()
        if text:
            event.input.value = ""
            self._process_input(text)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "send-btn":
            self.action_submit()
    
    async def _process_input(self, text: str):
        """Process user input through the agent."""
        log = self.query_one("#output-log", OutputLog)
        
        log.add_message("user", text)
        
        try:
            if self.agent:
                result = await self.agent.process_input(
                    text, show_thinking=self.show_thinking
                )
                log.add_message("assistant", str(result))
            else:
                log.add_message("error", "No agent configured")
        except Exception as e:
            log.add_message("error", f"Error: {e}")


def run_tui(agent=None, show_thinking: bool = True):
    """Run the TUI application."""
    app = NanoCodeApp(agent=agent, show_thinking=show_thinking)
    app.run()


if __name__ == "__main__":
    run_tui()