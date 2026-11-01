"""CLI adapter templates for Agent Workbench.

Verified on this machine (2026-11-01):
- codex 0.164.0-alpha.9: `codex exec --skip-git-repo-check "<prompt>"`
  runs, then fails with 401 without OpenAI/Codex auth. Template correct,
  auth is the remaining step.
- claude 2.1.316: `claude -p "<prompt>"` is the correct print mode,
  but it reports "Not logged in" without a Claude login/API key.
- kiro-cli 2.37.0: `kiro-cli chat --no-interactive --trust-workspace
  "<prompt>"` is the correct headless form, but it asks for browser
  authentication (`kiro-cli login --use-device-flow`) without a login.
- Grok and ChatGPT have no equivalent local CLI verified here; they
  are not auto-monitored adapters in this MVP.

Commands are built as a list, never a shell string, so prompts cannot
inject extra shell commands. If a tool binary is not installed,
dispatch fails with a clear error instead of a fake running status.
"""

import os
import shutil

ADAPTERS = {
    "demo": ["python3", "-c", "import sys; print(sys.argv[1])", "{prompt}"],
    "codex": ["codex", "exec", "--skip-git-repo-check", "{prompt}"],
    "claude": ["claude", "-p", "{prompt}"],
    "kiro": ["kiro-cli", "chat", "--no-interactive", "--trust-workspace", "{prompt}"],
}


def build_command(adapter, prompt):
    if adapter not in ADAPTERS:
        raise ValueError(f"unknown adapter: {adapter}")
    cmd = [part.replace("{prompt}", prompt) for part in ADAPTERS[adapter]]
    resolved = shutil.which(cmd[0])
    if resolved is None and cmd[0] == "kiro-cli":
        candidate = os.path.expanduser("~/.local/bin/kiro-cli")
        if os.path.isfile(candidate):
            resolved = candidate
    if resolved is None:
        raise FileNotFoundError(f"tool not installed: {cmd[0]}")
    cmd[0] = resolved
    return cmd


def available_adapters():
    return sorted(ADAPTERS)
