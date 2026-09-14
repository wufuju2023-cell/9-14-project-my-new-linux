"""m7-curriculum/curriculum.py — 验证门 + 课程调度（骨架）

验证门：Lean 语法 → 编译预检 → 去重 → 入池（通过率与类平衡报告）。
课程：难度分层（E1/E2/E3）→ budgets 调度（沿用 proof-curriculum/budgets.json v2）。
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from schemas import Problem  # noqa: E402
from variant_gen import VariantPool  # noqa: E402


@dataclass
class GateReport:
    submitted: int = 0
    syntax_ok: int = 0
    compiled_ok: int = 0
    dedup_ok: int = 0

    @property
    def pass_rate(self) -> float:
        return self.dedup_ok / self.submitted if self.submitted else 0.0


class ValidationGate:
    """lean_check/compile_check 由注入提供（本地=stub；云上=M2 ToolRuntime）。"""

    def __init__(self, lean_check, compile_check):
        self.lean_check = lean_check
        self.compile_check = compile_check

    def validate(self, problems: list[Problem], pool: VariantPool) -> GateReport:
        rep, seen = GateReport(), set()
        for p in problems:
            rep.submitted += 1
            if not self.lean_check(p.statement):
                continue
            rep.syntax_ok += 1
            if not self.compile_check(p.statement):
                continue
            rep.compiled_ok += 1
            h = hash(p.statement)
            if h in seen:
                continue
            seen.add(h)
            p.verified = True
            if pool.add(p):
                rep.dedup_ok += 1
        return rep


# ---- 课程调度 ----
DIFFICULTY_LAYERS = {1: "E1", 2: "E2", 3: "E3"}
DEFAULT_BUDGETS = {  # 与 proof-curriculum/budgets.json v2 字段对齐
    "E1": {"search_steps": 64, "num_samples": 4, "max_tokens": 512},
    "E2": {"search_steps": 128, "num_samples": 8, "max_tokens": 1024},
    "E3": {"search_steps": 256, "num_samples": 16, "max_tokens": 2048},
}


def schedule(pool_root: Path, family_balance_max: float = 0.30) -> dict:
    """按难度分层 + 类平衡检查，输出课程计划。"""
    items = [json.loads(m.read_text()) for m in Path(pool_root).rglob("meta.json")]
    by_layer: dict[str, list[str]] = {v: [] for v in DIFFICULTY_LAYERS.values()}
    for p in items:
        by_layer[DIFFICULTY_LAYERS.get(p["difficulty"], "E2")].append(p["problem_id"])
    fams: dict[str, int] = {}
    for p in items:
        fams[p["family"]] = fams.get(p["family"], 0) + 1
    total = max(sum(fams.values()), 1)
    balance = max(fams.values()) / total if fams else 0.0
    return {"plan": {k: len(v) for k, v in by_layer.items()},
            "budgets": DEFAULT_BUDGETS,
            "family_balance_max": balance,
            "balance_ok": balance <= (1 - family_balance_max) or len(fams) <= 1}
