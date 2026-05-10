"""GEME V6 — memory economy."""
import sys
sys.path.insert(0, r'G:\GEME\src')

from gira.phase6.geme_v6 import GEME
from gira.phase3.language import eq, fn, var, constant, forall
from gira.phase3.q_axioms import robinson_q


def numeral(n):
    t = constant("0")
    for _ in range(n): t = fn("s", t)
    return t

def swap(a, b, op):
    return eq(fn(op, numeral(a), numeral(b)), fn(op, numeral(b), numeral(a)))


ADD = [(swap(i, j, "+"), "ADD") for i in range(1, 6) for j in range(i+1, 6)]
MUL = [(swap(i, j, "\u00d7"), "MUL") for i in range(1, 5) for j in range(i+1, 5)]
ALL = ADD + MUL

x, y = var("x"), var("y")
T_ADD = forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))
T_MUL = forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x))))


def run():
    e = GEME(axioms=robinson_q(), memory_cap=15, merge_thresh=0.01, stress_threshold=0.6)
    
    s_add = [e.evaluate(T_ADD)]
    s_mul = [e.evaluate(T_MUL)]
    
    print("=" * 65)
    print("  GEME V6 — Memory Economy + Self-Observation")
    print("=" * 65)
    print("  Frm  sig         mem  eff     util  stress accum  L(E)")
    print("  " + "-" * 58)
    
    for rnd in range(6):
        for form, label in ALL:
            r = e.process(form)
            if r["frame"] <= 12 or r["frame"] % 18 == 0:
                print("  %-4d %-12s %-4d %-6.4f %-6.4f %-6.4f %-6.4f %d"
                      % (r["frame"], r["sig"][:12],
                         r["mem"], r["eff"], r["util"],
                         r["stress"], r["accum"], r["L_E"]))
        if e.system_level > 0:
            break
    
    s_add.append(e.evaluate(T_ADD))
    s_mul.append(e.evaluate(T_MUL))
    
    print(f"\n  Universal formulas:")
    for nm, pre, post in [("add-swap", s_add[0], s_add[1]),
                           ("mul-swap", s_mul[0], s_mul[1])]:
        print("  %-14s S%d -> S%d  %s" % (nm, pre, post, "EMERGED" if post < pre else "-"))
    print(f"\n  L(E)={e.system_level}  rules={len(e.extracted_rules)}")
    for r in e.extracted_rules:
        print(f"    {r.name()}")
    print("=" * 65)


if __name__ == "__main__":
    run()
