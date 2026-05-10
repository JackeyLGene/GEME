"""
GEME GO — Chain proof starter. Parallel line propositions + angle relations.
Test if GEME can organize: parallel lines → angle relations → triangle angle sum.
"""
import sys, os, random
sys.path.insert(0, r'G:\GEME\src')
from gira.phase3.language import *
from gira.phase6.geme_go import GEME, formula_source

OUT = r'g:\GEME\docs\go_tri'
os.makedirs(OUT, exist_ok=True)
_rnd = random.Random(42)

A,B,C,D,E,F,G,H,I,J,K,L = [var(c) for c in "ABCDEFGHIJKL"]

# ── Parallel line encoding ──
# parallel(AB, CD) → "line AB ∥ line CD"
# transversal(L1, L2, T) → "T cuts L1 and L2"
# angle equality: ∠A = ∠B (corresponding, alt interior, etc.)

def line_pts(p,q): return fn("seg",p,q) if _rnd.random()<0.5 else fn("line",p,q)

def make_chain_step(step_type="parallel"):
    """Generate a step in a parallel-line proof stream."""
    if step_type == "parallel":
        # "L1 ∥ L2" — parallel lines claim
        return eq(fn("parallel",A,B,C,D), fn("parallel",A,B,C,D))
        # ↑ tautological: trivially true for demonstration
    elif step_type == "corresponding":
        # Corresponding angles equal (consequence of ∥)
        return eq(fn("angle",A,B,C), fn("angle",D,E,F))
    elif step_type == "triangle":
        # Triangle formed by transversal + parallels
        return eq(fn("△",A,B,C), fn("△",D,E,F))
    elif step_type == "alt_interior":
        # Alternate interior angles equal
        return eq(fn("angle",B,A,C), fn("angle",B,D,C))
    else:
        return eq(fn("angle",A,B,C), fn("angle",A,B,C))

# ── Mixed proof stream ──
print("=" * 60)
print("  GEME GO — Chain proof: parallel + triangle + angle")
print("=" * 60)

types = ["parallel","corresponding","triangle","alt_interior"]

for exp_idx, (label, cap, rounds, noise_ratio) in enumerate([
    ("E1: parallel-heavy", 8, 20, 0.3),
    ("E2: balanced",      10, 25, 0.4),
    ("E3: triangle-heavy", 8, 25, 0.5),
]):
    e = GEME(axioms=[], memory_cap=cap, merge_thresh=0.75)
    total = 0
    type_counts = {t:0 for t in types}
    
    for rnd in range(rounds):
        for _ in range(20):
            if _rnd.random() < noise_ratio:
                t = _rnd.choice(types)
            else:
                t = _rnd.choice(types[:2])  # bias parallel+corresp
            step = make_chain_step(t)
            e.process(step)
            type_counts[t] += 1
            total += 1
    
    med = sorted(f.weight for f in e.memory.frames)[len(e.memory.frames)//2] if e.memory.frames else 0
    
    print(f"\n  {label}")
    print(f"    Input: {total} steps  Output: {len(e.memory.frames)} frames")
    print(f"    Comp: {total/max(len(e.memory.frames),1):.0f}:1  median={med:.0f}")
    for i, f in enumerate(sorted(e.memory.frames, key=lambda x: x.weight, reverse=True)[:4]):
        src_s = f.src[:60].replace("\n","")
        em = "E" if f.weight >= med else " "
        # Categorize
        cat = "UNK"
        if "parallel" in src_s: cat = "∥"
        elif "△" in src_s: cat = "△"
        elif "∠" in src_s and "parallel" not in src_s: cat = "∠"
        elif "seg" in src_s: cat = "SEG"
        print(f"    [{i}] [{em}] [{cat:3}] w={f.weight:6.1f}  {src_s}...")
    
    # Check if chain formed: parallel frame + angle frame + triangle frame all present
    has_par = any("parallel" in f.src for f in e.memory.frames)
    has_ang = any("∠" in f.src for f in e.memory.frames if "parallel" not in f.src)
    has_tri = any("△" in f.src for f in e.memory.frames)
    chain_depth = sum([has_par, has_ang, has_tri])
    print(f"    Chain depth: {chain_depth}/3 (∥={has_par}, ∠={has_ang}, △={has_tri})")

# ── SSS assembly: multi-edge from different data ──
print("\n" + "=" * 60)
print("  CHAIN VERIFICATION: SSS from separate edge data")
print("=" * 60)

e4 = GEME(axioms=[], memory_cap=8, merge_thresh=0.70)
# Feed three separate edge equations + triangle conclusion as SEQUENTIAL steps
for step_i in range(300):
    # Step A: feed an edge equality
    e4.process(eq(fn("seg",A,B), fn("seg",D,E)))
    # Step B: feed another edge equality  
    e4.process(eq(fn("seg",B,C), fn("seg",E,F)))
    # Step C: feed third edge equality
    e4.process(eq(fn("seg",C,A), fn("seg",F,D)))
    # Step D: feed triangle congruence CONCLUSION
    e4.process(eq(fn("△",A,B,C), fn("△",D,E,F)))
    
    if step_i % 100 == 0:
        print(f"    @{step_i*4}: {len(e4.memory.frames)} frames, "
              f"seg_weights={[f.weight for f in e4.memory.frames if 'seg' in f.src][:3]}")

med4 = sorted(f.weight for f in e4.memory.frames)[len(e4.memory.frames)//2] if e4.memory.frames else 0
print(f"\n  Final memory ({len(e4.memory.frames)} frames, med={med4:.0f}):")
# Check: are the 3 edge equalities + conclusion assembled?
seg_frames = [f for f in e4.memory.frames if "seg" in f.src and "△" not in f.src]
tri_frames = [f for f in e4.memory.frames if "△" in f.src]
print(f"    Segment frames: {len(seg_frames)}  Triangle frames: {len(tri_frames)}")
for i, f in enumerate(sorted(e4.memory.frames, key=lambda x: x.weight, reverse=True)):
    cat = "SEG" if "seg" in f.src else "△" if "△" in f.src else "OTHER"
    em = "E" if f.weight >= med4 else " "
    print(f"    [{i}] [{em}] [{cat:4}] w={f.weight:6.1f}  {f.src[:55]}")

# Are SSS three edges present?
all_three_seg = len(seg_frames) >= 3
sss_chain = all_three_seg and len(tri_frames) >= 1
print(f"\n    SSS chain: {'YES (3 edges + △ formed)' if sss_chain else 'NO'}")
print("=" * 60)

# ── Parallel+Triangle chain test ──
print("\n  PARALLEL + TRIANGLE CHAIN TEST:")
e5 = GEME(axioms=[], memory_cap=10, merge_thresh=0.75)
# Feed 500 mixed steps: parallel statements + angle equalities + triangle conclusions
for step_i in range(500):
    parity = step_i % 3
    if parity == 0:
        # "lines L1 and L2 are parallel"
        e5.process(eq(fn("parallel",A,B), fn("parallel",C,D)))
    elif parity == 1:
        # "corresponding angles are equal"
        e5.process(eq(fn("angle",A,B,C), fn("angle",D,E,F)))
    else:
        # "the triangle formed has known properties"
        e5.process(eq(fn("△",A,B,C), fn("△",D,E,F)))

med5 = sorted(f.weight for f in e5.memory.frames)[len(e5.memory.frames)//2] if e5.memory.frames else 0
print(f"    Frames: {len(e5.memory.frames)}  med={med5:.0f}  comp={500/max(len(e5.memory.frames),1):.0f}:1")
for i, f in enumerate(sorted(e5.memory.frames, key=lambda x: x.weight, reverse=True)[:5]):
    em = "E" if f.weight >= med5 else " "
    cat = "∥" if "parallel" in f.src else "∠" if "∠" in f.src else "△" if "△" in f.src else "?"
    print(f"    [{i}] [{em}] [{cat}] w={f.weight:6.1f}  {f.src[:60]}")
print("=" * 60)
