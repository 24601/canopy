"""
Missing widgets for the Canopy TUI
"""

from datetime import datetime, timedelta

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import ProgressBar, Static


class SystemStatusWidget(Widget):
    """System status display widget."""

    status: reactive[str] = reactive("Initializing...")
    agent_count: reactive[int] = reactive(0)
    uptime: reactive[str] = reactive("00:00:00")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = datetime.now()

    def compose(self) -> ComposeResult:
        """Compose the system status widget."""
        with Vertical():
            yield Static("🌟 Canopy Multi-Agent System", classes="title")
            yield Static(self.status, id="status-text", classes="status")
            yield Static(f"Agents: {self.agent_count}", id="agent-count", classes="metric")
            yield Static(f"Uptime: {self.uptime}", id="uptime-text", classes="metric")

    def update_duration(self) -> None:
        """Update the uptime display."""
        duration = datetime.now() - self.start_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.uptime = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

        try:
            uptime_widget = self.query_one("#uptime-text", Static)
            uptime_widget.update(f"Uptime: {self.uptime}")
        except:
            pass

    def update_status(self, status: str) -> None:
        """Update the system status."""
        self.status = status
        try:
            status_widget = self.query_one("#status-text", Static)
            status_widget.update(status)
        except:
            pass

    def update_agent_count(self, count: int) -> None:
        """Update the agent count."""
        self.agent_count = count
        try:
            count_widget = self.query_one("#agent-count", Static)
            count_widget.update(f"Agents: {count}")
        except:
            pass


class VoteVisualizationWidget(Widget):
    """Vote visualization widget."""

    votes: reactive[dict] = reactive({})
    consensus: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        """Compose the vote visualization widget."""
        with Vertical():
            yield Static("🗳️ Voting Status", classes="title")
            yield Static("No votes yet", id="vote-status", classes="vote-info")
            yield ProgressBar(total=100, id="consensus-progress", classes="consensus-bar")

    def update_votes(self, votes: dict) -> None:
        """Update the vote visualization."""
        self.votes = votes

        if not votes:
            status_text = "No votes yet"
            progress = 0
        else:
            total_votes = sum(votes.values())
            if total_votes > 0:
                max_votes = max(votes.values())
                consensus_pct = (max_votes / total_votes) * 100

                # Create vote summary
                vote_items = []
                for option, count in votes.items():
                    pct = (count / total_votes) * 100
                    vote_items.append(f"{option}: {count} ({pct:.1f}%)")

                status_text = " | ".join(vote_items)
                progress = consensus_pct
            else:
                status_text = "No votes cast"
                progress = 0

        try:
            status_widget = self.query_one("#vote-status", Static)
            status_widget.update(status_text)

            progress_widget = self.query_one("#consensus-progress", ProgressBar)
            progress_widget.update(progress=progress)
        except:
            pass
