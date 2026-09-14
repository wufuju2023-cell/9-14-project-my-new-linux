# M7 — 课程与数据（2k 代数题生成）

## 数学/方法引用
- 变体受限变换：`cpu_runtime/target_variants.py`（`nat_forall_instance` / `and_left/right`）；
- 课程预算：`proof-curriculum/budgets.json`（v2 契约）；
- 类平衡教训：scaling-plan-1 经验 #4（×8 过采样塌至 0.17 → 类平衡约束）。

## 两条生成路线
### R1（立即可用）：受限确定性变换
```text
seeds(50-100 抽象代数 statement) × {nat_forall_instance, and_left, and_right, ...}
→ Lean 语法检查 → 编译预检 → 去重 → variant_pool（目标 ≥300 题）
```

### R2（计划正路）：agent 变体生成器（opencode/LLM）
```text
for seed in seeds:
  for template in [simplify, generalize, decompose, lemma, analogy, local_transform]:
      draft = agent_generate(seed, template, isolation=session_i)   # 高温度
      if lean_syntax_ok(draft) and compile_preflight(draft):
          variant_pool.add(draft, family=seed.family, difficulty=estimate(draft))
目标 ≥2000 题；通过率门 >25%；类平衡偏差 <30%
```

## 难度分层（课程调度）
| 层 | 判据 | 用途 |
|---|---|---|
| E1 | `simp`/`omega` 直接可解 | 冷启动 |
| E2 | 需 1-3 步引理 | 主体课程 |
| E3 | 需分解/多引理（≥4 步） | 难题池 |

## 数据管道（与 M5 对接）
```text
variant_pool/{id}/meta.json  {statement, family, difficulty, source, verified}
成功树 → replay 数据（state,action,reward,value_pred, tool_calls）
→ M5 训练集（含 Mathlib 混批 90/10）
```

## 与 Q1-1（冷门领域）衔接
- higher topos/higher algebra/Kerodon 翻译成 LeanTree 属"长期素材"，
  本模块先用"标准代数 + 生成变体"，翻译线独立推进（成本数百亿 token 级，需单独评估）。

## 门
- [ ] R1 ≥300 题（通过率>90%）；
- [ ] R2 ≥100 题（通过率>25%，类平衡<30%）；
- [ ] 难度分层直方图 + 课程调度 dry-run。
