# M5 — 训练器（主：MCTS 蒸馏 / 辅：GRPO 轨迹级）

> 修正（2026-09-14）：主更新 = **AlphaZero/AlphaProof 式搜索蒸馏**（π_MCTS + z）；
> GRPO 降级为**工具级 credit assignment 的辅助信号**（可选消融），不再作主循环。

## 数学

### 主更新（每次课程批次后）
$$
\mathcal{L}_{\text{main}} = -\sum_a \pi_{\text{MCTS}}(a\mid s)\log \pi_\theta(a\mid s)
\;+\; \lambda_v\,(v_\theta(s)-z)^2
\;+\; \beta\,\mathrm{KL}(\pi_\theta\,\|\,\pi_{\text{ref}})
$$

- `π_MCTS`：搜索 visit 分布（根策略 $\propto N^{1/\tau}$，即"更好的策略"）；
- `z`：搜索结果（proof 成功 +1 / 失败按距离头 −d̂，与 value 语义一致）；
- `KL(·‖π_ref)`：防遗忘（frozen base 或上一 release）。

### 辅助（GRPO）：**暂时禁用（2026-09-14）**

> 裁定：GRPO **暂时禁用**，主循环只用 MCTS 蒸馏。保留条款（供将来评估）：
> ① 仅在工具级 credit assignment 场景启用；② 启用前必须有 A/τ 软化 + 熵正则方案；
> ③ 必过 M8 多样性门（pass@k 降>30% 回滚）；④ 以消融实验形式跑，不混入主训练。
>
> 历史公式（存档）：
> $A_i = \frac{r_i - \mathrm{mean}(\{r\})}{\mathrm{std}(\{r\})}$，
> $\mathcal{L}_{\text{tool}} = -\sum_i A_i \log \pi_\theta(a_i\mid s_i)$


## 两个训练层级（更新）

| 层级 | 触发 | 数据 | 目标 |
|---|---|---|---|
| 题内 TTT | 每题 | 本题轨迹 | NLL+KL+CE（现有 learn/v1） |
| **跨题主更新** | 课程批次 | MCTS 树（π_MCTS, z） | **搜索蒸馏（本页主公式）** |
| ~~工具级辅助~~ | — | — | **GRPO 暂时禁用** |

## 伪代码（主循环）

```text
for batch in curriculum:                     # 大量问题
    data = []
    for p in batch.problems:
        tree = run_mcts(expert, p, budget)   # M1：GPU policy/value + 工具环(M2/opencode)
        data += extract(tree)                # (s, π_MCTS(·), z)
    update_policy_value(expert, data,        # 主公式（唯一更新路径）
        loss = CE(policy, π_MCTS) + λ_v·MSE(value, z) + β·KL(π‖π_ref))
    release(expert)                          # 版本+1（M3 registry）
```

## 数据格式
```json
{"problem_id":"...","nodes":[{"state":"...","pi_mcts":{"simp":0.6,"omega":0.3},
  "z":-2.0,"tool_calls":[...]}],"source":"mcts"}
```

## 门
- [ ] 一次主更新：π_MCTS 蒸馏 loss 下降 + value 回归收敛；
- [ ] 100-200 题课程批次稳定（无 NaN/OOM）；
- [ ] （GRPO 禁用期内）无任何 GRPO 路径进入训练。 
