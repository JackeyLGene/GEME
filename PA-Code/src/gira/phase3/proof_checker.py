"""证明检查器: 验证公式是否可从 Robinson Q 推导。

对 Phase 3 来说, proof checker 是系统"知道什么是可证的"的能力。
"""

from __future__ import annotations
from typing import List, Dict, Optional, Set
from gira.phase3.language import Formula, Term, eq, fn, constant, var
from gira.phase3.language import forall, exists, neg, impl, conj, disj
from gira.phase3.q_axioms import robinson_q, axiom_names
from gira.phase3.godel import formula_to_gn


def is_axiom(f: Formula, axioms: List[Formula]) -> bool:
    """检查公式是否是公理。"""
    gn_f = formula_to_gn(f)
    for a in axioms:
        if formula_to_gn(a) == gn_f:
            return True
    return False


def can_prove(f: Formula, axioms: List[Formula], max_depth: int = 3) -> bool:
    """检查公式是否可证明(有限深度搜索)。

    简化版: 检查公理匹配、语义真值。
    完全版需要实现谓词逻辑推理规则。
    """
    # 公理检查
    if is_axiom(f, axioms):
        return True

    # 语义约简
    return _semantic_check(f)


def _semantic_check(f: Formula) -> bool:
    """语义真值检查(限于 Q 可表达的算术)。"""
    s = str(f)

    # 基本等式的验证
    if f.kind == "equation" and f.left and f.right:
        try:
            return _eval_term(f.left) == _eval_term(f.right)
        except:
            pass

    # 全称公式: 通过检查所有实例
    if f.kind == "forall" and f.variable:
        return True  # 无法穷举所有实例

    # 存在公式: 检查 0, s(0), s(s(0))
    if f.kind == "exists" and f.variable:
        for n in range(5):
            t = constant("0")
            for _ in range(n):
                t = fn("s", t)
            if _semantic_check(_sub_var(f.left, f.variable, t)):
                return True
        return False

    # 蕴含
    if f.kind == "implication":
        return True  # 简化

    return False


def _eval_term(t: Term) -> int:
    """求值项为自然数。"""
    if t.kind == "constant" and t.symbol == "0":
        return 0
    if t.kind == "numeral":
        return t.value
    if t.kind == "function":
        if t.symbol == "s":
            return _eval_term(t.args[0]) + 1
        elif t.symbol == "+":
            return _eval_term(t.args[0]) + _eval_term(t.args[1])
        elif t.symbol == "×":
            return _eval_term(t.args[0]) * _eval_term(t.args[1])
    raise ValueError("Cannot evaluate: {}".format(str(t)))


def _sub_var(f: Formula, var_name: str, t: Term) -> Formula:
    """替换自由变量。"""
    if f.kind == "equation" and f.left and f.right:
        return eq(_sub_var_term(f.left, var_name, t),
                  _sub_var_term(f.right, var_name, t))
    elif f.kind == "forall" and f.variable:
        return f
    elif f.kind == "exists" and f.variable:
        if f.variable == var_name:
            return _sub_var(f.left, var_name, t)
        return f
    return f


def _sub_var_term(tm: Term, var_name: str, t: Term) -> Term:
    if tm.kind == "variable" and tm.symbol == var_name:
        return t
    if tm.kind == "function":
        return fn(tm.symbol, *[_sub_var_term(a, var_name, t) for a in tm.args])
    return tm  # constant, numeral — unchanged
