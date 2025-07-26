"""
DuckDB-based OpenTelemetry trace exporter for local storage.
Extensions and modifications for pluggable algorithms by Basit Mustafa (@24601).
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Sequence

import duckdb
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.trace import Span, StatusCode


class DuckDBSpanExporter(SpanExporter):
    """Export OpenTelemetry spans to a local DuckDB database."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the DuckDB span exporter.

        Args:
            db_path: Path to the DuckDB database file. If None, uses default location.
        """
        if db_path is None:
            # Create a traces directory in the project
            traces_dir = Path.cwd() / "traces"
            traces_dir.mkdir(exist_ok=True)

            # Use timestamp in filename for unique sessions
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            db_path = traces_dir / f"massgen_traces_{timestamp}.duckdb"

        self.db_path = str(db_path)
        self.conn = duckdb.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        """Create the necessary tables for storing spans."""
        # Main spans table
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS spans (
                span_id VARCHAR PRIMARY KEY,
                trace_id VARCHAR NOT NULL,
                parent_span_id VARCHAR,
                name VARCHAR NOT NULL,
                kind INTEGER,
                start_time BIGINT NOT NULL,
                end_time BIGINT NOT NULL,
                duration_ms DOUBLE,
                status_code INTEGER,
                status_description VARCHAR,
                service_name VARCHAR,
                service_version VARCHAR,
                attributes JSON,
                events JSON,
                links JSON,
                resource JSON,
                context JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Span attributes table for efficient querying
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS span_attributes (
                span_id VARCHAR NOT NULL,
                key VARCHAR NOT NULL,
                value VARCHAR,
                value_type VARCHAR,
                FOREIGN KEY (span_id) REFERENCES spans(span_id)
            )
        """
        )

        # Create indexes for better query performance
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_spans_trace_id ON spans(trace_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_spans_start_time ON spans(start_time)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_spans_name ON spans(name)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_span_attributes_key ON span_attributes(key)")

        # Create useful views
        self.conn.execute(
            """
            CREATE OR REPLACE VIEW trace_summary AS
            SELECT
                trace_id,
                COUNT(*) as span_count,
                MIN(start_time) as trace_start,
                MAX(end_time) as trace_end,
                (MAX(end_time) - MIN(start_time)) / 1000000.0 as duration_ms,
                STRING_AGG(DISTINCT name, ', ') as operations
            FROM spans
            GROUP BY trace_id
        """
        )

        self.conn.execute(
            """
            CREATE OR REPLACE VIEW agent_operations AS
            SELECT
                s.trace_id,
                s.name,
                s.start_time,
                s.duration_ms,
                json_extract_string(s.attributes, '$."agent.id"') as agent_id,
                json_extract_string(s.attributes, '$."agent.model"') as agent_model,
                json_extract_string(s.attributes, '$."massgen.correlation_id"') as correlation_id,
                json_extract_string(s.attributes, '$."massgen.algorithm"') as algorithm
            FROM spans s
            WHERE json_extract_string(s.attributes, '$."agent.id"') IS NOT NULL
        """
        )

    def export(self, spans: Sequence[Span]) -> SpanExportResult:
        """Export spans to DuckDB."""
        try:
            for span in spans:
                # Convert span to exportable format
                span_data = self._span_to_dict(span)

                # Insert main span record
                self.conn.execute(
                    """
                    INSERT INTO spans (
                        span_id, trace_id, parent_span_id, name, kind,
                        start_time, end_time, duration_ms, status_code, status_description,
                        service_name, service_version, attributes, events, links, resource, context
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    [
                        span_data["span_id"],
                        span_data["trace_id"],
                        span_data["parent_span_id"],
                        span_data["name"],
                        span_data["kind"],
                        span_data["start_time"],
                        span_data["end_time"],
                        span_data["duration_ms"],
                        span_data["status_code"],
                        span_data["status_description"],
                        span_data["service_name"],
                        span_data["service_version"],
                        json.dumps(span_data["attributes"]),
                        json.dumps(span_data["events"]),
                        json.dumps(span_data["links"]),
                        json.dumps(span_data["resource"]),
                        json.dumps(span_data["context"]),
                    ],
                )

                # Insert attributes for easier querying
                for key, value in span_data["attributes"].items():
                    value_type = type(value).__name__
                    self.conn.execute(
                        """
                        INSERT INTO span_attributes (span_id, key, value, value_type)
                        VALUES (?, ?, ?, ?)
                    """,
                        [span_data["span_id"], key, str(value), value_type],
                    )

            self.conn.commit()
            return SpanExportResult.SUCCESS

        except Exception as e:
            print(f"Error exporting spans to DuckDB: {e}")
            return SpanExportResult.FAILURE

    def _span_to_dict(self, span) -> dict:
        """Convert a span to a dictionary for storage."""
        context = span.get_span_context()

        # Extract attributes
        attributes = {}
        if span.attributes:
            for key, value in span.attributes.items():
                attributes[key] = value

        # Extract events
        events = []
        if span.events:
            for event in span.events:
                events.append(
                    {
                        "name": event.name,
                        "timestamp": event.timestamp,
                        "attributes": (dict(event.attributes) if event.attributes else {}),
                    }
                )

        # Extract links
        links = []
        if span.links:
            for link in span.links:
                links.append(
                    {
                        "trace_id": format(link.context.trace_id, "032x"),
                        "span_id": format(link.context.span_id, "016x"),
                        "attributes": dict(link.attributes) if link.attributes else {},
                    }
                )

        # Extract resource attributes
        resource = {}
        if span.resource:
            for key, value in span.resource.attributes.items():
                resource[key] = value

        # Calculate duration
        duration_ms = (span.end_time - span.start_time) / 1_000_000 if span.end_time else 0

        return {
            "span_id": format(context.span_id, "016x"),
            "trace_id": format(context.trace_id, "032x"),
            "parent_span_id": (format(span.parent.span_id, "016x") if span.parent else None),
            "name": span.name,
            "kind": span.kind.value,
            "start_time": span.start_time,
            "end_time": span.end_time or span.start_time,
            "duration_ms": duration_ms,
            "status_code": (span.status.status_code.value if span.status else StatusCode.UNSET.value),
            "status_description": span.status.description if span.status else None,
            "service_name": resource.get("service.name", "unknown"),
            "service_version": resource.get("service.version", "unknown"),
            "attributes": attributes,
            "events": events,
            "links": links,
            "resource": resource,
            "context": {
                "trace_id": format(context.trace_id, "032x"),
                "span_id": format(context.span_id, "016x"),
                "trace_flags": context.trace_flags,
                "trace_state": (str(context.trace_state) if context.trace_state else None),
                "is_remote": context.is_remote,
            },
        }

    def shutdown(self) -> None:
        """Shutdown the exporter and close database connection."""
        if hasattr(self, "conn"):
            self.conn.close()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any pending spans."""
        # DuckDB commits are synchronous, so nothing to flush
        return True


def create_trace_analysis_queries(db_path: str):
    """
    Create useful analysis queries for the trace database.

    Returns a dictionary of query functions.
    """
    conn = duckdb.connect(db_path, read_only=True)

    def get_trace_timeline(trace_id: str):
        """Get timeline of all spans in a trace."""
        return conn.execute(
            """
            SELECT
                name,
                span_id,
                parent_span_id,
                (start_time - (SELECT MIN(start_time) FROM spans WHERE trace_id = ?)) / 1000000.0 as relative_start_ms,
                duration_ms,
                json_extract_string(attributes, '$.["agent.id"]') as agent_id,
                status_code
            FROM spans
            WHERE trace_id = ?
            ORDER BY start_time
        """,
            [trace_id, trace_id],
        ).fetchdf()

    def get_agent_activity(agent_id: str):
        """Get all activity for a specific agent."""
        return conn.execute(
            """
            SELECT
                trace_id,
                name,
                start_time,
                duration_ms,
                json_extract_string(attributes, '$.["massgen.phase"]') as phase,
                status_code
            FROM spans
            WHERE json_extract_string(attributes, '$.["agent.id"]') = ?
            ORDER BY start_time
        """,
            [agent_id],
        ).fetchdf()

    def get_slow_operations(threshold_ms: float = 1000):
        """Find operations slower than threshold."""
        return conn.execute(
            """
            SELECT
                name,
                duration_ms,
                trace_id,
                span_id,
                json_extract_string(attributes, '$.["agent.id"]') as agent_id,
                json_extract_string(attributes, '$.["massgen.algorithm"]') as algorithm
            FROM spans
            WHERE duration_ms > ?
            ORDER BY duration_ms DESC
        """,
            [threshold_ms],
        ).fetchdf()

    def get_error_spans():
        """Get all spans with errors."""
        return conn.execute(
            """
            SELECT
                name,
                trace_id,
                span_id,
                status_description,
                json_extract_string(attributes, '$.["agent.id"]') as agent_id,
                events
            FROM spans
            WHERE status_code = 2  -- ERROR status
            ORDER BY start_time DESC
        """
        ).fetchdf()

    def get_consensus_patterns():
        """Analyze consensus patterns across traces."""
        return conn.execute(
            """
            WITH consensus_spans AS (
                SELECT
                    trace_id,
                    json_extract_string(attributes, '$.["massgen.algorithm"]') as algorithm,
                    json_extract_string(attributes, '$.["consensus.rounds"]') as debate_rounds,
                    json_extract_string(attributes, '$.["consensus.reached"]') as consensus_reached,
                    duration_ms
                FROM spans
                WHERE name LIKE '%consensus%'
            )
            SELECT
                algorithm,
                COUNT(*) as trace_count,
                AVG(CAST(debate_rounds AS INTEGER)) as avg_debate_rounds,
                SUM(CASE WHEN consensus_reached = 'true' THEN 1 ELSE 0 END) as consensus_count,
                AVG(duration_ms) as avg_duration_ms
            FROM consensus_spans
            GROUP BY algorithm
        """
        ).fetchdf()

    return {
        "get_trace_timeline": get_trace_timeline,
        "get_agent_activity": get_agent_activity,
        "get_slow_operations": get_slow_operations,
        "get_error_spans": get_error_spans,
        "get_consensus_patterns": get_consensus_patterns,
        "conn": conn,
    }
