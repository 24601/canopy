# OpenTelemetry Tracing for MassGen Canopy

This document describes the OpenTelemetry (OTel) tracing integration added to MassGen Canopy.

## Overview

The tracing system provides comprehensive observability for all MassGen operations, including:
- Agent interactions and voting patterns
- Algorithm execution flow
- Performance metrics and bottlenecks
- Distributed correlation across components

## Default Configuration

By default, traces are stored in a local DuckDB database for easy analysis without external dependencies.

## Environment Variables

Configure tracing behavior with these environment variables:

- `MASSGEN_TRACE_ENABLED` (default: `"true"`): Enable/disable tracing
- `MASSGEN_TRACE_BACKEND` (default: `"duckdb"`): Backend to use (`duckdb`, `otlp`, `jaeger`, `console`)
- `MASSGEN_TRACE_DB_PATH` (default: auto-generated): Path to DuckDB database file
- `MASSGEN_OTLP_ENDPOINT` (default: `"http://localhost:4317"`): OTLP endpoint for remote tracing
- `MASSGEN_JAEGER_ENDPOINT` (default: `"localhost:6831"`): Jaeger endpoint
- `MASSGEN_SERVICE_NAME` (default: `"massgen-canopy"`): Service name in traces

## Trace Storage

When using the default DuckDB backend, traces are stored in:
```
traces/massgen_traces_YYYYMMDD_HHMMSS.duckdb
```

## Analyzing Traces

### Using the Test Script

Run the test script to see trace analysis:
```bash
python test_tracing.py --analyze-only
```

### Direct DuckDB Queries

Connect to the trace database and run SQL queries:

```python
import duckdb
conn = duckdb.connect('traces/massgen_traces_*.duckdb')

# View all spans
conn.execute("SELECT * FROM spans LIMIT 10").fetchdf()

# Get trace summary
conn.execute("SELECT * FROM trace_summary").fetchdf()

# View agent operations
conn.execute("SELECT * FROM agent_operations").fetchdf()
```

### Available Views

1. **trace_summary**: Overview of all traces
2. **agent_operations**: Agent-specific operations with correlation IDs

### Key Attributes Tracked

- `agent.id`: Agent identifier
- `agent.model`: Model used by agent
- `massgen.correlation_id`: Unique ID for cross-component tracking
- `massgen.orchestration_id`: Orchestration session ID
- `massgen.algorithm`: Algorithm being used
- `task.id`: Task identifier
- `massgen.phase`: Current phase (working, voting, consensus, etc.)

## Integrating with External Backends

### Jaeger

1. Start Jaeger:
```bash
docker run -d --name jaeger \
  -p 6831:6831/udp \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

2. Set environment variables:
```bash
export MASSGEN_TRACE_BACKEND=jaeger
export MASSGEN_JAEGER_ENDPOINT=localhost:6831
```

3. View traces at http://localhost:16686

### OTLP Collector

1. Configure OTLP endpoint:
```bash
export MASSGEN_TRACE_BACKEND=otlp
export MASSGEN_OTLP_ENDPOINT=http://localhost:4317
```

2. Traces will be sent to any OTLP-compatible backend (Arize Phoenix, Datadog, etc.)

## Performance Impact

The tracing system is designed for minimal overhead:
- Async span export
- Batch processing
- Configurable sampling (future enhancement)

## Troubleshooting

### No Traces Appearing

1. Check if tracing is enabled:
```bash
echo $MASSGEN_TRACE_ENABLED
```

2. Verify the traces directory exists and has write permissions

3. Check for errors in console output when using `console` backend:
```bash
export MASSGEN_TRACE_BACKEND=console
```

### Database Locked Errors

The DuckDB file may be locked if another process is reading it. Ensure only one process accesses the database at a time.

## Future Enhancements

- [ ] Sampling configuration for high-volume scenarios
- [ ] Real-time trace streaming
- [ ] GitHub Pages UI for trace visualization
- [ ] Trace data included in benchmark submissions
- [ ] Custom span processors for specific analysis
