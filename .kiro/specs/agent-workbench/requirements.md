# Requirements — Agent Workbench

## Goal
One local dashboard to dispatch, monitor and review tasks run by
incompatible local CLI agent tools.

## Requirements
1. A user can create a task with a title, prompt and an adapter
   (claude, codex, kiro, or a generic shell adapter).
2. Dispatching a task starts a real local subprocess; status is
   derived from that process, never hard-coded.
3. Status values are exactly: queued, running, completed, failed,
   stalled. Stalled means running with no log output for longer
   than the heartbeat timeout.
4. A user can view the live log tail for any task.
5. A user can retry a failed task and can stop a running task.
6. Web-only tools with no status interface must not be shown as
   auto-monitored; they may only be recorded manually.
7. No credentials are stored in the task store or logs.
