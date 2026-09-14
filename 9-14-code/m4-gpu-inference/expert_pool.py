"""m4-gpu-inference/expert_pool.py — GPU 专家池（服务端骨架）

复用云端 gpu_runtime（server.py L178/180/182 路由 + real_backend + categorical_search_backend）。
本文件只做"多专家适配层"：
  - adapter_id → LoRA 热切换（LRU）；
  - 无 NVLink 多卡：每卡一进程，本层不涉及张量并行。
"""
from __future__ import annotations
import os
import sys
from dataclasses import dataclass
from pathlib import Path

# 云端运行时（已含 torch2.11 补丁）
sys.path.insert(0, os.environ.get("GPU_RUNTIME", "/work/v1-1-agentic-tool/gpu"))


@dataclass
class ExpertPoolConfig:
    base_model: str                      # /work/models/REAL-Prover 或 Qwen3.8-9B
    adapters: dict[str, str]             # adapter_id → lora 权重路径
    value_artifact: str | None = None    # full-v3 head（REAL）或新训 Qwen head
    value_artifact_sha256: str | None = None
    device: str = "cuda:0"
    max_resident: int = 2


class ExpertPool:
    """骨架：真实加载委托给 gpu_runtime.real_backend / qwen35_backend。"""

    def __init__(self, cfg: ExpertPoolConfig):
        self.cfg = cfg
        self.resident: list[str] = []
        # from gpu_runtime.real_backend import RealProverBackend   # 生产路径
        # self.backend = RealProverBackend(cfg.base_model, device=cfg.device)

    def _ensure(self, adapter_id: str) -> None:
        if adapter_id in self.resident:
            return
        if len(self.resident) >= self.cfg.max_resident:
            self.resident.pop(0)             # LRU 卸载
        # self.backend.load_adapter(adapter_id, self.cfg.adapters[adapter_id])
        self.resident.append(adapter_id)

    def policy(self, adapter_id: str, prompt: str, n: int, temperature: float) -> list[str]:
        self._ensure(adapter_id)
        # return self.backend.policy(prompt, n=n, temperature=temperature)
        return []

    def value(self, adapter_id: str, prompt: str) -> float:
        self._ensure(adapter_id)
        # return self.backend.value(prompt)   # -d̂
        return -1000.0


def main() -> int:
    """最小服务入口：用 gpu_runtime.server 的 RuntimeHandler 包装（生产时直接复用）。"""
    # 生产：python -m gpu_runtime.server --backend real-search-categorical ...
    print("M4 skeleton: delegate to gpu_runtime.server (see AGENT.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
