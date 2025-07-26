"""
Advanced Textual TUI for Canopy Multi-Agent System

Features:
- Real-time streaming updates with reactive programming
- DataTable for agent status tracking
- RichLog for live output streaming
- Advanced animations and visual feedback
- Proper error handling and logging integration
- Modern Textual 5 best practices
"""

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.css.query import NoMatches
from textual.logging import TextualHandler
from textual.reactive import reactive, var
from textual.timer import Timer
from textual.widget import Widget
from textual.widgets import Button, DataTable, Footer, Header, LoadingIndicator, ProgressBar, RichLog, Static

from ..logging import get_logger
from ..types import AgentState, SystemState, VoteDistribution
from .themes import THEMES, ThemeManager

logger = get_logger(__name__)


class AgentProgressWidget(Widget):
    """Advanced agent progress widget with streaming updates."""

    agent_id: reactive[int] = reactive(0)
    model_name: reactive[str] = reactive("")
    status: reactive[str] = reactive("idle")
    progress: reactive[float] = reactive(0.0)
    current_output: reactive[str] = reactive("")

    def __init__(self, agent_id: int, model_name: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_id = agent_id
        self.model_name = model_name
        self._spinner = Spinner("dots", style="cyan")
        self._console = Console()

    def compose(self) -> ComposeResult:
        """Compose the agent progress widget."""
        with Container(classes="agent-progress"):
            yield Static(f"🤖 Agent {self.agent_id}", classes="agent-header")
            yield Static(self.model_name, classes="model-name")
            yield ProgressBar(total=100, classes="progress-bar")
            yield RichLog(classes="agent-output", max_lines=5, markup=True, highlight=True)

    def watch_status(self, status: str) -> None:
        """Update widget when status changes."""
        try:
            header = self.query_one(".agent-header", Static)
            status_icon = {
                "idle": "⏸️",
                "working": "⚡",
                "thinking": "🧠",
                "voting": "🗳️",
                "completed": "✅",
                "failed": "❌",
            }.get(status, "⚪")

            header.update(f"{status_icon} Agent {self.agent_id}")

            # Update progress bar based on status
            progress_bar = self.query_one(".progress-bar", ProgressBar)
            if status == "working":
                progress_bar.advance(10)
            elif status == "completed":
                progress_bar.progress = 100
            elif status == "failed":
                progress_bar.progress = 0

        except NoMatches:
            pass

    def watch_current_output(self, output: str) -> None:
        """Stream new output to the log."""
        if output.strip():
            try:
                log = self.query_one(".agent-output", RichLog)
                timestamp = datetime.now().strftime("%H:%M:%S")
                log.write(f"[dim]{timestamp}[/] {output}")
            except NoMatches:
                pass

    def stream_output(self, text: str) -> None:
        """Stream text output to the agent log."""
        self.current_output = text


class SystemStatusWidget(Widget):
    """Advanced system status widget with real-time metrics."""

    phase: reactive[str] = reactive("initialization")
    consensus_reached: reactive[bool] = reactive(False)
    debate_rounds: reactive[int] = reactive(0)
    total_agents: reactive[int] = reactive(0)
    active_agents: reactive[int] = reactive(0)
    session_duration: reactive[float] = reactive(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._start_time = time.time()

    def compose(self) -> ComposeResult:
        """Compose the system status widget."""
        with Container(classes="system-status"):
            yield Static("🌟 Canopy Multi-Agent System", classes="title")
            yield DataTable(classes="status-table", zebra_stripes=True)

    def on_mount(self) -> None:
        """Initialize the status table."""
        try:
            table = self.query_one(".status-table", DataTable)
            table.add_columns("Metric", "Value", "Status")
            table.add_rows(
                [
                    ("Phase", "initialization", "🔄"),
                    ("Consensus", "No", "❌"),
                    ("Debate Rounds", "0", "⏸️"),
                    ("Active Agents", "0/0", "⏸️"),
                    ("Duration", "00:00", "⏱️"),
                ]
            )
        except Exception as e:
            self.log(f"Error initializing status table: {e}")

    def watch_phase(self, phase: str) -> None:
        """Update phase in the table."""
        self._update_table_cell("Phase", phase, "🔄" if phase != "completed" else "✅")

    def watch_consensus_reached(self, consensus: bool) -> None:
        """Update consensus status."""
        self._update_table_cell("Consensus", "Yes" if consensus else "No", "✅" if consensus else "❌")

    def watch_debate_rounds(self, rounds: int) -> None:
        """Update debate rounds."""
        self._update_table_cell("Debate Rounds", str(rounds), "🔄" if rounds > 0 else "⏸️")

    def watch_active_agents(self, active: int) -> None:
        """Update active agent count."""
        self._update_table_cell("Active Agents", f"{active}/{self.total_agents}", "⚡" if active > 0 else "⏸️")

    def _update_table_cell(self, metric: str, value: str, status: str) -> None:
        """Update a specific cell in the status table."""
        try:
            table = self.query_one(".status-table", DataTable)
            # Find the row for this metric and update it
            for row_key in table.rows:
                row_data = table.get_row(row_key)
                if row_data[0] == metric:
                    table.update_cell(row_key, "Value", value)
                    table.update_cell(row_key, "Status", status)
                    break
        except Exception as e:
            self.log(f"Error updating table cell {metric}: {e}")

    def update_duration(self) -> None:
        """Update session duration."""
        duration = time.time() - self._start_time
        minutes, seconds = divmod(duration, 60)
        time_str = f"{int(minutes):02d}:{int(seconds):02d}"
        self._update_table_cell("Duration", time_str, "⏱️")


class VoteVisualizationWidget(Widget):
    """Advanced vote visualization with real-time updates."""

    vote_distribution: reactive[Dict[int, int]] = reactive({})

    def compose(self) -> ComposeResult:
        """Compose the vote visualization."""
        with Container(classes="vote-viz"):
            yield Static("📊 Vote Distribution", classes="vote-header")
            yield RichLog(classes="vote-display", max_lines=10, markup=True)

    def watch_vote_distribution(self, votes: Dict[int, int]) -> None:
        """Update vote visualization."""
        if not votes:
            return

        try:
            display = self.query_one(".vote-display", RichLog)
            display.clear()

            total_votes = sum(votes.values())
            if total_votes == 0:
                display.write("[dim]No votes cast yet[/]")
                return

            # Create a visual bar chart of votes
            max_votes = max(votes.values())
            for agent_id, count in sorted(votes.items()):
                percentage = (count / total_votes) * 100
                bar_length = int((count / max_votes) * 20) if max_votes > 0 else 0
                bar = "█" * bar_length + "░" * (20 - bar_length)

                display.write(f"Agent {agent_id}: [green]{bar}[/] {count} ({percentage:.1f}%)")

        except Exception as e:
            self.log(f"Error updating vote visualization: {e}")


class AdvancedCanopyTUI(App):
    """
    Advanced Canopy TUI with streaming updates and modern Textual 5 features.

    Features:
    - Real-time agent monitoring with DataTable
    - Streaming output with RichLog
    - Advanced animations and progress indicators
    - Proper error handling and logging
    - Reactive programming patterns
    """

    CSS_PATH = "advanced_styles.css"
    TITLE = "🌟 Canopy - Advanced Multi-Agent TUI"
    SUB_TITLE = "Real-time Streaming Intelligence"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "refresh", "Refresh"),
        Binding("p", "pause", "Pause/Resume"),
        Binding("c", "clear_logs", "Clear Logs"),
        Binding("s", "save_session", "Save Session"),
        Binding("ctrl+t", "toggle_theme", "Theme"),
        Binding("ctrl+c", "quit", "Quit", show=False),
    ]

    # Reactive state
    agents: reactive[Dict[int, AgentProgressWidget]] = reactive({})
    system_state: reactive[SystemState] = reactive(SystemState())
    is_paused: reactive[bool] = reactive(False)
    session_active: reactive[bool] = reactive(False)

    def __init__(self, theme: str = "dark", **kwargs):
        # Remove theme from kwargs before passing to parent
        kwargs.pop("theme", None)
        super().__init__(**kwargs)
        self.theme_name = theme
        self.theme_manager = ThemeManager(theme)
        self._setup_logging()
        self._session_timer: Optional[Timer] = None

    def get_css_path(self) -> list[str | Path]:
        """Override to inject theme CSS."""
        return [self.CSS_PATH]

    @property
    def css(self) -> str:
        """Generate CSS with hardcoded high contrast values."""
        # Read the CSS file which now has hardcoded high contrast values
        css_path = Path(__file__).parent / self.CSS_PATH
        return css_path.read_text() if css_path.exists() else ""

    def _setup_logging(self) -> None:
        """Configure advanced logging with TextualHandler."""
        try:
            # Remove existing handlers
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            # Add Textual handler with custom formatting
            textual_handler = TextualHandler()
            textual_handler.setLevel(logging.INFO)
            formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s", datefmt="%H:%M:%S")
            textual_handler.setFormatter(formatter)

            # Configure root logger
            root_logger.addHandler(textual_handler)
            root_logger.setLevel(logging.INFO)

            # Suppress noisy third-party loggers
            for logger_name in ["httpx", "urllib3", "requests", "openai"]:
                logging.getLogger(logger_name).setLevel(logging.WARNING)

            self.log("✅ Advanced logging system initialized")

        except Exception as e:
            self.log(f"❌ Failed to setup logging: {e}")
            # Fallback: disable logging to prevent console spam
            logging.disable(logging.CRITICAL)

    def compose(self) -> ComposeResult:
        """Compose the advanced TUI layout."""
        yield Header()

        with Vertical(id="main-layout"):
            # Top: System status
            yield SystemStatusWidget(id="system-status", classes="panel")

            with Horizontal(id="content-layout"):
                # Left: Agent panels
                with ScrollableContainer(id="agents-container", classes="panel"):
                    yield Static("🤖 Agents will appear here...", id="agents-placeholder")

                # Right: Logs and visualization
                with Vertical(id="info-panel", classes="panel"):
                    yield RichLog(id="main-log", classes="main-log", markup=True, highlight=True, max_lines=50)
                    yield VoteVisualizationWidget(id="vote-viz")

            # Bottom: Control buttons
            with Horizontal(id="controls", classes="controls"):
                yield Button("⏸️ Pause", id="pause-btn", variant="primary")
                yield Button("🔄 Refresh", id="refresh-btn", variant="default")
                yield Button("🗑️ Clear", id="clear-btn", variant="warning")
                yield Button("💾 Save", id="save-btn", variant="success")

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the advanced TUI."""
        self.log("🚀 Advanced Canopy TUI starting...")

        # Start system monitoring
        self._session_timer = self.set_interval(1.0, self._update_session_metrics)

        # Start periodic refresh
        self.set_interval(0.1, self._refresh_display)

        self.log("✅ TUI initialization complete")

    def _update_session_metrics(self) -> None:
        """Update session metrics periodically."""
        try:
            status_widget = self.query_one("#system-status", SystemStatusWidget)
            status_widget.update_duration()
        except NoMatches:
            pass

    def _refresh_display(self) -> None:
        """Refresh display elements periodically."""
        if not self.is_paused:
            # Update any dynamic content that needs periodic refresh
            pass

    async def add_agent(self, agent_id: int, model_name: str) -> None:
        """Add a new agent to the TUI."""
        try:
            # Create agent widget
            agent_widget = AgentProgressWidget(agent_id=agent_id, model_name=model_name, id=f"agent-{agent_id}")

            # Add to container
            container = self.query_one("#agents-container")

            # Remove placeholder if it exists
            try:
                placeholder = self.query_one("#agents-placeholder")
                placeholder.remove()
            except NoMatches:
                pass

            await container.mount(agent_widget)

            # Update system status
            status_widget = self.query_one("#system-status", SystemStatusWidget)
            status_widget.total_agents += 1

            self.log(f"✅ Added Agent {agent_id} ({model_name})")

        except Exception as e:
            self.log(f"❌ Error adding agent {agent_id}: {e}")

    async def update_agent_status(self, agent_id: int, status: str, output: str = "") -> None:
        """Update agent status and stream output."""
        try:
            agent_widget = self.query_one(f"#agent-{agent_id}", AgentProgressWidget)
            agent_widget.status = status

            if output:
                agent_widget.stream_output(output)

            # Update active agent count
            active_count = len(
                [w for w in self.query(AgentProgressWidget) if w.status in ["working", "thinking", "voting"]]
            )

            status_widget = self.query_one("#system-status", SystemStatusWidget)
            status_widget.active_agents = active_count

        except NoMatches:
            self.log(f"⚠️ Agent {agent_id} not found for status update")
        except Exception as e:
            self.log(f"❌ Error updating agent {agent_id}: {e}")

    async def log_message(self, message: str, level: str = "info") -> None:
        """Log a message to the main log."""
        try:
            main_log = self.query_one("#main-log", RichLog)
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

            level_colors = {"debug": "dim", "info": "blue", "warning": "yellow", "error": "red", "success": "green"}

            color = level_colors.get(level, "white")
            main_log.write(f"[{color}]{timestamp} | {message}[/]")

        except Exception as e:
            # Fallback to app log
            self.log(f"Logging error: {e}")

    async def update_system_state(self, state: SystemState) -> None:
        """Update the system state."""
        try:
            self.system_state = state

            status_widget = self.query_one("#system-status", SystemStatusWidget)
            status_widget.phase = state.phase
            status_widget.consensus_reached = state.consensus_reached
            status_widget.debate_rounds = state.debate_rounds

            # Update vote visualization
            if hasattr(state, "vote_distribution") and state.vote_distribution:
                vote_widget = self.query_one("#vote-viz", VoteVisualizationWidget)
                vote_widget.vote_distribution = state.vote_distribution.votes

        except Exception as e:
            self.log(f"❌ Error updating system state: {e}")

    # Action handlers
    def action_quit(self) -> None:
        """Quit the application."""
        self.log("👋 Shutting down Advanced Canopy TUI...")
        self.exit()

    def action_pause(self) -> None:
        """Pause/resume the session."""
        self.is_paused = not self.is_paused
        try:
            button = self.query_one("#pause-btn", Button)
            button.label = "▶️ Resume" if self.is_paused else "⏸️ Pause"
        except NoMatches:
            pass

        status = "⏸️ Paused" if self.is_paused else "▶️ Resumed"
        self.log(f"{status} session")

    def action_refresh(self) -> None:
        """Refresh the display."""
        self.log("🔄 Refreshing display...")
        self.refresh()

    def action_clear_logs(self) -> None:
        """Clear all logs."""
        try:
            main_log = self.query_one("#main-log", RichLog)
            main_log.clear()

            for agent_widget in self.query(AgentProgressWidget):
                agent_log = agent_widget.query_one(".agent-output", RichLog)
                agent_log.clear()

            self.log("🗑️ Logs cleared")
        except Exception as e:
            self.log(f"❌ Error clearing logs: {e}")

    def action_save_session(self) -> None:
        """Save the current session."""
        self.log("💾 Session save functionality not implemented yet")

    def action_toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        current = self.theme_name
        new_theme = "light" if current == "dark" else "dark"
        self.theme_name = new_theme
        self.theme_manager.set_theme(new_theme)
        # Force CSS refresh by recomposing
        self.stylesheet.clear()
        self.stylesheet.parse(self.css)
        self.refresh(recompose=True)
        self.log(f"🎨 Switched to {new_theme} theme")

    # Button event handlers
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "pause-btn":
            self.action_pause()
        elif button_id == "refresh-btn":
            self.action_refresh()
        elif button_id == "clear-btn":
            self.action_clear_logs()
        elif button_id == "save-btn":
            self.action_save_session()


# Export the main class
__all__ = ["AdvancedCanopyTUI"]
