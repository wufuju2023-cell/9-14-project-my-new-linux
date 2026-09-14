# AGENT.md — m8-eval

> 引用文件完整路径（本地 + GitHub + 云端）见 `../../9-14-plan/03-references.md`（REF 编号索引）。

## 用途
评测 harness：pass@1/pass@k、多样性（Jaccard 中位）、value 距离直方图、工具质量；
塌缩门（RL 后 pass@k 降 >30% → 建议回退）。

## 文件
| 文件 | 说明 |
|---|---|
| `eval_harness.py` | `evaluate()` / `collapse_gate()` / `EvalReport` |

## 被引用（精确到行）
| 引用对象 | 位置 | 用途 |
|---|---|---|
| pass@k 重要性论证 | `2-9-14-Q.md` Q2/Q3 | 指标选择依据 |
| 多样性实测基线 | `v1-1-9-7-experiment-1/03-E3-E4-E5.md`（E4 distinct 7-11/16） | 门阈值参考 |
| Jaccard 门（0.7） | `9-7-agent-alpha-proof/07-does-it-produce-different-nodes.md` | 路线多样性判据 |
| RL 目标 | `9-14-plan/00-math-theory.md` §5（主更新公式；GRPO 禁用） | 与 M5 联动 |
| 回退对象 | `m3-multiagent/expert_router.py` `Registry.bump_version` | 版本回退接口 |

## 依赖
- `shared/schemas.py`；标准库 only（statistics/json）。
- 真实 rollout 由 M1+M4 提供（注入 `rollout_fn`）。

## 上云/环境
- 评测集放 `/work/eval/holdout/`（theorem-family 与训练隔离）；
- 预算固定（与训练一致），种子固定，重复 3 次取中位。

## 门
- [ ] 3 题 smoke 与参考一致（1.786/1.962/3.216 的 value 域）；
- [ ] RL 一轮后 pass@1/pass@k 双报；
- [ ] 塌缩门演练（注入塌缩 → rollback=True）。
