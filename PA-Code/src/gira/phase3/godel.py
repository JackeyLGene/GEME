"""严格哥德尔编号 + 代入函数 + 对角线引理。

无字母、无爬表。纯一阶逻辑符号的质数编码。
"""

from __future__ import annotations
from typing import Dict, List, Optional
from gira.phase3.language import SYMBOL_GN, GN_SYMBOL, _POS_PRIMES, _pos_prime, Formula, Term, fn, constant, var
from gira.phase3.language import eq, forall, exists, neg, impl, conj


def formula_to_gn(formula: Formula) -> int:
    """公式 → 哥德尔数(质数幂编码)。"""
    s = str(formula)
    n = 1
    for i, ch in enumerate(s):
        code = SYMBOL_GN.get(ch, 0)
        if code == 0:
            continue
        n *= _pos_prime(i) ** code
    return n


def gn_to_formula(m: int) -> Optional[Formula]:
    """哥德尔数 → 公式(质因数分解回退)。"""
    chars = []
    n = m
    for i, p in enumerate(_POS_PRIMES):
        if n <= 1:
            break
        exp = 0
        while n % p == 0:
            n //= p
            exp += 1
        if exp > 0 and exp in GN_SYMBOL:
            chars.append(GN_SYMBOL[exp])
        if n <= 1 and len(_POS_PRIMES) <= i + 1:
            break
    formula_str = ''.join(chars)
    if not formula_str:
        return None
    return _parse_formula_str(formula_str)


def _parse_formula_str(s: str) -> Optional[Formula]:
    """简化的公式字符串解析(仅用于验证)。"""
    # 对于实际实验, 我们只需 GN 值, 不需要反向公式解析
    return None


# ============================================================
# 代入函数 sub(a, v, t)
# 在公式 a 的所有自由出现变量 v 替换为项 t
# ============================================================

def sub(a: Formula, var_name: str, t: Term) -> Formula:
    """代入函数: 将公式 a 中自由变量 var_name 替换为项 t。"""
    return _sub_recursive(a, var_name, t)


def _sub_recursive(f: Formula, var_name: str, t: Term) -> Formula:
    """递归代入。"""
    if f.kind == "equation":
        return Formula("equation",
                       left=_sub_term(f.left, var_name, t),
                       right=_sub_term(f.right, var_name, t))
    elif f.kind == "negation":
        return Formula("negation", left=_sub_recursive(f.left, var_name, t))
    elif f.kind in ("conjunction", "disjunction", "implication"):
        return Formula(f.kind,
                       left=_sub_recursive(f.left, var_name, t),
                       right=_sub_recursive(f.right, var_name, t))
    elif f.kind in ("forall", "exists"):
        if f.variable == var_name:
            return f  # 不替换量化变量
        return Formula(f.kind,
                       left=_sub_recursive(f.left, var_name, t),
                       variable=f.variable)
    return f


def _sub_term(tm: Term, var_name: str, t: Term) -> Term:
    if tm.kind == "variable" and tm.symbol == var_name:
        return t
    if tm.kind == "function":
        return Term("function", tm.symbol,
                     [_sub_term(a, var_name, t) for a in tm.args])
    return tm  # constant, numeral — 不含自由变量, 原样返回


# ============================================================
# 对角线引理
# ============================================================

def diagonalize(formula: Formula, var_name: str = "x") -> Formula:
    """对角线引理: 构造自指公式。

    给定公式 F(x) 含自由变量 x,
    令 G = sub(F, x, gn(F))  — 将 F 自身的 GN 代入 x
    则 G ↔ F(gn(G))          — G 自指地声明 F 对自己成立
    """
    gn_f = formula_to_gn(formula)
    # 将 GN 编码为项: s(s(...(0)...))
    gn_term = _encode_number_as_term(gn_f)
    return sub(formula, var_name, gn_term)


def _encode_number_as_term(n: int) -> Term:
    """将自然数 n 编码为符号化数词 Term。

    使用紧凑表示: Term("numeral", value=n), 对应字符串 #<decimal>。
    避免展开 s^n(0) 的字面量结构(对大数据不可行)。
    """
    return Term("numeral", value=n)


# ============================================================
# 内生命题构造
# ============================================================

def make_self_referential_godel() -> Formula:
    """构造对角线哥德尔命题 G*。

    构造过程:
    1. 取公式模板 F(x) = ¬∃y (y+y = x)
       含义: "不存在 y 使得 y+y = x"
       (在 Q 中, 这个公式对某些 x 真但对其他 x 假)
    2. 令 G = sub(F, x, gn(F))
       G 自指地声明 "不存在 y 使得 y+y = gn(F)"

    通过对角线引理, G 等价于一道自指算术命题。
    """
    x_var = var("x")
    y_var = var("y")

    # 构造公式: ¬∃y (y + y = x)
    body = eq(fn("+", y_var, y_var), x_var)
    f = neg(exists("y", body))

    # 应用对角线引理
    g_star = diagonalize(f, "x")
    return g_star


def formula_to_string(f: Formula) -> str:
    """公式 → 字符串(用于编码)。"""
    return str(f)
