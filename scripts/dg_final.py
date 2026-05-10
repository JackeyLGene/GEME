"""DG = collision probability with Godel number.

  v  = formula_vector(F)
  v' = formula_vector(diag(F))
  DG = 1 / (1 + d(v, v'))
"""
import sys, math
sys.path.insert(0, r'G:\GEME\src')

from gira.phase3.language import eq, fn, var, constant, Term, forall
from gira.phase3.godel import sub


def formula_vector(formula):
    """v(F): structural components from formula tree itself."""
    nodes = [0]
    leaves = [0]
    depth = [0]
    var_count = [0]
    const_count = [0]
    func_count = [0]
    quant_count = [0]
    
    def walk(node, d):
        if node is None:
            return
        nodes[0] += 1
        depth[0] = max(depth[0], d)
        if hasattr(node, 'kind'):
            if node.kind == "variable":
                var_count[0] += 1; leaves[0] += 1
            elif node.kind in ("constant", "numeral"):
                const_count[0] += 1; leaves[0] += 1
            elif node.kind == "function":
                func_count[0] += 1
            elif node.kind in ("forall", "exists"):
                quant_count[0] += 1
        if hasattr(node, 'args'):
            for a in node.args:
                walk(a, d + 1)
        if hasattr(node, 'left') and node.left:
            walk(node.left, d + 1)
        if hasattr(node, 'right') and node.right:
            walk(node.right, d + 1)
    
    walk(formula, 0)
    n = max(nodes[0], 1)
    return (leaves[0]/n, depth[0]/n, var_count[0]/n,
            const_count[0]/n, func_count[0]/n, quant_count[0]/n)


def vec_dist(v1, v2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


def dg(formula):
    """DG(F) = 1 / (1 + d(v, v')) — collision probability."""
    v = formula_vector(formula)
    
    # diag proxy: vector after one diagonalization
    try:
        g = formula.gn()
        diag_f = sub(formula, "x", "#%d" % g)
        vp = formula_vector(diag_f)
    except:
        vp = v  # no diagonalization possible → no change
    
    d = vec_dist(v, vp)
    return 1.0 / (1.0 + d), v, vp, d


if __name__ == "__main__":
    x, y = var("x"), var("y")
    z0, z1 = constant("0"), constant("1")
    
    formulas = [
        ("1=1",      eq(z1, z1)),
        ("1+1=2",    eq(fn("+", z1, z1), fn("s", fn("s", z0)))),
        ("x=1",      eq(x, z1)),
        ("x+0=x",    eq(fn("+", x, z0), x)),
        ("x+y=y+x",  eq(fn("+", x, y), fn("+", y, x))),
        ("forall swap", forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))),
    ]
    
    print("=== DG = 1/(1+d(v,v')) ===")
    for label, F in formulas:
        dgv, v, vp, dist = dg(F)
        print("  %-14s  v=(leaf=%.2f var=%.2f const=%.2f func=%.2f quant=%.2f)"
              % (label, v[0], v[2], v[3], v[4], v[5]))
        print("           v'=(leaf=%.2f var=%.2f const=%.2f func=%.2f quant=%.2f)"
              % (vp[0], vp[2], vp[3], vp[4], vp[5]))
        print("           d=%.3f  DG=%.4f" % (dist, dgv))
        print()
