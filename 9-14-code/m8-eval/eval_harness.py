"""m8-eval/eval_harness.py — 评测与多样性门（骨架）

指标：pass@1 / pass@k（k=8/16）/ 多样性（Jaccard 中位）/ value 距离直方图 / 工具质量。
塌缩门：RL 后 pass@k 下降 >30% → 建议回退（与 M3 registry 联动）。
"""
from __future__ import annotations
import json
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


@dataclass
class EvalReport:
    pass_at_1: float = 0.0
    pass_at_k: float = 0.0
    jaccard_med: float = 1.0
    tool_quality: float = 0.0
    d_hist: list[int] = field(default_factory=lambda: [0] * 64)

    def to_json(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False)


def _jaccard(a: str, b: str) -> float:
    sa, sb = set(a.split()), set(b.split())
    u = sa | sb
    return len(sa & sb) / len(u) if u else 1.0


def evaluate(problems: list[str], rollout_fn: Callable[[str, int], list[dict]],
             k: int = 8) -> EvalReport:
    """rollout_fn(problem, seed) -> [{"verified":bool,"route_text":str,"steps":int,"value":float}]"""
    rep = EvalReport()
    p1_hits = pk_hits = 0
    all_j, tool_ok, tool_n = [], 0, 0
    for p in problems:
        runs = [rollout_fn(p, seed) for seed in range(k)]
        ok = [r for r in runs if r["verified"]]
        p1_hits += 1 if ok else 0
        pk_hits += 1 if ok else 0
        for i, a in enumerate(ok):
            for b in ok[i + 1:]:
                all_j.append(_jaccard(a["route_text"], b["route_text"]))
        for r in runs:
            for tc in r.get("tool_calls", []):
                tool_n += 1
                tool_ok += 1 if tc.get("ok", False) else 0
            rep.d_hist[min(int(max(r.get("value", 0), 0)), 63)] += 1
    n = max(len(problems), 1)
    rep.pass_at_1 = p1_hits / n          # 至少一次成功（k 次中）
    rep.pass_at_k = pk_hits / n
    rep.jaccard_med = statistics.median(all_j) if all_j else 1.0
    rep.tool_quality = tool_ok / tool_n if tool_n else 0.0
    return rep


def collapse_gate(prev: EvalReport, cur: EvalReport, threshold: float = 0.30) -> dict:
    """RL 后调用；返回是否需回退。"""
    if prev.pass_at_k <= 0:
        return {"rollback": False, "reason": "no baseline"}
    drop = 1 - cur.pass_at_k / prev.pass_at_k
    return {"rollback": drop > threshold, "pass_k_drop": round(drop, 3),
            "threshold": threshold,
            "hint": "entropy-regularize or soften advantage A/τ" if drop > threshold else ""}
