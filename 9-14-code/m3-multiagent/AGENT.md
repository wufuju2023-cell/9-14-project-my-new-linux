# AGENT.md — m3-multiagent

> 引用文件完整路径（本地 + GitHub + 云端）见 `../../9-14-plan/03-references.md`（REF 编号索引）。

## 用途
外层多智能体调度：专家注册/路由、联合奖励结算、版本与经验继承。
可运行于无 GPU 的调度机（CPU 侧）。

## 文件
| 文件 | 说明 |
|---|---|
| `expert_router.py` | `Registry`（注册/升版本/持久化）+ `Router.route` |
| `joint_reward.py` | `joint_reward()` / `complementarity()`（Q0 公式） |

## 被引用（精确到行）
| 引用对象 | 位置 | 用途 |
|---|---|---|
| 联合奖励公式 | `9-14-plan/00-math-theory.md` §6 | 数学定义 |
| Q0 裁定 | `2-9-14-Q.md` Q0/Q0-1 | 版本继承/专家数 |
| adapter 路由契约 | `9-14-plan/01` I3 | model 字段=adapter_id |
| M4 会话 | `9-14-code/shared/http_contract.py` `GpuSession` | 调用专家 |
| M5 learn | `gpu/gpu_runtime/server.py` L182 | 提交更新 |

## 依赖
- `shared/schemas.py`（ExpertSpec/Problem）；标准库 only。

## 上云/环境
- 无特殊依赖；registry.json 放 `/work/registry/`（NFS 持久）；
- 多卡时 `ExpertSpec.endpoint` 指向各卡服务地址。
