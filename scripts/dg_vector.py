"""
DG — vector trajectory via formula self-structure.
No pre-assigned symbol coordinates.
The formula IS the vector.
"""
import sys, math
sys.path.insert(0, r'G:\GEME\src')

from gira.phase3.language import eq, fn, var, constant, Term, forall


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
                var_count[0] += 1
                leaves[0] += 1
            elif node.kind == "constant":
                const_count[0] += 1
                leaves[0] += 1
            elif node.kind == "numeral":
                const_count[0] += 1
                leaves[0] += 1
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
    return (
        leaves[0] / n,        # leaf ratio
        depth[0] / n,         # depth per node
        var_count[0] / n,     # variable ratio
        const_count[0] / n,   # constant ratio
        func_count[0] / n,    # function ratio
        quant_count[0] / n,   # quantifier ratio
    )


def vector_distance(v1, v2):
    """Euclidean distance between two vectors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


def dg_vector(formula, steps=3):
    """DG: gap crossings in vector trajectory.
    
    Gap = distance between consecutive vectors in trajectory.
    """
    trajectory = []
    current = formula
    v0 = formula_vector(current)
    trajectory.append(v0)
    
    for i in range(steps):
        try:
            g = current.gn()
            # diagonalize
            current = sub(current, "x", "#%d" % g)
        except:
            pass
        v = formula_vector(current)
        trajectory.append(v)
    
    # Each step's jump size
    jump_sizes = []
    for i in range(len(trajectory) - 1):
        d = vector_distance(trajectory[i], trajectory[i + 1])
        jump_sizes.append(d)
    
    if not jump_sizes:
        return 0.0, trajectory, jump_sizes
    
    # Cantor Gap = max jump in this trajectory
    max_jump = max(jump_sizes) if max(jump_sizes) > 0 else 1.0
    
    # Gap crossings: jumps that exceed 80% of max
    crossings = sum(1 for d in jump_sizes if d >= max_jump * 0.8)
    dg = crossings / len(jump_sizes)
    
    return dg, trajectory, jump_sizes


if __name__ == "__main__":
    from gira.phase3.godel import sub
    
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
    
    print("=== DG — Vector Trajectory ===")
    for label, F in formulas:
        v0 = formula_vector(F)
        dg_value, traj, jumps = dg_vector(F, steps=2)
        print("  %-14s v0=(leaf=%.2f depth=%.2f var=%.2f const=%.2f func=%.2f quant=%.2f)"
              % (label, v0[0], v0[1], v0[2], v0[3], v0[4], v0[5]))
        print("           DG=%.3f jumps=%s" % (dg_value, ["%.3f" % j for j in jumps]))
        print()
