# 05 — 验证门与数据质量

> 验证是整条产线的瓶颈与唯一质量真源：**题面/证明不通过 Lean，一律不入库**。

## 1. 验证流水（每批生成后执行，远程并发）

```text
输入：generated/<domain>/<gen>/batch_*.jsonl.zst
步骤：
  1) parse：Lean 语法解析（拒收即记 rejected/parse）
  2) elab ：题面类型检查（`theorem … : … := by sorry` 能编译）
  3) prove：proof_lean 非空时验证证明（无 sorry / 无 axiom 违规）
  4) bucket：难度分桶（E1/E2/E3）
  5) dedup ：题面规范化哈希 + MinHash
  6) leak ：基准黑名单过滤
  7) write：verified/<domain>/batch_*.jsonl.zst（原子 mv）
```

- 批量执行器：`tools/verify_batch.sh` + `lake env lean` 进程池（16 线程）；
- 每批产出 `reports/verify_<batch>.json`（计数、通过率、拒绝原因直方图）。

## 2. 难度分桶（与 M7 一致）

| 桶 | 判据 | 用途 |
|---|---|---|
| E1 | `by simp` / `by omega` / `by decide` 秒过 | 冷启动 |
| E2 | 需 1–3 步引理（搜索预算内可解） | 主体课程 |
| E3 | 需分解 / 多引理（≥4 步） | 难题池 / 评测 |

分桶由编译探测（预设 tactic 序列尝试）给出，成本纳入验证批。

## 3. 去重

- 题面规范化：去空白、统一 binder 名、`_` 替换，再 AST 指纹；
- 精确重复：哈希相等 → 拒；
- 近似重复：MinHash + Jaccard 阈值 **0.9** → 保留来源更权威者（mathlib 优先）；
- family 级：同 `family_id` 的题只进一个数据切分（train/eval 不串）。

## 4. Benchmark 泄漏黑名单（零容忍）

| 来源 | 处理 |
|---|---|
| miniF2F-lean4、ProofNet (#, v2/v3)、PutnamBench-lean4、LeanEuclid | 题面哈希 + 源 decl 前缀双黑名单 |
| `formal-conjectures` | 其全部声明进入 holdout 候选，不得进训练 |
| 未来新增基准 | 新增黑名单文件 `blacklist/<name>.json` 并重跑 leak 检查 |

## 5. 类平衡

- 12 领域目标各 20K，允许 ±30%（即 14K–26K 区间内视为达标）；
- 偏差超限时对缺口领域重采样（提高 R2/R4 配额），从超配领域降采样；
- 每轮报告 `reports/balance_*.json`。

## 6. 许可台账

- 每行数据强制 `license` 字段（源头许可）；
- `lean-liquid`（无许可）数据单独存放 `restricted/`，**不进任何对外产物**；
- `ProofPile-2` 等混合来源需在大规模入库前逐项核验（P2 前置任务）；
- 汇总报告 `reports/licenses.md`（按 repo × 许可 × 行数）。

## 7. 验收口径回顾

见 `00-goals-and-metrics.md` 第 4 节：总量 ≥ 200K、可编译 100%、
proved ≥ 60%、唯一率 ≥ 95%、类平衡 < 30%、泄漏 0。
