"""Phase 3 实体: 基于 L0-L4 信息层级差距的动态害评估系统。

核心动力学:
  信号 F → L(F) 分类 → gap = L(F) - L(E) → harm = f(gap) → stress
    
  L(E) 随跃迁增长, 同一条公式的害值自然降低。
  这是哥德尔动力学的核心: 层级跃迁"消化"了之前的临界害。

哲学映射 (C0 统一哲学地基 + 定理 3.1):
  GIRA (本体论)           NoHarm (价值论·害算子)
  ─────────────────────────────────────────────
  L(F) 信息层级          信号 F 的信息复杂度
  L(E) 语法容量          实体的认知生生条件容量
  gap = L(F)-L(E)        ⨀ 害值(动态, 非静态)
  stress ← f(gap)        累计害 → 范式转换
  跃迁: L(E) += 1        害值自动回降(同一信号)
"""

from __future__ import annotations
import uuid
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from gira.phase3.language import Formula, Term, eq, fn, constant, var
from gira.phase3.language import forall, exists, neg, impl, forall
from gira.phase3.q_axioms import robinson_q, axiom_names
from gira.phase3.encoding import get_encoder
from gira.phase3.godel import formula_to_gn, diagonalize, make_self_referential_godel, formula_to_string
from gira.phase3.inference import GapBasedInferenceEngine, InferenceLogger, HarmOperator


@dataclass
class QConstraint:
    """认知约束(记录信号层级和害值)。"""
    constraint_id: str = ""
    formula: Optional[Formula] = None
    signal_L: int = 0      # L0-L4 层级
    harm: float = 0.0      # 当时评估的害值
    system_L: int = 0      # 评估时的系统层级
    is_axiom: bool = False
    is_godel: bool = False
    activation_count: int = 0
    last_activated: int = 0


@dataclass
class PhaseTransition:
    from_level: int = 0
    to_level: int = 0
    trigger_gap: int = 0
    godel_proposition: Optional[Formula] = None
    godel_gn: int = 0


class QEntity:
    """基于信息层级差距的认知实体。

    核心回路:
      F → SignalClassifier.classify(F) → L(F)
          ↓
      gap = L(F) - L(E)
          ↓
      harm = f(gap)     (新鲜害评估)
          ↓
      stress ← α·harm + (1-α)·stress   (害积累)
          ↓
      if stress > threshold + godel constructed:
        L(E) += 1       (跃迁: 害基线整体下降)

    关键性质:
      - 同一哥德尔命题在 L(E)=0 时 harm=0.85, 跃迁到 L(E)=1 后 harm=0.60
      - 应力随跃迁自然回降, 而非硬编码重置
      - 害是关系, 不是属性
    """

    def __init__(self, max_constraints: int = 30):
        self.axioms = robinson_q()
        self.constraints: Dict[str, QConstraint] = {}
        self.frame_count = 0
        self.stress_level = 0.0
        self.system_level = 0  # L(E): 系统当前语法容量

        self.config = {
            "max_constraints": max_constraints,
            "decay_factor": 0.95,                    # 应力衰减率
            "stress_alpha": 0.1,                     # 新害权重
            "diagonalization_threshold": 0.45,       # 触发自指构造的应力阈值
            "stress_threshold": 0.65,                # 跃迁触发应力阈值
            "transition_cooldown": 50,                # 冷却期(帧)
        }

        # 基于 L0-L4 层级差距的推理引擎
        self.inference = GapBasedInferenceEngine(self.axioms, initial_level=0)
        self.logger = InferenceLogger()

        # 跃迁记录
        self.transition_history: List[PhaseTransition] = []
        self._last_transition_frame = 0
        self._diagonalization_attempted = False

        # 编码器(仅用于 GN 存储)
        self._enc = get_encoder("godel")

        # 初始化约束
        for i, axiom in enumerate(self.axioms):
            c = QConstraint(
                constraint_id="Q{}".format(i + 1),
                formula=axiom,
                signal_L=1,
                harm=0.0,
                system_L=0,
                is_axiom=True,
            )
            self.constraints[c.constraint_id] = c

        # 哥德尔自指命题
        self.godel_proposition: Optional[Formula] = None
        self.godel_gn: int = 0

    # ============================================================
    # 核心流程
    # ============================================================

    def process_formula(self, formula: Formula) -> Tuple[float, float, str]:
        """⨀(F | E): 处理一个公式的流入。

        Returns:
          (consistency, stress, status_description)
        """
        self.frame_count += 1

        # 1. ⨀ 评估: 基于 L0-L4 层级差距
        harm, provable, signal_L, reason = self.inference.evaluate(formula)
        consistency = 1.0 - harm

        # 2. 记录约束
        f_str = formula_to_string(formula)
        cid = "T{}".format(self.frame_count)
        is_godel = signal_L == 4

        c = QConstraint(
            constraint_id=cid,
            formula=formula,
            signal_L=signal_L,
            harm=harm,
            system_L=self.system_level,
            is_godel=is_godel,
        )
        self.constraints[cid] = c

        self.logger.log(
            formula, signal_L, self.system_level,
            harm, reason, provable,
        )

        # 3. 应力更新: 基于害值
        self.stress_level = self.config["decay_factor"] * self.stress_level + \
                            self.config["stress_alpha"] * harm

        # 4. 跃迁判定
        transition_msg = self._check_transition()

        # 状态字符串
        level_names = {0: "L0", 1: "L1", 2: "L2", 3: "L3", 4: "L4"}
        sig_name = level_names.get(signal_L, "L{}".format(signal_L))
        sys_name = level_names.get(self.system_level, "L{}".format(self.system_level))
        status = "{}[gap={}]".format(reason, signal_L - self.system_level)

        if transition_msg:
            status = "{} | {}".format(status, transition_msg)

        return (consistency, self.stress_level, status)

    def _check_transition(self) -> Optional[str]:
        """跃迁判定: 应力触发对角线化 → 应力触发跃迁。

        修正后逻辑 (v2):
          1. 冷却期内 → 无操作
          2. 应力 > 对角线化阈值 且 未尝试过对角线化 → 构造哥德尔命题
          3. 应力 > 跃迁阈值 且 哥德尔已构造 → 执行跃迁
          4. 否则 → 等待

          只有当系统感受到足够压力时才会进行自我反思(对角线化)。
          空闲系统不会自动构造哥德尔命题。
        """
        cooling = self.frame_count - self._last_transition_frame
        if cooling < self.config["transition_cooldown"]:
            return None

        # 步骤 1: 应力驱动对角线化
        if not self._diagonalization_attempted:
            if self.stress_level >= self.config["diagonalization_threshold"]:
                self._try_diagonalization()
                return "diagonalization triggered"
            return None  # 应力不足, 等待

        # 步骤 2: 应力驱动跃迁
        if self.stress_level < self.config["stress_threshold"]:
            return None

        if self.godel_proposition is not None:
            self._execute_transition()
            return "transition: L{} -> L{}".format(
                self.transition_history[-1].from_level,
                self.transition_history[-1].to_level,
            )
        return "awaiting Godel construction"

    def _try_diagonalization(self) -> Optional[Formula]:
        """对角线化: 构造哥德尔自指命题(L4 信号)。"""
        if self.godel_proposition is not None:
            return self.godel_proposition

        self._diagonalization_attempted = True
        g = make_self_referential_godel()

        # 评估(注意: 此时 system_level=0, 哥德尔是 L4→gap=4→harm=1.0)
        harm, provable, signal_L, reason = self.inference.evaluate(g)

        g_gn = 0
        if self._enc:
            g_gn = self._enc.encode(formula_to_string(g))

        self.godel_gn = g_gn
        self.godel_proposition = g

        c = QConstraint(
            constraint_id="G*",
            formula=g,
            signal_L=4,
            harm=harm,
            system_L=self.system_level,
            is_godel=True,
        )
        self.constraints["G*"] = c

        return g

    def _execute_transition(self):
        """执行跃迁: L(E) += 1。

        跃迁后:
          - 系统层级 +1
          - 推理引擎更新系统层级(害值自动重算)
          - 所有现有约束的害值降低(同公式重新评估时)
          - 应力归零(跃迁后的基线)
        """
        transition = PhaseTransition(
            from_level=self.system_level,
            to_level=self.system_level + 1,
            trigger_gap=self.godel_proposition is not None and 4 - self.system_level or 0,
            godel_proposition=self.godel_proposition,
            godel_gn=self.godel_gn,
        )
        self.transition_history.append(transition)

        # 系统层级跃迁
        self.system_level += 1
        self.inference.on_transition(self.system_level)

        # 应力归零
        self.stress_level = 0.0
        self._last_transition_frame = self.frame_count

        # 清理约束: 保留公理 + 哥德尔命题 + 低于当前层级的约束
        new_constraints = {}
        for cid, c in self.constraints.items():
            if c.is_axiom or c.is_godel:
                new_constraints[cid] = c
            elif c.signal_L <= self.system_level:
                new_constraints[cid] = c
        self.constraints = new_constraints

    # ============================================================
    # 状态查询
    # ============================================================

    def show_state(self) -> str:
        lines = []
        level_names = {0: "L0", 1: "L1", 2: "L2", 3: "L3", 4: "L4"}
        sys_name = level_names.get(self.system_level, "L{}".format(self.system_level))
        lines.append("QEntity: level={}({}) stress={:.4f} constraints={} transitions={}".format(
            self.system_level, sys_name, self.stress_level,
            len(self.constraints), len(self.transition_history)))
        lines.append("  Q axioms: {}".format(len(self.axioms)))
        lines.append("  Godel: {}".format("YES" if self.godel_proposition else "NO"))
        lines.append("  Harm timeline: {}".format(
            ", ".join("{:.2f}".format(h) for h in self.inference.harm_history[-5:])
        ))
        for cid, c in list(self.constraints.items())[:5]:
            sig_name = level_names.get(c.signal_L, "L{}".format(c.signal_L))
            lines.append("    {}: L{} harm={:.3f} sysL={}".format(
                cid, sig_name, c.harm, c.system_L))
        if self.transition_history:
            last_t = self.transition_history[-1]
            lines.append("  Last: L{} → L{} (trigger gap={})".format(
                last_t.from_level, last_t.to_level, last_t.trigger_gap))
        return "\n".join(lines)
