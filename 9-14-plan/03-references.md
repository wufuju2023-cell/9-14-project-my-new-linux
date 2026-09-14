# 03 — 引用文件索引（唯一权威：完整本地路径 + GitHub URL + 云端路径）

> 所有模块文档中的「REF-n」均指向本表。**禁止**在其他文档里只写相对路径。
> 三层路径 = 本地开发机（WSL，`/mnt/f/projects/…`）｜GitHub（可直接点开，含行号）
> ｜云端部署路径（AMD 192GB 实例，`/work/…`）。

## A. 代码：`v1-1-agentic-tool`（GitHub `main`）

本地根：`/mnt/f/projects/v1-1-agentic-tool`
GitHub 根：`https://github.com/wufuju2023-cell/v1-1-agentic-tool/blob/main`
云端根：`/work/v1-1-agentic-tool`

| REF | 文件（本地/云端相对路径） | 关键行 | GitHub URL（含行号） |
|---|---|---|---|
| REF-01 | `cpulean/Reap/Tactic/TreeSearch.lean` | L176/L185（getNode!/getChild!）、**L333**（PUCT）、**L375**（selectChild） | `…/cpulean/Reap/Tactic/TreeSearch.lean#L333` |
| REF-02 | `cpulean/Reap/Agentic.lean` | **L51**（Evidence）、**L72–74**（evidenceComposite/tanh）、**L85–86**（reweightBayes） | `…/cpulean/Reap/Agentic.lean#L72` |
| REF-03 | `cpulean/Reap/TreeSearch/MCTS.lean` | 纯 Std 化后版本 | `…/cpulean/Reap/TreeSearch/MCTS.lean` |
| REF-04 | `driver/runtime_transport.py` | **L4–7**（端点表）、L31（session）、**L39**（policy 嵌套解析）、L49（value） | `…/driver/runtime_transport.py#L39` |
| REF-05 | `gpu/gpu_runtime/server.py` | **L178**（policy）、**L180**（value）、**L182**（learn） | `…/gpu/gpu_runtime/server.py#L178` |
| REF-06 | `gpu/gpu_runtime/real_backend.py` | L20（TARGET_MODULES）、**L686/L753/L770**（weights_only=False 补丁） | `…/gpu/gpu_runtime/real_backend.py#L686` |
| REF-07 | `gpu/gpu_runtime/categorical_search_backend.py` | L39（ONLINE_TARGET）、**L127**（class）、**L273**（value） | `…/gpu/gpu_runtime/categorical_search_backend.py#L127` |
| REF-08 | `gpu/gpu_runtime/qwen35_backend.py` | L89（class）、L287（value）、L330（policy） | `…/gpu/gpu_runtime/qwen35_backend.py#L89` |
| REF-09 | `gpu/gpu_runtime/learner.py` | 学习器实现 | `…/gpu/gpu_runtime/learner.py` |
| REF-10 | `gpu/gpu_runtime/mixed_learner.py` | 混合学习器 | `…/gpu/gpu_runtime/mixed_learner.py` |
| REF-11 | `gpu/gpu_runtime/mixed_objective.py` | KL/CE 目标 | `…/gpu/gpu_runtime/mixed_objective.py` |
| REF-12 | `gpu/gpu_runtime/lean_action_format.py` | Lean 动作格式化 | `…/gpu/gpu_runtime/lean_action_format.py` |

> 完整 URL 前缀 = `https://github.com/wufuju2023-cell/v1-1-agentic-tool/blob/main/`

## B. 代码/证据：`reap-new-update-model-value-head`（默认分支 `value-head-nanoproof`）

本地根：`/mnt/f/projects/reap-new-update-model-value-head`
GitHub 前缀：`https://github.com/wufuju2023-cell/reap-new-update-model-value-head/blob/value-head-nanoproof`
云端根：`/home/admin/workspace/new_value_head/`（runtime 运行时目录）

| REF | 路径 | GitHub URL |
|---|---|---|
| REF-13 | `v1-result/20260828-real7b-pell-success/code/cpu_runtime/target_variants.py` | `…/v1-result/20260828-real7b-pell-success/code/cpu_runtime/target_variants.py` |
| REF-14 | `…/code/cpu_runtime/verified_dataset_store.py` | 同上路径替换文件名 |
| REF-15 | `…/code/cpu_runtime/online_ttt.py` / `run_ttt.py` / `segmented_ttt.py` | 同上 |
| REF-16 | `…/code/experiments/proof-curriculum/budgets.json`（v2 契约） | `…/experiments/proof-curriculum/budgets.json` |
| REF-17 | `…/code/experiments/proof-curriculum/prepare_attempt.py` | 同上 |
| REF-18 | `…/code/experiments/proof-curriculum/runner/course_driver.py` | 同上 |
| REF-19 | `…/code/gpu_runtime/*`（V1 原始 GPU 运行时，33 模块） | `…/code/gpu_runtime/` |

## C. 文档：`reap-new-update-model`（现 PUBLIC）

本地根：`/mnt/f/projects/reap-publicize-work`
| REF | 分支/路径 | GitHub URL |
|---|---|---|
| REF-20 | `master: discussion/new_value_head_in7b_ex1/01_设计说明/01_Value设计与评价方法.md` | `https://github.com/wufuju2023-cell/reap-new-update-model/blob/master/discussion/new_value_head_in7b_ex1/01_设计说明/01_Value设计与评价方法.md` |
| REF-21 | `new-reap-mcts-ttt-public: explain/wiki/by-hand/2026-9-5-plan-original-paper/00-v1-scope-and-source-of-truth.md` | `…/blob/new-reap-mcts-ttt-public/explain/wiki/by-hand/2026-9-5-plan-original-paper/00-v1-scope-and-source-of-truth.md` |
| REF-22 | `…/2026-9-5-plan-original-paper/01-paper-baseline.md` | 同上（换文件名） |
| REF-23 | `…/9-7-agent-alpha-proof/09-bayesian-view.md` | `…/blob/new-reap-mcts-ttt-public/explain/wiki/by-hand/9-7-agent-alpha-proof/09-bayesian-view.md` |
| REF-24 | `…/9-7-agent-alpha-proof/07-does-it-produce-different-nodes.md` | 同上（换文件名） |
| REF-25 | `…/9-7-temperature-distribution-agent-distill/01-temperature-math.md` | `…/blob/new-reap-mcts-ttt-public/explain/wiki/by-hand/9-7-temperature-distribution-agent-distill/01-temperature-math.md` |
| REF-26 | `…/v1-1-9-7-experiment-1/03-E3-E4-E5.md`（E4/E5 实测） | `…/blob/new-reap-mcts-ttt-public/explain/wiki/by-hand/v1-1-9-7-experiment-1/03-E3-E4-E5.md` |
| REF-27 | `…/scaling-plan-1/10-lessons-and-artifacts.md`（7 条经验） | `…/blob/new-reap-mcts-ttt-public/explain/wiki/by-hand/scaling-plan-1/10-lessons-and-artifacts.md` |
| REF-28 | `…/9-8-plan/README.md`（工具调用优先路线） | `…/blob/new-reap-mcts-ttt-public/explain/wiki/by-hand/9-8-plan/README.md` |

> 完整 URL 前缀 = `https://github.com/wufuju2023-cell/reap-new-update-model/blob/new-reap-mcts-ttt-public/explain/wiki/by-hand/`

## D. 本地专属资料（my-new-linux）

本地根：`/home/a/文档/project/`
| REF | 路径 | GitHub |
|---|---|---|
| REF-29 | `2-9-14-Q.md`（Q0–Q4 方案来源） | 未上云（本地 only；如需引用请先入库） |
| REF-30 | `1-QLoRA-zhihu.md`（QLoRA 数学） | 未上云（本地 only） |

## E. 模型/权重（HuggingFace）
| REF | 资源 | URL |
|---|---|---|
| REF-31 | REAL-Prover base | `https://huggingface.co/FrenzyMath/REAL-Prover` |
| REF-32 | Qwen3.8-9B-Distill | `https://huggingface.co/empero-ai/Qwen3.8-9B-Distill` |
| REF-33 | full-v3 artifact（head/adapter） | `https://huggingface.co/WufuJu/v1-1-fullv3-artifact` |
| REF-34 | 私有原始 artifact | `https://huggingface.co/alpha-proof-open-source/alphaproof-full-v3-value-head`（private，需授权） |
