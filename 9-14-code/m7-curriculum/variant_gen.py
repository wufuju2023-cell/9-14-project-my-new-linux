"""m7-curriculum/variant_gen.py — R1 受限变换 / R2 agent 生成器（骨架）

R1: 复用 cpu_runtime/target_variants.py 的受限确定性变换（nat_forall_instance / and_left/right）。
R2: agent 生成（模板化提示 × 隔离 session）→ Lean 语法+编译预检 → variant_pool。
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from schemas import Problem  # noqa: E402


@dataclass
class VariantPool:
    root: Path

    def add(self, p: Problem) -> bool:
        if not p.verified:
            return False
        key = hashlib.sha256(p.statement.encode()).hexdigest()[:16]
        d = self.root / key
        d.mkdir(parents=True, exist_ok=True)
        (d / "meta.json").write_text(json.dumps(asdict(p), ensure_ascii=False, indent=2))
        return True

    def stats(self) -> dict:
        fams: dict[str, int] = {}
        for m in self.root.rglob("meta.json"):
            p = json.loads(m.read_text())
            fams[p["family"]] = fams.get(p["family"], 0) + 1
        return {"total": sum(fams.values()), "families": fams}


# ---- R1: 受限变换（薄封装，真实实现在 cpu_runtime/target_variants.py） ----
R1_TRANSFORMS = ("nat_forall_instance", "and_left", "and_right")


def r1_expand(seed: Problem, transform: str, value: int | None = None) -> Problem:
    assert transform in R1_TRANSFORMS
    stmt = seed.statement
    if transform == "nat_forall_instance" and value is not None:
        stmt = stmt.replace("∀ n : ℕ", f"∀ n : ℕ, n = {value} →", 1)
    elif transform == "and_left":
        stmt = f"({stmt}) ∧ True"
    elif transform == "and_right":
        stmt = f"True ∧ ({stmt})"
    return Problem(problem_id=f"{seed.problem_id}-{transform}-{value or 0}",
                   statement=stmt, family=seed.family, difficulty=seed.difficulty,
                   source="r1-variant", verified=False)


# ---- R2: agent 生成（调用注入；生产接 opencode/LLM） ----
R2_TEMPLATES = ("simplify", "generalize", "decompose", "lemma", "analogy", "local_transform")


def r2_generate(seed: Problem, template: str, agent_fn) -> Problem:
    """agent_fn(seed, template) -> Lean statement 草稿；验证门在 curriculum.py。"""
    draft = agent_fn(seed, template)
    return Problem(problem_id=f"{seed.problem_id}-r2-{template}",
                   statement=draft, family=seed.family,
                   difficulty=min(seed.difficulty + 1, 3), source="r2-agent",
                   verified=False)
