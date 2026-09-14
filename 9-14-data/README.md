# 9-14-data — Lean 代数语料 → 20 万生成题 + 证明树（数据与训练方案）

本目录是 `9-14-project-my-new-linux` 的数据子项目：把 Lean 4 形式化数学语料
转成按领域配额的大规模「问题 + 证明树」数据集，并给出与 M5/M6/M7/M8 对接的训练方案。

## 1. 目标（一句话）

在 12 个代数风格领域各产出约 20K 道**可编译验证**的 question（自然语言题面 +
Lean 形式化题面），总量 **≥ 200K**，每条附声明级 / 步骤级 proof tree；
训练上先做 SFT 冷启动（对齐 LeanTree / nanoproof 路线），再进入 M5 的
MCTS 蒸馏主循环（π_MCTS + z，见 `9-14-plan/modules/M5-trainer-lora/README.md`）。

## 2. 执行分工（硬约束，2026-09-14 用户裁定）

| 机器 | 角色 | 禁止 |
|---|---|---|
| 本机（zhai 的 WSL / F 盘） | 文档、协调、轻量网络与少量 I/O | **禁止** build / 抽取 / 训练等重型 CPU、内存任务 |
| `a@my-new-linux`（Ryzen 7 5700X 16 线程 / 60GB / /home 278G 可用 / 无 GPU） | CPU 侧抽取、批处理、Lean 编译验证、服务 | 训练（无 GPU） |
| AMD MI300X 192GB 云实例 | M4 推理、M5/M6 训练、GPU 端批量补证 | — |
| E:（资料库，只读复用） | 已有 mathlib 构建与 packages | 不再往 E 写重型产物 |
| F:（1.7T 可用） | 语料克隆、中间产物、备份镜像 | — |

## 3. 现状盘点（2026-09-14）

- E: `/mnt/e/projects/lean/mathlib` = mathlib @ `5edf93c`（lean 4.33.0-rc2），
  `.lake` 已有部分 olean（已抽样确认存在），`.lake/packages` 含 `importGraph`、`batteries`、`aesop` 等
- F: `/mnt/f/projects/lean-corpus/mathlib4` = mathlib4 **v4.28.0** 浅克隆 @ `8f9d9cf`
  （与 9-14 项目 Lean 4.28 基线一致，首选数据源）
- 本机 elan 已有 toolchain：`v4.28.0`、`v4.28.0-rc1`、`v4.33.0-rc2`
- `my-new-linux` 当前无 `elan/lake/lean`，需按 `02-harvest-pipeline.md` 安装
- 本机 HF 缓存为空；E/F 上未发现 LeanTree / LeanDojo 数据副本，需要按 01 重新拉取

## 4. 文件索引

| 文件 | 内容 |
|---|---|
| `00-goals-and-metrics.md` | 数据模型（schema）、12 领域配额、验收指标 |
| `01-corpus-inventory.md` | 语料清单：仓库（mathlib/FLT/…）+ HF 数据集 + 获取方式 |
| `02-harvest-pipeline.md` | 抽取管线：环境搭建、导出器、领域分类、断点续传 |
| `03-question-generation.md` | R1–R4 四类生成器（确定性变换 / agent 变体 / 步骤题 / 反向 autoformalization） |
| `04-proof-trees.md` | 证明树三档（声明级 DAG / 步骤级 / 项级）与格式 |
| `05-verification-and-quality.md` | 编译验证门、难度分桶、去重、泄漏过滤、类平衡、许可台账 |
| `06-training-plan.md` | 训练方案：SFT 冷启动 → MCTS 蒸馏 → value head → 评估门 |
| `07-infra-and-storage.md` | 机器矩阵、目录规范、断点续传与备份、成本预算 |
| `08-roadmap-milestones.md` | P0–P4 里程碑与每阶段验收标准 |
| `09-risks-licenses.md` | 风险、许可与合规、红线 |

## 5. 下一步（P0，立即可执行）

1. 在 `my-new-linux` 安装 elan，构建 **v4.28.0** mathlib（优先 `lake exe cache get`）
2. 运行导出器，统计 12 领域各自原始定理数，冻结 `00` 的配额表
3. 跑通 GroupTheory 一个最小切片（≥500 条导出 + 编译验证），回填本文件与 08

> 所有重型命令一律走 my-new-linux / 云，且遵守全局断点续传规则
> （`state/*.done` 标记、原子写、幂等、下载 `-c` / `--resume`）。
