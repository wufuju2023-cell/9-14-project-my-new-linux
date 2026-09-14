# 04 — 证明树（三档格式与来源）

## 1. L1 声明级 DAG（全量，成本最低）

- 节点：声明（theorem/def/instance…），边：`定义/证明中引用的常量`；
- 来源：`importGraph`（首选，E 盘 mathlib packages 已有）、或导出器遍历证明项常量；
- 格式：

```json
{"src":"Sylow.exists_subgroup_card_pow_prime","dst":"Nat.Prime","kind":"type|proof"}
```

- 存储：`trees/L1/<domain>/edges-*.parquet`（列：src,dst,kind）+ 节点表 `nodes.parquet`；
- 用途：前提选择（premise selection）训练、检索增强、定理依赖查询。

## 2. L2 步骤级树（主训练数据）

- 结构：`state（goal 上下文）--tactic--> 子 state*`，含 visit 分布 / 候选分布（后续由 M1 搜索填充）；
- 来源优先级：
  1. `ufal/leantree`（factorized proof trees，CC-BY-4.0，26 万 transitions）——直接可用；
  2. `l3lab/ntp-mathlib`（miniCTX，mathlib tactic 数据）；
  3. `LeanDojo` / `harrywsanders/mathlib_extracted`；
  4. 自己用 Lean server 重放 mathlib 证明导出（成本高，最后手段）。
- 存储：`trees/L2/<domain>/<decl>.jsonl`，单证明一文件，便于增量更新。

## 3. L3 项级证明（可选）

- `lean --export` / `lean4export` 导出内核项；体量大（每声明数 MB）；
- 只对「难度 E3 且训练失败率高」的题存档，路径 `trees/L3/<domain>/<decl>.out.zst`。

## 4. 转 M5 训练格式（与 M5 README 对齐）

```json
{"problem_id":"group-theory-000123","domain":"group-theory",
 "nodes":[{"state":"h : P x ⊢ Q x","pi_mcts":{"simp":0.6,"exact h":0.3},
           "z":-2.0,"tool_calls":[]}],
 "source":"mcts|leantree|dojo","decl":"Sylow…","difficulty":"E2"}
```

- `π_MCTS`：初始用原证明的下一步 one-hot（SFT 冷启动），训练后由 M1 搜索分布替换；
- `z`：证明成功 +1；失败按距离头 `-d̂`（与 value 语义一致，见 M5 README）；
- 转换脚本：`tools/l2_to_m5.py`（P1 交付），同时产出 M7 `variant_pool` 投影。

## 5. 质量与一致性

- L2 树的每个 `state` 必须能被 Lean 复现（用 Lean server 重放校验）；
- 树与 question 的关联字段：`proof_tree_ref = {level, shard, line}`；
- 去重：同一 proof tree 只归属一个 question（family 内共享则标 `family_id`，训练时按 family 划分避免泄漏）。
