"""GEME V6 — hard mode: small window + lots of noise + S4 drive."""
import sys, random
sys.path.insert(0, r'G:\GEME\src')

from gira.phase6.geme_v6 import GEME
from gira.phase3.language import eq, fn, var, constant, forall, Term
from gira.phase3.q_axioms import robinson_q


def numeral(n):
    t = constant("0")
    for _ in range(n): t = fn("s", t)
    return t


def gen_S4(formula, label=""):
    gn = formula.gn()
    gn_t = Term("numeral", value=gn)
    code_t = Term("numeral", value=17)
    s = Term("function", "sub", [gn_t, code_t, gn_t])
    return (eq(s, s), f"S4:{label}")


def gen_S0(n):
    data = []
    for i in range(n):
        a = random.randint(0, 9)
        b = random.randint(0, 9)
        op = random.choice(["+", "\u00d7", ""])
        if random.random() < 0.5:
            c = chr(ord('a') + (i % 7))
            t = eq(constant(c), constant(c))
        else:
            t = eq(fn(op, numeral(a), numeral(b)), fn(op, numeral(a), numeral(b)))
        data.append((t, "S0"))
    return data


def gen_S1(n):
    data = []
    for _ in range(n):
        a = random.randint(0, 8)
        b = random.randint(0, 8)
        v = a + b if random.random() < 0.7 else a * b + random.randint(0, 3)
        op = "+" if random.random() < 0.5 else "\u00d7"
        t = eq(fn(op, numeral(a), numeral(b)), numeral(v))
        data.append((t, "S1"))
    return data


def gen_S3(n):
    x, y = var("x"), var("y")
    sources = [
        forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x)))),
        forall("x", eq(fn("+", x, constant("0")), x)),
        forall("x", eq(fn("\u00d7", x, constant("1")), x)),
    ]
    return [(sources[i % len(sources)], "S3") for i in range(n)]


x, y = var("x"), var("y")
T_ADD = forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))
T_MUL = forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x))))


def run():
    e = GEME(axioms=robinson_q(), memory_cap=10, merge_thresh=0.15)
    
    s4_data = [
        gen_S4(T_ADD, "add-swap"),
        gen_S4(T_MUL, "mul-swap"),
        gen_S4(eq(fn("+", x, constant("0")), x), "x+0=x"),
    ]
    
    # Heavy noise, smaller S1/S3
    data = gen_S0(25) + gen_S1(15) + gen_S3(8) + s4_data
    random.Random(42).shuffle(data)
    
    print("=" * 65)
    print("  GEME V6 — HARD MODE")
    print("  Window=8  50% noise  3 S4 self-ref")
    print("=" * 65)
    print(f"  S0: {len(gen_S0(25))} noise")
    print(f"  S1: {len(gen_S1(15))} ground")
    print(f"  S3: {len(gen_S3(8))} quantified")
    print(f"  S4: {len(s4_data)} self-ref")
    print(f"  Total: {len(data)} frames")
    print()
    
    s_add_pre = e.evaluate(T_ADD)
    s_mul_pre = e.evaluate(T_MUL)
    
    print("  Frm cat       mem rules eff    util  stress accum L(E)")
    print("  " + "-" * 60)
    
    for rnd in range(20):
        for form, cat in data:
            r = e.process(form)
            if r["frame"] % 12 == 0 or r["frame"] == 1:
                print("  %-4d %-8s %-4d %-4d %-5.4f %-5.3f %-5.4f %-6.4f %d"
                      % (r["frame"], cat[:8], r["mem"], r.get("rules", 0),
                         r["eff"], r["util"], r["stress"], r["accum"], r["L_E"]))
        if e.system_level > 1:
            break
    
    s_add_post = e.evaluate(T_ADD)
    s_mul_post = e.evaluate(T_MUL)
    
    print(f"\n  UNIVERSALS:")
    for nm, pre, post in [("add-swap", s_add_pre, s_add_post),
                           ("mul-swap", s_mul_pre, s_mul_post)]:
        print(f"    {nm:12}  S{pre} -> S{post} {'EMERGED' if post < pre else '-'}")
    clf_rules = e.entity.inference.harm_operator.classifier._rules
    extra = [r for r in clf_rules[6:]]
    print(f"\n  L(E)={e.system_level}  mem-rules(w>2x)={e.memory.rule_count}  class-rules={len(extra)}")
    for r in extra:
        print(f"    {r.name()}")
    print("=" * 65)


if __name__ == "__main__":
    run()
