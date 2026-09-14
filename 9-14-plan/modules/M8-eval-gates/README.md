# M8 — 评测与门（含多样性保护）

## 核心指标（Q2 裁定：pass@k 对 MCTS 更关键）
| 指标 | 定义 | 用途 |
|---|---|---|
| pass@1 | 单次采样证明成功率 | 参考（RLHF 式方法常优化它） |
| **pass@k** | k 次独立采样的至少一次成功率（k=8/16） | **MCTS 生命线** |
| 多样性 | 成功轨迹两两 Jaccard 中位；distinct 计数 | 树扩展性 |
| value 距离域 | d̂ 分布（直方图） | 头质量监控 |
| 工具质量 | tool_call 合规率/成功率 | RL 奖励分量 |

## 防多样性塌缩门（任何 RL 更新；GRPO 若启用时重点监控）
```text
每轮 RL 后：
  p1 = pass@1(eval_set); pk = pass@k(eval_set)
  if pk < 0.7 * pk_prev:      # 下降超 30%
      ROLLBACK 本轮 adapter（版本回退，M3 registry）
      记录 incident；提示：加入熵正则/优势软化 A/τ
```
- 同时监控 Jaccard 中位（>0.7 告警，9-7 系列 RULE）；
- 成功轨迹家族数 <2 的题不进 RL 数据（防单点回放）。

## 评测协议（可复现）
```text
eval_set: 固定 theorem-level holdout（与训练 theorem-family 隔离）
预算: 固定 N_sim / tokens（与训练一致）
种子: 固定；重复 3 次取中位
输出: eval_report.json {pass@1, pass@k, jaccard_med, d_hist, tool_quality}
```

## 与 scaling-plan-1 经验联动
- E1 门（value 端点 sd=0 或分布报告）作为每次评测前置自检；
- 类平衡报告（按 family/难度分层）——防止评测集偏斜伪装成"进步"。

## 门
- [ ] 评测 harness 在 3 题 smoke 上跑通（输出与参考一致）；
- [ ] RL 一轮后 pass@1/pass@k 双报；
- [ ] 塌缩门演练一次（人为注入塌缩 → 回退路径生效）。
