"""Main Textual application for MassGen TUI."""

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widgets import Footer, Header, Static

from ..logging import get_logger
from ..types import AgentState, SystemState, VoteDistribution
from .themes import ThemeManager
from .widgets.agent_panel import AgentPanel
from .widgets.log_viewer import LogViewer
from .widgets.system_status_panel import SystemStatusPanel
from .widgets.trace_panel import TracePanel
from .widgets.vote_distribution import VoteDistributionWidget

logger = get_logger(__name__)


class MassGenApp(App):
    """MassGen Terminal User Interface using Textual."""

    CSS_PATH = "styles.css"
    TITLE = "MassGen - Multi-Agent Structured System"
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("l", "toggle_logs", "Toggle Logs"),
        Binding("t", "toggle_traces", "Toggle Traces"),
        Binding("r", "refresh", "Refresh"),
        Binding("ctrl+t", "cycle_theme", "Theme"),
        Binding("ctrl+c", "quit", "Quit", show=False),
    ]

    # Reactive properties
    system_state: reactive[SystemState] = reactive(SystemState())
    agent_states: reactive[Dict[str, AgentState]] = reactive({})
    vote_distribution: reactive[VoteDistribution] = reactive(VoteDistribution())
    current_phase: reactive[str] = reactive("initialization")
    consensus_reached: reactive[bool] = reactive(False)
    debate_rounds: reactive[int] = reactive(0)

    show_logs: reactive[bool] = reactive(False)
    show_traces: reactive[bool] = reactive(False)

    def __init__(self, theme: str = "dark", **kwargs):
        """Initialize the MassGen TUI app."""
        super().__init__(**kwargs)
        self.agent_panels: Dict[str, AgentPanel] = {}
        self.update_lock = asyncio.Lock()
        self.log_files: Dict[str, Path] = {}
        self.theme_manager = ThemeManager(theme)

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Container(id="main-container"):
            # Top section: System status
            yield SystemStatusPanel(id="system-status")

            # Middle section: Agent panels
            with ScrollableContainer(id="agents-container"):
                yield Static("Agents will appear here...", id="agents-placeholder")

            # Bottom section: Vote distribution
            yield VoteDistributionWidget(id="vote-distribution")

        # Optional panels (hidden by default)
        yield LogViewer(id="log-viewer", classes="hidden")
        yield TracePanel(id="trace-panel", classes="hidden")

        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the app when mounted."""
        logger.info("MassGen TUI started")
        # Apply initial theme
        self._apply_theme()
        self.set_interval(0.1, self._update_display)

    def action_quit(self) -> None:
        """Quit the application."""
        logger.info("MassGen TUI shutting down")
        self.exit()

    def action_toggle_logs(self) -> None:
        """Toggle the log viewer panel."""
        self.show_logs = not self.show_logs
        try:
            log_viewer = self.query_one("#log-viewer", LogViewer)
            log_viewer.toggle_class("hidden")
        except NoMatches:
            pass

    def action_toggle_traces(self) -> None:
        """Toggle the trace panel."""
        self.show_traces = not self.show_traces
        try:
            trace_panel = self.query_one("#trace-panel", TracePanel)
            trace_panel.toggle_class("hidden")
        except NoMatches:
            pass

    def action_refresh(self) -> None:
        """Refresh the display."""
        self.refresh()

    def action_cycle_theme(self) -> None:
        """Cycle through available themes."""
        new_theme = self.theme_manager.cycle_theme()
        self._apply_theme()
        self.notify(f"Theme changed to: {new_theme}", severity="information")

    def _apply_theme(self) -> None:
        """Apply the current theme CSS."""
        # Get theme CSS
        theme_css = self.theme_manager.get_theme_css()

        # Update the app's CSS
        # In Textual, we can dynamically update CSS by rebuilding styles
        self.stylesheet.update(theme_css)
        self.refresh(recompose=True)

    async def update_agent(self, agent_id: str, state: AgentState) -> None:
        """Update an agent's state."""
        async with self.update_lock:
            self.agent_states = {**self.agent_states, agent_id: state}

            # Create or update agent panel
            if agent_id not in self.agent_panels:
                await self._create_agent_panel(agent_id)
            else:
                panel = self.agent_panels[agent_id]
                panel.update_state(state)

    async def _create_agent_panel(self, agent_id: str) -> None:
        """Create a new agent panel."""
        try:
            # Remove placeholder if it exists
            try:
                placeholder = self.query_one("#agents-placeholder")
                await placeholder.remove()
            except NoMatches:
                pass

            # Create new agent panel
            container = self.query_one("#agents-container", ScrollableContainer)
            panel = AgentPanel(agent_id=agent_id, id=f"agent-{agent_id}")
            self.agent_panels[agent_id] = panel
            await container.mount(panel)

        except Exception as e:
            logger.error(f"Error creating agent panel: {e}")

    async def update_system_state(self, state: SystemState) -> None:
        """Update the system state."""
        async with self.update_lock:
            self.system_state = state
            self.current_phase = state.phase
            self.consensus_reached = state.consensus_reached
            self.debate_rounds = state.debate_rounds

            # Update system status panel
            try:
                status_panel = self.query_one("#system-status", SystemStatusPanel)
                status_panel.update_state(state)
            except NoMatches:
                pass

    async def update_vote_distribution(self, distribution: VoteDistribution) -> None:
        """Update the vote distribution."""
        async with self.update_lock:
            self.vote_distribution = distribution

            # Update vote distribution widget
            try:
                vote_widget = self.query_one("#vote-distribution", VoteDistributionWidget)
                vote_widget.update_distribution(distribution)
            except NoMatches:
                pass

    async def add_log_entry(self, agent_id: Optional[str], message: str) -> None:
        """Add a log entry."""
        if self.show_logs:
            try:
                log_viewer = self.query_one("#log-viewer", LogViewer)
                await log_viewer.add_entry(agent_id, message)
            except NoMatches:
                pass

    async def add_trace(self, trace_data: Dict[str, Any]) -> None:
        """Add a trace entry."""
        if self.show_traces:
            try:
                trace_panel = self.query_one("#trace-panel", TracePanel)
                await trace_panel.add_trace(trace_data)
            except NoMatches:
                pass

    async def _update_display(self) -> None:
        """Periodic display update."""
        # This can be used for any periodic updates needed

    def watch_current_phase(self, old_phase: str, new_phase: str) -> None:
        """React to phase changes."""
        logger.info(f"Phase changed from {old_phase} to {new_phase}")

    def watch_consensus_reached(self, old: bool, new: bool) -> None:
        """React to consensus status changes."""
        if new:
            logger.info("Consensus reached!")
            self.notify("Consensus reached!", severity="success")
