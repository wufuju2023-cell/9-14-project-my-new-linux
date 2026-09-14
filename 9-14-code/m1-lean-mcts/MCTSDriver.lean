/-
M1 — Lean MCTS 驱动骨架（Lean 4.28 兼容）

定位：接口级实现。真实树逻辑复用 cpulean/Reap/Tactic/TreeSearch.lean：
  - L333 PUCT 探索项 U
  - L375 selectChild
  - L176/L185 节点边界
φ 重加权复用 cpulean/Reap/Agentic.lean L72-74/L85-86。

本文件独立可编译（不依赖上游 olean），用于：
  1) 工具状态机 + φ 钩子的结构定义；
  2) 与 M2/M4 的接口契约（stub）。
-/
import Lean.Data.Json

namespace M1

/-- 证据（与 shared/schemas.py Evidence 同构） -/
structure Evidence where
  id : String
  kind : String
  weight : Float
  payload : String

/-- φ = tanh(Σw)（与 Agentic.lean L72-74 同式） -/
def phi (evs : Array Evidence) : Float :=
  Float.tanh (evs.foldl (fun acc e => acc + e.weight) 0.0)

/-- 工具调用请求（JSONL 契约见 9-14-plan/01 I2） -/
structure ToolCall where
  reqId : String
  kind : String          -- lean_search / lean_compile / file_read / script_run
  argsJson : String
  deriving Inhabited

/-- 节点状态（精简）：E 为工具证据累积，Δ 为完成标记 -/
structure NodeState where
  statePp : String       -- pretty-printed Lean state
  evidence : Array Evidence := #[]
  done : Bool := false
  deriving Inhabited

/-- M1 的外部依赖接口（由 M4/M2 实现；本骨架假定已提供） -/
structure Runtime where
  /-- GPU policy+value：返回 (candidates, value) -/
  gpuForward : NodeState → IO (Array (String × Float) × Float)
  /-- 工具执行：确定性 -/
  execTool : NodeState → ToolCall → IO NodeState
  /-- 是否应触发工具链（启发式；由 M2 提供） -/
  shouldCallTool : NodeState → IO Bool
  /-- 工具策略：选下一个工具（确定性） -/
  toolPolicy : NodeState → IO ToolCall

/-- Q3 方案1：工具确定性链，原地更新，不建树节点 -/
partial def toolChain (rt : Runtime) (s : NodeState) : IO NodeState := do
  if ← rt.shouldCallTool s then
    let τ ← rt.toolPolicy s
    let s' ← rt.execTool s τ
    toolChain rt s'
  else
    pure s

/-- 一次模拟的骨架（选择/扩展/评估/回传的真实实现复用上游 TreeSearch） -/
def simulateOnce (rt : Runtime) (root : NodeState) : IO (NodeState × Float) := do
  let s ← toolChain rt root
  let (cands, v) ← rt.gpuForward s
  -- φ 钩子：prior 重加权 π' ∝ π·φ（真实接入点=上游 selectChild 前）
  let φ := phi s.evidence
  let weighted := cands.map (fun (a, p) => (a, p * φ))
  let _ := weighted
  return (s, v)

end M1
