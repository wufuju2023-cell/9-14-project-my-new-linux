"""shared/http_contract.py — GPU 服务 HTTP 契约（M1/M3/M5/M8 共用）

对应 gpu/gpu_runtime/server.py 的路由（L178 policy / L180 value / L182 learn），
以及 driver/runtime_transport.py L4-7 的端点表。
⚠️ 响应为 OpenAI 嵌套：choices[].message.content
"""
from __future__ import annotations
import json
import urllib.request
from typing import Any


class GpuSession:
    """一个专家会话（adapter_id 通过 model 字段路由）。"""

    def __init__(self, base: str, theorem_id: str, adapter_id: str,
                 session_id: str | None = None, timeout: int = 180):
        self.base = base.rstrip("/")
        self.adapter = adapter_id
        self.timeout = timeout
        self.sid = session_id or f"s-{theorem_id}-{abs(hash((base, theorem_id))) % 100000}"
        self._post(f"/sessions/{self.sid}", {"theorem_id": theorem_id})

    # -- low level --
    def _post(self, path: str, payload: dict) -> dict:
        req = urllib.request.Request(
            self.base + path, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read().decode())

    @staticmethod
    def _content(choice: dict) -> str:
        return choice.get("message", {}).get("content", "") or choice.get("text", "")

    # -- contract methods --
    def policy(self, prompt: str, n: int = 8, temperature: float = 1.0) -> list[str]:
        out = self._post(f"/sessions/{self.sid}/policy/v1/chat/completions", {
            "model": self.adapter,
            "messages": [{"role": "user", "content": prompt}],
            "n": n, "temperature": temperature})
        return [self._content(c) for c in out.get("choices", [])]

    def value(self, prompt: str) -> float:
        out = self._post(f"/sessions/{self.sid}/value/v1/chat/completions", {
            "model": self.adapter,
            "messages": [{"role": "user", "content": prompt}]})
        try:
            inner = self._content(out["choices"][0])
            return float(json.loads(inner).get("score", -1000.0))
        except Exception:
            return -1000.0

    def learn(self, expected_version: int, event: dict) -> dict:
        return self._post(f"/sessions/{self.sid}/learn/v1", {
            "expected_policy_version": expected_version, "event": event})

    def retire(self) -> None:
        try:
            urllib.request.urlopen(f"{self.base}/sessions/{self.sid}/retire/v1",
                                   timeout=30).read()
        except Exception:
            pass
