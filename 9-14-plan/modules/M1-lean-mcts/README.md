# M1 — Lean MCTS 核心（Lean 4.28）

## 数学
见 `../../00-math-theory.md` §1（PUCT）、§3（φ 证据注入）。
核心不变量：树内采样由 GPU policy 提供（RULE-0）；工具阶段确定性（Q3 方案1）。

## 伪代码（Q3 方案1 扩展版）

```text
INPUT: root state s0=(C0,Δ0,E0), N_sim, τ, c_puct, expert e
TREE: nodes[], 每节点 {state, N, W, Q, P, children, expanded}

for sim in 1..N_sim:
  # ---- 阶段1 选择 ----
  node ← root; path ← [node]
  while node.expanded and not terminal(node):
      if should_call_tool(node.state):        # 工具条件（启发式/独立策略）
          while should_call_tool(node.state): # 确定性链，原地更新
              τ_tool ← tool_policy(node.state)
              node.state ← Exec_tool(node.state, τ_tool)   # 更新 E
          continue
      a ← argmax_a [ Q + c_puct·P(a)·√ΣN / (1+N(a)) ]      # PUCT
      node ← child(node,a); path.append(node)

  # ---- 阶段2 扩展 ----
  if not node.expanded and not terminal(node):
      (p(·), v) ← GPU_Forward(e, Prefix(node))              # M4 policy+value
      p ← reweight(p, φ(RingLog))                            # φ 证据重加权（π'∝π·φ）
      for a in A_tactic: 新建 child, N=W=0, P=p(a)

  # ---- 阶段3 评估 ----
  z ← +1 if terminal(Δ≡⊤) else v

  # ---- 阶段4 回传 ----
  for n in path: n.N+=1; n.W+=z; n.Q=W/N

OUTPUT: π_MCTS(a|s0) ∝ N(s0,a)^{1/τ}
```

## 与现有代码的关系
| 现有 | 位置 | 复用方式 |
|---|---|---|
| PUCT 探索项 | `cpulean/Reap/Tactic/TreeSearch.lean` L333 | 原样（c_puct 参数化） |
| 子节点选择 | 同文件 L375 `selectChild` | 扩展：插入 φ 重加权钩子 |
| 节点/边界 | 同文件 L176/L185 | 原样 |
| φ 数据层 | `cpulean/Reap/Agentic.lean` L72–74, L85–86 | 接入 reweight 钩子 |

## 伪代码 → 代码映射（本模块）
- `lean/MCTSDriver.lean`（骨架）：树循环 + 工具状态机（占位 `should_call_tool`/`Exec_tool` 走 M2 接口）；
- **M2 = opencode 直驱**（任意 shell 的工具环，2026-09-14 裁定）：工具阶段由 opencode 会话执行；
- 接口桩：`LeanMCTS.lean` 假定 `GPU_Forward`/`Exec_tool` 已实现（本工程约定）。

## 门
- [ ] 3 题（IMO2019Q1/Pell×2）跑通工具链 MCTS（本地 Lean 4.28 编译+运行）；
- [ ] φ 重加权开关可切换（off 时结果与基线一致）。
