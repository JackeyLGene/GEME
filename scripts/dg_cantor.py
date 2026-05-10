"""
DG via Cantor Gap — PA domain, Wittgenstein coordinate table.

Principle:
  Formula tree → extract all leaf symbols → map to (0,1) coords.
  x(F) = mean( leaf coords ).
  Trajectory: x₀ → re-project → x₁ → re-project → ...
  Gap = empty interval between symbol clusters.
  DG = gap crossings / total steps.
"""
import sys, math
sys.path.insert(0, r'G:\GEME\src')

from gira.phase3.language import eq, fn, var, constant, Term, forall


# ============================================================
# Wittgenstein coordinate table — PA domain
# ============================================================

WT_COORDS = {
    "0": 0.05,
    "1": 0.08,
    "s": 0.15,
    "+": 0.30,
    "x": 0.35,    # mult symbol (ASCII x)
    "\u00d7": 0.35,
    "=": 0.60,
    "forall": 0.75,
    "exists": 0.72,
    "x_var": 0.90,
    "y_var": 0.93,
    "z_var": 0.96,
}


def leaf_symbols(formula):
    """Extract (kind, symbol) from all leaf nodes in formula tree."""
    leaves = []
    def walk(node):
        if node is None:
            return
        if hasattr(node, 'args'):
            for a in node.args:
                walk(a)
        if hasattr(node, 'left') and node.left:
            walk(node.left)
        if hasattr(node, 'right') and node.right:
            walk(node.right)
        # leaf detection: no children
        if hasattr(node, 'args') and node.args:
            return
        if hasattr(node, 'left') and node.left:
            return
        if hasattr(node, 'right') and node.right:
            return
        leaves.append((getattr(node, 'kind', ''), getattr(node, 'symbol', '')))
    walk(formula)
    return leaves


def formula_position(formula):
    """Compute x(F) = mean of all leaf symbol coordinates."""
    leaves = leaf_symbols(formula)
    coords = []
    for kind, sym in leaves:
        if kind == "variable":
            c = WT_COORDS.get(sym + "_var", WT_COORDS.get(sym, 0.90))
        else:
            c = WT_COORDS.get(sym, WT_COORDS.get(kind, 0.50))
        coords.append(c)
    return sum(coords) / len(coords) if coords else 0.50


def logistic_next(x):
    """Chaotic logistic map: x → 4x(1-x). Natural form evolution."""
    return 4.0 * x * (1.0 - x)


def compute_gaps(coords):
    """Identify gap regions between clusters."""
    centers = sorted(set(coords))
    gaps = []
    for i in range(len(centers) - 1):
        width = centers[i + 1] - centers[i]
        if width > 0.03:  # significant gap
            gaps.append((centers[i] + 0.01, centers[i + 1] - 0.01))
    return gaps


def dg_cantor(formula, steps=8):
    """DG: gap crossings in logistic trajectory.

    x0 = formula position from tree leaves
    xi+1 = 4*xi*(1-xi) (logistic map)
    DG = (gap crossings) / steps
    """
    coords = set(WT_COORDS.values())
    gaps = compute_gaps(coords)
    
    trajectory = []
    x = formula_position(formula)
    trajectory.append(x)
    
    for i in range(steps):
        x = logistic_next(x)
        trajectory.append(x)
    
    crossings = 0
    for i in range(len(trajectory) - 1):
        a, b = trajectory[i], trajectory[i + 1]
        for gap_low, gap_high in gaps:
            if min(a, b) <= gap_low and max(a, b) >= gap_high:
                crossings += 1
                break
    
    dg = min(1.0, crossings / max(steps, 1))
    return dg, trajectory, gaps


# ============================================================
# Test
# ============================================================
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
    
    print("=== DG via Cantor Gap ===")
    print("clusters: %s" % [round(c, 2) for c in sorted(set(WT_COORDS.values()))])
    print("gaps:     %s" % [(round(l, 2), round(h, 2)) for l, h in compute_gaps(set(WT_COORDS.values()))])
    print()
    for label, F in formulas:
        dg, traj, _ = dg_cantor(F, steps=8)
        t = " -> ".join("%.3f" % v for v in traj[:5])
        t += "..." if len(traj) > 5 else ""
        print("  %-14s  x0=%.3f  DG=%.3f   traj: %s" % (label, traj[0], dg, t))
