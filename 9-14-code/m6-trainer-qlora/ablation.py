"""m6-trainer-qlora/ablation.py — LoRA vs QLoRA 对照研究（预注册判定）

判定规则（预注册，禁止事后解释）:
  1. ROCm bitsandbytes 不可用 → 不用 QLoRA（直接裁定）
  2. 可用时需同时满足: 显存降幅>40% 且 精度差<5% 且 速度降幅<30% → 建议用
  3. 否则不用
"""
from __future__ import annotations
from dataclasses import dataclass, asdict


@dataclass
class RunReport:
    name: str
    peak_vram_mb: float
    tok_per_s: float
    val_mae: float
    tactic_pass_rate: float


def verdict(lora: RunReport, qlora: RunReport | None, rocm_ok: bool) -> dict:
    if not rocm_ok or qlora is None:
        return {"use_qlora": False, "reason": "ROCm/bitsandbytes unavailable"}
    vram_drop = 1 - qlora.peak_vram_mb / lora.peak_vram_mb
    speed_drop = 1 - qlora.tok_per_s / lora.tok_per_s
    mae_gap = abs(qlora.val_mae - lora.val_mae) / max(lora.val_mae, 1e-9)
    use = vram_drop > 0.40 and mae_gap < 0.05 and speed_drop < 0.30
    return {"use_qlora": use,
            "vram_drop": round(vram_drop, 3),
            "speed_drop": round(speed_drop, 3),
            "mae_gap": round(mae_gap, 4),
            "inputs": {"lora": asdict(lora), "qlora": asdict(qlora)}}


if __name__ == "__main__":
    from qlora_trainer import check_rocm
    import json
    print(json.dumps(check_rocm(), indent=2, ensure_ascii=False))
