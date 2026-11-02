# MonitAudit Examples

The MonitAudit examples demonstrate how to configure and use MonitAudit in
practical Python applications.

The examples cover basic logging, tracing, parameter capture, redaction,
exception handling, multiple sinks, Delta storage, sink failure handling and
concurrent execution.

The complete example suite is executed with:

```bash
./run_examples.sh
```

`run_examples.sh` is the recommended entry point for running all examples.

## Quick start

From the MonitAudit project root:

```bash
uv sync
cd examples

export MONITAUDIT_ENV=dev

chmod +x run_examples.sh
./run_examples.sh
```

Generated output can be inspected under:

```text
output/
```

## Setup

### Requirements

The examples require:

- Python
- `uv`
- MonitAudit and its dependencies

Check that Python and `uv` are available:

```bash
python --version
uv --version
```

Install or synchronise the project environment from the MonitAudit project
root:

```bash
uv sync
```

Then enter the examples directory:

```bash
cd examples
```

The examples are now ready to run.

## Running the examples

The example suite is controlled by:

```text
run_examples.sh
```

If required, make the script executable:

```bash
chmod +x run_examples.sh
```

Run the complete suite with:

```bash
./run_examples.sh
```

The individual `main_<example>.py` programs are described later in this README
so that it is clear which MonitAudit feature each example demonstrates.

The normal workflow is to use `run_examples.sh` rather than execute individual
Python scripts manually.

## Environment

The examples can use the MonitAudit runtime environment configuration.

For development:

```bash
export MONITAUDIT_ENV=dev
```

Environment selection can use:

- `MONITAUDIT_ENVIRONMENT`
- `MONITAUDIT_ENV`
- `ENV`

For normal development use:

```bash
export MONITAUDIT_ENV=dev
```

## Directory structure

The examples are organised into scripts, configuration, input data and
generated output.

```text
examples/
├── README.md
├── run_examples.sh
│
├── config/
│   ├── main_basic.yaml
│   ├── main_file_sink.yaml
│   ├── main_json_sink.yaml
│   ├── main_delta_local.yaml
│   └── main_all_sinks.yaml
│
├── data/
│   └── ...
│
├── output/
│   ├── file_sink/
│   ├── json_sink/
│   └── delta_sink/
│
└── scripts/
    ├── basic/
    ├── tracing/
    ├── parameters/
    ├── redaction/
    ├── exceptions/
    ├── sinks/
    └── concurrency/
```

### `scripts/`

The `scripts/` directory contains the runnable Python examples.

The principal example programs use the naming convention:

```text
main_<example>.py
```

These programs are executed by `run_examples.sh`.

### `config/`

The `config/` directory contains YAML runtime configuration used by the
examples.

Where an example requires configuration, it is loaded from this directory.

Configuration values such as sink paths and Delta table names should remain in
YAML instead of being duplicated as constants inside the Python programs.

### `data/`

The `data/` directory contains input data required by examples.

Keeping input data separate from the Python programs makes the examples easier
to understand and modify.

### `output/`

Generated output is written below:

```text
output/
```

Typical output locations include:

```text
output/file_sink/
output/json_sink/
output/delta_sink/
```

This keeps generated files separate from scripts, configuration and input data.

## Configuration

A typical MonitAudit example configuration has the following structure:

```yaml
monitaudit:
  application: monitaudit-example

  global:
    logging:
      level: DEBUG

    timer: true
    parameters: true
    max_parameter_length: 1000
    sink_failure_mode: continue

  sinks:
    console_sink:
      enabled: true
```

Individual examples enable additional sinks or settings where required.

The YAML configuration should be treated as the source of truth for sink
settings such as paths and Delta table names.

### `ConsoleSink`

`ConsoleSink` writes MonitAudit records to standard output.

Example configuration:

```yaml
console_sink:
  enabled: true
```

Typical uses include:

- development
- interactive execution
- immediate diagnostics

### `FileSink`

`FileSink` writes records to a persistent log file.

Example configuration:

```yaml
file_sink:
  enabled: true
  path: output/file_sink/main_file_sink.log
```

Typical uses include:

- persistent application logging
- local development
- human-readable diagnostic logs

### `JsonSink`

`JsonSink` writes structured records using JSON Lines.

Example configuration:

```yaml
json_sink:
  enabled: true
  path: output/json_sink/main_json_sink.jsonl
```

Typical uses include:

- structured logging
- machine-readable output
- downstream data processing
- ingestion into analytics platforms

### `DeltaSink`

`DeltaSink` writes structured MonitAudit records to Delta storage.

Example configuration:

```yaml
delta_sink:
  enabled: true
  table: main.delta.local
  path: output/delta_sink/main_delta_local
```

The table and path should come from YAML configuration.

Typical uses include:

- data-platform workloads
- structured observability
- audit datasets
- analytics
- querying logging records as structured data

## Example catalogue

The following sections describe the individual main programs in the example
suite.

All examples are normally executed through:

```bash
./run_examples.sh
```

### `main_basic.py`

Category: Basic logging

Purpose: Introduction to MonitAudit.

`main_basic.py` demonstrates the basic structure of a MonitAudit-enabled
application.

It is the recommended starting point for understanding how MonitAudit fits
into normal Python application code.

It demonstrates:

- loading MonitAudit configuration
- initialising MonitAudit
- creating a logger
- writing normal application log records
- producing structured logging output
- executing a small MonitAudit-enabled application

The basic flow is:

```text
Configuration
     |
     v
MonitAudit
     |
     v
Logger
     |
     v
Application logging
```

Use this example first when exploring MonitAudit.

### `main_file_sink.py`

Category: Sinks

Purpose: Persistent logging with `FileSink`.

`main_file_sink.py` demonstrates how MonitAudit records can be written to a
normal log file.

It demonstrates:

- enabling `FileSink`
- reading the output path from YAML
- writing persistent log records
- separating application code from sink configuration
- inspecting generated log output

Example configuration:

```yaml
file_sink:
  enabled: true
  path: output/file_sink/main_file_sink.log
```

Output:

```text
output/file_sink/main_file_sink.log
```

Use this example when an application requires persistent, human-readable log
files.

### `main_json_sink.py`

Category: Sinks

Purpose: Structured JSON Lines logging with `JsonSink`.

`main_json_sink.py` demonstrates writing structured MonitAudit records using
`JsonSink`.

Each output line represents a structured logging record.

It demonstrates:

- enabling `JsonSink`
- reading the output path from YAML
- serialising structured MonitAudit records
- writing JSON Lines output
- inspecting generated JSON records

Example configuration:

```yaml
json_sink:
  enabled: true
  path: output/json_sink/main_json_sink.jsonl
```

Output:

```text
output/json_sink/main_json_sink.jsonl
```

Use this example when observability records need to be processed by other
applications, data pipelines or analytics platforms.

### `main_delta_local.py`

Category: Sinks and Delta

Purpose: Write MonitAudit records to local Delta storage.

`main_delta_local.py` demonstrates `DeltaSink` using a local Delta location.

It demonstrates:

- enabling `DeltaSink`
- reading the Delta table name from YAML
- reading the Delta storage path from YAML
- writing structured MonitAudit records to Delta
- creating local Delta output
- validating persistent structured observability data

Example configuration:

```yaml
delta_sink:
  enabled: true
  table: main.delta.local
  path: output/delta_sink/main_delta_local
```

Output:

```text
output/delta_sink/main_delta_local
```

The Delta table and storage path belong in the configuration rather than as
separate hard-coded values in the Python example.

Use this example as the starting point for MonitAudit Delta integration.

### `main_query_delta.py`

Category: Delta

Purpose: Query and inspect Delta output.

`main_query_delta.py` complements `main_delta_local.py` by demonstrating how
the resulting Delta records can be inspected.

The relationship between the examples is:

```text
main_delta_local.py
        |
        v
    DeltaSink
        |
        v
   Delta data
        |
        v
main_query_delta.py
        |
        v
 Inspect records
```

It demonstrates:

- opening Delta output
- inspecting persisted MonitAudit records
- querying structured observability data
- validating records after persistence

The Delta location used by the query should correspond to the location
configured for the Delta example.

Use `main_delta_local.py` and `main_query_delta.py` together to understand the
Delta write and query workflow.

### `main_all_sinks.py`

Category: Sinks

Purpose: Use several MonitAudit sinks in the same application.

`main_all_sinks.py` demonstrates how one application can publish MonitAudit
records to several configured destinations.

A typical configuration enables:

```yaml
sinks:
  console_sink:
    enabled: true

  json_sink:
    enabled: true
    path: output/json_sink/main_all_sinks.jsonl

  file_sink:
    enabled: true
    path: output/file_sink/main_all_sinks.log

  delta_sink:
    enabled: true
    table: main.logging.all_sinks
    path: output/delta_sink/main_all_sinks
```

It demonstrates:

- `ConsoleSink`
- `FileSink`
- `JsonSink`
- `DeltaSink`
- multiple sinks enabled together
- one logging flow publishing to multiple destinations

Possible output locations include:

```text
output/file_sink/
output/json_sink/
output/delta_sink/
```

Console output is displayed directly in the terminal.

This example is useful as an integration example after experimenting with the
individual sinks.

## Tracing examples

Tracing provides function-level observability.

For a successful traced function call, the lifecycle is conceptually:

```text
FUNCTION_START
      |
      v
Function execution
      |
      v
FUNCTION_END
```

For an unsuccessful function call:

```text
FUNCTION_START
      |
      v
Function execution
      |
      v
Exception
      |
      v
FUNCTION_ERROR
```

The tracing examples demonstrate:

- `FUNCTION_START`
- `FUNCTION_END`
- `FUNCTION_ERROR`
- execution timing
- function instrumentation

Tracing is useful when important application operations require consistent
observability without repetitive start and end logging statements.

## Parameter capture examples

MonitAudit can capture function arguments when tracing functions.

For example:

```python
def process_customer(customer_id: int, region: str) -> None:
    ...
```

Parameter logging can be enabled with configuration such as:

```yaml
global:
  parameters: true
```

The maximum parameter representation length can be controlled with:

```yaml
global:
  max_parameter_length: 1000
```

The examples demonstrate:

- parameter capture
- structured representation of inputs
- limiting large parameter representations
- combining parameters with tracing information

Parameter capture provides additional context when investigating function
execution.

## Redaction examples

Parameter capture can expose information that should not appear directly in
logging output.

The redaction examples demonstrate how MonitAudit handles values that should
not be exposed in observability records.

Relevant values can include:

- credentials
- tokens
- secrets
- connection information
- application-sensitive values

Redaction is particularly important when parameter capture is enabled.

Applications should verify their redaction configuration before logging objects
that may contain sensitive data.

## Exception and traceback examples

The exception examples demonstrate MonitAudit behaviour when application code
fails.

They demonstrate:

- exception logging
- structured error information
- stack traces
- traceback preservation
- `FUNCTION_ERROR` records
- traced function failures

MonitAudit adds diagnostic context while preserving the original application
failure information.

## Sink failure examples

Logging infrastructure can fail independently of the application operation
being observed.

For example:

```text
Application
     |
     v
 MonitAudit
     |
     +--> ConsoleSink   OK
     |
     +--> FileSink      OK
     |
     +--> JsonSink      FAILED
```

The sink failure examples demonstrate how MonitAudit behaves when a configured
output destination cannot write its record.

Example configuration:

```yaml
global:
  sink_failure_mode: continue
```

These examples are particularly useful when applications use several sinks and
need defined behaviour when one destination becomes unavailable.

## Concurrency examples

The concurrency examples demonstrate MonitAudit in applications using
`ThreadPoolExecutor`.

The execution pattern is conceptually:

```text
Main thread
     |
     +--> Worker 1
     |
     +--> Worker 2
     |
     +--> Worker 3
     |
     +--> Worker n
```

These examples exercise situations where several operations generate
MonitAudit records concurrently.

They are relevant to applications using:

- `ThreadPoolExecutor`
- worker pools
- parallel operations
- concurrent processing

## Generated output

After running:

```bash
./run_examples.sh
```

inspect:

```text
output/
```

Depending on the examples and enabled sinks, generated output can include:

```text
output/
├── file_sink/
│   └── log files
│
├── json_sink/
│   └── JSON Lines files
│
└── delta_sink/
    └── Delta data
```

`ConsoleSink` output appears directly in the terminal.

## Recommended learning path

A useful order for understanding MonitAudit is:

1. Basic logging
2. Function tracing
3. Parameter capture
4. Redaction
5. Exception handling
6. `FileSink`
7. `JsonSink`
8. `DeltaSink`
9. Delta queries
10. Multiple sinks
11. Sink failure handling
12. Concurrency

You do not need to start these examples individually.

Run the suite with:

```bash
./run_examples.sh
```

## Troubleshooting

### `run_examples.sh`: permission denied

Make the runner executable:

```bash
chmod +x run_examples.sh
```

Then run:

```bash
./run_examples.sh
```

### Missing Python dependencies

Synchronise the project environment:

```bash
uv sync
```

Then rerun:

```bash
./run_examples.sh
```

### Configuration cannot be found

Verify that the examples are being executed from the expected directory:

```bash
cd examples
```

Check that the required configuration exists under:

```text
config/
```

### `FileSink` output is missing

Check that `FileSink` is enabled in the corresponding YAML configuration:

```yaml
file_sink:
  enabled: true
```

Then inspect:

```text
output/file_sink/
```

### `JsonSink` output is missing

Check that `JsonSink` is enabled:

```yaml
json_sink:
  enabled: true
```

Then inspect:

```text
output/json_sink/
```

### `DeltaSink` output is missing

Verify the Delta configuration:

```yaml
delta_sink:
  enabled: true
  table: main.delta.local
  path: output/delta_sink/main_delta_local
```

Then inspect:

```text
output/delta_sink/
```

The table and path should come from YAML configuration.

### Output appears in the wrong directory

Check the path in the corresponding YAML file.

For example:

```yaml
json_sink:
  enabled: true
  path: output/json_sink/main_json_sink.jsonl
```

Avoid maintaining a second independent copy of the same output path inside the
Python example.

### Existing output affects an example

Some examples create persistent files or Delta data.

When troubleshooting, check whether output from an earlier execution is still
present under:

```text
output/
```

Do not remove existing output when it is intentionally required by another
example, such as an example that queries previously generated Delta data.

## Using the examples as templates

The examples can also serve as starting points for integrating MonitAudit into
other applications.

A typical integration follows this flow:

```text
Application configuration
          |
          v
Load MonitAudit configuration
          |
          v
Configure sinks
          |
          v
Create logger
          |
          v
Run application
          |
          +--> Logging
          |
          +--> Tracing
          |
          +--> Error reporting
          |
          v
Configured sinks
```

For a basic integration, examine:

```text
main_basic.py
```

For persistent text logging, examine:

```text
main_file_sink.py
```

For structured JSON logging, examine:

```text
main_json_sink.py
```

For Delta storage and querying, examine:

```text
main_delta_local.py
main_query_delta.py
```

For an application using several destinations, examine:

```text
main_all_sinks.py
```

## Summary

The MonitAudit example suite demonstrates the main library capabilities through
small, practical applications.

The examples cover:

- basic structured logging
- configuration loading
- function tracing
- execution timing
- parameter capture
- parameter length handling
- redaction
- exception handling
- traceback preservation
- `ConsoleSink`
- `FileSink`
- `JsonSink`
- `DeltaSink`
- Delta queries
- multiple sinks
- sink failure isolation
- concurrent execution

The standard entry point for the complete example suite is:

```bash
./run_examples.sh
```

