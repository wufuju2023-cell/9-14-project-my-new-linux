# AGENT.md — m4-gpu-inference

> 引用文件完整路径（本地 + GitHub + 云端）见 `../../9-14-plan/03-references.md`（REF 编号索引）。

## 用途
GPU 专家池适配层：adapter 热切换（LRU）、多专家共享基座、无 NVLink 多卡按"每卡一进程"扩展。
真实推理/训练委托 `gpu_runtime`（已含 torch2.11 `weights_only=False` 补丁）。

## 文件
| 文件 | 说明 |
|---|---|
| `expert_pool.py` | `ExpertPool`（加载/切换/调用骨架） |

## 被引用（精确到行）
| 引用对象 | 位置 | 用途 |
|---|---|---|
| 服务路由 | `gpu/gpu_runtime/server.py` L178（policy）/L180（value）/L182（learn） | 端点实现 |
| 加载器补丁 | `gpu/gpu_runtime/real_backend.py` L686/L753/L770（`weights_only=False`） | torch2.11 兼容 |
| 分类头后端 | `gpu/gpu_runtime/categorical_search_backend.py` L127（class）/L273（value） | 64-bin 头 |
| Qwen 后端 | `gpu/gpu_runtime/qwen35_backend.py` L89（class）/L287（value）/L330（policy） | Qwen 路线 |
| 协议封装 | `9-14-code/shared/http_contract.py` | 客户端调用 |

## 依赖
- torch 2.11 / transformers 5.14 / peft 0.19（ROCm）；bitsandbytes（仅 M6 实验）；
- 模型：`/work/models/REAL-Prover`、`/work/models/Qwen3.8-9B`；
- artifact：`/work/artifact/backend.full.pt`（sha `c1d025…`）。

## 上云/环境（从零）
```bash
python -m gpu_runtime.server --backend real-search-categorical \
  --model-path /work/models/REAL-Prover \
  --categorical-value-artifact /work/artifact/backend.full.pt \
  --categorical-value-artifact-sha256 c1d0255221cc1b3a6e80e1d5567f6c535ef0a62f1ab300d237aeaa2610e0385d \
  --categorical-value-artifact-role pretrained --gamma 0.999 --host 0.0.0.0 --port 8000
curl -s http://127.0.0.1:8000/health
```
多卡：每卡重复启动（换 --device cuda:N 与端口），M3 维护 endpoint 表。
