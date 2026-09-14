# 06 — 训练方案（SFT 冷启动 → MCTS 蒸馏 → 评估门）

> 训练全部在 AMD MI300X 云实例（M4/M5/M6）；本机与 my-new-linux 不训练。
> 主更新公式与接口以 `9-14-plan/modules/M5-trainer-lora/README.md` 与
> `9-14-plan/01-architecture-interfaces.md`（I4/I5）为唯一真源，本文只写数据侧。

## 1. 总路线

```text
T0 SFT 冷启动（LeanTree + 本数据集步骤题）
T1 跨题主更新：MCTS 蒸馏（M5 主公式，π_MCTS + z + KL）
T2 value head 训练（z 回归 / 64-bin tokenized）
T3 可选对照：QLoRA（M6，预注册判定）
```

## 2. T0 — SFT 冷启动

| 项 | 值 |
|---|---|
| 基座 | `FrenzyMath/REAL-Prover` 或 `empero-ai/Qwen3.8-9B-Distill` |
| 数据 | L2 步骤题（LeanTree ~26 万 transitions + 本管线 R3 增补） |
| 格式 | `{state, tactic}` 序列 + 完整证明序列两种样本混合 |
| 配比 | 本数据集 : mathlib 混批 = **90 : 10**（防遗忘，沿用 M7 约定） |
| 目标 | 下一步 tactic 预测 top-1 提升；完整证明 pass@1 不低于基线 |

## 3. T1 — MCTS 蒸馏主循环（与 M5 对齐）

```text
for batch in curriculum:                # E1 → E2 → E3，每领域轮转
    for p in batch:                     # 起始 100–200 题/批，逐步放大到 2K
        tree = run_mcts(expert, p)      # M1 建树；M4 policy/value；M2 工具环可选
    update_policy_value(                # 唯一主更新路径（M5 主公式）
        loss = CE(policy, π_MCTS) + λ_v·MSE(value, z) + β·KL(π‖π_ref))
    release(expert)                     # M3 registry 版本 +1
```

- 数据落到 `04` 第 4 节的 M5 格式，来源 `source:"mcts"`；
- **GRPO 保持禁用**（2026-09-14 裁定）；工具级辅助信号只在消融档启用。

## 4. T2 — value head

- 目标 `z`：proof 成功 +1 / 失败按距离头 `-d̂`（与 M5、nanoproof 的经验一致）；
- 输出：64-bin tokenized value（共享 LM head，沿用 nanoproof 方案）；
- 训练信号来源：本数据集 L2 树的 `z` 字段（由 T1 每批回填）。

## 5. 课程设计（数据侧）

| 阶段 | 难度 | 数据量/批 | 领域 |
|---|---|---|---|
| 热身 | E1 | 2K | 全部 12 领域轮转（每领域 ~166） |
| 主体 | E2 | 1–2K | 每批 2–3 个领域，防单领域塌陷 |
| 难题 | E3 | 0.2–0.5K | 优先 `higher-category`、`algebraic-geometry` |

类平衡约束：每 3 批统计一次领域分布，偏差 > 30% 时下一批强制补缺口领域。

## 6. 评估（M8 门）

| 评测 | 用途 |
|---|---|
| miniF2F-valid / test | 与历史曲线对比（nanoproof 42–52% 区间为参照） |
| ProofNet / PutnamBench | 泛化与竞赛难度 |
| 领域 holdout（本数据集切分） | 12 领域各 ≥200 题，pass@1 / pass@k |
| pass@k 多样性门 | 相比上一 release 下降 > 30% → 回滚（M8） |

每轮训练报告写入 `reports/train_round_*.md`（含数据配比、loss 曲线、门结果）。

## 7. 依赖与顺序

```text
P2 数据出口（≥200K verified、L2 树就绪）
  → T0 SFT（云）
  → T1 第一批 MCTS 蒸馏（100–200 题）
  → M8 评估门
  → 放大批次（2K）与领域轮转
```

数据侧交付物：`verified/`（题）、`trees/L2/`（树）、`variant_pool/`（M7 视图）、
`reports/`（全部验证与平衡报告）。
