# AGENT.md — m2-tool-runtime（opencode 直驱版）

> 引用文件完整路径（本地 + GitHub + 云端）见 `../../9-14-plan/03-references.md`（REF 编号索引）。

## 用途
工具运行时 = **opencode 桥**（不再自制工具层）。发起 opencode 会话、导出原生轨迹、
解析 tool parts 供 M1（状态更新）与 M5/M8（训练/评测）使用。
**shell 不设白名单**（专用容器裁定）；护栏 = workdir 隔离 + 轨迹留痕 + 预算超时。

## 文件
| 文件 | 说明 |
|---|---|
| `opencode_bridge.py` | `OpencodeBridge.run/export_session/tool_round` |
| （已废弃）`tool_runtime.py` | 旧自制工具层——**移除**，勿引用 |

## 被引用（精确到行）
| 引用对象 | 位置 | 用途 |
|---|---|---|
| 双层 opencode 语义 | `2-9-14-Q.md` Q1-2（本地 `/home/a/文档/project/2-9-14-Q.md`） | 内层工具环定位 |
| M1 调用点 | `m1-lean-mcts/MCTSDriver.lean` `Runtime.execTool/toolChain` | 接口对接 |
| φ 证据 | `cpulean/Reap/Agentic.lean` L72–74/L85–86（REF-02） | 轨迹→证据 |
| 轨迹消费 | `m5-trainer-lora/lora_trainer.py`（`TraceStep.tool_calls`） | 训练数据 |
| 预算参考 | REF-16 `budgets.json`（v2） | wall/token 上限 |

## 依赖
- `opencode` CLI（版本不敏感，建议 ≥1.18）；无需 GPU；
- Lean 4.28 + lake（云上就位；opencode 的 bash 直接调用）。

## 上云/环境（从零）
```bash
# opencode 安装（容器内）
curl -fsSL https://opencode.ai/install | bash    # 或 npm i -g opencode
opencode --version
# 冒烟（在 workdir 内）
python3 opencode_bridge.py /work/agent
# 期望：ok=true 且 calls 含一次 bash（lean --version）
```

## 门
- [ ] `opencode run` 冒烟（bash/read 轨迹可导出解析）；
- [ ] 轨迹字段完整（kind/args/ok）进 `TraceStep.tool_calls`；
- [ ] 超时护栏：infra_error=True 且不入训练数据。
