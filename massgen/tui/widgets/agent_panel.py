"""Agent panel widget for displaying individual agent output."""

from typing import List, Optional

from rich.text import Text
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Static

from massgen.logging import get_logger
from massgen.types import AgentState

logger = get_logger(__name__)


class AgentPanel(Widget):
    """Panel for displaying individual agent information and output."""

    # Reactive properties
    agent_id: reactive[int] = reactive(0)
    model_name: reactive[str] = reactive("")
    status: reactive[str] = reactive("unknown")
    chat_round: reactive[int] = reactive(0)
    update_count: reactive[int] = reactive(0)
    votes_cast: reactive[int] = reactive(0)
    vote_target: reactive[Optional[int]] = reactive(None)

    # Output buffer for streaming
    output_buffer: reactive[str] = reactive("")

    def __init__(self, agent_id: int, **kwargs):
        """Initialize the agent panel.

        Args:
            agent_id: The ID of the agent this panel represents
        """
        super().__init__(**kwargs)
        self.agent_id = agent_id
        self._output_lines: List[str] = []
        self._max_lines = 100  # Keep last N lines

    def compose(self):
        """Compose the agent panel layout."""
        with Vertical(id=f"agent-panel-{self.agent_id}"):
            # Header with agent info
            yield Label(f"🤖 Agent {self.agent_id}", id=f"agent-header-{self.agent_id}", classes="agent-header")

            # Status bar
            with Horizontal(classes="agent-status-bar"):
                yield Static("", id=f"agent-model-{self.agent_id}", classes="agent-model")
                yield Static("", id=f"agent-status-{self.agent_id}", classes="agent-status")

            # Metadata row
            with Horizontal(classes="agent-metadata"):
                yield Static("", id=f"agent-round-{self.agent_id}", classes="agent-meta-item")
                yield Static("", id=f"agent-updates-{self.agent_id}", classes="agent-meta-item")
                yield Static("", id=f"agent-votes-{self.agent_id}", classes="agent-meta-item")
                yield Static("", id=f"agent-vote-target-{self.agent_id}", classes="agent-meta-item")

            # Output area using ScrollableContainer for better performance
            with ScrollableContainer(id=f"agent-output-container-{self.agent_id}"):
                yield Static("", id=f"agent-output-{self.agent_id}", classes="agent-output")

    def on_mount(self):
        """Initialize the panel when mounted."""
        self._update_header()
        self._update_status_display()
        self._update_metadata_display()

    def update_state(self, state: AgentState):
        """Update the agent state.

        Args:
            state: The new agent state
        """
        # Update reactive properties
        if hasattr(state, "model_name"):
            self.model_name = state.model_name
        if hasattr(state, "status"):
            self.status = state.status
        if hasattr(state, "chat_round"):
            self.chat_round = state.chat_round
        if hasattr(state, "update_count"):
            self.update_count = state.update_count
        if hasattr(state, "votes_cast"):
            self.votes_cast = state.votes_cast
        if hasattr(state, "vote_target"):
            self.vote_target = state.vote_target

    def stream_output(self, content: str):
        """Stream output content to the agent panel.

        Args:
            content: The content to add to the output
        """
        # Add to output buffer
        self.output_buffer += content

        # Split into lines and update display
        lines = self.output_buffer.split("\n")

        # Keep incomplete line in buffer
        if not content.endswith("\n"):
            self.output_buffer = lines[-1]
            lines = lines[:-1]
        else:
            self.output_buffer = ""

        # Add complete lines to output
        self._output_lines.extend(lines)

        # Trim to max lines
        if len(self._output_lines) > self._max_lines:
            self._output_lines = self._output_lines[-self._max_lines :]

        # Update display
        self._update_output_display()

    def _update_header(self):
        """Update the agent header."""
        header = self.query_one(f"#agent-header-{self.agent_id}", Label)

        # Status emoji mapping
        status_emoji = {"working": "🔄", "voted": "✅", "failed": "❌", "unknown": "❓"}

        emoji = status_emoji.get(self.status, "❓")
        header.update(f"{emoji} Agent {self.agent_id}")

    def _update_status_display(self):
        """Update the status bar display."""
        # Update model name
        model_widget = self.query_one(f"#agent-model-{self.agent_id}", Static)
        if self.model_name:
            model_widget.update(Text(f"📱 {self.model_name}", style="bright_magenta"))

        # Update status
        status_widget = self.query_one(f"#agent-status-{self.agent_id}", Static)
        status_colors = {
            "working": "bright_yellow",
            "voted": "bright_green",
            "failed": "bright_red",
            "unknown": "white",
        }
        color = status_colors.get(self.status, "white")
        status_widget.update(Text(f"[{self.status}]", style=color))

    def _update_metadata_display(self):
        """Update the metadata display."""
        # Round info
        round_widget = self.query_one(f"#agent-round-{self.agent_id}", Static)
        round_widget.update(Text(f"Round: {self.chat_round}", style="bright_green"))

        # Updates count
        updates_widget = self.query_one(f"#agent-updates-{self.agent_id}", Static)
        updates_widget.update(Text(f"Updates: {self.update_count}", style="bright_magenta"))

        # Votes cast
        votes_widget = self.query_one(f"#agent-votes-{self.agent_id}", Static)
        votes_widget.update(Text(f"Votes: {self.votes_cast}", style="bright_cyan"))

        # Vote target
        target_widget = self.query_one(f"#agent-vote-target-{self.agent_id}", Static)
        if self.vote_target is not None:
            target_widget.update(Text(f"→ Agent {self.vote_target}", style="bright_green"))
        else:
            target_widget.update(Text("→ None", style="dim"))

    def _update_output_display(self):
        """Update the output display area."""
        output_widget = self.query_one(f"#agent-output-{self.agent_id}", Static)

        # Join lines and update
        output_text = "\n".join(self._output_lines)
        output_widget.update(output_text)

        # Auto-scroll to bottom
        container = self.query_one(f"#agent-output-container-{self.agent_id}", ScrollableContainer)
        container.scroll_end(animate=False)

    def watch_model_name(self, old_value: str, new_value: str):
        """React to model name changes."""
        self._update_status_display()

    def watch_status(self, old_value: str, new_value: str):
        """React to status changes."""
        self._update_header()
        self._update_status_display()

    def watch_chat_round(self, old_value: int, new_value: int):
        """React to chat round changes."""
        self._update_metadata_display()

    def watch_update_count(self, old_value: int, new_value: int):
        """React to update count changes."""
        self._update_metadata_display()

    def watch_votes_cast(self, old_value: int, new_value: int):
        """React to votes cast changes."""
        self._update_metadata_display()

    def watch_vote_target(self, old_value: Optional[int], new_value: Optional[int]):
        """React to vote target changes."""
        self._update_metadata_display()
