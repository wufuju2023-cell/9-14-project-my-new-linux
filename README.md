# 9-14-project-my-new-linux

多智能体 AlphaProof 工程（计划 + 代码）。从 `2-9-14-Q.md` 的问题集出发，把
「CPU 端 Lean MCTS + opencode 工具环」与「GPU 端策略/价值/训练（LoRA 与 QLoRA 双轨）」
封装为可并行开发的模块（M1–M8），并给出上云（AMD MI300X 192GB）从零搭建的完整路径。

## 目录结构

```
.
├── README.md                  # 本文件
├── 2-9-14-Q.md                # 问题集（Q0–Q4）：多智能体/QLoRA/工具环/多样性/蒸馏
├── 1-QLoRA-zhihu.md           # QLoRA 数学参考（NF4/双重量化/分页）
├── 9-14-plan/                 # 计划层（文档）
│   ├── README.md              #   模块地图 / 接口矩阵 / 分工建议
│   ├── 00-math-theory.md      #   完整数学理论（引用式）
│   ├── 01-architecture-interfaces.md  # 接口契约（I1–I5）
│   ├── 02-milestones-gates.md #   里程碑与门
│   ├── 03-references.md       #   引用文件索引（本地+GitHub+云端三层路径）
│   └── modules/M1..M8/README.md       # 每模块数学+伪代码
└── 9-14-code/                 # 代码层（接口级实现，可并行开发）
    ├── README.md              #   组装指南 / 从零搭环境
    ├── shared/                #   唯一契约源（schemas.py / http_contract.py）
    ├── m1-lean-mcts/          #   Lean 4.28：MCTS 驱动 + 工具状态机 + φ 钩子
    ├── m2-tool-runtime/       #   opencode 直驱工具环（任意 shell + 轨迹导出）
    ├── m3-multiagent/         #   专家注册/路由 + 联合奖励
    ├── m4-gpu-inference/      #   GPU 专家池（adapter 热切换，无 NVLink 多卡）
    ├── m5-trainer-lora/       #   LoRA：TTT + MCTS 蒸馏主更新（GRPO 暂时禁用）
    ├── m6-trainer-qlora/      #   QLoRA：NF4 对照研究（预注册判定）
    ├── m7-curriculum/         #   代数题生成（R1 变换 / R2 agent）+ 验证门
    └── m8-eval/               #   评测（pass@1/k、多样性、塌缩门）
```

## 快速开始

1. **读计划**：`9-14-plan/README.md` → `01-architecture-interfaces.md`（接口真源）
   → 各模块 `modules/M*/README.md`（数学+伪代码）。
2. **写代码**：以 `9-14-code/shared/` 为契约，按模块分工（见 plan README 的分工建议）。
3. **上云**：`9-14-code/README.md` 的「从零搭环境」（AMD 192GB；Lean 4.28；hf-mirror）。

## 关键裁定（当前生效）

| 项 | 裁定 |
|---|---|
| 工具运行时 | **opencode 直驱**（不再自制工具层）；**shell 不设白名单**，护栏=workdir 隔离+轨迹留痕+预算超时 |
| 工具阶段与树 | **Q3 方案1**：工具=确定性链、原地更新、不建树节点；仅 Lean 状态变化处采样 K |
| 训练主路径 | **MCTS 蒸馏**（π_MCTS + z + KL），即"大量问题 → MCTS+RL" |
| GRPO | **暂时禁用**（2026-09-14）；恢复条件见 M5 README |
| QLoRA | 待 ROCm 可用性 + 四维对照后**书面裁定**（M6） |
| Lean | **4.28**（容器评估基线） |
| 引用规范 | 所有文件引用必须给三层路径（见 `9-14-plan/03-references.md`） |

## 开发约定（git 工作流）

```bash
git pull                       # 开始工作前
# 编辑（小步提交；每次只改一个模块/一个主题）
git add <files> && git commit -m "mN: <what & why>"
git push
```

- 提交信息前缀：`plan:` / `code-mN:` / `fix:` / `docs:`；
- 禁止提交 `__pycache__/`、`*.bak-*`（已 gitignore）；
- 模块间只通过 `shared/` 交互，跨模块改动必须同步更新 `01-architecture-interfaces.md`。

## 环境

| 层 | 环境 |
|---|---|
| 本地（本机） | Ubuntu 26.04，python3+git（文档与代码编辑） |
| 云端训练 | AMD MI300X 192GB（ROCm；torch 2.11 / transformers 5.14 / peft 0.19） |
| 模型 | `FrenzyMath/REAL-Prover`、`empero-ai/Qwen3.8-9B-Distill`、artifact `WufuJu/v1-1-fullv3-artifact` |

## 状态

- [x] 计划全套（00–03 + M1–M8）
- [x] 代码骨架（shared + 8 模块，接口级）
- [ ] M-0 接口冻结评审
- [ ] M-1 单专家最小闭环（云上）
