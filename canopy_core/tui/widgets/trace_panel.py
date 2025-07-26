"""Trace panel widget for displaying OpenTelemetry traces."""

from datetime import datetime
from typing import Any, Dict, List

from rich.text import Text
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Label, Static

from ...logging import get_logger

logger = get_logger(__name__)


class TracePanel(Widget):
    """Panel for displaying OpenTelemetry trace information."""

    # Reactive properties
    traces: reactive[List[Dict[str, Any]]] = reactive([])
    max_traces: int = 100

    def compose(self):
        """Compose the trace panel layout."""
        with Vertical(id="trace-panel-container"):
            yield Label("🔍 Traces", id="trace-title", classes="panel-title")

            # Trace statistics
            yield Static("", id="trace-stats", classes="trace-stats")

            # Trace table
            yield DataTable(id="trace-table", show_header=True, show_cursor=True, zebra_stripes=True)

    def on_mount(self):
        """Initialize the panel when mounted."""
        # Set up trace table columns
        table = self.query_one("#trace-table", DataTable)
        table.add_column("Time", width=12)
        table.add_column("Operation", width=20)
        table.add_column("Duration", width=10)
        table.add_column("Status", width=10)
        table.add_column("Agent", width=8)

        # Update display
        self._update_display()

    async def add_trace(self, trace_data: Dict[str, Any]):
        """Add a new trace entry.

        Args:
            trace_data: Dictionary containing trace information
        """
        # Add to traces list
        self.traces = self.traces + [trace_data]

        # Trim to max traces
        if len(self.traces) > self.max_traces:
            self.traces = self.traces[-self.max_traces :]

        # Update display
        self._update_display()

    def _update_display(self):
        """Update the trace display."""
        self._update_statistics()
        self._update_trace_table()

    def _update_statistics(self):
        """Update trace statistics."""
        stats_widget = self.query_one("#trace-stats", Static)

        if not self.traces:
            stats_widget.update(Text("No traces collected", style="dim italic"))
            return

        # Calculate statistics
        total_traces = len(self.traces)

        # Count by status
        status_counts = {}
        for trace in self.traces:
            status = trace.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        # Count by operation
        operation_counts = {}
        for trace in self.traces:
            operation = trace.get("operation", "unknown")
            operation_counts[operation] = operation_counts.get(operation, 0) + 1

        # Build statistics text
        stats_parts = [f"Total: {total_traces}"]

        # Add status breakdown
        if status_counts:
            status_str = ", ".join(f"{status}: {count}" for status, count in status_counts.items())
            stats_parts.append(f"Status: {status_str}")

        stats_text = " | ".join(stats_parts)
        stats_widget.update(Text(stats_text, style="bright_white"))

    def _update_trace_table(self):
        """Update the trace table."""
        table = self.query_one("#trace-table", DataTable)

        # Clear existing rows
        table.clear()

        # Add rows for each trace
        for trace in self.traces:
            # Extract trace information
            timestamp = trace.get("timestamp", datetime.now())
            if isinstance(timestamp, datetime):
                time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]
            else:
                time_str = str(timestamp)

            operation = trace.get("operation", "unknown")
            duration = trace.get("duration_ms", 0)
            status = trace.get("status", "unknown")
            agent_id = trace.get("agent_id", "-")

            # Format duration
            if duration > 1000:
                duration_str = f"{duration/1000:.1f}s"
            else:
                duration_str = f"{duration}ms"

            # Status styling
            status_styles = {
                "success": "bright_green",
                "error": "bright_red",
                "warning": "bright_yellow",
                "running": "bright_blue",
                "unknown": "dim",
            }
            status_style = status_styles.get(status.lower(), "white")

            # Add row to table
            table.add_row(
                Text(time_str, style="dim"),
                Text(operation, style="bright_cyan"),
                Text(duration_str, style="bright_magenta"),
                Text(status, style=status_style),
                Text(str(agent_id), style="bright_white"),
            )

    def watch_traces(self, old: List[Dict[str, Any]], new: List[Dict[str, Any]]):
        """React to trace list changes."""
        self._update_display()

    def clear_traces(self):
        """Clear all traces."""
        self.traces = []

    def export_traces(self) -> List[Dict[str, Any]]:
        """Export current traces.

        Returns:
            List of trace dictionaries
        """
        return self.traces.copy()
