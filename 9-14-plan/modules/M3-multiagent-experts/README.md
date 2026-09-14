# M3 — 多智能体/专家框架（外层调用者）

## 数学
见 `../../00-math-theory.md` §6：联合策略/奖励、专家互补项、版本与继承。

## 概念模型（Q0/Q0-1 裁定）
- **专家 = (base_model, adapter_id, domain, version)**；异构允许（REAL-Prover 与 Qwen 混编）；
- **不做版本分裂**：更新只升 `version`，经验走 `experience 链` 继承；
- **类 MoE 但更灵活**：无需同一模型；跨卡分布式 = 每卡独立专家进程（无 NVLink 需求）。

## 专家数与领域划分（Q0-1）
| 阶段 | 专家数 | 划分 |
|---|---|---|
| MVP | 2-4 | 群论 / 环论 / 域论 / 综合 |
| 扩展 | 8-16 | +伽罗瓦/表示论/代数几何/范畴论 |
| 上限 | 16-32 | 依据「路由冲突率 + 数据量 2k-10k/类」动态增删 |

## 伪代码

```text
registry: {adapter_id → {base, domain, version, endpoint, stats}}

def route(problem, k=2):
    # 规则优先：领域标签匹配；冷启动用 embedding/LLM 分类器兜底
    scores = [domain_match(problem, e) for e in registry]
    return top_k(scores, k)

def joint_reward(traces, e_list):
    R = Σ_e 1[proof_e] · γ^{steps_e}
    R += λ_collab · complementarity(traces)     # 互补：不同专家解决不同子目标
    R -= λ_cost · Σ_e steps_e / budget_e
    return R

def update_cycle(problem_batch):
    for p in problem_batch:
        experts = route(p)
        traces = [run_expert(e, p) for e in experts]   # 内部各自 MCTS
        R = joint_reward(traces, experts)
        for e in experts:
            submit_learn(e, event=trace_e, advantage=R) # M4 learn/v1
        registry.update_versions(experts)
```

## 接口
- 对 M1：`run_expert(e, p)` = 以 `adapter_id=e` 起 session（I3 契约）；
- 对 M4：`model` 字段传 adapter_id；对 M5/M6：提交 learn 事件；
- 对 M7：课程难度/领域标签输入路由。

## 门
- [ ] 路由正确率 ≥95%（离线 200 题集）；
- [ ] 联合奖励一次完整结算（含互补项数值可见）；
- [ ] 版本继承：新 expert 可复用旧 experience 链（记录可查）。
