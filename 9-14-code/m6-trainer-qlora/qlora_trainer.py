"""m6-trainer-qlora/qlora_trainer.py — QLoRA 训练器（骨架）

形态：基座 NF4 冻结 + LoRA 适配器 bf16 训练（QLoRA 三件套：NF4/双重量化/分页）。
关键前置：ROCm 下 bitsandbytes 可用性（见 ablation.py 的 check_rocm()）。
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class QLoRAConfig:
    base_model: str
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.0
    quant_type: str = "nf4"          # nf4 / fp4
    double_quant: bool = True
    paged_optim: bool = True
    device: str = "cuda:0"


def check_rocm() -> dict:
    """第一优先：环境可用性检查（无异常才算可用）。"""
    report = {"torch": None, "cuda_available": None, "bitsandbytes": None, "ok": False}
    try:
        import torch
        report["torch"] = torch.__version__
        report["cuda_available"] = bool(torch.cuda.is_available())
        report["device_name"] = torch.cuda.get_device_name(0) if report["cuda_available"] else None
    except Exception as e:
        report["torch_error"] = repr(e)
    try:
        import bitsandbytes as bnb
        report["bitsandbytes"] = getattr(bnb, "__version__", "unknown")
        report["ok"] = report["cuda_available"] is True
    except Exception as e:
        report["bitsandbytes_error"] = repr(e)
    return report


def build_model(cfg: QLoRAConfig):
    """生产实现（在 ROCm 环境验证后启用）：
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    """
    raise NotImplementedError("enable after check_rocm() ok (see AGENT.md)")


def train(cfg: QLoRAConfig, dataset, steps: int = 100) -> dict:
    """训练循环骨架：返回 {peak_vram_mb, tok_per_s, val_mae, tactic_pass_rate}"""
    raise NotImplementedError("delegate to transformers Trainer after build_model")
