"""Experiment 3: Shapes from Pure Connection — GEME learns "shape" types.

Three shape types, different function names → separate concepts:
- triangle (closed 3-loop) : eq(fn("triangle",Const("XYZ")),Const("yes"))
- chain (open 3-line)      : eq(fn("chain",Const("XYZ")),Const("yes"))
- pair (single edge)       : eq(fn("pair",Const("XY")),Const("yes"))

Result (verified 2026-05-04):
  triangle eval=2 chain eval=2 pair eval=2 unknown eval=3
  3 concept clusters + instance frames, clean separation
"""
import sys, random
sys.path.insert(0, r"g:\GEME\src")
from gira.phase3.language import eq, fn, constant as Const
from gira.phase6.geme_v6 import GEME
from gira.phase6.geme_go import structural_signature

_rnd = random.Random(42)
tris=[("A","B","C"),("D","E","F"),("G","H","I"),("J","K","L"),
      ("M","N","O"),("P","Q","R"),("S","T","U")]

def gen_tri(n):
    return [(eq(fn("triangle",Const(f"{x}{y}{z}")),Const("yes")),
             structural_signature(eq(fn("triangle",Const(f"{x}{y}{z}")),Const("yes"))))
            for _ in range(n) for x,y,z in[_rnd.choice(tris)]]

def gen_chain(n):
    return [(eq(fn("chain",Const(f"{x}{y}{z}")),Const("yes")),
             structural_signature(eq(fn("chain",Const(f"{x}{y}{z}")),Const("yes"))))
            for _ in range(n) for x,y,z in[_rnd.choice(tris)]]

def gen_pair(n):
    ps=[(_rnd.choice("ABCDEFGH"),_rnd.choice("IJKLMNOP")) for _ in range(n)]
    return [(eq(fn("pair",Const(f"{x}{y}")),Const("yes")),
             structural_signature(eq(fn("pair",Const(f"{x}{y}")),Const("yes"))))
            for x,y in ps]

e=GEME(memory_cap=16,cooccur_window=80,cooccur_thresh=0.15,max_chains=0)
all_d=gen_tri(1000)+gen_chain(1000)+gen_pair(500); _rnd.shuffle(all_d)
for i,(f,s) in enumerate(all_d):
    e.process_sig(f,s)
    if i>0 and i%500==0: e.memory.induction_clean()

print("=== E3: Shapes from Pure Connection ===")
print(f"Memory: {len(e.memory.frames)}/{e.memory.capacity}")
for f in sorted(e.memory.frames,key=lambda x:x.weight,reverse=True):
    sig=f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
    t="CONCEPT" if "──" in sig else "INST"
    print(f"  [{t}] w={f.weight:6.1f} merged={f.merged} {sig[:55]}")

print("\n── Recognition ──")
for lbl,form in [
    ("triangle (closed)", eq(fn("triangle",Const("XYZ")),Const("yes"))),
    ("chain (open)     ", eq(fn("chain",Const("XYZ")),Const("yes"))),
    ("pair (single)    ", eq(fn("pair",Const("XY")),Const("yes"))),
    ("unknown          ", eq(fn("unknown",Const("XY")),Const("yes"))),
]:
    s=structural_signature(form); e2=e.evaluate_sig(s)
    print(f"  {'✓' if e2==2 else '✗'} {lbl}: eval={e2}")
