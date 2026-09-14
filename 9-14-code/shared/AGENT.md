# AGENT.md — shared 模块

> 引用文件完整路径（本地 + GitHub + 云端）见 `../../9-14-plan/03-references.md`（REF 编号索引）。

## 用途
唯一契约源。**其它模块不得自定义数据结构**——一律 import 本目录。

## 文件
| 文件 | 内容 |
|---|---|
| `schemas.py` | Problem/Evidence/ToolCall/ToolResult/TraceStep/Trace/LearnEvent/ExpertSpec + `phi()` |
| `http_contract.py` | `GpuSession`（policy/value/learn/retire，OpenAI 嵌套解析） |

## 被引用（精确到行）
| 本文件 | 引用自 | 位置 | 说明 |
|---|---|---|---|
| `phi()` 公式 | `cpulean/Reap/Agentic.lean` | L72–74（`evidenceComposite`） | φ=tanh(Σw) 与 Lean 同式 |
| 端点表 | `driver/runtime_transport.py` | L4–7 | session 协议 |
| policy 嵌套解析 | 同上 | L39–47 | `message.content` |
| value 嵌套解析 | 同上 | L49–58 | `{"score": d}` |
| learn 路由 | `gpu/gpu_runtime/server.py` | L182 | `/learn/v1` |

## 依赖
- 标准库 only（`json/urllib/math`）；测试用 `pytest`。

## 上云/环境
- 无 GPU 依赖；任何 python3.10+ 环境可直接用；
- 单测：`pytest tests/ -q`（含 `phi` 数值与解析回归）。
