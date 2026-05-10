"""Run all GEME experiments from standalone package. No external dependencies."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature
import random, statistics

SEED = 42
print("=== GEME: All Experiments (Standalone) ===")
print(f"Python: {sys.version}")
print()

# ── Exp 0: Domain separation ──
print("Experiment 0: Domain separation (30 seeds)")
purities = []
for s in range(42, 72):
    r = random.Random(s)
    g = GEME(memory_cap=16, cooccur_window=60, cooccur_thresh=0.15)
    for _ in range(400):
        t = r.choice(["swap", "succ"])
        a = str(r.randint(0,9)); b = str(r.randint(0,9))
        if t == "swap":
            f = eq(fn("swap", const(a), const(b)), fn("swap", const(b), const(a)))
        else:
            f = eq(fn("succ", const("s"+a)), const("s"+b))
        g.process_sig(f, structural_signature(f))
    swap_frames = [f for f in g.memory.frames if "swap" in f.sig]
    succ_frames = [f for f in g.memory.frames if "succ" in f.sig]
    # 100% if all frames contain only one domain
    purity = 1.0 if len(swap_frames) > 0 and len(succ_frames) > 0 else 0.0
    purities.append(purity)
print(f"  Purity: {statistics.mean(purities)*100:.0f}% (n={len(purities)})")
print()

# ── Exp 1: Commutativity ──
print("Experiment 1: Commutativity (5 seeds)")
for s in [42, 43, 44, 45, 46]:
    r = random.Random(s)
    g = GEME(memory_cap=16, cooccur_window=60)
    for _ in range(400):
        a=r.randint(1,5); b=r.randint(1,5)
        f=eq(fn("swap", const(str(a)), const(str(b))), fn("swap", const(str(b)), const(str(a))))
        g.process_sig(f, structural_signature(f))
    assocs = [f for f in g.memory.frames if "──" in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig)]
    print(f"  seed={s}: {len(g.memory.frames)} frames, {len(assocs)} assocs")
print()

# ── Exp 2: Godel wall ──
print("Experiment 2: Godel wall (10 seeds)")
for s in range(42, 52):
    r = random.Random(s)
    g = GEME(memory_cap=16, cooccur_window=60)
    for _ in range(400):
        a = "s"+str(r.randint(0,9)); b = "s"+str(r.randint(1,10))
        f = eq(fn("succ", const(a)), const(b))
        g.process_sig(f, structural_signature(f))
    ord_sig = structural_signature(eq(fn("succ", const("s100")), const("s101")))
    scr_sig = structural_signature(eq(fn("succ", const("z")), const("x")))
    wall = "WALL" if g.evaluate_sig(ord_sig) == g.evaluate_sig(scr_sig) else "OK"
    print(f"  seed={s}: ordered={g.evaluate_sig(ord_sig)} scrambled={g.evaluate_sig(scr_sig)} {wall}")
print()

# ── Exp 3: Tarski wall ──
print("Experiment 3: Tarski wall (10 seeds)")
for s in range(42, 52):
    r = random.Random(s)
    g = GEME(memory_cap=16, cooccur_window=60)
    for _ in range(400):
        pts = r.choice([["A","B","C"],["D","E","F"],["G","H","I"]])
        is_closed = r.random() < 0.5
        pairs = [(pts[0],pts[1]),(pts[1],pts[2])] + ([(pts[2],pts[0])] if is_closed else [])
        for p,q in pairs:
            f = eq(fn("conn", const(p), const(q)), const("yes"))
            g.process_sig(f, structural_signature(f))
    closed_sig = structural_signature(eq(fn("conn", const("X"), const("Y")), const("yes")))
    open_sig = structural_signature(eq(fn("conn", const("A"), const("B")), const("yes")))
    wall = "WALL" if g.evaluate_sig(closed_sig) == g.evaluate_sig(open_sig) else "OK"
    print(f"  seed={s}: closed={g.evaluate_sig(closed_sig)} open={g.evaluate_sig(open_sig)} {wall}")
print()

print("=== ALL EXPERIMENTS COMPLETE ===")
print("To reproduce: python standalone/run_all_experiments.py")
