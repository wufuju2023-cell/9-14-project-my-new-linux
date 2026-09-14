# 00 — 目标、数据模型与验收指标

## 1. 领域配额表（目标 12 × 20K = 240K，验收 ≥ 200K）

| # | domain id | 中文 | Lean 来源（路径前缀） | 20K 实现策略 |
|---|---|---|---|---|
| 1 | `algebra` | 代数（一般） | `Mathlib/Algebra`（除 Homology） | 直接题 + 变体 |
| 2 | `linear-algebra` | 线性代数（含矩阵/数值侧） | `Mathlib/LinearAlgebra`、`Mathlib/Analysis/InnerProductSpace`、SciLean | 直接题 + 实例化；数值浮点类以精确代数题替代 |
| 3 | `group-theory` | 群论 | `Mathlib/GroupTheory`、`Mathlib/Algebra/Group*` | 直接题 + 变体（P1 试点） |
| 4 | `ring-theory` | 环论 | `Mathlib/RingTheory`、`Mathlib/Algebra/Ring*` | 直接题 + 变体 |
| 5 | `field-theory` | 域论 | `Mathlib/FieldTheory`、`Mathlib/Algebra/Char*` | 直接题 + 变体 |
| 6 | `number-theory` | 数论 | `Mathlib/NumberTheory`、`PrimeNumberTheoremAnd`、`FLT`（数论部分） | 直接题 + 变体 + 竞赛题 |
| 7 | `representation-theory` | 表示论 | `Mathlib/RepresentationTheory`、`physlib`、`FLT`（模形式） | 直接题 + 变体，缺口用特化题补 |
| 8 | `category-theory` | 范畴论 | `Mathlib/CategoryTheory` | 直接题 + 对偶/泛化变体 |
| 9 | `higher-category` | 高阶范畴论 | `CategoryTheory/Bicategory`、`Monoidal`、`Enriched` + 合成 | 以合成/类比变体为主（语料最缺） |
| 10 | `homological-algebra` | 同调论 | `Mathlib/Algebra/Homology`、`Mathlib/Homology`、SpectralSequence | 直接题 + 拆解变体 |
| 11 | `algebraic-topology` | 代数拓扑 | `Mathlib/AlgebraicTopology`、`Mathlib/Topology/Algebraic` | 直接题 + 特化变体 |
| 12 | `algebraic-geometry` | 代数几何 | `Mathlib/AlgebraicGeometry`、`LTE`、`FLT`（scheme 部分） | 直接题 + 拆解变体（语料偏少） |

配额为**柔性**：某领域达不到 20K 时，用相邻领域的步骤级题补足总量 ≥ 200K，
差额与理由写入 `reports/quota_adjust_*.md`。

## 2. Question 数据模型（每行 = 一个 question）

强制字段（JSONL / parquet 同构）：

```text
id                全局唯一（domain-000001 形式）
domain            上表 domain id
subdomain         可选：文件目录二级名（如 GroupTheory.Sylow）
source_repo       如 leanprover-community/mathlib4
source_commit     如 8f9d9cf（必须记录，版本漂移时回溯用）
source_decl       如 Sylow.exists_subgroup_card_pow_prime
source_file       Mathlib/GroupTheory/Sylow.lean
statement_lean    Lean 题面（`theorem ... : ... := by sorry` 形式，可编译）
statement_nl      自然语言题面（中文/英文，可空，后续回填）
proof_lean        参考答案（原证明或补出的证明，可空）
proof_status      proved | open
proof_tree_ref    指向 proof tree 分片与行号
difficulty        E1 | E2 | E3（见 05）
generators        生成器列表，如 ["direct","specialize"]
license           源许可（如 Apache-2.0）
hash              题面规范化哈希（去重用）
verified_at       最近一次验证时间戳
```

## 3. Proof tree 三档

- **L1 声明级 DAG**：`theorem → 使用到的其它声明` 有向图（从 importGraph / 导出器拿），
  全量覆盖，成本最低，用于检索与前提选择训练。
- **L2 步骤级树**：`state --tactic--> state'`，含 goal 上下文、候选 tactic 分布 π_MCTS。
  主训练格式，来自 LeanTree factorized trees / LeanDojo traces / 步骤题生成器。
- **L3 项级**：完整证明项（kernel term），可选，只对难题存档，来自 `lean --export`。

## 4. 验收指标（P2 出口）

| 指标 | 阈值 |
|---|---|
| question 总量 | ≥ 200,000（verified=true） |
| statement_lean 可编译率 | 100%（parse + elab 通过） |
| 有证明率（proved） | ≥ 60%（open 题单独归档，可作定理证明评测题） |
| 去重后唯一率 | ≥ 95%（题面哈希 + MinHash 双重） |
| 领域类平衡偏差 | < 30% |
| benchmark 泄漏 | 0（黑名单命中即为缺陷） |
| 许可台账完整度 | 100%（无 license 字段的行数 = 0） |

## 5. 与既有契约的对接

- M7：`variant_pool/{problem_id}/meta.json` 字段
  `{statement, difficulty, family, source, verified:true}` 是本 schema 的视图，
  导出脚本负责投影（`tools/export_variant_pool.py`，P1 交付）。
- M5：步骤级树转 `{problem_id, nodes:[{state, pi_mcts, z, tool_calls}], source}`，
  见 `04-proof-trees.md` 第 4 节。
- M8：评测用 holdout 子集与泄漏黑名单同源（`05` 第 4 节）。
