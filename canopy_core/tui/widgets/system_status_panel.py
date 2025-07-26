"""System status panel widget for displaying overall system state."""

from datetime import datetime
from typing import Dict, List, Optional

from rich.table import Table
from rich.text import Text
from textual.containers import Grid, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Label, Static

from ...logging import get_logger
from ...types import SystemState

logger = get_logger(__name__)


class SystemStatusPanel(Widget):
    """Panel for displaying system-wide status and metrics."""

    # Reactive properties
    algorithm_name: reactive[str] = reactive("massgen")
    current_phase: reactive[str] = reactive("initialization")
    consensus_reached: reactive[bool] = reactive(False)
    debate_rounds: reactive[int] = reactive(0)
    representative_agent: reactive[Optional[int]] = reactive(None)
    vote_distribution: reactive[Dict[int, int]] = reactive({})

    # System messages buffer
    system_messages: reactive[List[str]] = reactive([])
    max_messages: int = 20

    def compose(self):
        """Compose the system status panel layout."""
        with Vertical(id="system-status-panel"):
            # Title
            yield Label("📊 SYSTEM STATUS", id="system-title", classes="system-title")

            # Main status grid
            with Grid(id="status-grid", classes="status-grid"):
                # Algorithm info
                with Vertical(classes="status-item"):
                    yield Label("Algorithm", classes="status-label")
                    yield Static("", id="algorithm-display", classes="status-value")

                # Phase info
                with Vertical(classes="status-item"):
                    yield Label("Phase", classes="status-label")
                    yield Static("", id="phase-display", classes="status-value")

                # Consensus info
                with Vertical(classes="status-item"):
                    yield Label("Consensus", classes="status-label")
                    yield Static("", id="consensus-display", classes="status-value")

                # Debate rounds
                with Vertical(classes="status-item"):
                    yield Label("Debate Rounds", classes="status-label")
                    yield Static("", id="rounds-display", classes="status-value")

                # Representative agent
                with Vertical(classes="status-item"):
                    yield Label("Representative", classes="status-label")
                    yield Static("", id="representative-display", classes="status-value")

            # Vote distribution
            yield Label("📊 Vote Distribution", classes="section-title")
            yield Static("", id="vote-distribution", classes="vote-distribution")

            # System messages
            yield Label("📋 System Messages", classes="section-title")
            yield DataTable(id="system-messages-table", show_header=False, show_cursor=False, zebra_stripes=True)

    def on_mount(self):
        """Initialize the panel when mounted."""
        # Initialize system messages table
        messages_table = self.query_one("#system-messages-table", DataTable)
        messages_table.add_column("timestamp", width=10)
        messages_table.add_column("message", width=None)  # Auto-width

        # Update all displays
        self._update_all_displays()

    def update_state(self, state: SystemState):
        """Update the system state.

        Args:
            state: The new system state
        """
        # Update reactive properties from state
        if hasattr(state, "algorithm_name"):
            self.algorithm_name = state.algorithm_name
        if hasattr(state, "phase"):
            self.current_phase = state.phase
        if hasattr(state, "consensus_reached"):
            self.consensus_reached = state.consensus_reached
        if hasattr(state, "debate_rounds"):
            self.debate_rounds = state.debate_rounds
        if hasattr(state, "representative_agent_id"):
            self.representative_agent = state.representative_agent_id
        if hasattr(state, "vote_distribution"):
            self.vote_distribution = state.vote_distribution.copy()

    def add_system_message(self, message: str):
        """Add a system message to the display.

        Args:
            message: The message to add
        """
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Update messages list
        self.system_messages = self.system_messages + [(timestamp, message)]

        # Trim to max messages
        if len(self.system_messages) > self.max_messages:
            self.system_messages = self.system_messages[-self.max_messages :]

        # Update table
        self._update_messages_table()

    def _update_all_displays(self):
        """Update all display elements."""
        self._update_algorithm_display()
        self._update_phase_display()
        self._update_consensus_display()
        self._update_rounds_display()
        self._update_representative_display()
        self._update_vote_distribution()

    def _update_algorithm_display(self):
        """Update the algorithm display."""
        widget = self.query_one("#algorithm-display", Static)
        widget.update(Text(self.algorithm_name.upper(), style="bright_cyan bold"))

    def _update_phase_display(self):
        """Update the phase display."""
        widget = self.query_one("#phase-display", Static)
        phase_colors = {
            "initialization": "bright_blue",
            "collaboration": "bright_yellow",
            "consensus": "bright_green",
            "complete": "bright_green",
        }
        color = phase_colors.get(self.current_phase, "white")
        widget.update(Text(self.current_phase.upper(), style=f"{color} bold"))

    def _update_consensus_display(self):
        """Update the consensus display."""
        widget = self.query_one("#consensus-display", Static)
        if self.consensus_reached:
            widget.update(Text("✅ YES", style="bright_green bold"))
        else:
            widget.update(Text("❌ NO", style="bright_red bold"))

    def _update_rounds_display(self):
        """Update the debate rounds display."""
        widget = self.query_one("#rounds-display", Static)
        widget.update(Text(str(self.debate_rounds), style="bright_cyan bold"))

    def _update_representative_display(self):
        """Update the representative display."""
        widget = self.query_one("#representative-display", Static)
        if self.representative_agent is not None:
            widget.update(Text(f"Agent {self.representative_agent}", style="bright_green bold"))
        else:
            widget.update(Text("None", style="dim"))

    def _update_vote_distribution(self):
        """Update the vote distribution display."""
        widget = self.query_one("#vote-distribution", Static)

        if not self.vote_distribution:
            widget.update(Text("No votes yet", style="dim italic"))
            return

        # Create a rich table for vote distribution
        table = Table(show_header=True, header_style="bold bright_white")
        table.add_column("Agent", style="bright_cyan", justify="center")
        table.add_column("Votes", style="bright_green", justify="center")
        table.add_column("Bar", justify="left")

        # Find max votes for bar scaling
        max_votes = max(self.vote_distribution.values()) if self.vote_distribution else 1

        # Add rows
        for agent_id, votes in sorted(self.vote_distribution.items()):
            # Create a simple bar chart
            bar_width = int((votes / max_votes) * 20)  # Max 20 chars wide
            bar = "█" * bar_width

            table.add_row(str(agent_id), str(votes), Text(bar, style="bright_green"))

        widget.update(table)

    def _update_messages_table(self):
        """Update the system messages table."""
        table = self.query_one("#system-messages-table", DataTable)

        # Clear and repopulate table
        table.clear()

        for timestamp, message in self.system_messages:
            # Add row with timestamp and message
            table.add_row(Text(timestamp, style="dim"), Text(message))

    # Watch methods for reactive updates
    def watch_algorithm_name(self, old: str, new: str):
        """React to algorithm name changes."""
        self._update_algorithm_display()

    def watch_current_phase(self, old: str, new: str):
        """React to phase changes."""
        self._update_phase_display()

    def watch_consensus_reached(self, old: bool, new: bool):
        """React to consensus status changes."""
        self._update_consensus_display()

    def watch_debate_rounds(self, old: int, new: int):
        """React to debate round changes."""
        self._update_rounds_display()

    def watch_representative_agent(self, old: Optional[int], new: Optional[int]):
        """React to representative agent changes."""
        self._update_representative_display()

    def watch_vote_distribution(self, old: Dict[int, int], new: Dict[int, int]):
        """React to vote distribution changes."""
        self._update_vote_distribution()
