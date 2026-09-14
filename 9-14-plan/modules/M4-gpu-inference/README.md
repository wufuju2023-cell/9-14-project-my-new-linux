# M4 — GPU 推理服务（AMD MI300X 192GB）

## 数学
见 `../../00-math-theory.md` §2（64-bin 价值头）。value 语义：

$$
V(s) = -\hat d(s),\qquad \hat d(s)=\sum_{d=1}^{64} d\, p_\phi(d\mid s)
$$

## 服务契约（唯一真源，I1）
沿用已验证的 session 协议（`runtime_transport.py` L4–7）：
- `POST /sessions/{sid}` create；`policy/v1`、`value/v1`、`learn/v1`、`retire/v1`；
- **响应嵌套**：`choices[].message.content`（读取必须嵌套解析）。

## 多专家部署（无 NVLink）
```
单卡（MI300X）：1 进程 = 1 基座 + N adapter（热切换，adapter 以 model 字段选择）
多卡独立：每卡 1 进程（同一服务代码），M3 维护 endpoint 表（HTTP 负载均衡）
```

## 伪代码（服务端）

```text
class ExpertPool:
    def __init__(base_path, adapters: dict[adapter_id, path]):
        self.base = load(base_path)          # bf16 或 NF4（M6 决定）
        self.adapters = {id: load_lora(base, p) for id,p in adapters.items()}
        self.resident = LRU(capacity=cfg.max_resident)

    def forward(self, adapter_id, messages, n, temperature):
        adapter = self.resident.get_or_load(adapter_id)
        with adapter.active():               # 热切换（低开销）
            return generate(messages, n, temperature)

    def value(self, adapter_id, messages):
        h = hidden_last(adapter, messages)   # 4096/3584 维
        return -expected_distance(head[adapter_id], h)   # d̂
```

## 资源预算（MI300X 192GB 实测参考）
- REAL-Prover 7B bf16 ≈ 15GB + KV/激活 ≈ 20-30GB（n=16 短序列）；
- Qwen3.8-9B bf16 ≈ 19GB；同卡 2 基座 + 多 adapter：≤ 80GB（富余）；
- 若 QLoRA 结论为"用"（M6）：基座 NF4 ≈ 5-7GB/模型 → 同卡可挂更多专家。

## 门
- [ ] `/health` + smoke 3 题（value 1.786/1.962/3.216）；
- [ ] adapter 热切换延迟报告（p50/p99）；
- [ ] learn/v1 一次更新回执（版本递增）。
