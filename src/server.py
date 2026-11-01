"""Agent Workbench MVP server (Python standard library only).

Run: python3 src/server.py
Open: http://127.0.0.1:8000

Status is derived honestly from the underlying subprocess:
queued -> running -> completed (exit 0) / failed (exit non-zero)
stalled: running with no log output for > HEARTBEAT_TIMEOUT seconds.
"""

import json
import os
import subprocess
import sys
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(__file__))
from adapters import available_adapters, build_command  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE, "data", "logs")
STATIC_DIR = os.path.join(BASE, "static")
HEARTBEAT_TIMEOUT = 120

os.makedirs(LOG_DIR, exist_ok=True)

tasks = {}
lock = threading.Lock()


def now():
    return time.time()


def refresh(task):
    """Update status from the live process / log file. Caller holds lock."""
    if task["status"] in ("completed", "failed"):
        return
    proc = task.get("_proc")
    if proc is None:
        return
    rc = proc.poll()
    if rc is None:
        if now() - task["last_log_at"] > HEARTBEAT_TIMEOUT:
            task["status"] = "stalled"
        else:
            task["status"] = "running"
        return
    task["exit_code"] = rc
    task["status"] = "completed" if rc == 0 else "failed"
    task["_proc"] = None


def public_unlocked(task):
    refresh(task)
    return {k: v for k, v in task.items() if not k.startswith("_")}


def public(task):
    with lock:
        return public_unlocked(task)


def log_path(task_id):
    return os.path.join(LOG_DIR, f"{task_id}.log")


def watch_log(task):
    """Update last_log_at whenever the log file grows."""
    path = log_path(task["id"])
    size = 0
    while True:
        with lock:
            if task["status"] in ("completed", "failed"):
                return
            try:
                cur = os.path.getsize(path)
            except OSError:
                cur = 0
            if cur > size:
                size = cur
                task["last_log_at"] = now()
        time.sleep(2)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep console quiet
        pass

    def send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/tasks":
            with lock:
                out = [public_unlocked(t) for t in tasks.values()]
            return self.send_json(out)
        if parsed.path.startswith("/api/tasks/") and parsed.path.endswith("/log"):
            task_id = parsed.path.split("/")[3]
            try:
                with open(log_path(task_id), encoding="utf-8", errors="replace") as f:
                    text = f.read()[-8000:]
            except OSError:
                text = ""
            return self.send_json({"log": text})
        if parsed.path == "/":
            parsed_path = "/index.html"
        else:
            parsed_path = parsed.path
        path = os.path.normpath(os.path.join(STATIC_DIR, parsed_path.lstrip("/")))
        if not path.startswith(STATIC_DIR) or not os.path.isfile(path):
            return self.send_json({"error": "not found"}, 404)
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html" if path.endswith(".html") else "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/tasks":
            data = self.read_json()
            adapter = data.get("adapter", "demo")
            prompt = (data.get("prompt") or "").strip()
            if not prompt:
                return self.send_json({"error": "prompt required"}, 400)
            try:
                cmd = build_command(adapter, prompt)
            except (ValueError, FileNotFoundError) as exc:
                return self.send_json({"error": str(exc)}, 400)
            task_id = uuid.uuid4().hex[:12]
            task = {
                "id": task_id, "title": data.get("title") or prompt[:40],
                "prompt": prompt, "adapter": adapter, "status": "running",
                "exit_code": None, "created_at": now(),
                "last_log_at": now(), "_proc": None,
            }
            with open(log_path(task_id), "w", encoding="utf-8") as log:
                proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, text=True)
            task["_proc"] = proc
            with lock:
                tasks[task_id] = task
            threading.Thread(target=watch_log, args=(task,), daemon=True).start()
            return self.send_json(public(task), 201)
        if parsed.path.startswith("/api/tasks/") and parsed.path.endswith("/stop"):
            task_id = parsed.path.split("/")[3]
            with lock:
                task = tasks.get(task_id)
                if task and task.get("_proc"):
                    task["_proc"].terminate()
            return self.send_json({"ok": True})
        if parsed.path.startswith("/api/tasks/") and parsed.path.endswith("/retry"):
            task_id = parsed.path.split("/")[3]
            with lock:
                old = tasks.get(task_id)
                if not old:
                    return self.send_json({"error": "not found"}, 404)
                try:
                    cmd = build_command(old["adapter"], old["prompt"])
                except (ValueError, FileNotFoundError) as exc:
                    return self.send_json({"error": str(exc)}, 400)
                with open(log_path(task_id), "w", encoding="utf-8") as log:
                    proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, text=True)
                old["_proc"] = proc
                old["status"] = "running"
                old["exit_code"] = None
                old["last_log_at"] = now()
            threading.Thread(target=watch_log, args=(old,), daemon=True).start()
            return self.send_json(public(old))
        return self.send_json({"error": "not found"}, 404)


if __name__ == "__main__":
    print("Agent Workbench on http://127.0.0.1:8000  (adapters:", ", ".join(available_adapters()) + ")")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
