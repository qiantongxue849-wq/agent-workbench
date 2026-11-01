"""CLI adapter templates for Agent Workbench.

Each adapter maps to a local command-line tool. The prompt is passed
as a single argument; commands are built as a list, never a shell
string, so prompts cannot inject extra shell commands.

If a tool binary is not installed, dispatch fails with a clear
error instead of reporting a fake running status. Fill in the exact
CLI flags for the tools on the demo machine and test each adapter
once before the hackathon submission.
"""

import shutil

# adapter name -> command template. {prompt} is replaced by the task prompt.
ADAPTERS = {
    # Generic adapter used for the demo: runs a harmless local command
    # that prints the prompt back, so status derivation can be shown
    # without any vendor CLI installed.
    "demo": ["python3", "-c", "import sys; print(sys.argv[1])", "{prompt}"],
    # Templates below: uncomment / adjust after verifying the CLI on
    # the demo machine. Do not claim an adapter works until tested.
    # "claude": ["claude", "-p", "{prompt}"],
    # "codex": ["codex", "exec", "{prompt}"],
    # "kiro": ["kiro", "run", "{prompt}"],
}


def build_command(adapter, prompt):
    if adapter not in ADAPTERS:
        raise ValueError(f"unknown adapter: {adapter}")
    cmd = [part.replace("{prompt}", prompt) for part in ADAPTERS[adapter]]
    if not shutil.which(cmd[0]):
        raise FileNotFoundError(f"tool not installed: {cmd[0]}")
    return cmd


def available_adapters():
    return sorted(ADAPTERS)
