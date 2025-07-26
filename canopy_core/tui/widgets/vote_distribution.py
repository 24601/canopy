"""Vote distribution widget for visualizing agent voting patterns."""

from typing import Dict

from rich.text import Text
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, ProgressBar, Static

from ...logging import get_logger

logger = get_logger(__name__)


class VoteDistributionWidget(Widget):
    """Widget for displaying vote distribution across agents."""

    # Reactive vote distribution
    vote_distribution: reactive[Dict[int, int]] = reactive({})

    def compose(self):
        """Compose the vote distribution widget."""
        with Vertical(id="vote-distribution-widget"):
            yield Label("📊 Vote Distribution", id="vote-title", classes="section-title")

            # Vote bars container
            yield Vertical(id="vote-bars-container", classes="vote-bars")

            # Summary statistics
            yield Static("", id="vote-summary", classes="vote-summary")

    def on_mount(self):
        """Initialize the widget when mounted."""
        self._update_display()

    def update_distribution(self, distribution: Dict[int, int]):
        """Update the vote distribution.

        Args:
            distribution: Dictionary mapping agent IDs to vote counts
        """
        self.vote_distribution = distribution.copy()

    def _update_display(self):
        """Update the vote distribution display."""
        bars_container = self.query_one("#vote-bars-container", Vertical)
        summary_widget = self.query_one("#vote-summary", Static)

        # Clear existing bars
        bars_container.remove_children()

        if not self.vote_distribution:
            bars_container.mount(Static("No votes yet", classes="empty-message"))
            summary_widget.update("")
            return

        # Calculate statistics
        total_votes = sum(self.vote_distribution.values())
        max_votes = max(self.vote_distribution.values()) if self.vote_distribution else 0
        num_agents = len(self.vote_distribution)

        # Find leader(s)
        leaders = [agent_id for agent_id, votes in self.vote_distribution.items() if votes == max_votes]

        # Create vote bars
        for agent_id in sorted(self.vote_distribution.keys()):
            votes = self.vote_distribution[agent_id]

            # Create horizontal container for each vote bar
            with bars_container:
                with Horizontal(classes="vote-bar-container"):
                    # Agent label
                    label = Static(f"Agent {agent_id}:", classes="vote-bar-label")

                    # Progress bar showing votes
                    if max_votes > 0:
                        progress = (votes / max_votes) * 100
                    else:
                        progress = 0

                    bar = ProgressBar(total=100, show_eta=False, show_percentage=True, classes="vote-bar")
                    bar.update(progress=progress)

                    # Vote count
                    count = Static(f"{votes} votes", classes="vote-count")

                    bars_container.mount(Horizontal(label, bar, count))

        # Update summary
        summary_parts = []
        summary_parts.append(f"Total Votes: {total_votes}")
        summary_parts.append(f"Participating Agents: {num_agents}")

        if leaders:
            if len(leaders) == 1:
                summary_parts.append(f"Leader: Agent {leaders[0]} ({max_votes} votes)")
            else:
                leader_str = ", ".join(f"Agent {id}" for id in leaders)
                summary_parts.append(f"Tied Leaders: {leader_str} ({max_votes} votes each)")

        summary_text = " | ".join(summary_parts)
        summary_widget.update(Text(summary_text, style="bright_white"))

    def _create_ascii_bar(self, votes: int, max_votes: int, width: int = 20) -> str:
        """Create an ASCII bar chart.

        Args:
            votes: Number of votes for this agent
            max_votes: Maximum votes any agent has
            width: Width of the bar in characters

        Returns:
            ASCII bar string
        """
        if max_votes == 0:
            return ""

        filled = int((votes / max_votes) * width)
        empty = width - filled

        return "█" * filled + "░" * empty

    def watch_vote_distribution(self, old: Dict[int, int], new: Dict[int, int]):
        """React to vote distribution changes."""
        self._update_display()
