"""
GEM 6.1 — Controlled Q-Sandbox Experiment.

Mixed training data by category (S-level aligned):
  S1-CALC:  ground arithmetic calculations
  S1-TRUE:  identity instantiations  
  S1-FALSE: provably false statements
  S2-SWAP:  commutation patterns (compression target)
  NOISE:    fragments and random statements

Observations:
  - Does induction emerge from mixed signal?
  - Which categories contribute most to internal stress?
  - Does the system correctly distinguish patterns from noise?
"""

import sys, io
sys.path.insert(0, r'G:\GEME\src')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from gira.phase6.entity import GEME
from gira.phase3.language import var, forall, eq, fn, constant
from gira.phase3.q_axioms import robinson_q
from collections import Counter, defaultdict
import random


x, y = var("x"), var("y")


class DataGenerator:
    """Controlled generation of Q arithmetic training data by S-level category."""
    
    def __init__(self, seed=42):
        random.seed(seed)
        self.generated = []
    
    def numeral(self, n):
        t = constant("0")
        for _ in range(n):
            t = fn("s", t)
        return t
    
    def gen_S0_frag(self):
        a, b = random.randint(0,9), random.randint(0,9)
        op = random.choice(["+", "\u00d7"])
        t = fn(op, self.numeral(a), self.numeral(b))
        self.generated.append((eq(t,t), f"{a}{op}{b}", "S0"))
    
    def gen_S0_char(self, ch="a"):
        self.generated.append((eq(constant(ch), constant(ch)),
                               f"'{ch}'", "S0"))
    
    def gen_S1(self, a, b, op, make_true):
        val = a+b if op=="+" else a*b
        if not make_true:
            val += max(1, random.randint(1,3))
        f = eq(fn(op, self.numeral(a), self.numeral(b)), self.numeral(val))
        lbl = f"{a}{op}{b}={val}"
        self.generated.append((f, lbl, "S1"))
    
    def gen_S2(self, a, b, op, subcat):
        if subcat == "swap":
            f = eq(fn(op, self.numeral(a), self.numeral(b)),
                   fn(op, self.numeral(b), self.numeral(a)))
            lbl = f"{a}{op}{b}={b}{op}{a}"
        elif subcat == "id":
            f = eq(fn(op, self.numeral(a), constant("0")), self.numeral(a))
            lbl = f"{a}{op}0={a}"
        else:
            f = eq(fn(op, self.numeral(a), self.numeral(b)),
                   fn(op, self.numeral(a), self.numeral(b)))
            lbl = f"{a}{op}{b}={a}{op}{b}"
        self.generated.append((f, lbl, "S2"))
    
    def batch(self, config):
        self.generated = []
        for cat, params in config.items():
            count = params[0]
            if cat == "S0":
                for _ in range(count):
                    self.gen_S0_frag() if random.random() < 0.6 else self.gen_S0_char("abc"[random.randint(0,2)])
            elif cat == "S1":
                rng, ops = params[1], params[2]
                for _ in range(count):
                    self.gen_S1(random.randint(rng[0], rng[1]),
                                random.randint(rng[0], rng[1]),
                                random.choice(ops),
                                random.random() < 0.7)
            elif cat == "S2":
                rng, ops = params[1], params[2]
                for _ in range(count):
                    a = random.randint(rng[0], rng[1])
                    b = random.randint(rng[0], rng[1])
                    op = random.choice(ops)
                    sc = random.choice(["swap","swap","swap","id","reflex"])
                    self.gen_S2(a, b, op, sc)
        random.shuffle(self.generated)
        return self.generated


TEST_FORMULAS = {
    "∀x∀y(x+y=y+x)": forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x)))),
    "∀x∀y(x×y=y×x)": forall("x", forall("y", eq(fn("\u00d7", x, y), fn("\u00d7", y, x)))),
}


def run():
    gen = DataGenerator(seed=42)
    
    config = {
        "S0": (10,),
        "S1": (30, (0, 10), ["+", "\u00d7"]),
        "S2": (30, (1, 8), ["+", "\u00d7"]),
    }
    
    data = gen.batch(config)
    
    entity = GEME(axioms=robinson_q(), stress_threshold=0.65)
    
    # Pre-test
    test_pre = {}
    for name, formula in TEST_FORMULAS.items():
        S_pre, _, _ = entity.evaluate(formula)
        test_pre[name] = S_pre
    
    cat_stress = defaultdict(list)
    sep = "=" * 70
    
    print(sep)
    print("  GEM 6.1 — CONTROLLED Q-SANDBOX")
    print("  S0: fragments / non-formulas")
    print("  S1: ground arithmetic")
    print("  S2: identity / structural equivalence")
    print(sep)
    
    cats = Counter(c for _, _, c in data)
    print(f"\n  Dataset: {len(data)} statements")
    for cat in ["S0", "S1", "S2"]:
        print(f"    {cat}: {cats.get(cat,0)}")
    
    print(f"\n{' TRAINING ':=^58}")
    print(f"  {'Frm':<5} {'Stmt':<18} {'S':<3} {'Cat':<4} {'E-str':<7} {'I-str':<7}")
    print(f"  {'-'*45}")
    
    for rnd in range(8):
        for formula, label, cat in data:
            r = entity.process(formula)
            cat_stress[cat].append(r["stress_int"])
            if rnd == 0 and r["frame"] <= 20:
                print(f"  {r['frame']:<5} {label:<18} S{r['S_F']:<2} {cat:<4} {r['stress_ext']:<7.3f} {r['stress_int']:<7.3f}")
        if entity.system_level > 0:
            print(f"  [transition round {rnd+1}]")
            break
    
    print(f"\n{' EMERGENCE ':=^50}")
    for name, formula in TEST_FORMULAS.items():
        S_post, _, _ = entity.evaluate(formula)
        pre = test_pre[name]
        delta = f"S{pre} → S{S_post}"
        emerged = pre >= 3 and S_post < 3
        status = "EMERGED" if emerged else "—"
        print(f"  {name:<35} {delta:<10} {status}")
    
    print(f"\n{' CATEGORY STRESS ':=^40}")
    for cat in sorted(cat_stress.keys()):
        avg_i = sum(cat_stress[cat]) / len(cat_stress[cat])
        print(f"  {cat}: freq={len(cat_stress[cat]):>3}  avg I-str={avg_i:.3f}")
    
    ev = entity.stress_vector()
    print(f"\n{' SUMMARY ':=^40}")
    print(f"  Frames:   {entity.entity.frame_count}")
    print(f"  L(E):     {entity.system_level}")
    print(f"  Stress:   E={ev[0]:.3f}  I={ev[1]:.3f}")
    print(f"  Rules:    {len(entity.extracted_rules)}")
    print(f"  Induction: {'YES' if len(entity.extracted_rules) > 0 else 'NO'}")
    for r in entity.extracted_rules:
        print(f"    {r.name()}")
    
    print(f"\n{sep}")
    print("  GEME — controlled Q-sandbox")
    print(sep)


if __name__ == "__main__":
    run()
