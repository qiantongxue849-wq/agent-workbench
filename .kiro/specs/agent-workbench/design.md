# Design — Agent Workbench

## Task model
Task { id, title, prompt, adapter, status, pid, log_path,
created_at, updated_at, last_log_at, exit_code }

## Status derivation
- queued: created, not yet started
- running: process alive
- completed: process exited with code 0
- failed: process exited with non-zero code, or spawn failed
- stalled: running and now - last_log_at > heartbeat timeout (120s)

## Adapters
Each adapter is a command template that receives the prompt.
Adapters are CLI only. If the tool binary is missing, dispatch
fails with a clear error instead of a fake running status.
See `src/adapters.py` for the template table; fill in the exact
CLI flags for the tools installed on the demo machine before
the hackathon submission, and test each adapter once.

## Dashboard
A single page polling `/api/tasks` every 2 seconds, showing
status, adapter, log tail and retry/stop actions.
