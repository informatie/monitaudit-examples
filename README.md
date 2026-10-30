# monitaudit-examples
Here is a highly professional, scannable, and engaging repository description and README.md layout for your monitaudit-examples companion repository.


monitaudit-examples

A collection of ready-to-run blueprints, orchestration scripts, and implementation architectures demonstrating real-time log monitoring and structured auditing using the monitaudit framework.
This repository serves as a practical cookbook for system administrators, DevOps engineers, and Python developers looking to implement lightweight, low-overhead system observability on Ubuntu Server environments.

Demonstration index
-------------------
01: Build monitaudit from the example-specific YAML configuration.
02: Write normal log records with structured attributes.
03: Trace authentication and redact password and token parameters.
04: Trace a database check with defaults and nested secret redaction.
05: Return a value from a traced function and validate that value.
06: Create nested traces with call_id and parent_call_id relationships.
07: Record function_start and function_end with execution duration.
08: Generate function_error with exception details and traceback.
09: Catch the child failure and allow the parent trace to continue.
10: Complete the parent process successfully after handling the failure.

Demonstrates
------------
- build_observability()
- example-specific YAML configuration
- normal logging
- structured attributes
- @obs.trace
- nested traces
- call_id
- parent_call_id
- duration_ms
- parameter capture
- default parameter capture
- password/token/secret redaction
- nested redaction
- successful function completion
- return values
- function_error
- error_type
- error_message
- traceback
- parent continuation after a handled child error
