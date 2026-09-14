"""shared/schemas.py — 唯一契约源（所有模块只依赖本文件的数据结构）

命名规则:
  session_id   = "s-{theorem_id}-{seq}"        (≤64 chars, 仅 [a-z0-9-])
  adapter_id   = "exp.{domain}.v{n}"           (如 exp.group-theory.v3)
  experience   = "exp-{hex12}-{nn}"
  event_id     = "ev-{hex16}"
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Problem:
    problem_id: str                 # theorem-family safe id
    statement: str                  # Lean statement text
    family: str = "unknown"         # group-theory / ring-theory / ...
    difficulty: int = 2             # 1(easy)..3(hard)
    source: str = "seed"            # seed / r1-variant / r2-agent / leantree
    verified: bool = False


@dataclass
class Evidence:
    id: str
    kind: str                       # linkSearch/leanSearch/fileSearch/toolCall/manual
    weight: float                   # [0,1]
    payload: str
    source_desc: str = ""


@dataclass
class ToolCall:
    req_id: str
    kind: str                       # lean_search / lean_compile / file_read / script_run
    args: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    req_id: str
    ok: bool
    output: Any = None
    artifacts: dict[str, str] = field(default_factory=dict)
    wall_ms: int = 0


@dataclass
class TraceStep:
    state: str
    action: str
    reward: float = -1.0
    value_pred: float = 0.0
    tool_calls: list[ToolCall] = field(default_factory=list)


@dataclass
class Trace:
    problem_id: str
    steps: list[TraceStep] = field(default_factory=list)
    terminal: bool = False
    verified: bool = False
    policy_version: int = 0


@dataclass
class LearnEvent:
    event_id: str
    steps: list[TraceStep]
    terminal: bool
    source: str = "mcts"            # mcts / agent / replay
    advantage: Optional[float] = None   # RL 组内归一化优势（TTT 时为 None）


@dataclass
class ExpertSpec:
    adapter_id: str                 # exp.{domain}.v{n}
    base_model: str                 # real-prover-7b / qwen3.8-9b
    domain: str
    version: int = 0
    endpoint: str = ""              # http://host:port
    stats: dict[str, Any] = field(default_factory=dict)


def phi(evidence: list[Evidence]) -> float:
    """φ = tanh(Σ w)（与 Lean Agentic.lean L72-74 同式）。"""
    import math
    return math.tanh(sum(e.weight for e in evidence))
