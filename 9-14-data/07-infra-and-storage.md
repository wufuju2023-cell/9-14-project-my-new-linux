# 07 — 机器分工、存储与运维

## 1. 机器矩阵

| 机器 | 规格 | 角色 | 约束 |
|---|---|---|---|
| 本机（zhai WSL） | F 盘 1.7T 可用；E 盘 104G 可用 | 文档、协调、轻量 I/O、少量网络下载 | **不跑重型任务** |
| `a@my-new-linux` | Ryzen 7 5700X（16T）/ 60GB / /home 278G，无 GPU | Lean 编译、抽取、验证、批处理、CPU 服务 | 不训练 |
| AMD MI300X 云 | 192GB HBM | M4 推理、M5/M6 训练、GPU 批量补证 | /work 随实例销毁，产物归档 ModelScope |

## 2. 存储布局

```text
# my-new-linux（主工作区）
/home/a/data/9-14-data/
  repos/        # 语料仓库克隆（mathlib4 v4.28.0、FLT、…）
  exported/     # 02 导出器产物（分片 jsonl.zst）
  generated/    # 03 生成器产物
  verified/     # 05 验证后的题（入库唯一出口）
  trees/L1|L2|L3/
  rejected/     # 被拒题面与原因
  state/        # 批次清单与 .done/.failed 标记
  reports/      # 计数、平衡、许可、训练报告
  logs/

# 本机
/mnt/f/projects/lean-corpus/        # 已有 mathlib4 v4.28.0 克隆
/mnt/f/9-14-data-mirror/            # （建议）verified/ 与 trees/ 的 rsync 镜像
/mnt/e/projects/lean/               # 已有 mathlib v4.33（只读参考）

# 云端
/work/9-14-data/                    # 训练时挂载/同步 verified + trees
```

## 3. 断点续传与幂等（强制）

- 批次开始前检查 `state/batch_<id>.done`，存在即跳过；
- 产物一律「临时文件 + `mv` 原子替换」；禁用半截文件入库；
- 下载：`wget -c` / `curl -C -` / `hf --resume-download` / `rsync --partial --append-verify`；
- 验证批并发 ≤ 12 进程（16 线程留余量），内存峰值 < 40GB；
- 每批结束写 `reports/verify_<batch>.json`，用于断点定位。

## 4. 备份与 E 盘策略（历史教训）

- E 盘曾多次自发掉线（2026-09-13 21:19 再次 DROP）；
- E 盘定位为**只读资料库**：mathlib v4.33 构建与 importGraph 仅作参考；
- 所有 P2 产物在 my-new-linux 生成后 **双备份**：F 盘镜像 + 云实例工作区（训练前同步）；
- 备份脚本 `tools/backup_to_f.sh`（P1 交付，rsync + 校验和清单）。

## 5. 成本与耗时估计（数量级）

| 项 | 估计 |
|---|---|
| mathlib v4.28.0 克隆 + olean 缓存 | ~10GB 下载 + 解压（1–2h，网络受限） |
| 全量导出（32 万+ 声明 → jsonl） | 数小时（16 线程） |
| 生成 240K 题（R1–R4） | 数天（含 agent 生成） |
| 验证 240K 题（Lean 编译） | 约 240K × 3s / 12 并 ≈ 17 小时（理想） |
| L2 树收集（下载为主） | 数小时 |
| 磁盘峰值 | ~150GB（仓库 + 全产物 + 树） |
| 云训练 | 按 M5/M6 预算另计 |

## 6. 监控与日志

- 每批：`reports/<phase>_<batch>.json` + `logs/<batch>.log`（含耗时、内存峰值）；
- 日终：汇总 `reports/daily_YYYYMMDD.md`（完成批次数、通过率、异常）；
- 异常（OOM、编译崩溃、下载失败）计入 `state/*.failed`，不中断全局流水。
