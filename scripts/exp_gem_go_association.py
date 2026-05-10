"""
GEME GO — Co-occurrence association mechanism test.
Feed parallel + angle + triangle propositions as SEPARATE inputs.
System must detect: they co-occur → create association frames.
NO structural similarity needed.
"""
import sys, os, random
sys.path.insert(0, r'G:\GEME\src')
from gira.phase3.language import *
from gira.phase6.geme_go import GEME, formula_source
from gira.phase6.proof_viewer import ProofViewer

OUT = r'g:\GEME\docs\go_tri'
os.makedirs(OUT, exist_ok=True)
_rnd = random.Random(42)

A,B,C,D,E,F,G,H = [var(c) for c in "ABCDEFGH"]

print("=" * 60)
print("  GEME GO — Co-occurrence Association")
print("=" * 60)
print("\n  Mechanism: system detects which FRAME TYPES appear together")
print("  in a sliding time window — creates ASSOCIATION frames.")
print("  No structural merge = no problem. Co-occurrence IS the merge.\n")

e = GEME(axioms=[], memory_cap=10, merge_thresh=0.75,
         cooccur_window=60, cooccur_thresh=0.35)
v = ProofViewer(e)

for step_i in range(600):
    # Each "proof step" = 3 inputs: parallel + angle + triangle
    # They co-occur in time → system detects association
    
    # 1: parallel line statement
    e.process(eq(fn("parallel",A,B), fn("parallel",C,D)))
    # 2: angle equality (consequence of parallel lines)
    e.process(eq(fn("angle",A,B,C), fn("angle",D,E,F)))
    # 3: triangle congruence (related to the parallel+angle context)
    e.process(eq(fn("△",A,B,C), fn("△",D,E,F)))
    
    # Sometimes add noise (random position)
    if _rnd.random() < 0.3:
        e.process(eq(fn("seg",G,H), fn("seg",E,F)))

    if step_i % 150 == 0 and step_i > 0:
        print(f"  @{step_i*4}: {len(e.memory.frames)} frames, "
              f"{e.memory._assoc_frames} associations detected")
        for f in sorted(e.memory.frames, key=lambda x:x.weight, reverse=True)[:4]:
            s = f.src[:45] if f.src else "(assoc)"
            # Show association links
            link = "──" if "──" in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig) else "   "
            print(f"    w={f.weight:5.1f} {link} {s}")

# Final state
path = v.save_run(OUT)
print(f"\n  Final memory ({len(e.memory.frames)} frames):")
for i,f in enumerate(sorted(e.memory.frames, key=lambda x:x.weight, reverse=True)):
    link_mark = "⇄" if "──" in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig) else " "
    s = f.src[:50]
    print(f"  [{i}] {link_mark} w={f.weight:.1f}  {s}")
print(f"\n  Total associations created: {e.memory._assoc_frames}")
print(f"  -> {os.path.basename(path)}")
print("=" * 60)
