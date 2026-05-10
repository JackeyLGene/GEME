"""S4 signal constructor for GEME."""

import sys, io
sys.path.insert(0, r'G:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from gira.phase3.language import eq, fn, Term


class S4Signal:
    """S4 signal with human-readable semantic annotation."""
    def __init__(self, formula, s4_term):
        self.source_formula = formula
        self.s4_term = s4_term
        self.gn = formula.gn()
    
    def human_readable(self) -> str:
        return (f"S4: GN({self.source_formula}) = GN({self.source_formula})\n"
                f"     → (#{str(self.gn)[:20]}...) = (#{str(self.gn)[:20]}...)")
    
    def __str__(self):
        return str(self.s4_term)


class S4Constructor:
    """Build S4 signals from any formula.
    
    S4 = GN(formula) = GN(formula)
    The formula references its own Godel encoding.
    """
    
    @staticmethod
    def self_equation(formula) -> S4Signal:
        gn = formula.gn()
        gn_term = Term("numeral", value=gn)
        s4_term = eq(gn_term, gn_term)
        return S4Signal(formula, s4_term)


if __name__ == "__main__":
    from gira.phase3.language import forall, var, eq, fn, constant
    x, y = var("x"), var("y")
    swap = forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))
    x0 = eq(fn("+", x, constant("0")), x)

    s4_swap = S4Constructor.self_equation(swap)
    s4_x0 = S4Constructor.self_equation(x0)

    print("S4 signal for swap formula:")
    print(f"  formula:  {swap}")
    print(f"  GN:       {swap.gn()}")
    print(f"  S4:       {s4_swap}")
    print(f"  S4 kind:  {s4_swap.left.kind if hasattr(s4_swap.left,'kind') else '?'} value={s4_swap.left.value if hasattr(s4_swap.left,'value') else '?'}")
    print()
    print("S4 signal for x+0=x:")
    print(f"  formula:  {x0}")
    print(f"  GN:       {x0.gn()}")
    print(f"  S4:       {s4_x0}")
    print(f"  S4 kind:  {s4_x0.left.kind if hasattr(s4_x0.left,'kind') else '?'} value={s4_x0.left.value if hasattr(s4_x0.left,'value') else '?'}")

