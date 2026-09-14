# AGENT.md — m7-curriculum

> 引用文件完整路径（本地 + GitHub + 云端）见 `../../9-14-plan/03-references.md`（REF 编号索引）。

## 用途
代数题语料：R1 受限变换（立即可用）+ R2 agent 生成（计划正路）；
验证门（语法/编译/去重）+ 课程调度（难度分层 + 类平衡门）。

## 文件
| 文件 | 说明 |
|---|---|
| `variant_gen.py` | `VariantPool` / `r1_expand()` / `r2_generate()` |
| `curriculum.py` | `ValidationGate` / `schedule()`（budgets 对齐） |

## 被引用（精确到行）
| 引用对象 | 位置 | 用途 |
|---|---|---|
| 受限变换实现 | `v1-result/…/cpu_runtime/target_variants.py`（`SCHEMA_VERSION` L28 附近） | R1 变换语义 |
| 预算契约 | `v1-result/…/experiments/proof-curriculum/budgets.json`（v2） | 课程预算字段 |
| 预检入口 | `experiments/proof-curriculum/prepare_attempt.py` | 编译预检 |
| 类平衡教训 | `scaling-plan-1/10-lessons-and-artifacts.md` 经验 #4 | 防过采样塌缩 |
| 难度参考 | `leantree_mathlib.jsonl`（proof_depth） | 难度估计素材 |

## 依赖
- `shared/schemas.py`；标准库 only；云上接 `m2.tool_runtime` 做真实编译预检。

## 上云/环境
- 池目录 `/work/pools/variant_pool/`（NFS 持久）；
- R2 的 `agent_fn` 注入：本地=stub；云上=opencode/LLM 调用。

## 门
- [ ] R1 ≥300 题（通过率>90%）；
- [ ] R2 ≥100 题（通过率>25%，类平衡 `balance_ok`）；
- [ ] `schedule()` 分层直方图 + budgets 输出。
