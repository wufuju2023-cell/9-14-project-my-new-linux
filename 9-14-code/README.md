# 9-14-code — 代码总览与组装指南

> 全部引用文件的三层完整路径（本地 WSL / GitHub URL / 云端 /work）见 `03-references.md`。

> 8 个模块的接口级实现骨架。每个模块的 `AGENT.md` 给出：引用文件（精确到行）、依赖、
> 上云部署与从零搭环境步骤。模块间**只依赖 `shared/` 的契约**，可并行开发。

## 目录

```
shared/              # 唯一契约源：schemas.py（数据结构）+ http_contract.py（端点封装）
m1-lean-mcts/        # Lean 4.28：MCTSDriver.lean（工具状态机 + φ 钩子）
m2-tool-runtime/     # opencode 直驱：opencode_bridge.py（任意 shell + 轨迹导出）
m3-multiagent/       # Python：expert_router.py + joint_reward.py
m4-gpu-inference/    # Python：expert_pool.py（服务端适配，复用 gpu_runtime）
m5-trainer-lora/     # Python：lora_trainer.py（TTT + MCTS 蒸馏；GRPO 禁用）
m6-trainer-qlora/    # Python：qlora_trainer.py + ablation.py（对照研究）
m7-curriculum/       # Python：curriculum.py + variant_gen.py（R1/R2）
m8-eval/             # Python：eval_harness.py（pass@1/k、塌缩门）
```

## 从零搭环境（本地开发 → 上云）

### 本地（无 GPU，写代码+单测）
```bash
python3 -m venv .venv && . .venv/bin/activate
pip install pytest requests            # 仅单测依赖
pytest tests/ -q                       # 每模块自带 tests/
```
Lean（4.28，仅 M1 需要）：
```bash
curl -fsSL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain v4.28.0
lean --version   # 期望 4.28.0
```

### 云上（AMD 192GB）
```bash
# 1) 代码与模型
git clone <repo> && cd 9-14-code
export HF_ENDPOINT=https://hf-mirror.com
hf download FrenzyMath/REAL-Prover --local-dir /work/models/REAL-Prover
hf download empero-ai/Qwen3.8-9B-Distill --local-dir /work/models/Qwen3.8-9B
hf download WufuJu/v1-1-fullv3-artifact --local-dir /work/artifact
# 2) GPU 服务（M4 适配自 gpu_runtime）
python -m m4_gpu_inference.expert_pool --config configs/m4.yaml
# 3) 训练/课程/评测按模块 README 顺序拉起
```

## 组装顺序（首次跑通）
1. `shared` 单测 → 2. `m4` 起服务（smoke 3 题）→ 3. `m2` 工具单测 →
4. `m1` 本地 Lean 跑 3 题 → 5. `m8` 评测 smoke → 6. `m5` 一次 TTT →
7. `m7` R1 语料 → 8. `m3` 双专家 → 9. `m6` QLoRA 对照。

## 约定
- 所有模块 import 只允许来自 `shared/`（禁止跨模块直接 import）；
- 单测以"接口桩"驱动（不依赖其它模块真实实现）；
- 版本号、adapter_id、session_id 命名规则见 `shared/schemas.py`。
