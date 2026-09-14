# 08 — 里程碑与验收（P0–P4）

> 每阶段只依赖上一阶段的出口；所有重型执行在 my-new-linux / 云端。

## P0 — 环境与计数（预计 1–2 天）

| 任务 | 命令入口 |
|---|---|
| my-new-linux 安装 elan、克隆 mathlib v4.28.0、`lake exe cache get` | `02` 第 1 节 |
| 导出器编译运行（先 GroupTheory 切片冒烟） | `02` 第 2 节 |
| `domain_counts.json`（12 领域真实定理数） | `02` 第 4 节 |

**验收**
- [ ] 远程 `lake env lean --version` = v4.28.0
- [ ] GroupTheory 切片导出 ≥ 5,000 条且抽样 20 条 `#check` 通过
- [ ] `domain_counts.json` 产出并回填 `00` 配额表

## P1 — 单领域闭环（GroupTheory 2K，预计 2–4 天）

| 任务 | 说明 |
|---|---|
| R1 生成器全量跑 GroupTheory | `03` R1 |
| 验证批（编译 + 分桶 + 去重） | `05` |
| L2 树接入（LeanTree 下载 + 对齐） | `04` |
| M7 投影 + M5 转换脚本交付 | `03` 末节、`04` 第 4 节 |

**验收**
- [ ] ≥ 2,000 条 verified question（GroupTheory）
- [ ] 可编译率 100%；proved ≥ 50%
- [ ] `variant_pool/` 与 `l2_to_m5.py` 产物各一个可训练批次（含 π_MCTS/z 占位）

## P2 — 全量 12 领域 ≥ 200K（预计 2–4 周）

| 任务 | 说明 |
|---|---|
| R1–R4 全领域生成 + 验证流水 | `03`、`05` |
| L1 DAG 全量 + L2 树归集 | `04` |
| 许可核验（混合来源） | `05` 第 6 节 |
| 平衡与泄漏报告 | `05` 第 3/4/5 节 |

**验收**（即 `00` 第 4 节全部指标）
- [ ] verified ≥ 200,000；proved ≥ 60%
- [ ] 唯一率 ≥ 95%；类平衡偏差 < 30%；泄漏 = 0
- [ ] `reports/licenses.md` 完成

## P3 — 训练第一轮（预计 1–2 周）

| 任务 | 说明 |
|---|---|
| T0 SFT（LeanTree + R3 增补） | `06` 第 2 节 |
| T1 第一批 MCTS 蒸馏（100–200 题） | `06` 第 3 节 |
| 评估门（miniF2F / 领域 holdout / pass@k） | `06` 第 6 节 |

**验收**
- [ ] π_MCTS 蒸馏 loss 下降 + value 回归收敛
- [ ] miniF2F-valid 不低于 SFT 基线；pass@k 降幅 < 30%
- [ ] 训练日志与报告归档 `reports/train_round_1.md`

## P4 — 规模化（持续）

- 批次放大到 2K 题/批、E1→E3 课程轮转；
- 与 M3 专家路由联动（按领域注册 adapter）；
- 数据增量：每月重跑增量导出（`source_commit` 变更）与新题生成；
- 开放问题：`higher-category` / `algebraic-geometry` / 数值线代语料缺口专题（R4 为主）。

## 风险对冲（对应 `09`）

- E 盘随时可能掉线 → P0 起就不依赖 E 在线（F + 远程为主）；
- 验证吞吐不足 → 提前在 P1 标定单题编译成本并调并发；
- agent 变体通过率低于 25% → 回退 R1 配额并收紧模板。
