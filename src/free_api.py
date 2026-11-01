"""Free demo adapter: calls the public, no-key Pollinations text API.

This is a demo-only adapter, not a Claude Code replacement. It exists
so the workbench can run a real remote task without a paid account.
Do not send sensitive prompts through it: it is a public service,
its availability and output quality are not guaranteed, and it must
not be presented as a vendor agent (Codex/Claude/Kiro).
"""

import sys
import urllib.parse
import urllib.request

prompt = sys.argv[1] if len(sys.argv) > 1 else ""
url = "https://text.pollinations.ai/" + urllib.parse.quote(prompt)
req = urllib.request.Request(url, headers={"User-Agent": "AgentWorkbench/1.0"})
with urllib.request.urlopen(req, timeout=120) as resp:
    sys.stdout.write(resp.read().decode("utf-8", errors="replace"))
