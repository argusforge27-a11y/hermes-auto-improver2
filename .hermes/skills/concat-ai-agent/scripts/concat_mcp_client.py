"""
MCP stdio client for Concat's built-in server.
Speaks newline-delimited JSON-RPC 2.0 over stdin/stdout.
"""
import json
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from queue import Queue, Empty


class ConcatMCPClient:
    """Persistent MCP client over stdio."""

    def __init__(self, binary: Optional[str] = None, mode: str = "headless"):
        self.binary = binary or self._find_concat_binary()
        self.mode = mode
        self.proc: Optional[subprocess.Popen] = None
        self.reader_thread: Optional[threading.Thread] = None
        self.response_queue: Queue = Queue()
        self.notification_queue: Queue = Queue()
        self.request_id = 0
        self._running = False

    def _find_concat_binary(self) -> str:
        """Locate concat binary."""
        # Check env first
        if env_bin := os.environ.get("CONCAT_BINARY"):
            return env_bin
        # Standard macOS locations
        candidates = [
            "/Applications/Concat.app/Contents/MacOS/concat",
            "/Volumes/Concat/Concat.app/Contents/MacOS/concat",
            os.path.expanduser("~/Applications/Concat.app/Contents/MacOS/concat"),
        ]
        for c in candidates:
            if Path(c).exists():
                return c
        # Fallback to PATH
        return "concat"

    def start(self) -> None:
        """Launch concat --mcp headless and initialize."""
        if self._running:
            return
        self.proc = subprocess.Popen(
            [self.binary, "--mcp", self.mode],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._running = True
        self.reader_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.reader_thread.start()
        
        # Legacy initialize handshake (protocol 2025-06-18)
        req_id = self._next_id()
        self._send({
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "concat-ai-agent", "version": "0.1.0"},
            },
        })
        reply = self._wait_for_id(req_id, timeout=10)
        
        # Send initialized notification
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def _read_loop(self) -> None:
        """Read stdout line by line."""
        assert self.proc and self.proc.stdout
        for line in self.proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            # Route by id (response) or method (notification)
            if "id" in msg:
                self.response_queue.put(msg)
            else:
                self.notification_queue.put(msg)

    def _next_id(self) -> int:
        self.request_id += 1
        return self.request_id

    def _send(self, msg: Dict) -> None:
        assert self.proc and self.proc.stdin
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()

    def _wait_for_id(self, req_id: int, timeout: float = 30) -> Dict:
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                msg = self.response_queue.get(timeout=0.5)
                if msg.get("id") == req_id:
                    return msg
                # Put back if not ours (shouldn't happen with sequential)
                self.response_queue.put(msg)
            except Empty:
                continue
        raise TimeoutError(f"MCP request {req_id} timed out")

    def call(self, method: str, params: Dict = None) -> Any:
        """Call an MCP tool and return result."""
        req_id = self._next_id()
        self._send({
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "tools/call",
            "params": {"name": method, "arguments": params or {}},
        })
        reply = self._wait_for_id(req_id)
        if "error" in reply:
            raise RuntimeError(f"MCP error: {reply['error']}")
        result = reply.get("result", {})
        if result.get("isError"):
            raise RuntimeError(f"Tool error: {result.get('content', [{'text': 'unknown'}])[0].get('text')}")
        # Extract structured content if present
        content = result.get("content", [])
        for c in content:
            if c.get("type") == "text" and c.get("text", "").startswith("{"):
                try:
                    return json.loads(c["text"])
                except json.JSONDecodeError:
                    pass
        return content[0].get("text") if content else None

    def list_tools(self) -> List[Dict]:
        """Get available tools."""
        req_id = self._next_id()
        self._send({"jsonrpc": "2.0", "id": req_id, "method": "tools/list"})
        reply = self._wait_for_id(req_id)
        return reply.get("result", {}).get("tools", [])

    def stop(self) -> None:
        """Shutdown."""
        if self.proc:
            self.proc.terminate()
            self.proc.wait(timeout=5)
            self.proc = None
        self._running = False

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
