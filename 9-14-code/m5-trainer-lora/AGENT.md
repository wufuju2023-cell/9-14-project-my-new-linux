# AGENT.md — m5-trainer-lora

> 引用文件完整路径（本地 + GitHub + 云端）见 `../../9-14-plan/03-references.md`（REF 编号索引）。

## 用途
LoRA 训练器：题内 TTT（learn/v1）+ **跨题主更新（MCTS 蒸馏：π_MCTS + z）**；
GRPO 仅作工具级辅助（可选，必过 M8 多样性门）。

## 文件
| 文件 | 说明 |
|---|---|
| `lora_trainer.py` | `TTTConfig` / `LoRATrainer.ttt_update()` / **`az_step()`（主）** / `grpo_step()`（辅，可选） |

## 被引用（精确到行）
| 引用对象 | 位置 | 用途 |
|---|---|---|
| 联合更新目标 | `discussion/new_value_head_in7b_ex1/01_设计说明/01_Value设计与评价方法.md` | NLL+KL+CE |
| learn 路由 | `gpu/gpu_runtime/server.py` **L182** | 提交更新 |
| 学习器实现 | `gpu/gpu_runtime/learner.py` / `mixed_learner.py` / `mixed_objective.py` | 真实更新委托 |
| KL 项 | `gpu/gpu_runtime/mixed_objective.py` | β·KL(π‖frozen) |
| 会话客户端 | `9-14-code/shared/http_contract.py` `GpuSession.learn` | 调用 |

## 依赖
- `shared/schemas.py`（Trace/LearnEvent）、`shared/http_contract.py`；
- GPU 侧：torch/peft（LoRA rank16/α32，与现有对齐）。

## 上云/环境
- 训练进程可与推理服务同机（192GB 富余）或独立卡；
- 数据路径：`/work/data/replay/{family}/{problem_id}.jsonl`（M7/M8 产出）。

## 门
- [ ] TTT 回执断言（版本递增）；
- [ ] 一轮 RL 后 pass@1/pass@k 双报（接 M8）；
- [ ] 无 NaN/OOM（100-200 题规模）。
