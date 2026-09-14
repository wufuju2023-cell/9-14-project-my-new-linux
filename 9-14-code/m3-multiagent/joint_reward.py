"""m3-multiagent/joint_reward.py — 联合奖励（Q0 公式落地）

R_joint = Σ_e 1[proof_e]·γ^steps_e + λ_collab·complementarity − λ_cost·Σ steps/budget
complementarity: 不同专家证明不同子目标/路线 → 用成功轨迹两两距离度量。
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class TraceView:
    expert_id: str
    verified: bool
    steps: int
    budget: int
    route_text: str  # 证明路线文本（用于互补度量）


def _jaccard(a: str, b: str) -> float:
    sa, sb = set(a.split()), set(b.split())
    u = sa | sb
    return len(sa & sb) / len(u) if u else 1.0


def complementarity(traces: list[TraceView]) -> float:
    """成功轨迹的路线差异：越不同越高（0..1）。"""
    ok = [t for t in traces if t.verified]
    if len(ok) < 2:
        return 0.0
    pairs = [(1 - _jaccard(a.route_text, b.route_text))
             for i, a in enumerate(ok) for b in ok[i + 1:]]
    return sum(pairs) / len(pairs)


def joint_reward(traces: list[TraceView], gamma: float = 0.99,
                 lam_collab: float = 0.3, lam_cost: float = 0.1) -> float:
    base = sum((gamma ** t.steps) for t in traces if t.verified)
    comp = complementarity(traces)
    cost = sum(t.steps / max(t.budget, 1) for t in traces)
    return base + lam_collab * comp - lam_cost * cost
