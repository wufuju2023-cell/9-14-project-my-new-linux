"""m2-tool-runtime/opencode_bridge.py — opencode 直驱工具运行时

裁定：工具调用不使用自制 Python 工具层；直接借助 opencode（任意 shell，不设白名单）。
本桥职责：发起 opencode 会话 → 导出原生轨迹 → 解析为 (新状态, 工具调用) 返回 M1。

形态：
  run    : opencode run "<prompt>"（cwd=workdir，单次）
  serve  : opencode serve（常驻，HTTP 会话；高频时启用）
护栏：workdir 隔离 / 轨迹留痕 / 预算超时（见 9-14-plan/modules/M2-tool-runtime/README.md）
"""
from __future__ import annotations
import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ToolRunResult:
    ok: bool
    session_id: str = ""
    tool_calls: list[dict] = field(default_factory=list)   # [{kind, args, ok}]
    artifacts: dict = field(default_factory=dict)          # 文件变更/编译输出
    stdout: str = ""
    wall_ms: int = 0
    infra_error: bool = False                              # 超时/崩溃：不进训练数据


class OpencodeBridge:
    def __init__(self, binary: str = "opencode", workdir: str = "/work/agent",
                 wall_timeout: int = 300, pure: bool = True):
        self.binary = binary
        self.workdir = Path(workdir)
        self.wall_timeout = wall_timeout
        self.pure = pure            # --pure: 不带外部插件（确定性更好）
        self.workdir.mkdir(parents=True, exist_ok=True)

    # ---------- 会话 ----------
    def run(self, prompt: str) -> ToolRunResult:
        """CLI 单次会话。任意 shell 可用（opencode 内建 bash 等工具）。"""
        t0 = time.time()
        cmd = [self.binary, "run", prompt]
        if self.pure:
            cmd.insert(2, "--pure")
        try:
            proc = subprocess.run(cmd, cwd=self.workdir, capture_output=True,
                                  text=True, timeout=self.wall_timeout)
            ok = proc.returncode == 0
            stdout = proc.stdout
        except subprocess.TimeoutExpired:
            return ToolRunResult(ok=False, infra_error=True,
                                 wall_ms=int((time.time() - t0) * 1000))
        return ToolRunResult(ok=ok, stdout=stdout[-100_000:],
                             wall_ms=int((time.time() - t0) * 1000))

    # ---------- 轨迹 ----------
    def export_session(self, session_id: str) -> list[dict]:
        """opencode export <id> → JSON；解析 tool parts 为统一格式。"""
        proc = subprocess.run([self.binary, "export", session_id],
                              capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            return []
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return []
        calls = []
        for msg in data.get("messages", []):
            for part in msg.get("parts", []):
                if part.get("type") == "tool":
                    calls.append({"kind": part.get("tool", "unknown"),
                                  "args": part.get("state", {}).get("input", {}),
                                  "ok": part.get("state", {}).get("status") == "completed"})
        return calls

    # ---------- M1 契约 ----------
    def tool_round(self, prompt: str, session_id: str | None = None) -> ToolRunResult:
        res = self.run(prompt)
        if res.session_id and not res.tool_calls:
            res.tool_calls = self.export_session(res.session_id)
        return res


if __name__ == "__main__":
    import sys
    bridge = OpencodeBridge(workdir=sys.argv[1] if len(sys.argv) > 1 else "/work/agent")
    out = bridge.tool_round("Run `lean --version` and report it.")
    print(json.dumps({"ok": out.ok, "calls": out.tool_calls,
                      "wall_ms": out.wall_ms}, ensure_ascii=False, indent=2))
