# 9-14-plan — 多智能体 AlphaProof 工程总览

> 全部引用文件的三层完整路径（本地 WSL / GitHub URL / 云端 /work）见 `03-references.md`。

> 来源：`2-9-14-Q.md`（Q0–Q4）的扩展方案。目标：把「CPU 端 Lean MCTS + 工具链」与
> 「GPU 端策略/价值/训练（LoRA 与 QLoRA 双方案）」模块化封装，支持并行开发与分工。
> 环境终点：AMD MI300X 192GB 云 GPU（现本地准备，零部署）。

## 模块地图（8+1）

| 模块 | 名称 | 语言 | 职责 | 依赖 |
|---|---|---|---|---|
| M0 | 接口总纲 | 文档 | 接口矩阵/数据流/契约 | — |
| M1 | Lean MCTS 核心 | Lean 4.28 | 选择/扩展/回传/根策略、工具状态机、φ 证据注入 | M4 |
| M2 | 工具运行时 | **opencode 直驱** | opencode 会话工具环（bash/文件/搜索，任意 shell）、轨迹导出 | M1 |
| M3 | 多智能体/专家 | Python | 专家注册/路由（多 LoRA adapter）、联合奖励、版本与继承 | M4/M5 |
| M4 | GPU 推理服务 | Python | policy/value/learn 端点（64-bin 头）、adapter 热切换 | — |
| M5 | 训练器（LoRA） | Python | TTT、MCTS 蒸馏主更新（GRPO 暂时禁用） | M4/M7 |
| M6 | 训练器（QLoRA） | Python | NF4/双重量化/分页；**LoRA vs QLoRA 对照研究** | M5 |
| M7 | 课程与数据 | Python | 代数题生成（R1 变换/R2 agent）、验证门、LeanTree 管道 | M2 |
| M8 | 评测与门 | Python | pass@k 多样性、E 系列、防 GRPO 多样性塌缩门 | M4/M5 |

## 核心接口（细节见 `01-architecture-interfaces.md`）

```
M1(Lean) ──JSONL──► M2(工具) ──JSONL──► M1
M1 ──HTTP(session协议)──► M4(GPU) ──► value/policy
M3 ──adapter_id 路由──► M4
M5/M6 ──learn/v1──► M4
M7 ──variant_pool──► M1/M5
M8 ──metrics──► 全链
```

## 关键设计裁定（承接 Q 文档）

1. **Q3 方案1 采纳**：工具阶段=确定性链、原地更新状态、**不分叉不建树节点**；
   仅 Lean tactic 状态变化处采样 K。价值头只用 Lean 状态监督（SFT 自 agent 成功轨迹）。
2. **双层 opencode**：外层（多智能体调用者）与内层（子 agent 的 tactic 生成工具环）分离；
   随机性只来自策略采样（工具执行确定性）。
3. **多样性保护**：GRPO 提高 pass@1 可能伤 pass@k → M8 设多样性门（见 M8 文档）。
4. **专家=异构 LoRA adapter**（可不同基座），无 NVLink 的多卡用"数据/专家并行"而非张量并行。
5. **LoRA 与 QLoRA 并行研究**：M6 负责判定（显存/速度/精度/适配性四维对照）。

## 分工建议（并行开发）
- 开发者 A：M1+M2（Lean/工具）
- 开发者 B：M4+M5（GPU 推理+LoRA 训练）
- 开发者 C：M6+M7（QLoRA+课程数据）
- 开发者 D：M3+M8（多智能体+评测）

## 里程碑
见 `02-milestones-gates.md`；每个模块的详细数学与伪代码见 `modules/M*/README.md`。
