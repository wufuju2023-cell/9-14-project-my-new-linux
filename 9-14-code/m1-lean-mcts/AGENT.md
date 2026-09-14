# AGENT.md — m1-lean-mcts

> 引用文件完整路径（本地 + GitHub + 云端）见 `../../9-14-plan/03-references.md`（REF 编号索引）。

## 用途
Lean 4.28 的 MCTS 驱动骨架：工具状态机（Q3 方案1：确定性链、原地更新、不建树节点）
+ φ 证据重加权钩子（π' ∝ π·φ）。

## 文件
| 文件 | 说明 |
|---|---|
| `MCTSDriver.lean` | `Evidence/phi/ToolCall/NodeState/Runtime/simulateOnce`（独立可编译） |

## 被引用（精确到行）
| 引用对象 | 位置 | 用途 |
|---|---|---|
| PUCT 探索项 | `cpulean/Reap/Tactic/TreeSearch.lean` **L333** | `U := c*p*sqrt(N)/(numVisit+1)` |
| 子节点选择 | 同文件 **L375** `selectChild` | 真实 selection |
| 节点边界 | 同文件 **L176/L185** `getNode!/getChild!` | 越界保护 |
| φ 公式 | `cpulean/Reap/Agentic.lean` **L72–74**（`evidenceComposite`）/ **L85–86**（`reweightBayes`） | 与 Lean 同式 |
| 证据结构 | 同文件 **L51**（`structure Evidence`） | 字段对齐 |
| opencode 桥契约 | `9-14-plan/01-architecture-interfaces.md` I2（2026-09-14 更新版） | M2 接口 |

## 依赖
- Lean 4.28（`lean-toolchain` 已固定）；本骨架仅需 core+`Lean.Data.Json`；
- 真实树逻辑需 `cpulean` 工程的 olean（按 `v1-1-agentic-tool/README` 编译）。

## 上云/环境（从零）
```bash
curl -fsSL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh | sh -s -- -y --default-toolchain v4.28.0
cd <repo>/cpulean && OUT=$(pwd)/.build/olean && mkdir -p "$OUT/Reap/..." && export LEAN_PATH="$OUT:$PWD"
lean -o "$OUT/Reap/Agentic.olean" Reap/Agentic.lean
lean --run ../m1-lean-mcts/MCTSDriver.lean   # 骨架自检（无 IO 依赖）
```

## 门
- [ ] 骨架独立编译通过（lean 4.28）；
- [ ] 与 M2 的 JSONL 对接冒烟（req→resp 一轮）；
- [ ] φ 开关 off 时与基线选择一致（钩子空转）。
