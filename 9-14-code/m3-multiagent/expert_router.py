"""m3-multiagent/expert_router.py — 专家注册表与路由（外层调用者）

概念：专家=(base, adapter_id, domain, version)；路由=领域匹配；
联合奖励见 joint_reward.py；版本只升不裂（Q0 裁定）。
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from schemas import ExpertSpec, Problem  # noqa: E402


@dataclass
class Registry:
    path: Path
    experts: dict[str, ExpertSpec] = field(default_factory=dict)

    def load(self) -> "Registry":
        if self.path.exists():
            raw = json.loads(self.path.read_text())
            self.experts = {k: ExpertSpec(**v) for k, v in raw.items()}
        return self

    def save(self) -> None:
        self.path.write_text(json.dumps(
            {k: v.__dict__ for k, v in self.experts.items()}, indent=2))

    def register(self, e: ExpertSpec) -> None:
        self.experts[e.adapter_id] = e
        self.save()

    def bump_version(self, adapter_id: str) -> int:
        e = self.experts[adapter_id]
        e.version += 1
        self.save()
        return e.version


class Router:
    """领域标签优先 + 统计兜底（冷启动时 top-1，有历史时 top-k）。"""

    def __init__(self, registry: Registry):
        self.registry = registry

    def route(self, problem: Problem, k: int = 2) -> list[ExpertSpec]:
        scored = []
        for e in self.registry.experts.values():
            score = 1.0 if e.domain == problem.family else 0.2
            score += min(e.stats.get("solves", 0), 100) / 1000.0  # 历史微调
            scored.append((score, e))
        scored.sort(key=lambda t: -t[0])
        return [e for _, e in scored[:k]]
