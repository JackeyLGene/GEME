"""
GEME V6 — Comprehensive experiment suite.
S4 singularity, Q dependency, memory dynamics.
"""
import sys, random
sys.path.insert(0, r'G:\GEME\src')

from gira.phase6.geme_v6 import GEME
from gira.phase3.language import eq, fn, var, constant, forall, Term
from gira.phase3.q_axioms import robinson_q

def NUM(n):
    t = constant("0")
    for _ in range(n): t = fn("s", t)
    return t
x, y = var("x"), var("y")
T_ADD = forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))
T_MUL = forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x))))
T_ZERO = forall("x", eq(fn("+", x, constant("0")), x))
T_ONE = forall("x", eq(fn("\u00d7", x, constant("1")), x))

def gen_S0(n, seed=42):
    random.seed(seed)
    r = []
    for _ in range(n):
        a, b = random.randint(1, 9), random.randint(1, 9)
        op = random.choice(["+", "\u00d7"])
        r.append((eq(fn(op, NUM(a), NUM(b)), NUM(a + b if op == "+" else a * b)), "S0"))
    return r

def gen_S1(n, seed=43):
    random.seed(seed)
    r = []
    for _ in range(n):
        a, b = random.randint(1, 6), random.randint(0, 3)
        r.append((eq(fn("+", NUM(a), NUM(b)), NUM(a + b)), "S1"))
    return r

def gen_S2(n, op="+", seed=None):
    if seed is not None: random.seed(seed)
    """Concrete swap instances: a op b = b op a"""
    random.seed(seed)
    r = []
    for _ in range(n):
        a, b = random.randint(1, 5), random.randint(1, 5)
        r.append((eq(fn(op, NUM(a), NUM(b)), fn(op, NUM(b), NUM(a))), "S2"))
    return r

def gen_S4(formula, label):
    gn = formula.gn()
    s = Term("function", "sub", [Term("numeral", value=gn), Term("numeral", value=17), Term("numeral", value=gn)])
    return (eq(s, s), label)

def run_experiment(label, axioms, s4_sigs, s0_cnt=10, s1_cnt=5, s2_cnt=5, s2_op="+", mem_cap=10, rounds=20):
    e = GEME(axioms=axioms, memory_cap=mem_cap, merge_thresh=0.15)
    pre = {"add_comm": e.evaluate(T_ADD), "mul_comm": e.evaluate(T_MUL)}
    data = gen_S0(s0_cnt) + gen_S1(s1_cnt) + gen_S2(s2_cnt, s2_op) + s4_sigs
    random.Random(42).shuffle(data)
    for rnd in range(rounds):
        for form, _ in data:
            r = e.process(form)
    post = {"add_comm": e.evaluate(T_ADD), "mul_comm": e.evaluate(T_MUL)}
    # Emergence = pattern frame weight >= axiom baseline at end state
    add_em, add_ratio = e.emergence_score("equation_add_swap")
    mul_em, mul_ratio = e.emergence_score("equation_mul_swap")
    return {
        "label": label,
        "ax": len(axioms),
        "L_E": e.system_level,
        "mem_rules": e.memory.rule_count,
        "add_comm": (pre["add_comm"], post["add_comm"], add_em, add_ratio),
        "mul_comm": (pre["mul_comm"], post["mul_comm"], mul_em, mul_ratio),
        "classes": [r.name() if hasattr(r, 'name') else type(r).__name__
                   for r in e.entity.inference.harm_operator.classifier._rules[6:]],
    }

def print_result(r):
    emoji = lambda em: "EMERGED" if em else "-"
    print(f"  L(E)={r['L_E']}  ax={r['ax']}  mem_rules={r['mem_rules']}  class_rules={len(r['classes'])}")
    print(f"    add_comm:  S{r['add_comm'][0]} -> S{r['add_comm'][1]}  {emoji(r['add_comm'][2])}  (w/base={r['add_comm'][3]:.2f})")
    print(f"    mul_comm:  S{r['mul_comm'][0]} -> S{r['mul_comm'][1]}  {emoji(r['mul_comm'][2])}  (w/base={r['mul_comm'][3]:.2f})")

def run_all():
    q_full = robinson_q()
    q_no7 = [a for i, a in enumerate(q_full) if i != 6]
    q_core = q_full[3:7]  # Q4-Q7
    q_core_no7 = q_core[:3]  # Q4-Q6

    s4_3 = [gen_S4(T_ADD, "S4:add"), gen_S4(T_MUL, "S4:mul"), gen_S4(T_ZERO, "S4:zero")]

    exps = [
        # A: Baseline
        ("A01: Q1-Q7 + S2(add)", q_full, s4_3, 3, "+"),
        ("A02: Q1-Q7 NO S4 + S2(add)", q_full, [], 3, "+"),
        # B: No concrete S2
        ("B01: Q1-Q6 + S4 NO S2", q_no7, s4_3, 0, "+"),
        ("B02: Q1-Q7 NO S4 NO S2", q_full, [], 0, "+"),
        # C: S4 substitutes for concrete S2
        ("C01: Q1-Q6 + S4", q_no7, s4_3, 3, "+"),
        ("C02: Q4-Q6 + S4", q_core_no7, s4_3, 3, "+"),
        # D: Q dependency
        ("D01: Q1-Q7 no axioms", [], [gen_S4(T_ADD, "S4")], 3, "+"),
        # E: Mul swap
        ("E01: Q1-Q7 + S2(mul)", q_full, s4_3, 3, "\u00d7"),
        ("E02: Q1-Q6 + S2(mul)", q_no7, s4_3, 3, "\u00d7"),
    ]

    print("=" * 65)
    print("  GEME V6 — Final Experiment Matrix")
    print("=" * 65)
    print(f"\n{'#':4} {'Experiment':35} {'L(E)':6} {'rules':6} {'add_comm':20} {'mul_comm':20}")
    print("  " + "-" * 92)

    results = []
    for label, axioms, s4_list, s2_cnt, s2_op in exps:
        r = run_experiment(label, axioms, s4_list, s2_cnt=s2_cnt, s2_op=s2_op)
        results.append(r)
        ac = f"S{r['add_comm'][0]}->S{r['add_comm'][1]} " + ("E" if r['add_comm'][2] else "-")
        mc = f"S{r['mul_comm'][0]}->S{r['mul_comm'][1]} " + ("E" if r['mul_comm'][2] else "-")
        print(f"  {len(results)}.  {label:30} {r['L_E']:6} {r['mem_rules']:6} {ac:20} {mc:20}")

    print("\n" + "=" * 65)
    print("  SUMMARY")
    print("=" * 65)
    # S4 singularity: compare A02 vs C01
    a02 = next(r for r in results if "A02" in r['label'])
    c01 = next(r for r in results if "C01" in r['label'])
    print(f"\n  S4 Singularity:")
    print(f"    NO S4 + S2:   add={a02['add_comm'][2]} mul={a02['mul_comm'][2]}")
    print(f"    S4 + Q1-Q6:   add={c01['add_comm'][2]} mul={c01['mul_comm'][2]}")

    print(f"\n  Q dependency:")
    for r in results:
        if "Q1-Q6" in r['label'] or "Q4-Q6" in r['label']:
            print(f"    {r['label']:35} add={'E' if r['add_comm'][2] else '-'} mul={'E' if r['mul_comm'][2] else '-'}")

    print(f"\n  No Q axioms:")
    for r in results:
        if "no axioms" in r['label']:
            print(f"    {r['label']:35} add={'E' if r['add_comm'][2] else '-'} mul={'E' if r['mul_comm'][2] else '-'}")

    emerged = sum(1 for r in results if r['add_comm'][2])
    print(f"\n  Total add_comm emerged: {emerged}/{len(results)}")
    print("=" * 65)

if __name__ == "__main__":
    run_all()
