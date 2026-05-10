"""Robinson Arithmetic Q — 7 条核心公理。

Q1: ∀x ¬(sx = 0)          — 零不是后继
Q2: ∀x ∀y (sx = sy → x = y) — 后继是单射
Q3: ∀x (x = 0 ∨ ∃y (x = sy)) — 每个数=0或某数的后继
Q4: ∀x (x + 0 = x)          — 加法零元
Q5: ∀x ∀y (x + sy = s(x + y)) — 加法递归
Q6: ∀x (x × 0 = 0)          — 乘法零元
Q7: ∀x ∀y (x × sy = (x × y) + x) — 乘法递归
"""

from gira.phase3.language import *
from typing import List


def robinson_q() -> List[Formula]:
    """返回 Robinson Q 的 7 条公理。"""
    x, y, z = var("x"), var("y"), var("z")

    Q1 = forall("x", neg(eq(fn("s", x), constant("0"))))

    Q2 = forall("x", forall("y",
        impl(eq(fn("s", x), fn("s", y)), eq(x, y))))

    Q3 = forall("x",
        disj(eq(x, constant("0")),
             exists("y", eq(x, fn("s", var("y"))))))

    Q4 = forall("x", eq(fn("+", x, constant("0")), x))

    Q5 = forall("x", forall("y",
        eq(fn("+", x, fn("s", y)), fn("s", fn("+", x, y)))))

    Q6 = forall("x", eq(fn("×", x, constant("0")), constant("0")))

    Q7 = forall("x", forall("y",
        eq(fn("×", x, fn("s", y)),
           fn("+", fn("×", x, y), x))))

    return [Q1, Q2, Q3, Q4, Q5, Q6, Q7]


def axiom_names() -> List[str]:
    return ["Q1: ∀x ¬(sx=0)", "Q2: ∀x∀y(sx=sy→x=y)",
            "Q3: ∀x(x=0∨∃y(x=sy))", "Q4: ∀x(x+0=x)",
            "Q5: ∀x∀y(x+sy=s(x+y))", "Q6: ∀x(x×0=0)",
            "Q7: ∀x∀y(x×sy=(x×y)+x)"]
