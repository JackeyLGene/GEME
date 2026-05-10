"""推理引擎: 基于 L0-L4 信号层级的动态害评估。

核心原则:
  害值不是公式的固有属性, 而是"信号信息层级"与"系统语法层级"之间的动态差距。
  
  ⨀(F | E) = f(L(F) - L(E))
    其中 L(F) = 信号 F 的信息层级 (L0-L4)
         L(E) = 系统 E 的当前语法容量层级
  
  同一公式对 L0 系统是临界害, 对 L2 系统可能是无害。
  害是关系, 不是属性。

L0-L4 信号层级分类 (继承 Phase 2 C1 v0.5):
  L1: 公理内运算 — 语义可直接求值的无变量算术式
  L2: 公理内推理 — 需要推理链验证的公式
  L3: 元描述 — 在语法内可表达但不可判定的公式
  L4: 哥德尔命题/语法外 — 包含自指数词或不可消解的自指
  L0: 空白令牌 — 预留占位符

C0 哲学映射:
  GIRA (本体论)                NoHarm (价值论)
  ───────────────────────────────────────────
  信号层级 L(F)                F 的信息复杂度
  系统层级 L(E)                实体的认知容量
  层级差距 gap = L(F)-L(E)     ⨀ 害值
  跃迁 L(E+1)                  范式转换 · 害归零
"""

from __future__ import annotations
from typing import List, Dict, Optional, Set, Tuple, Callable
from dataclasses import dataclass, field
import math

from gira.phase3.language import Formula, Term, eq, fn, constant, var
from gira.phase3.language import forall, exists, neg, impl, conj, disj
from gira.phase3.godel import formula_to_string, sub


# ============================================================
# L0-L4 信号层级分类器
# ============================================================

class SignalClassifier:
    """根据系统当前容量对信号进行 L0-L4 层级分类。
    
    分类是动态的——它取决于系统当前语法 Γ 的容量。
    """

    def __init__(self):
        self._rules = _init_inference_rules()

    def classify(self, formula: Formula, axioms: List[Formula],
                 theorems: List[Formula]) -> Tuple[int, str]:
        """⨀(F | Γ): 将信号分类为 L0-L4, 返回 (level, reason)。
        
        L0: 空白令牌 — 公式中不含任何可识别符号
        L1: 公理内运算 — 语义可求值的算术式(无变量) 或 已知公理/定理
        L2: 公理内推理 — 可在有限步内推理验证
        L3: 元描述 — 语法内可表达但不可判定
        L4: 哥德尔/语法外 — 自指或不可消解
        """
        f_str = formula_to_string(formula)

        # L0 检测: 空公式或占位符
        if not f_str or f_str == "?":
            return (0, "L0: empty token")

        # L4 检测: 哥德尔自指命题(包含 # 数词)
        if "#" in f_str:
            return (4, "L4: Godel self-reference")

        # L4 检测: 语法外符号
        from gira.phase3.language import SYMBOL_GN
        for ch in f_str:
            if ch not in SYMBOL_GN:
                return (4, "L4: extra-grammatical")

        # 公理/已知定理直接匹配 → L1 (已知真, 无害)
        all_known = axioms + theorems
        for k in all_known:
            if str(k) == f_str:
                return (1, "L1: known theorem")

        # L1 检测: 无变量算术等式, 可语义求值
        if formula.kind == "equation" and formula.left and formula.right:
            if self._is_ground(formula):
                sem = self._semantic_value(formula)
                if sem is not None:
                    return (1, "L1: axiom-level operation")

        # L2 检测: 可通过推理链证明
        if self._try_prove(formula, axioms, theorems, max_depth=3):
            return (2, "L2: in-grammar derivation")

        # L1(回退): ground 等式已求值为假(仍可判定, 在语法内)
        if formula.kind == "equation" and formula.left and formula.right:
            if self._is_ground(formula):
                sem = self._semantic_value(formula)
                if sem is not None and sem is False:
                    return (1, "L1: provably false via Q axioms")

        # L1(回退): 无变量且无乘法的 Presburger 等式
        if self._is_presburger(formula) and not self._has_free_vars(formula):
            return (1, "L1: Presburger decidable")

        # L3 检测: 语法内可表达但不可判定
        return (3, "L3: in-grammar undecidable")

    def _is_ground(self, formula: Formula) -> bool:
        """检查公式是否不含自由变量(ground)。
        
        通过递归遍历公式树来检测自由变量。
        """
        return len(self._collect_free_vars(formula)) == 0

    def _collect_free_vars(self, f: Formula) -> set:
        """收集公式中的自由变量。"""
        vars_found = set()
        self._walk_vars(f, set(), vars_found)
        return vars_found

    def _walk_vars(self, f, bound: set, found: set):
        """递归遍历公式树收集自由变量。
        
        Formula 节点: kind + left/right (left/right 是 Term)
        Term 节点:    kind + symbol + args[]
        """
        if f is None:
            return
        
        # Term 节点 (用 args 列表 + symbol)
        if hasattr(f, 'args') and not hasattr(f, 'left'):
            if f.kind == "variable" and f.symbol not in bound:
                found.add(f.symbol)
            for arg in f.args:
                self._walk_vars(arg, bound, found)
            return
        
        # Formula 节点:
        # forall/exists: 绑定变量
        if f.kind in ("forall", "exists"):
            new_bound = set(bound)
            if f.variable:
                new_bound.add(f.variable)
            if getattr(f, 'left', None) is not None:
                self._walk_vars(f.left, new_bound, found)
        else:
            if getattr(f, 'left', None) is not None:
                self._walk_vars(f.left, bound, found)
            if getattr(f, 'right', None) is not None:
                self._walk_vars(f.right, bound, found)

    def _normalize_ground(self, term: "Term") -> Optional[tuple]:
        """递归归一化无变量项为 sⁿ(0) 数值。
        
        使用 Q 自身的递归规则规约:
          x + 0 → x
          x + s(y) → s(x + y)  
          x × 0 → 0
          x × s(y) → (x × y) + x
        
        Term 使用 symbol 和 args[], 不是 name/left/right。
        """
        if term is None:
            return None
        
        # 变量 → 非 ground
        if term.kind in ("variable",):
            return None
        
        # 常数: "0" → 0
        if term.kind == "constant":
            if term.symbol == "0":
                return (0, "0")
            return None
        
        # numeral: #n → n
        if term.kind == "numeral":
            return (term.value, str(term.value))
        
        # 函数: s(t), t1 + t2, t1 × t2
        if term.kind == "function" and len(term.args) >= 1:
            sym = term.symbol
            # s(t) → 数值 + 1
            if sym == "s" and len(term.args) == 1:
                inner = self._normalize_ground(term.args[0])
                if inner is not None:
                    return (inner[0] + 1, f"s({inner[1]})")
                return None
            
            # t1 + t2
            if sym == "+" and len(term.args) == 2:
                l = self._normalize_ground(term.args[0])
                r = self._normalize_ground(term.args[1])
                if l is not None and r is not None:
                    return (l[0] + r[0], f"{l[1]}+{r[1]}")
                return None
            
            # t1 × t2
            if sym in ("\u00d7", "x") and len(term.args) == 2:
                l = self._normalize_ground(term.args[0])
                r = self._normalize_ground(term.args[1])
                if l is not None and r is not None:
                    return (l[0] * r[0], f"{l[1]}×{r[1]}")
                return None
        
        return None

    def _semantic_value(self, formula: Formula) -> Optional[bool]:
        """语义求值: 使用 Q 公理递归规约判真伪。
        
        对 ground 公式用 Q 的递归公理归约到 sⁿ(0) 形式, 然后比较。
        这不是外部真值表 — 是公理自身的递归规则执行。
        """
        if not self._is_ground(formula):
            return None
        
        left_norm = self._normalize_ground(formula.left)
        right_norm = self._normalize_ground(formula.right)
        
        if left_norm is not None and right_norm is not None:
            return left_norm[0] == right_norm[0]
        
        return None

    def _is_presburger(self, formula: Formula) -> bool:
        """检查公式是否仅使用 Presburger 算术(加, 无乘)。"""
        s = str(formula)
        if "×" in s or "∀" in s or "∃" in s:
            return False
        return True

    def _has_free_vars(self, formula: Formula) -> bool:
        """检查公式是否有自由变量。"""
        return len(self._collect_free_vars(formula)) > 0

    def _try_prove(self, formula: Formula, axioms: List[Formula],
                   theorems: List[Formula], max_depth: int = 3) -> bool:
        """Try to prove formula via inference rule chain.
        
        Includes the target formula in premises so that rules
        with structural verification (e.g. induction) can check it.
        
        max_depth=3 is sufficient for Robinson Q proof chains over
        the formula classes tested (atomic equations, single-quantifier
        formulae). InductionRule bypasses this depth limit entirely
        via semantic base-case evaluation.
        """
        if max_depth <= 0:
            return False
        premises = axioms + theorems + [formula]
        for rule in self._rules:
            result = rule.apply(premises, axioms)
            # Formula.__str__ is deterministic and structure-preserving;
            # a dedicated structural equality check would be more robust
            # but string comparison suffices for the current term algebra.
            if result is not None and str(result) == str(formula):
                return True
        if max_depth > 1:
            for rule in self._rules:
                result = rule.apply(premises, axioms)
                if result is not None:
                    new_theorems = theorems + [result]
                    if self._try_prove(formula, axioms, new_theorems, max_depth - 1):
                        return True
        return False


# ============================================================
# 推理规则 (与之前相同)
# ============================================================

class InferenceRule:
    """推理规则基类。"""
    def name(self) -> str:
        return self.__class__.__name__
    def apply(self, premises: List[Formula], axioms: List[Formula]) -> Optional[Formula]:
        raise NotImplementedError


class ModusPonens(InferenceRule):
    """MP: {A → B, A} ⊢ B"""
    def apply(self, premises: List[Formula], axioms: List[Formula]) -> Optional[Formula]:
        for i, p1 in enumerate(premises):
            if p1.kind != "implication":
                continue
            for j, p2 in enumerate(premises):
                if i == j:
                    continue
                if str(p2) == str(p1.left):
                    return p1.right
            for a in axioms:
                if str(a) == str(p1.left):
                    return p1.right
        return None


class UniversalInstantiation(InferenceRule):
    """UI: {∀x.F(x)} ⊢ F(t)"""
    def apply(self, premises: List[Formula], axioms: List[Formula]) -> Optional[Formula]:
        for p in premises:
            if p.kind == "forall" and p.variable and p.left:
                for n in range(3):
                    t = constant("0")
                    for _ in range(n):
                        t = fn("s", t)
                    return sub(p.left, p.variable, t)
        return None


class ExistentialGeneralization(InferenceRule):
    """EG: {F(t)} ⊢ ∃x.F(x)"""
    def apply(self, premises: List[Formula], axioms: List[Formula]) -> Optional[Formula]:
        for p in premises:
            if p.kind == "equation":
                for vn in ["x", "y", "z"]:
                    return exists(vn, eq(p.left, p.right))
        return None


class ConjunctionIntroduction(InferenceRule):
    """∧I: {A, B} ⊢ A ∧ B"""
    def apply(self, premises: List[Formula], axioms: List[Formula]) -> Optional[Formula]:
        return conj(premises[0], premises[1]) if len(premises) >= 2 else None


class ConjunctionElimination(InferenceRule):
    """∧E: {A ∧ B} ⊢ A"""
    def apply(self, premises: List[Formula], axioms: List[Formula]) -> Optional[Formula]:
        for p in premises:
            if p.kind == "conjunction":
                return p.left
        return None


class HypotheticalSyllogism(InferenceRule):
    """HS: {A → B, B → C} ⊢ A → C"""
    def apply(self, premises: List[Formula], axioms: List[Formula]) -> Optional[Formula]:
        imps = [p for p in premises if p.kind == "implication"]
        for i, imp1 in enumerate(imps):
            for j, imp2 in enumerate(imps):
                if i != j and str(imp1.right) == str(imp2.left):
                    return impl(imp1.left, imp2.right)
        return None


def _init_inference_rules() -> List[InferenceRule]:
    return [
        ModusPonens(), UniversalInstantiation(),
        ExistentialGeneralization(), ConjunctionIntroduction(),
        ConjunctionElimination(), HypotheticalSyllogism(),
    ]


# ============================================================
# ⨀ 害算子: 基于层级差距的动态害值计算
# ============================================================

class HarmOperator:
    """⨀ 算子 — 基于层级差距的二元害算子。

    核心公式:
      ⨀(F | E) = (L(F) > L(E)) ? 1.0 : 0.0

    L(F) = SignalClassifier.classify(F) → L0..L4
    L(E) = 系统当前语法层级 (0, 1, 2, ...)

    哲学基础:
      系统无法知道自己的绝对层级(哥德尔自指限制)。
      它只知道: "这个信号我是否能处理?"
        - 能 (L(F) ≤ L(E)) → harm = 0
        - 不能 (L(F) > L(E)) → harm = 1

      渐进感来自时间维度:
        多个连续的高层级信号 → 应力在时间上积累
        应力 = f(harm_sequence)  ← 这是动力学, 不是分类学
        害是瞬时的二元判断, 应力是历时的累积度量。

      工程常数:
        harm = 1.0 是量纲匹配常数, 需与应力动力学公式兼容。
        不是分级数值, 不是主观赋值。
    """

    def __init__(self):
        self.classifier = SignalClassifier()
        from gira.phase3.proof_checker import _eval_term as _eval
        self._eval_term = _eval

    def evaluate(self, formula: Formula, axioms: List[Formula],
                 theorems: List[Formula], system_level: int = 0) -> float:
        """⨀(F | E): 二元害判断。

        Returns:
          0.0: 信号在系统容量内 (L(F) ≤ L(E))
          1.0: 信号超出系统容量 (L(F) > L(E))
        """
        signal_level, reason = self.classifier.classify(formula, axioms, theorems)
        effective_signal = signal_level if signal_level > 0 else 4
        return 1.0 if effective_signal > system_level else 0.0

    def classify(self, formula: Formula, axioms: List[Formula],
                 theorems: List[Formula]) -> Tuple[int, str]:
        return self.classifier.classify(formula, axioms, theorems)


# ============================================================
# 基于层级差距的推理引擎
# ============================================================

class GapBasedInferenceEngine:
    """基于信息层级差距的推理引擎。
    
    整体推理过程:
      1. 接收公式 F
      2. 分类为 L0-L4
      3. 计算层级差距: gap = L(F) - L(E)
      4. 计算害值: harm = f(gap)
      5. 更新内部状态 (定理集/矛盾集)
    """

    def __init__(self, axioms: List[Formula], initial_level: int = 0):
        self.axioms = list(axioms)
        self.theorems: List[Formula] = []
        self.contradictions: List[Formula] = []
        self.system_level = initial_level
        self.harm_operator = HarmOperator()
        self.harm_history: List[float] = []
        self.level_history: List[int] = [(initial_level, "initialized")]

        # 公理是系统的基线(level-independent)
        for a in self.axioms:
            self.theorems.append(a)

    def evaluate(self, formula: Formula) -> Tuple[float, bool, int, str]:
        """⨀(F | E): 评估公式, 返回 (harm, provable, signal_L, reason)。
        
        Returns:
          harm:       害值 [0, 1]
          provable:   是否可证明(基于当前系统层级)
          signal_L:   信号的 L0-L4 层级
          reason:     分类理由
        """
        f_str = formula_to_string(formula)

        # 已在定理集中?
        for t in self.theorems:
            if str(t) == f_str:
                return (0.0, True, 1, "L1: known theorem")

        # 已在矛盾集中?(重新评估害值: 系统层级可能已改变)
        for c in self.contradictions:
            if str(c) == f_str:
                # 重新评估: 系统层级可能已跃迁, 公式可能不再有害
                harm_now = self.harm_operator.evaluate(
                    formula, self.axioms, self.theorems, self.system_level
                )
                # 如果害值为 0, 从矛盾集中移除并加入定理集
                if harm_now == 0.0:
                    self.contradictions.remove(c)
                    return (0.0, True, 1, "L1: 跃迁后已消化")
                return (1.0, False, 4, "L4: known contradiction (exceeds capacity)")

        # 分类 + 害评估
        signal_L, reason = self.harm_operator.classify(formula, self.axioms, self.theorems)
        harm = self.harm_operator.evaluate(
            formula, self.axioms, self.theorems, self.system_level
        )

        # 可证明性: 害=0 → 信号在系统容量内
        is_provable = (harm == 0.0)

        # 记录
        self.harm_history.append(harm)
        if is_provable:
            self.theorems.append(formula)
        elif signal_L >= 4:
            self.contradictions.append(formula)

        return (harm, is_provable, signal_L, reason)

    def on_transition(self, new_level: int):
        """系统层级跃迁回调: 更新系统层级, 害值将自动重新计算。"""
        self.system_level = new_level
        self.level_history.append((new_level, "transition"))

    def get_cumulative_harm(self, window: int = 10) -> float:
        if not self.harm_history:
            return 0.0
        recent = self.harm_history[-window:]
        return sum(recent) / len(recent)


# ============================================================
# 推理日志
# ============================================================

@dataclass
class InferenceStep:
    step_id: int
    signal_L: int = 0
    system_L: int = 0
    gap: int = 0
    harm: float = 0.0
    formula_str: str = ""
    classification: str = ""
    success: bool = False


class InferenceLogger:
    def __init__(self):
        self.steps: List[InferenceStep] = []
        self._counter = 0

    def log(self, formula: Formula, signal_L: int, system_L: int,
            harm: float, classification: str, success: bool):
        self._counter += 1
        self.steps.append(InferenceStep(
            step_id=self._counter,
            signal_L=signal_L,
            system_L=system_L,
            gap=signal_L - system_L,
            harm=harm,
            formula_str=str(formula)[:60],
            classification=classification,
            success=success,
        ))

    def last_n(self, n: int = 5) -> List[InferenceStep]:
        return self.steps[-n:]

    def harm_timeline(self) -> List[float]:
        return [s.harm for s in self.steps]
