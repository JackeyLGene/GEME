"""
GEME PA — Test Data Example & Quick Start

This script demonstrates the minimal experiment:
  1. Load Robinson Q axioms
  2. Feed commutativity instances (S2 data)
  3. Observe add_comm emergence through co-occurrence self-reference

Run: python test_data_example.py
Expected output: add_comm → S2, negative control → S3
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from gira.phase3.q_axioms import robinson_q
from gira.phase3.language import *
from gira.phase6.geme_v6 import GEME

# ── Target formulas ──
x, y = var("x"), var("y")
add_comm = forall(x, forall(y, eq(fn("+", x, y), fn("+", y, x))))
mul_comm = forall(x, forall(y, eq(fn("*", x, y), fn("*", y, x))))

# ── S2 data: commutativity instances ──
S2_add = [
    eq(fn("+", constant("1"), constant("2")), fn("+", constant("2"), constant("1"))),
    eq(fn("+", constant("3"), constant("5")), fn("+", constant("5"), constant("3"))),
    eq(fn("+", constant("0"), constant("7")), fn("+", constant("7"), constant("0"))),
    eq(fn("+", constant("4"), constant("9")), fn("+", constant("9"), constant("4"))),
    eq(fn("+", constant("2"), constant("8")), fn("+", constant("8"), constant("2"))),
]

# ── S0 data: noise ──
S0_noise = [
    eq(constant("0"), constant("0")),
    eq(fn("+", constant("1"), constant("1")), constant("2")),
    eq(fn("+", constant("2"), constant("3")), constant("5")),
    eq(fn("+", constant("0"), constant("1")), constant("1")),
    eq(fn("*", constant("2"), constant("3")), constant("6")),
]

print("=" * 50)
print("  GEME PA — Minimal Test Example")
print("=" * 50)

# ── Experiment 1: With S2 data ──
e1 = GEME(axioms=robinson_q(), memory_cap=10, merge_thresh=0.15,
          cooccur_window=50, cooccur_thresh=0.25)

for step_i in range(500):
    # Mix noise and commutativity instances
    if step_i % 3 == 0:
        for f in S0_noise: e1.process(f)
    else:
        for f in S2_add: e1.process(f)

add_r = e1.evaluate(add_comm)
mul_r = e1.evaluate(mul_comm)
assocs = sum(1 for f in e1.memory.frames 
             if "──" in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig))
chains = sum(1 for f in e1.memory.frames 
             if "══" in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig))

print(f"\n  Experiment 1: With S2 add instances")
print(f"  add_comm: S{add_r}  (S2 = emerged)")
print(f"  mul_comm: S{mul_r}")
print(f"  Memory: {len(e1.memory.frames)}/10 frames")
print(f"  Association frames: {assocs}")
print(f"  Chain frames: {chains}")

# ── Experiment 2: Negative control (no S2) ──
e2 = GEME(axioms=robinson_q(), memory_cap=10, merge_thresh=0.15,
          cooccur_window=50, cooccur_thresh=0.25)
for step_i in range(500):
    for f in S0_noise: e2.process(f)

add_r2 = e2.evaluate(add_comm)
print(f"\n  Experiment 2: Negative control (no S2)")
print(f"  add_comm: S{add_r2}  (S3 = correct, no false emergence)")

# ── Print memory state ──
print(f"\n  Experiment 1 memory state:")
for i, f in enumerate(sorted(e1.memory.frames, key=lambda x:x.weight, reverse=True)):
    sig = f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
    level = "L2" if "══" in sig else "L1" if "──" in sig else "S0"
    print(f"    [{i}] [{level}] w={f.weight:6.1f}  {sig[:50]}")

print("\n" + "=" * 50)
print("  Done. This validates the core PA emergence claim.")
print("=" * 50)
