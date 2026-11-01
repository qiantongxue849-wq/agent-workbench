# How Kiro was used

- Specs: `.kiro/specs/agent-workbench/requirements.md`,
  `design.md` and `tasks.md` define the task model and the
  honest-status rule before code was written.
- Steering: `.kiro/steering/product.md` (honest status only) and
  `tech.md` (standard library only, no build step) guided the MVP.
- Hooks (planned, not yet wired): a completion hook that marks a
  task completed only when its subprocess exits 0, and a stall
  hook that flags a task when its log stops growing. The current
  server implements both rules in `src/server.py` directly; wiring
  them as Kiro hooks is a remaining task before submission.
- The `.kiro` directory is kept in the repository root and is not
  gitignored, as required for Kiroween submissions.
