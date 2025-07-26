"""Log viewer widget for displaying system and agent logs."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from rich.text import Text
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Label, Static, TabbedContent, TabPane

from massgen.logging import get_logger

logger = get_logger(__name__)


class LogViewer(Widget):
    """Widget for viewing system and agent logs."""

    # Reactive properties
    log_entries: reactive[List[Dict[str, Any]]] = reactive([])
    max_entries: int = 1000
    filter_agent: reactive[Optional[int]] = reactive(None)
    filter_level: reactive[Optional[str]] = reactive(None)

    def compose(self):
        """Compose the log viewer layout."""
        with Vertical(id="log-viewer-container"):
            yield Label("📁 Log Viewer", id="log-title", classes="panel-title")

            # Log statistics
            yield Static("", id="log-stats", classes="log-stats")

            # Tabbed content for different log views
            with TabbedContent(id="log-tabs"):
                with TabPane("All Logs", id="all-logs-tab"):
                    yield DataTable(id="all-logs-table", show_header=True, show_cursor=True, zebra_stripes=True)

                with TabPane("System Logs", id="system-logs-tab"):
                    yield DataTable(id="system-logs-table", show_header=True, show_cursor=True, zebra_stripes=True)

                with TabPane("Agent Logs", id="agent-logs-tab"):
                    yield DataTable(id="agent-logs-table", show_header=True, show_cursor=True, zebra_stripes=True)

    def on_mount(self):
        """Initialize the log viewer when mounted."""
        # Set up log tables
        self._setup_log_table("all-logs-table")
        self._setup_log_table("system-logs-table")
        self._setup_log_table("agent-logs-table")

        # Update display
        self._update_display()

    def _setup_log_table(self, table_id: str):
        """Set up a log table with columns.

        Args:
            table_id: The ID of the table to set up
        """
        table = self.query_one(f"#{table_id}", DataTable)
        table.add_column("Time", width=12)
        table.add_column("Level", width=8)
        table.add_column("Source", width=12)
        table.add_column("Message", width=None)  # Auto-width

    async def add_entry(self, agent_id: Optional[int], message: str, level: str = "INFO"):
        """Add a log entry.

        Args:
            agent_id: The agent ID (None for system logs)
            message: The log message
            level: The log level
        """
        entry = {
            "timestamp": datetime.now(),
            "agent_id": agent_id,
            "message": message,
            "level": level,
            "source": f"Agent {agent_id}" if agent_id else "System",
        }

        # Add to log entries
        self.log_entries = self.log_entries + [entry]

        # Trim to max entries
        if len(self.log_entries) > self.max_entries:
            self.log_entries = self.log_entries[-self.max_entries :]

        # Update display
        self._update_display()

    def _update_display(self):
        """Update all log displays."""
        self._update_statistics()
        self._update_all_logs()
        self._update_system_logs()
        self._update_agent_logs()

    def _update_statistics(self):
        """Update log statistics."""
        stats_widget = self.query_one("#log-stats", Static)

        if not self.log_entries:
            stats_widget.update(Text("No log entries", style="dim italic"))
            return

        # Calculate statistics
        total_entries = len(self.log_entries)

        # Count by level
        level_counts = {}
        for entry in self.log_entries:
            level = entry.get("level", "INFO")
            level_counts[level] = level_counts.get(level, 0) + 1

        # Count system vs agent logs
        system_logs = sum(1 for e in self.log_entries if e.get("agent_id") is None)
        agent_logs = total_entries - system_logs

        # Build statistics text
        stats_parts = [f"Total: {total_entries}"]
        stats_parts.append(f"System: {system_logs}")
        stats_parts.append(f"Agents: {agent_logs}")

        # Add level breakdown
        if level_counts:
            level_str = ", ".join(f"{level}: {count}" for level, count in level_counts.items())
            stats_parts.append(f"Levels: {level_str}")

        stats_text = " | ".join(stats_parts)
        stats_widget.update(Text(stats_text, style="bright_white"))

    def _update_all_logs(self):
        """Update the all logs table."""
        table = self.query_one("#all-logs-table", DataTable)
        self._populate_log_table(table, self.log_entries)

    def _update_system_logs(self):
        """Update the system logs table."""
        table = self.query_one("#system-logs-table", DataTable)
        system_logs = [e for e in self.log_entries if e.get("agent_id") is None]
        self._populate_log_table(table, system_logs)

    def _update_agent_logs(self):
        """Update the agent logs table."""
        table = self.query_one("#agent-logs-table", DataTable)
        agent_logs = [e for e in self.log_entries if e.get("agent_id") is not None]
        self._populate_log_table(table, agent_logs)

    def _populate_log_table(self, table: DataTable, entries: List[Dict[str, Any]]):
        """Populate a log table with entries.

        Args:
            table: The DataTable to populate
            entries: The log entries to display
        """
        # Clear existing rows
        table.clear()

        # Add rows for each entry
        for entry in entries:
            # Extract entry information
            timestamp = entry.get("timestamp", datetime.now())
            if isinstance(timestamp, datetime):
                time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
            else:
                time_str = str(timestamp)

            level = entry.get("level", "INFO")
            source = entry.get("source", "Unknown")
            message = entry.get("message", "")

            # Level styling
            level_styles = {
                "ERROR": "bright_red bold",
                "WARNING": "bright_yellow",
                "INFO": "bright_white",
                "DEBUG": "dim",
                "TRACE": "dim italic",
            }
            level_style = level_styles.get(level.upper(), "white")

            # Add row to table
            table.add_row(
                Text(time_str, style="dim"),
                Text(level, style=level_style),
                Text(source, style="bright_cyan"),
                Text(message),
            )

    def filter_by_agent(self, agent_id: Optional[int]):
        """Filter logs by agent ID.

        Args:
            agent_id: The agent ID to filter by (None for all)
        """
        self.filter_agent = agent_id
        self._update_display()

    def filter_by_level(self, level: Optional[str]):
        """Filter logs by level.

        Args:
            level: The log level to filter by (None for all)
        """
        self.filter_level = level
        self._update_display()

    def clear_logs(self):
        """Clear all log entries."""
        self.log_entries = []

    def export_logs(self) -> List[Dict[str, Any]]:
        """Export current log entries.

        Returns:
            List of log entry dictionaries
        """
        return self.log_entries.copy()

    def watch_log_entries(self, old: List[Dict[str, Any]], new: List[Dict[str, Any]]):
        """React to log entry changes."""
        # Auto-scroll to bottom if at bottom
        for table_id in ["all-logs-table", "system-logs-table", "agent-logs-table"]:
            try:
                table = self.query_one(f"#{table_id}", DataTable)
                if table.cursor_row >= len(old) - 1:
                    table.move_cursor(row=len(new) - 1)
            except:
                pass
