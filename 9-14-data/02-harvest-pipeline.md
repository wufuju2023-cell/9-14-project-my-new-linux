# 02 — 抽取管线（环境、导出器、分类、断点续传）

> 执行位置：`my-new-linux`（CPU 抽取/编译）。本机不跑任何 build。
> 数据根：`/home/a/data/9-14-data/`（278G 可用）；文档根：本目录。

## 1. 环境搭建（my-new-linux，一次性，P0）

```bash
# 1) elan（Lean 版本管理器）
curl -sSf https://elan.lean-lang.org/elan-init.sh | sh -s -- -y
source "$HOME/.profile"

# 2) 语料仓库（v4.28.0 与项目基线一致）
mkdir -p /home/a/data/9-14-data/repos
cd /home/a/data/9-14-data/repos
git clone --depth 1 --branch v4.28.0 https://github.com/leanprover-community/mathlib4

# 3) mathlib olean 缓存（避免本机式源码全量编译）
cd mathlib4
lake exe cache get        # 下载 ~5–10GB，wget -c 语义、可重跑
lake env lean --version   # 冒烟：应为 v4.28.0
```

备选：若网络到 GitHub/HF 不稳，用 F 盘已有克隆（`/mnt/f/projects/lean-corpus/mathlib4`）
经 `rsync --partial --append-verify` 同步到远程（省一次 clone）。

## 2. 导出器 A（首选：自写 Lean 程序）

目标：把 mathlib 环境里的声明导出为分片 JSONL。

```text
tools/Extract.lean（lake exe 或 lake env lean 运行）：
  import Mathlib
  遍历 env.constants（含 meta 侧）：
    只保留 thmInfo / defnInfo / inductInfo / ctorInfo
    输出：name, kind, module, isTheorem,
          type_pp（ppExpr，含类型签名与量词）
          value_pp（thmInfo 的证明项 pp，可截断）
          declRange?（源文件行号，用 DeclarationRange 接口）
  → 每 20k 行一个分片：exported/mathlib/<module>.jsonl.zst
```

- 编译与运行在 `my-new-linux`；运行时长按模块切片，**每批 < 1 小时**。
- 若 `ppExpr` 不稳，退回 `Lean.PrettyPrinter` 默认宽度 100，
  另存 `type_raw`（Expr 序列化）供程序化比对。

## 3. 导出器 B（成熟替代）

- **LeanDojo v2**（`lean-dojo/LeanDojo`、`lean-interact`）：直接给
  traced tactic / premises / 声明数据，省自写；缺点是版本绑定需核对。
- **importGraph**（E 盘 mathlib 的 packages 里已有）：产出声明级依赖 DAG，
  直接作为 L1 proof tree（见 `04-proof-trees.md`）。
- **lean4export / `lean --export`**：内核项级导出（L3），仅对难题子集使用。

## 4. 领域分类（路径前缀映射，导出后离线执行）

```text
Mathlib/Algebra/                    → algebra（Algeba/Homology 除外）
Mathlib/Algebra/Homology/           → homological-algebra
Mathlib/Homology/                   → homological-algebra
Mathlib/LinearAlgebra/              → linear-algebra
Mathlib/GroupTheory/                → group-theory
Mathlib/RingTheory/                 → ring-theory
Mathlib/FieldTheory/                → field-theory
Mathlib/NumberTheory/               → number-theory
Mathlib/RepresentationTheory/       → representation-theory
Mathlib/CategoryTheory/             → category-theory
Mathlib/CategoryTheory/Bicategory|Monoidal|Enriched/ → higher-category（同时保留在 category-theory 计数）
Mathlib/AlgebraicTopology/          → algebraic-topology
Mathlib/AlgebraicGeometry/          → algebraic-geometry
其它仓库 → 按仓库级白名单映射（FLT → number-theory/representation-theory）
```

规则实现为 `tools/classify.py`（表驱动，输出 `domain_counts.json`），
P0 用它产出**每个领域的真实原始定理数**，据此冻结 `00` 配额表。

## 5. 断点续传与幂等（全局规则落地）

```text
state/
  batches.tsv            # 批次总清单：id, repo, module, 状态
  batch_<id>.done        # 完成标记（空文件，touch 原子写）
logs/<batch>.log
exported/<repo>/<module>.jsonl.zst   # 产物：先写 .tmp 再 mv 原子替换
```

- 每批开始前检查 `.done`：存在即跳过；
- 批内命令幂等（重复执行结果一致）；
- 失败重试 ≤ 3 次，仍失败记 `state/batch_<id>.failed` 并继续后续批次；
- 全部完成后核对：`.done` 数量 == 批次总数，否则继续差额批次。

## 6. P0 验收

- [ ] `lake env lean --version` = v4.28.0（远程）
- [ ] `mathlib4` 全量导出完毕（分片完整、行数 > 30 万）
- [ ] `domain_counts.json` 产出，12 领域计数表回填 `00`
- [ ] importGraph DAG 产出（`deps/importgraph.jsonl`）
