# 01 — 语料清单（仓库 + 数据集 + 获取方式）

## 1. 形式化仓库（直接挖定理）

| 仓库 | 领域 | 规模/星标 | 许可 | 备注 |
|---|---|---|---|---|
| `leanprover-community/mathlib4` | 全领域（1–12） | 288,081 定理 + 136,946 定义（2026-09 官方统计） | Apache-2.0 | **主力**；F 盘已有 v4.28.0 克隆 |
| `ImperialCollegeLondon/FLT` | 数论/表示论/代数几何 | 39.5MB，1026★ | Apache-2.0 | 模形式、椭圆曲线；代数味最浓的独立项目 |
| `AlexKontorovich/PrimeNumberTheoremAnd` | 数论 | 8.8MB，343★ | Apache-2.0 | 解析数论 |
| `teorth/pfr` | 加性组合/代数 | 5.6MB，234★ | Apache-2.0 | PFR 猜想 |
| `leanprover-community/lean-liquid` | 凝聚数学/同调 | 7.4MB，252★ | **无许可** | 仅本地研究，禁止再分发 |
| `leanprover-community/sphere-eversion` | 拓扑/几何 | 10.9MB，49★ | Apache-2.0 | 偏几何 |
| `leanprover-community/con-nf` | 集合论 | 19.2MB，87★ | Apache-2.0 | 邻域外 |
| `YaelDillies/cam-combi` | 组合 | 1MB，88★ | Apache-2.0 | 可用变体源 |
| `leanprover-community/physlib` | 李代数/表示论 | 15.7MB，741★ | Apache-2.0 | HepLean+PhysLean 合并 |
| `Verified-zkEVM/ArkLib` | 有限域/多项式/编码 | 72MB，336★ | 查仓库 | 代数应用型 |
| `Verified-zkEVM/VCVio` | 密码学代数 | 53MB，147★ | 查仓库 | 可选 |
| `CBirkbeck/LeanModularForms` | 模形式 | 13.8MB | Apache-2.0 | 与 FLT 互补 |
| `MichaelStollBayreuth/EllipticCurves` | 椭圆曲线 | <1MB | 查仓库 | 小而专 |
| `dagurtomas/LeanCondensed` | 凝聚数学 | 863KB | 查仓库 | lean-liquid 的 Lean 4 后继 |
| `dwrensha/compfiles` | 竞赛数学 | 6MB，255★ | 查仓库 | 含代数/数论题 |
| `leanprover-community/lean-perfectoid-spaces` | 代数几何 | 12.3MB，134★ | Apache-2.0 | **Lean 3 时代**，仅参考语料 |

## 2. HF 数据集（现成题 / 轨迹 / 树，不必重造）

### 2.1 题面 + 证明（SFT / 冷启动）
| 数据集 | 内容 | 规模 | 备注 |
|---|---|---|---|
| `internlm/Lean-Workbook` | 57,231 + 82,893（Plus）条 NL 题面 + Lean 形式化 + 证明 | ~14 万行 | 竞赛风格，做 NL 改写素材 |
| `internlm/Lean-Github` | 100+ 仓库编译出的定理数据 | 数万级 | 与本题「仓库定理 → 题」同思路 |
| `Goedel-LM/Lean-workbook-proofs` | 29.7K 条 LeanWorkbook 求解证明 | 29.7K | 补齐 Workbook 的证明 |
| `kfdong/STP_Lean` | mathlib 抽取 + 自博弈 + 合成猜想 | 100 万+ 行 | 体量最大，需过滤 |
| `ScalableMath/Lean-STaR` / `Lean-CoT` | Lean-STaR / CoT 训练集 | 10 万级 | 过程监督格式 |

### 2.2 证明树 / 步骤级轨迹（L2 主力）
| 数据集 | 内容 | 规模 | 许可 |
|---|---|---|---|
| `ufal/leantree`（工具 `Kripner/leantree`） | **factorized proof trees**（state→tactic→state） | ~26 万 transitions | CC-BY-4.0 |
| `l3lab/ntp-mathlib`（miniCTX） | mathlib tactic 级 proof state 指令数据 | 10 万–100 万行 | 查数据集页 |
| `harrywsanders/mathlib_extracted` | LeanDojo extractor on Mathlib 4.18 | 10 万+ | 查数据集页 |
| `cat-searcher/leandojo-benchmark-4-*` | LeanDojo Benchmark 4 各切分 | 10 万–100 万行 | 查数据集页 |
| `JohnYang88/lean-dojo-mathlib4` | LeanDojo mathlib4 数据 | 10 万–100 万行 | 查数据集页 |
| `EleutherAI/proof-pile-2` | `lean_proofsteps` + `github-lean` 分片 | 119GB 总量 | 混合，需逐项核 |

### 2.3 翻译 / 反向 autoformalization 素材（R4）
| 数据集 | 内容 | 规模 |
|---|---|---|
| `SJTULean/LeanStatement_SFT` | NL → Lean4 陈述翻译 | 100 万–1000 万行 |
| `SJTULean/LeanStatement_RL` | 翻译 + 质量标签 | 100 万–1000 万行 |
| `SJTULean/LeanStatement_CoT` | 带 CoT 的翻译 | ~14.2 万行 |

### 2.4 评测基准（**泄漏黑名单**，禁止进训练集）
`internlm/…` 之外的：`cat-searcher/minif2f-lean4`、`proofnet-lean4`（v2/v3）、
`PutnamBench-lean4`、`google-deepmind/formal-conjectures`（猜想陈述，可作 open 题）、
`loganrjmurphy/LeanEuclid`。

## 3. 获取方式（全部在远程执行，含断点续传）

```bash
# 仓库（浅克隆到 my-new-linux；F 盘镜像备份用 rsync --partial）
git clone --depth 1 --branch v4.28.0 https://github.com/leanprover-community/mathlib4
git clone --depth 1 https://github.com/ImperialCollegeLondon/FLT
# …其余仓库按 02 的 repos.tsv 批量执行

# HF 数据集（hf-mirror + 断点续传）
export HF_ENDPOINT=https://hf-mirror.com
huggingface-cli download ufal/leantree --repo-type dataset --resume-download
huggingface-cli download l3lab/ntp-mathlib --repo-type dataset --resume-download
# 其余同理；下载清单见 tools/hf_datasets.tsv（P1 交付）
```

## 4. 优先级

1. **复用**：E 盘 mathlib 构建（v4.33.0-rc2，含 importGraph）——仅参考/兜底
2. **首选源**：F 盘 `mathlib4` v4.28.0（与项目基线一致）→ 同步/克隆到 my-new-linux
3. **外部仓库**：按 FLT → PFR → PrimeNumberTheoremAnd → physlib → 其余顺序
4. **HF 数据集**：LeanTree、ntp-mathlib 先行（L2 树直接可用），Workbook/STP 次之
