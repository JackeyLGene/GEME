"""一阶逻辑语言 (First-Order Logic Language).

严格符号定义:
  - 常量: 0 (唯一数字)
  - 函数: s(后继), +(加法), ×(乘法)
  - 变量: x, y, z (带撇号的变量扩展: x', x'', ...)
  - 逻辑: ¬(非), ∧(且), ∨(或), →(蕴含), ↔(等价)
  - 量词: ∀(全称), ∃(存在)
  - 括号: (, )
  - 等号: =

语法规则:
  Term := 0 | s(Term) | Term + Term | Term × Term | Variable
  Formula := Term = Term | ¬Formula | Formula ∧ Formula | Formula ∨ Formula
           | Formula → Formula | ∀Variable Formula | ∃Variable Formula
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum


class Sort(Enum):
    CONSTANT = "constant"
    VARIABLE = "variable"
    FUNCTION = "function"
    PREDICATE = "predicate"
    CONNECTIVE = "connective"
    QUANTIFIER = "quantifier"


# 符号 → (sort, arity, display)
SYMBOLS: Dict[str, Tuple[Sort, int, str]] = {
    '0': (Sort.CONSTANT, 0, '0'),
    's': (Sort.FUNCTION, 1, 's'),
    '+': (Sort.FUNCTION, 2, '+'),
    '×': (Sort.FUNCTION, 2, '×'),
    '=': (Sort.PREDICATE, 2, '='),
    '¬': (Sort.CONNECTIVE, 1, '¬'),
    '∧': (Sort.CONNECTIVE, 2, '∧'),
    '∨': (Sort.CONNECTIVE, 2, '∨'),
    '→': (Sort.CONNECTIVE, 2, '→'),
    '∀': (Sort.QUANTIFIER, 1, '∀'),
    '∃': (Sort.QUANTIFIER, 1, '∃'),
    '(': (Sort.CONNECTIVE, 0, '('),
    ')': (Sort.CONNECTIVE, 0, ')'),
    ',': (Sort.CONNECTIVE, 0, ','),
    'x': (Sort.VARIABLE, 0, 'x'),
    'y': (Sort.VARIABLE, 0, 'y'),
    'z': (Sort.VARIABLE, 0, 'z'),
    # 数词符号（符号化数词用）
    '#': (Sort.CONNECTIVE, 0, '#'),
    '1': (Sort.CONNECTIVE, 0, '1'),
    '2': (Sort.CONNECTIVE, 0, '2'),
    '3': (Sort.CONNECTIVE, 0, '3'),
    '4': (Sort.CONNECTIVE, 0, '4'),
    '5': (Sort.CONNECTIVE, 0, '5'),
    '6': (Sort.CONNECTIVE, 0, '6'),
    '7': (Sort.CONNECTIVE, 0, '7'),
    '8': (Sort.CONNECTIVE, 0, '8'),
    '9': (Sort.CONNECTIVE, 0, '9'),
}

# 用于哥德尔编号的质数映射
# 符号化数词格式: #<decimal_digits> (如 #123)
SYMBOL_GN: Dict[str, int] = {
    '0': 2, 's': 3, '+': 5, '×': 7,
    '=': 11, '¬': 13, '∧': 17, '∨': 19, '→': 23,
    '∀': 29, '∃': 31,
    '(': 37, ')': 41, ',': 43,
    'x': 47, 'y': 53, 'z': 59,
    # 数词符号
    '#': 61, '1': 67, '2': 71, '3': 73, '4': 79,
    '5': 83, '6': 89, '7': 97, '8': 101, '9': 103,
    # 修正: 点号(∀x.∃y...)和空格(binary op分隔)被静默丢弃的bug
    '.': 107, ' ': 109,
}
GN_SYMBOL = {v: k for k, v in SYMBOL_GN.items()}

# 位置质数(最多100个, 超出时动态生成)
_POS_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
               53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107,
               109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167,
               173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
               233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283,
               293, 307, 311, 313, 317, 331, 337, 347, 349, 353, 359,
               367, 373, 379, 383, 389, 397, 401, 409, 419, 421, 431,
               433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491,
               499, 503, 509, 521, 523, 541]


def _pos_prime(i: int) -> int:
    """获取第 i 个位置质数, 超出缓存时动态扩展。"""
    global _POS_PRIMES
    if i < len(_POS_PRIMES):
        return _POS_PRIMES[i]
    p = _POS_PRIMES[-1] + 2
    while len(_POS_PRIMES) <= i:
        while True:
            is_prime = True
            for q in _POS_PRIMES:
                if q * q > p:
                    break
                if p % q == 0:
                    is_prime = False
                    break
            if is_prime:
                _POS_PRIMES.append(p)
                break
            p += 2
        p += 2
    return _POS_PRIMES[i]


# ============================================================
# 公式与项的树结构
# ============================================================

@dataclass
class Term:
    """一阶项: 常量、变量、函数应用、符号化数词。"""
    kind: str  # "constant" | "variable" | "function" | "numeral"
    symbol: str = ""
    args: List[Term] = field(default_factory=list)
    value: int = 0  # 用于 numeral: 存储数值

    def __str__(self) -> str:
        if self.kind == "constant":
            return self.symbol
        if self.kind == "variable":
            return self.symbol
        if self.kind == "function":
            if len(self.args) == 1:
                return "{}({})".format(self.symbol, str(self.args[0]))
            return "({} {} {})".format(str(self.args[0]), self.symbol, str(self.args[1]))
        if self.kind == "numeral":
            # 符号化数词: #<十进制数值>
            return "#{}".format(self.value)
        return "?"

    def gn(self) -> int:
        """项的哥德尔数。"""
        if self.kind in ("constant", "variable"):
            return SYMBOL_GN.get(self.symbol, 0)
        if self.kind == "function":
            n = SYMBOL_GN.get(self.symbol, 0)
            for i, arg in enumerate(self.args):
                n *= _pos_prime(i) ** arg.gn()
            return n
        if self.kind == "numeral":
            # 符号化数词 #n 的 GN: 直接计算自 compact 字符串
            s = "#{}".format(self.value)
            n = 1
            for i, ch in enumerate(s):
                code = SYMBOL_GN.get(ch, 0)
                if code == 0:
                    continue
                n *= _pos_prime(i) ** code
            return n
        return 0


def var(name: str = "x") -> Term:
    return Term("variable", name)

def constant(name: str = "0") -> Term:
    return Term("constant", name)

def fn(symbol: str, *args: Term) -> Term:
    return Term("function", symbol, list(args))


# ============================================================
# 一阶公式
# ============================================================

@dataclass
class Formula:
    """一阶公式。"""
    kind: str  # "equation" | "negation" | "conjunction" | "disjunction" | "implication" | "forall" | "exists"
    left: Optional[Union[Term, Formula]] = None
    right: Optional[Union[Term, Formula]] = None
    variable: Optional[str] = None

    def __str__(self) -> str:
        if self.kind == "equation":
            return "{} = {}".format(str(self.left), str(self.right))
        elif self.kind == "negation":
            return "(¬{})".format(str(self.left))
        elif self.kind == "conjunction":
            return "({} ∧ {})".format(str(self.left), str(self.right))
        elif self.kind == "disjunction":
            return "({} ∨ {})".format(str(self.left), str(self.right))
        elif self.kind == "implication":
            return "({} → {})".format(str(self.left), str(self.right))
        elif self.kind == "forall":
            return "∀{}.{}".format(self.variable, str(self.left))
        elif self.kind == "exists":
            return "∃{}.{}".format(self.variable, str(self.left))
        return "?"

    def gn(self) -> int:
        """公式的哥德尔数(通过位置质数编码)。"""
        s = str(self)
        n = 1
        for i, ch in enumerate(s):
            code = SYMBOL_GN.get(ch, 0)
            if code == 0:
                continue
            n *= _pos_prime(i) ** code
        return n


# ============================================================
# 快捷创建公式
# ============================================================

def eq(t1: Term, t2: Term) -> Formula:
    return Formula("equation", left=t1, right=t2)

def neg(f: Formula) -> Formula:
    return Formula("negation", left=f)

def conj(f1: Formula, f2: Formula) -> Formula:
    return Formula("conjunction", left=f1, right=f2)

def disj(f1: Formula, f2: Formula) -> Formula:
    return Formula("disjunction", left=f1, right=f2)

def impl(f1: Formula, f2: Formula) -> Formula:
    return Formula("implication", left=f1, right=f2)

def forall(var_name: str, f: Formula) -> Formula:
    return Formula("forall", left=f, variable=var_name)

def exists(var_name: str, f: Formula) -> Formula:
    return Formula("exists", left=f, variable=var_name)
