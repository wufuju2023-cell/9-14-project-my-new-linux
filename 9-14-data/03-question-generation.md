# 03 — 问题生成（R1–R4 四类生成器）

> 目标：把「原始定理池」（估计 8–12 万条代数风格定理）放大到每领域 20K、总量 ≥ 200K。
> 所有生成器都遵循：**题面必须过 Lean 编译验证**（05），否则不入库。

## R1 确定性变换（立即可用，高通过率，保证明）

对齐 M7 的受限变换（`cpu_runtime/target_variants.py` 同族），逐条定理做：

| 变换 | 输入 | 产出 | 证明处理 |
|---|---|---|---|
| `hide_proof` | 原定理 | 题面 = 原 statement；答案 = 原 proof | 原证明直接可用 |
| `specialize` | 泛化定理 | 具体实例（群/环/域/K 具体值） | `exact?`/原证明特化，通常 1 行 |
| `add_hypothesis` | 原定理 | 追加假设的弱化题 | `by exact orig …` 一行 |
| `dual` | 范畴/序/群对偶定理 | `.op` / 反向定题 | mathlib 常已有对偶版，重复检测后改用原版 |
| `unfold_def` | 定义包装的定理 | 展开定义后的等价题 | 原证明前加 `simp only [...]` |
| `decompose` | 长证明定理 | 逐条中间引理的子问题 | 子引理证明从原证明切段 |

预计放大倍率：1.5–2.5×，通过率目标 > 90%。

## R2 Agent 变体生成（计划正路，中通过率）

对齐 M7 的 R2 模板（`simplify / generalize / decompose / lemma / analogy / local_transform`）：

```text
for seed in seed_pool[domain]:
  for template in templates:
    draft = agent_generate(seed, template, isolation=session_i, temperature=high)
    if lean_parse_ok(draft) and compile_preflight(draft):
        pool.add(draft, family=seed.family, difficulty=estimate(draft))
```

- 生成端可放在 opencode 会话（本机只出提示词与审查）或云实例批量跑；
- 目标通过率 > 25%，类平衡偏差 < 30%（与 M7 门一致）；
- 生成失败的题面进入 `rejected/` 并记录原因，供提示词迭代。

## R3 步骤级题（把证明树直接变成题，量最大）

从 L2 树（LeanTree / ntp-mathlib / LeanDojo traces）抽取：

- 题型 a：`(state, context) → next tactic`（下一步预测）；
- 题型 b：给定不完整证明骨架，填 `sorry` 位置（hole filling）；
- 题型 c：给定证明，选错误的 tactic 步骤（判别题，低价值，限量）。

预计产出：每条完整证明 3–20 个步骤题；26 万 transitions 量级起步。

## R4 反向 autoformalization（NL 题面 → Lean）

- 素材：`Lean-Workbook` 的 NL 题面池、`SJTULean/LeanStatement_*`、`formal-conjectures`（open 题）；
- 流程：NL 题面 → LLM 形式化 → Lean 编译（题面层验证）→ 进 pool（proof_status=open 或补证）；
- 用途：补足 `higher-category`、`algebraic-geometry`、`linear-algebra（数值侧）` 等语料缺口领域。

## 各领域配额分解（示例，P0 计数后固化）

| 生成器 | 占比 | 说明 |
|---|---|---|
| R1 直接/变体 | ~40% | 每领域 ~8K |
| R2 agent 变体 | ~30% | 每领域 ~6K |
| R3 步骤题 | ~20% | 每领域 ~4K |
| R4 反向题 | ~10% | 补缺口领域 |

## 批次与状态（与 02 同一状态机）

- 每批 = `(领域, 生成器, 种子分片)`，产物 `generated/<domain>/<gen>/batch_*.jsonl.zst`；
- 每批完成后同步投影到 M7 的 `variant_pool/{problem_id}/meta.json`（P1 交付投影脚本）；
- 生成速度不是瓶颈，**验证吞吐**是：验证在 my-new-linux 并发跑（16 线程），
  单次 `lake env lean` 编译约 2–10s/题，200K 题 ≈ 数天量级，分领域流水。
