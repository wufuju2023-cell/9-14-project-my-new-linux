# M6 — 训练器（QLoRA）与 LoRA/QLoRA 对照研究

## 数学（引用 `1-QLoRA-zhihu.md`）
- NF4 分位数量化：$q_i = \frac12(Q_X(\frac{i}{2^k+1}) + Q_X(\frac{i+1}{2^k+1}))$（文章式(3)）；
- 双重量化（对量化常数再量化）；分页优化器（显存压力时借 CPU 内存）；
- 训练形态：**基座 NF4 冻结 + LoRA 适配器 bf16 训练**。

## 研究问题（本模块的核心交付）
**是否需要 QLoRA？** 在 AMD MI300X 192GB 上四维对照：

| 维度 | 指标 | 期望问题 |
|---|---|---|
| 显存 | 峰值 VRAM（训练/推理） | bf16 已 192G 富余 → QLoRA 可能无必要 |
| 速度 | tokens/s（训练） | NF4 反量化开销可能降低吞吐 |
| 精度 | value 距离 MAE / tactic 可用率 | 4-bit 基座对 9B 蒸馏模型的影响未知 |
| 适配性 | ROCm 兼容（bitsandbytes） | ROCm 支持是硬前提 |

## ROCm 兼容性检查（第一优先，先于一切）
```bash
python -c "import bitsandbytes as bnb; print(bnb.__version__)"     # 期望 ROCm 版
python -c "from transformers import BitsAndBytesConfig; print('ok')"
# 若不可用 → 结论直接为"不用 QLoRA"（除非使用 ROCm 分支或 GPTQ/AWQ 替代）
```

## 伪代码（对照实验）

```text
configs = [
  {"name":"lora-bf16",  "quant":None,        "lora":{r:16, α:32}},
  {"name":"qlora-nf4",  "quant":"nf4+dq+pg", "lora":{r:16, α:32}},
]
for cfg in configs:
    model = load(base, quant=cfg.quant)      # 同一 LoRA 超参
    log = train(model, data=D_ttt, steps=S)  # 相同数据/步数/种子
    report(cfg.name, peak_vram, tok_per_s, val_mae, tactic_pass_rate)

verdict = compare(configs)                   # 输出书面裁定
```

## 判定规则（预注册，避免事后解释）
- 若 ROCm 不可用 → 不用 QLoRA；
- 若可用且满足：显存降幅 >40% 且 精度差 <5% 且 速度降幅 <30% → 建议用；
- 否则不用（192GB 下单卡多专家的瓶颈更可能在 KV/并发，而非基座权重）。

## 对多专家部署的影响（与 M4 联动）
- QLoRA 结论为"用"时：同卡专家容量 ×2-3（NF4 基座 ≈5-7GB/模型）；
- 为"不用"时：多专家靠 adapter 热切换（M4 已支持），显存预算见 M4 文档。

## 门
- [ ] ROCm bitsandbytes 可用性结论（含命令输出）；
- [ ] 四维对照数据表（同数据/同超参/同种子）；
- [ ] 书面裁定：用/不用 + 依据。
