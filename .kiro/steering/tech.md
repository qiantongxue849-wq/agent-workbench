# Tech steering

- Python 3.11+, standard library only for the MVP server, so the
  demo runs without installs.
- Tasks are local subprocesses; never shell out with untrusted
  input without quoting.
- Logs are append-only files under `data/logs/` (created at runtime).
- The dashboard is plain HTML/JS polling JSON; no build step.
