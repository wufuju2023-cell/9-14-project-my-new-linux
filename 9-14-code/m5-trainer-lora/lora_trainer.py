"""m5-trainer-lora/lora_trainer.py — LoRA 训练器（TTT + GRPO 变体）

TTT 走 GPU learn/v1（现有能力）；跨题 RL 为离线管线（收集→归一化→更新）。
多样性保护：训练后必须过 M8 的 pass@k 门。
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shared"))
from schemas import Trace, LearnEvent  # noqa: E402
from http_contract import GpuSession  # noqa: E402


@dataclass
class TTTConfig:
    expected_version: int
    event_source: str = "mcts"


class LoRATrainer:
    def __init__(self, session: GpuSession):
        self.session = session

    # ---- 题内 TTT（生产：真实更新；骨架：提交事件 + 校验回执） ----
    def ttt_update(self, trace: Trace, cfg: TTTConfig) -> dict:
        event = LearnEvent(
            event_id=f"ev-{abs(hash((trace.problem_id, cfg.expected_version))) % 10**16:016x}",
            steps=trace.steps, terminal=trace.terminal, source=cfg.event_source)
        receipt = self.session.learn(cfg.expected_version, event.__dict__)
        assert receipt.get("new_version", cfg.expected_version + 1) > cfg.expected_version, \
            "policy version must increase after learn"
        return receipt

    # ---- 跨题主更新：MCTS 蒸馏（AlphaZero/AlphaProof 式） ----
    def az_step(self, trees: list[dict], lam_v: float = 0.5, beta_kl: float = 0.02) -> dict:
        """trees: [{problem_id, nodes:[{state, pi_mcts:{a:p}, z, tool_calls}]}]
        主公式: CE(policy, π_MCTS) + λ_v·MSE(value, z) + β·KL(π‖π_ref)
        真实更新委托 gpu_runtime learner；本函数负责数据整形与统计。"""
        pairs = 0
        z_values = []
        for t in trees:
            for n in t["nodes"]:
                pairs += 1
                z_values.append(n["z"])
        return {"policy_pairs": pairs,
                "z_mean": sum(z_values) / max(len(z_values), 1),
                "lam_v": lam_v, "beta_kl": beta_kl,
                "note": "delegate to gpu_runtime.mixed_learner (policy CE + value MSE + KL)"}

    # ---- 辅助：GRPO（**暂时禁用 2026-09-14**） ----
    def grpo_step(self, rollouts_by_problem: dict[str, list[Trace]],
                  beta_kl: float = 0.02, adv_temp: float = 1.0) -> dict:
        """暂时禁用。恢复条件见 9-14-plan/modules/M5-trainer-lora/README.md
        （A/τ 软化 + 熵正则 + M8 门 + 仅消融形式）。"""
        raise NotImplementedError("GRPO temporarily disabled (2026-09-14)")

    @staticmethod
    def _reward(t: Trace) -> float:
        if not t.verified:
            return 0.0
        tool_q = sum(len(s.tool_calls) for s in t.steps)
        return 1.0 + 0.1 * tool_q - 0.01 * len(t.steps)
