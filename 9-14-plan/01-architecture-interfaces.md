# 01 — 架构与接口契约（模块间唯一真源）

> 全部引用文件的三层完整路径（本地 WSL / GitHub URL / 云端 /work）见 `03-references.md`。

## 系统架构（Q 文档的扩展方案落地）

```
┌────────────────────────── CPU 侧（Lean 4.28 + Python） ──────────────────────────┐
│  M1 Lean MCTS 核心                                                                │
│   ├─ 选择/扩展/回传/根策略（引用 TreeSearch.lean L333/L375）                       │
│   ├─ 工具状态机（Q3 方案1：确定性链，原地更新，不建树节点）                          │
│   └─ φ 证据注入（Agentic.lean L72/L85）                                            │
│  M2 工具运行时（内层 opencode）                                                    │
│   ├─ lean_search / lean_compile / file_read / script_run                          │
│   └─ lake build 缓存 + 类型检查                                                     │
│  M3 多智能体调度（外层调用者）                                                      │
│   ├─ 专家注册表（adapter_id → 基座/领域/版本）                                      │
│   ├─ 路由：问题 → 专家集合（top-k 或全参）                                          │
│   └─ 联合奖励与版本继承（experience 链）                                             │
│  M7 课程与数据        M8 评测与门                                                   │
└──────────────┬──────────────────────────────┬────────────────────────────────────┘
               │ HTTP session 协议             │ JSONL 文件交换
┌──────────────▼──────────────────────────────▼────────────────────────────────────┐
│  M4 GPU 推理服务（AMD 192GB）                                                       │
│   ├─ /sessions/{id}（create）  /policy/v1/... /value/v1/... /learn/v1              │
│   └─ adapter 热切换（多专家共享基座或独立进程）                                      │
│  M5 LoRA 训练器   M6 QLoRA 训练器（对照研究）                                        │
└───────────────────────────────────────────────────────────────────────────────────┘
```

## 接口契约表（所有模块只依赖本表）

### I1. Lean ↔ GPU（HTTP，沿用已验证协议）
| 端点 | 方法 | 请求 | 响应 |
|---|---|---|---|
| `/sessions/{sid}` | POST | `{theorem_id, role?}` | session 元数据 |
| `/sessions/{sid}/policy/v1/chat/completions` | POST | `{model, messages:[…], n, temperature}` | `choices[].message.content`（tactic 文本） |
| `/sessions/{sid}/value/v1/chat/completions` | POST | `{model, messages:[…]}` | `choices[0].message.content` = `{"score": d}` |
| `/sessions/{sid}/learn/v1` | POST | `{expected_policy_version, event}` | 更新回执（新版本号） |
| `/sessions/{sid}/retire/v1` | GET/DELETE | — | 回收收据 |

**实现引用**：`driver/runtime_transport.py` L4–7（端点注释）、L31（session）、L39（policy）、L49（value）。
**注意**：policy/value 响应是 OpenAI 嵌套（`message.content`），读取必须走嵌套解析（教训）。

### I2. Lean ↔ 工具运行时（opencode 桥，任意 shell）
```
M1 提交工具环请求（prompt + 当前状态）→ M2 OpencodeBridge
  → opencode 会话（内建 bash/read/grep/…，无白名单）
  → 返回 (新状态, tool_calls 轨迹)；轨迹同时进 RingLog 与 TraceStep
```
- 实现：`m2-tool-runtime/opencode_bridge.py`（`run/export_session/tool_round`）；
- 旧 JSONL 自制工具协议**废弃**；
- 护栏（非限制）：workdir 隔离 / 轨迹留痕 / 预算超时（infra_error 不入训练数据）。

### I3. M3 ↔ M4（专家路由）
- `model` 字段 = `adapter_id`（如 `exp.group-theory.v3`）；M4 负责加载/路由；
- 无 NVLink 多卡：**每卡一进程一基座**，专家以 adapter 挂载（同卡多 adapter 热切换），
  跨卡=HTTP 负载均衡（M3 维护 endpoint 表）。

### I4. M5/M6 ↔ M4（训练）
- TTT/联合更新走 `learn/v1`（事件：成功/失败轨迹、tool 质量）；
- 跨题 RL 走 M5 离线管线：收集（M8 筛选）→ 训练 → 新 adapter 注册（M3 registry）。

### I5. M7 ↔ M1/M5（课程）
- `variant_pool/{problem_id}/meta.json`：`{statement, difficulty, family, source, verified:true}`；
- `budgets.json`：沿用 `proof-curriculum/budgets.json` 契约（v2）。

## 版本与继承（Q0 裁定）
- 每个专家 = `(base_model, adapter_id, version)`；联合奖励触发更新时**只升版本不复制专家**；
- experience 链：成功轨迹 → `exp-{id}` → 可被其它专家"继承"（增量训练数据），
  继承记录写入 `registry.json`（M3），避免"版本分裂"失去经验积累。

## 数据流（一次题内循环）
```
M3 路由题→专家e → M1 建树(s0)
  ├─ [工具阶段] M2 确定性链：搜索/编译/读文件（原地更新 E）
  ├─ [tactic 采样] M4 policy(e, K 候选, T)
  ├─ LeanApply → 新节点 → M4 value(e) 回传
  └─ 证明完成 → M8 验证 → M5 learn/v1（TTT 事件）→ M3 experience 链
```
