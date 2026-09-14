# 00 — 数学理论总纲（引用式，不重复造轮子）

> 本文只列**本工程需要的全部数学**及其出处。已有文档直接引用，不复制全文。

## 1. MCTS / PUCT（M1）

**参考**：`9-5-plan-original-paper/01-paper-baseline.md` §3（AlphaProof 论文对齐）；
本仓库 `cpulean/Reap/Tactic/TreeSearch.lean` 实现处：
- L333：PUCT 探索项 `U := c * p * sqrt(N) / (e.numVisit + 1)`
- L375：`selectChild`（子节点选择）
- L176/L185：`getNode!`/`getChild!`（边界）

论文公式：

$$
a = \arg\max_{a}\left[Q(s,a) + c_{\text{puct}}\, P(s,a)\, \frac{\sqrt{\sum_b N(s,b)}}{1 + N(s,a)}\right]
$$

AND 节点回传取子目标最小值（$V(s_{\text{AND}})=\min_i V(s_i)$）；根策略提取：

$$
\pi_{\text{MCTS}}(a\mid s_0) \propto N(s_0,a)^{1/\tau}
$$

## 2. 价值头（categorical 64-bin）（M4）

**参考**：`discussion/new_value_head_in7b_ex1/01_设计说明/01_Value设计与评价方法.md`；
实现：`gpu/gpu_runtime/categorical_search_backend.py`（L127 class，L273 `value`）。

$$
d \in \{1,\dots,64\},\quad y = -d,\quad \hat d(s)=\sum_{d} d\, p_\phi(d\mid s),\quad V(s) = -\hat d(s)
$$

在线非整数回传 → two-hot 分类目标（L39 `ONLINE_TARGET`）。

## 3. 贝叶斯证据环 φ（M1/M2）

**参考**：`9-7-agent-alpha-proof/09-bayesian-view.md`（B/C 分层）；
实现：`cpulean/Reap/Agentic.lean` L72–74（`evidenceComposite`），L85–86（`reweightBayes`）。

$$
P(t\mid s,R) \propto P_\theta(t\mid s)\cdot P(R\mid t,s),\qquad
\phi = \tanh\!\Big(\sum_k w_k\Big),\qquad
\pi'(a\mid s)\propto \pi(a\mid s)\cdot \phi
$$

## 4. 题内 TTT / 联合更新（M5）

**参考**：`00-v1-scope-and-source-of-truth.md`（训练对象）：

$$
\mathcal{L} = \mathcal{L}_{\text{policy NLL}} + \beta\, \mathrm{KL}(\pi_\theta \| \pi_{\text{frozen}}) + \lambda\, \mathcal{L}_{\text{categorical CE}}
$$

回执约束：LoRA + head 张量必须真实变化且被后续 generation/value 消费（版本递增）。

## 5. RL（跨题，M5）

### 主更新：MCTS 蒸馏（AlphaZero/AlphaProof 式，**主路径**）

$$
\mathcal{L}_{\text{main}} = -\sum_a \pi_{\text{MCTS}}(a\mid s)\log \pi_\theta(a\mid s)
\;+\; \lambda_v\,(v_\theta(s)-z)^2
\;+\; \beta\,\mathrm{KL}(\pi_\theta\,\|\,\pi_{\text{ref}})
$$

搜索即"改进算子"：π_MCTS（visit 分布，根 $\propto N^{1/\tau}$）与 z（搜索结果）
直接监督 policy/value——大量问题 → MCTS → 训练，无需 GRPO。

### 辅助：GRPO（**暂时禁用 2026-09-14**，存档公式）

$$
A_i = \frac{r_i - \mathrm{mean}(\{r\})}{\mathrm{std}(\{r\})},\qquad
\mathcal{L}_{\text{tool}} = -\mathbb{E}\Big[\sum_i A_i \log \pi_\theta(a_i\mid s_i)\Big] + \beta\, \mathrm{KL}
$$

- 禁用原因：pass@1↑/pass@k↓ 的塌缩风险（Q2），且主路径（搜索蒸馏）已足够；
- 恢复条件：工具级 credit assignment 确有必要 + A/τ 软化 + 熵正则 + M8 门 + 消融形式。

## 6. 多智能体联合（M3）

**参考**：`2-9-14-Q.md` Q0/Q0-1（联合状态/策略/奖励、专家=异构 adapter、类 MoE）。

$$
\max_{\{\theta_e\}}\; \mathbb{E}\big[\, R_{\text{joint}}(\tau_1,\dots,\tau_E) \,\big] \;-\; \beta\sum_e \mathrm{KL}(\pi_{\theta_e}\|\pi_{\text{ref},e})
$$

联合奖励设计（M3 代码 `joint_reward.py`）：

$$
R_{\text{joint}} = \sum_e \mathbb{1}[\text{proof}_e] \cdot \gamma^{t_e} \;+\; \lambda_{\text{collab}}\, \mathrm{cov}(\{\text{solve}_e\})
$$

（第二项奖励"专家互补"，抑制强者通吃。）

## 7. QLoRA 数学（M6）

**参考**：`1-QLoRA-zhihu.md`（NF4 分位数 $q_i$ 式(3)、双重量化、分页优化器）。
关键公式：

$$
q_i = \frac{1}{2}\Big(Q_X\big(\tfrac{i}{2^k+1}\big) + Q_X\big(\tfrac{i+1}{2^k+1}\big)\Big)
$$

工程含义：4-bit 冻结基座 + bf16 LoRA 适配器；ROCm 下需验证 bitsandbytes 兼容性
（M6 研究设计 §ROCm）。

## 8. 采样多样性与课程（M7/M8）

- 温度=分布宽度旋钮（`9-7-temperature-distribution-agent-distill/01-temperature-math.md`）；
- 实测：E4 distinct 7-11/16、E5 unique 2→4→6（`v1-1-9-7-experiment-1/03-E3-E4-E5.md`）；
- 课程防困：难度门 + 类平衡（scaling-plan-1 经验 #4：×8 过采样塌至 0.17）。
