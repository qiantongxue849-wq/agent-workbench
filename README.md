# Agent Workbench — Kiroween 2026, Frankenstein track

A unified dashboard that dispatches tasks to local CLI agents
(Codex, Grok, Kiro, ChatGPT, Claude Code), monitors their process
status and logs, and tracks each task from running to completed,
failed, or stalled — so multiple incompatible agent tools can be
managed in one place.

This is a new project created for Kiroween 2026. It is not a
re-submission of an earlier repository.

## Why Frankenstein

Each agent tool has its own vendor, CLI, task model and output
format. None of them was designed to be managed together.
Agent Workbench does not pretend otherwise: it adds one task
model on top of them — dispatch, running, completed, failed,
stalled (heartbeat timeout), log view, retry — and derives
status honestly from the underlying process and its log file.
Web-only tools with no task-status interface are not auto-reported;
they are recorded manually, never faked.

## Run (no dependencies, Python 3.11+)

```bash
python3 src/server.py
# open http://127.0.0.1:8000
```

Create a task, pick an adapter, and watch its status change as
the real subprocess runs. A task is only marked completed when
its process exits 0; failed when it exits non-zero; stalled
when it produces no log output for longer than the heartbeat
timeout while still running.

## Layout

- `src/server.py` — task store, process spawner, status polling, dashboard API
- `src/adapters.py` — per-tool command templates (CLI only, no credentials stored)
- `static/index.html` — dashboard: task list, status, log tail
- `.kiro/specs/agent-workbench/` — requirements, design, tasks
- `.kiro/steering/` — product and tech steering

## Safety notes

- No API keys, passwords or tokens are stored by this app.
- Agents run as local subprocesses under the user's own account.
- Do not paste credentials into task prompts or logs.
