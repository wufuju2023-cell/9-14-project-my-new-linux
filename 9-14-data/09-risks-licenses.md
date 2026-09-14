# 09 — 风险、许可与红线

## 1. 许可与合规

| 来源 | 许可 | 处理 |
|---|---|---|
| mathlib4 / FLT / PFR / PrimeNumberTheoremAnd / physlib / cam-combi / con-nf / sphere-eversion | Apache-2.0（多数） | 可直接使用，逐行记录 license |
| `lean-liquid` | **无 license** | 仅本地研究；产物放 `restricted/`，禁止再分发、禁入对外发布 |
| `ufal/leantree` | CC-BY-4.0 | 可用；保留出处署名 |
| LeanDojo / ntp-mathlib | MIT / 参见数据集页 | 使用前核对数据集页 |
| `EleutherAI/proof-pile-2` | 混合（含 The Stack 各语言） | 大规模入库前逐项核验（P2 前置） |
| `SJTULean/*`、`internlm/*` | 以数据集页为准 | 记录版本与页面快照 |
| 其它小仓库 | 逐个查 | 无 license 的按无许可处理 |

红线：不把 `restricted/` 内容混入训练集与任何对外产物；发布数据集前跑一次
`tools/license_audit.py`（P2 交付）。

## 2. 技术风险

| 风险 | 影响 | 对策 |
|---|---|---|
| E 盘 USB 掉线（历史高频） | 资料断供 | E 仅作只读参考；主链 F + my-new-linux + 云；产物双备份 |
| Lean 版本漂移 | 题面编不过 | 全链锁 v4.28.0；每行记 `source_commit`；E 的 v4.33 只做参考 |
| 加强命题（去假设）不可证 | 假题入库 | 编译验证门 + proved 优先；open 题单独归档并标注 |
| agent 变体幻觉 | 污染训练 | Lean 编译是唯一裁判；拒绝原因留档用于提示词迭代 |
| benchmark 污染 | 评测失信 | 双黑名单（哈希 + decl 前缀）；formal-conjectures 全量 holdout |
| 类塌陷（训练） | 模型偏科 | 领域轮转 + 类平衡门（<30%）+ pass@k 多样性门 |
| 验证吞吐瓶颈 | 产线卡住 | P1 标定单题成本；进程池 12 并发；必要时加云 CPU 批验 |
| 本机被重型任务拖垮 | 违反用户裁定 | 所有 build/训练命令禁止在本机执行；本机只允许文档与轻量 I/O |

## 3. 成本风险

- 云训练按 M5/M6 预算独立核算；数据侧主要成本是**验证机时**（约 17h×并发度）与下载流量；
- mathlib olean 缓存 ~10GB、语料产物 ~150GB 峰值——my-new-linux 278G 够用，
  但需在 P2 中旬清理 `exported/` 的中间分片（保留 rejected 原因与最终 verified）。

## 4. 停止条件（回滚/暂停）

- 泄漏检查 > 0：全库重扫，未通过前停止训练；
- 许可不明的来源占比 > 5%：暂停对外产物生成，先做核验；
- 类平衡连续 2 轮 > 30%：暂停生成，重采样后再继续；
- E 盘掉线：不影响主链（本就只读参考），无需人工介入。

## 5. 与全局规则的衔接

- 时间预算：单条同步命令 ≤ 4 分钟；长任务一律走 opencode-kilo 后台管理器；
- 断点续传：`state/*.done`、原子写、幂等、下载 `-c` —— 全管线强制（见 `07` 第 3 节）；
- 文档：本目录所有 md 遵循 md-latex 规则（公式块独立成行，前后空行）。
