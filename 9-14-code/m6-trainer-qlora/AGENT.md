# AGENT.md — m6-trainer-qlora

> 引用文件完整路径（本地 + GitHub + 云端）见 `../../9-14-plan/03-references.md`（REF 编号索引）。

## 用途
QLoRA 方案实现与「是否需要 QLoRA」对照研究（预注册判定，见 `ablation.py`）。

## 文件
| 文件 | 说明 |
|---|---|
| `qlora_trainer.py` | `QLoRAConfig` / `check_rocm()` / `build_model()` / `train()` |
| `ablation.py` | `verdict()` 判定 + ROCm 检查入口 |

## 被引用（精确到行）
| 引用对象 | 位置 | 用途 |
|---|---|---|
| NF4 数学 | `1-QLoRA-zhihu.md` 式(3) 段 | 分位数量化 |
| 双重量化/分页 | 同上 §2.2/§2.3 | 显存优化 |
| LoRA 超参基线 | `gpu/gpu_runtime/real_backend.py` L20（`TARGET_MODULES`） | 与现有 rank16/α32 对齐 |
| 头训练数据 | `v1-result/…/cpu_runtime/verified_dataset_store.py` | 精度评估数据源 |

## 依赖
- torch 2.11 / transformers 5.14 / peft 0.19（ROCm）
- **bitsandbytes（ROCm 版）**——硬前提，先跑 `check_rocm()`

## 上云/环境（从零）
```bash
pip install bitsandbytes --index-url <rocm-wheel-index>   # 或系统包
python -m m6_trainer_qlora.ablation     # 打印 check_rocm() 报告
# 若 ok：跑对照（同数据/超参/种子）→ verdict() 输出裁定
```

## 门
- [ ] `check_rocm()` 结论（含版本与设备名）；
- [ ] 四维对照表 + `verdict()` 书面裁定。
