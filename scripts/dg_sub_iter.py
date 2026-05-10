"""
DG via Sub iteration — collision probability.

Start: F, compute GN(F)=g0.
Iterate: gi+1 = GN(sub(#gi, 17, #gi)).
DG = number of iterations before convergence |gi+1 - gi| < eps.

Self-referential: converges in 1 step → DG=1.
Ground: never converges (or takes many steps) → DG≈0.
"""
import sys, math
sys.path.insert(0, r'G:\GEME\src')

from gira.phase3.language import eq, fn, var, constant, Term, forall


def make_sub_formula(gn_value, var_code=17):
    """Construct sub(#gn, 17, #gn) = sub(#gn, 17, #gn)."""
    g = Term("numeral", value=gn_value)
    v = Term("numeral", value=var_code)
    s = Term("function", "sub", [g, v, g])
    return eq(s, s)


def dg_iterative(formula, max_steps=5, eps_bits=10):
    """DG = 1 - steps_to_converge/max_steps."""
    v_prev = None
    g_current = formula.gn()
    step = 0
    
    for i in range(max_steps):
        s = make_sub_formula(g_current)
        # Compare GN sizes (bit lengths — proxy for formulas)
        bits_current = g_current.bit_length()
        bits_sub = s.gn().bit_length()
        
        if v_prev is not None and step == 0:
            # Check convergence after first iteration
            if i > 0:
                step = i
        
        g_current = s.gn()
        step += 1
    
    # Convergence = number of steps with similar bit lengths
    # Short formulas: similar bit lengths → fast convergence
    step = min(step, max_steps)
    dg = 1.0 - (step / max_steps)
    return dg, step


def formula_vector(formula):
    nodes = [0]; sub_cnt = [0]
    def walk(n):
        if n is None: return
        nodes[0] += 1
        if hasattr(n, 'kind') and n.kind == "function" and getattr(n,'symbol','')=="sub":
            sub_cnt[0] += 1
        for a in getattr(n, 'args', []): walk(a)
        if getattr(n, 'left', None): walk(n.left)
        if getattr(n, 'right', None): walk(n.right)
    walk(formula)
    n = max(nodes[0], 1)
    return (sub_cnt[0] / n, nodes[0])


if __name__ == "__main__":
    x, y = var("x"), var("y")
    z0, z1 = constant("0"), constant("1")
    
    # Build sub-formula F(x) = sub(x, x, x) = sub(x, x, x)
    sub_xxx = Term("function", "sub", [x, x, x])
    F_of_x = eq(sub_xxx, sub_xxx)
    g0_godel = F_of_x.gn()
    g_num = Term("numeral", value=g0_godel)
    s_g_g = Term("function", "sub", [g_num, g_num, g_num])
    F_godel = eq(s_g_g, s_g_g)
    
    formulas = [
        ("1=1",       eq(z1, z1)),
        ("1+1=2",     eq(fn("+", z1, z1), fn("s", fn("s", z0)))),
        ("x=1",       eq(x, z1)),
        ("x+0=x",     eq(fn("+", x, z0), x)),
        ("x+y=y+x",   eq(fn("+", x, y), fn("+", y, x))),
        ("forall swap", forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))),
        ("Godel F(#g)", F_godel),
    ]
    
    print("=== DG — Sub iteration collision ===")
    for label, F in formulas:
        dgv, steps = dg_iterative(F, max_steps=5)
        v = formula_vector(F)
        print("  %-14s sub-ratio=%.2f nodes=%d steps=%d DG=%.3f"
              % (label, v[0], v[1], steps, dgv))
