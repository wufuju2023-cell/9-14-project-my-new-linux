# M2 — 工具运行时（opencode 直驱版）

> 裁定（2026-09-14）：**不再自制 Python 工具层**。工具调用直接借助 opencode：
> 它的内建工具（bash/read/write/edit/grep/glob 等）就是工具环本体。
> **shell 不设白名单**——允许任意命令（专用容器内，收益>风险）；改为"护栏而非限制"。

## 为什么用 opencode 而不是自制工具层

| 维度 | 自制 Python 工具 | opencode 直驱（本方案） |
|---|---|---|
| 能力面 | 4 个手工工具 | 完整 agent 工具集（bash/文件/搜索/编辑…） |
| 扩展 | 每加能力写代码 | 模型自主组合（可跑 `lake build`、`lean`、`git`、`pip` 等） |
| 轨迹 | 自造 JSONL | 会话原生记录（session → export JSON） |
| 维护 | 高 | 低（跟随 opencode 版本） |

## 护栏（替代白名单，三条）
1. **轨迹留痕**：每次工具环会话以 `opencode` 原生 session 记录；
   导出（`opencode export <sessionID>`）→ 解析 tool parts → 存入 `TraceStep.tool_calls`
   （供 M5/M8 训练与评测使用）。
2. **快照护栏**：会话工作目录固定 `workdir=/work/agent-<sid>/`；
   `/mnt/workspace`（持久区）写入前先 `tar` 快照到 `backups/`（脚本级 hook）。
3. **预算护栏**：每会话 wall-clock 与 token 上限；超限终止并标记 `infra_error`
   （不计入学习信号，防污染训练数据）。

## 接入形态（三选一，按频率）
| 形态 | 命令 | 适用 |
|---|---|---|
| CLI 单次 | `opencode run "<prompt>"`（cwd=workdir） | 低频（每题 1-2 次） |
| Headless 服务 | `opencode serve` + HTTP/ACP 会话 | 高频/多专家并发 |
| ACP | `opencode acp` | 与 M1 协议直连（实验性） |

版本不敏感（用户裁定）；建议 ≥1.18。

## 伪代码（M2 桥）

```text
def tool_round(state, goal_hint, budget):
    prompt = render_tool_prompt(state, goal_hint)     # 含可用工具说明与目标
    session = opencode_run(prompt, cwd=workdir, timeout=budget.wall)   # 任意 shell
    events = opencode_export(session.id)              # 原生轨迹
    calls  = parse_tool_parts(events)                 # bash/read/grep/... 全部保留
    state' = merge(state, extract_lean_artifacts(events))  # 编译输出/文件变更
    return state', calls, budget.used
```

## 与 M1 的接口（更新 I2）
- 旧：JSONL 文件轮询（自制工具协议）→ **废弃**；
- 新：M1 侧 `should_call_tool/execTool` 的语义改为「向 M2 桥提交一次工具环请求」，
  M2 返回 `(新状态, 工具轨迹)`；轨迹同时进 RingLog（φ 证据）与 TraceStep（训练）。

## 与 Q1-2 双层结构的关系
本层=**内层 opencode**（子 agent 的工具环）；外层调用者（M3）是另一个独立 opencode/LLM。
两层会话互不共享上下文（隔离），随机性仍只来自策略采样。

## 门
- [ ] `opencode run` 冒烟：在 workdir 完成一次 `lean --version` + `lake env lean` 调用；
- [ ] 轨迹导出解析：tool parts → `TraceStep.tool_calls` 字段完整；
- [ ] 护栏演练：超时终止 → 标记 infra_error（不进训练数据）。
