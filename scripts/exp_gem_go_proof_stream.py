"""
GEME GO — Proof stream: feed valid+invalid proof-like steps.
System must ORGANIZE which premise→conclusion sequences are valid.
Multiple triangles, no default triangle assumption.
"""
import sys, os, random
sys.path.insert(0, r'G:\GEME\src')
from gira.phase3.language import *
from gira.phase6.geme_go import GEME
from gira.phase6.proof_viewer import ProofViewer

OUT = r'g:\GEME\docs\go_tri'
os.makedirs(OUT, exist_ok=True)
_rnd = random.Random()

# ── Triangle vertex pool ──
# Each triangle is a triple of distinct vertices
TRI = [
    ("A","B","C"), ("D","E","F"), ("P","Q","R"),
    ("G","H","I"), ("J","K","L"), ("M","N","O"),
    ("X","Y","Z"), ("U","V","W"),
]

def _v(name): return var(name)

def gen_seg_eq(t1, t2):
    """Generate segment equality between two triangles.
    t1_t2 = (A,B) ↔ (D,E)"""
    a,b = _v(t1[0]), _v(t1[1])
    c,d = _v(t2[0]), _v(t2[1])
    return eq(fn("seg",a,b), fn("seg",c,d))

def gen_angle_eq(t1, t2, vertex_idx=0):
    """Generate angle equality at vertex_idx of each triangle."""
    a = _v(t1[vertex_idx])
    d = _v(t2[vertex_idx])
    return eq(fn("angle",a), fn("angle",d))

def gen_triangle_eq(t1, t2):
    """△ABC ≡ △DEF"""
    return eq(fn("△",_v(t1[0]),_v(t1[1]),_v(t1[2])),
              fn("△",_v(t2[0]),_v(t2[1]),_v(t2[2])))

def make_proof_step(valid=True):
    """Generate a proof-like step: 3 premises → conclusion.
    If valid: premises are a valid congruence pattern (SSS/SAS/ASA/AAS).
    If invalid: premises are random (wrong correspondences).
    Multiple triangles used — no default triangle.
    """
    # Pick two triangles at random
    t1 = _rnd.choice(TRI)
    t2 = _rnd.choice(TRI)
    while t2 == t1: t2 = _rnd.choice(TRI)
    
    if valid:
        # Pick a valid pattern
        pattern = _rnd.choice([
            # SSS: all three sides
            lambda: [
                gen_seg_eq((t1[0],t1[1]),(t2[0],t2[1])),
                gen_seg_eq((t1[1],t1[2]),(t2[1],t2[2])),
                gen_seg_eq((t1[2],t1[0]),(t2[2],t2[0])),
            ],
            # SAS: seg, angle(vertex 0), seg
            lambda: [
                gen_seg_eq((t1[0],t1[1]),(t2[0],t2[1])),
                gen_angle_eq(t1, t2, 0),
                gen_seg_eq((t1[2],t1[0]),(t2[2],t2[0])),
            ],
            # ASA: angle(0), seg, angle(1)
            lambda: [
                gen_angle_eq(t1, t2, 0),
                gen_seg_eq((t1[0],t1[1]),(t2[0],t2[1])),
                gen_angle_eq(t1, t2, 1),
            ],
            # AAS: angle(0), angle(1), seg(2-0)
            lambda: [
                gen_angle_eq(t1, t2, 0),
                gen_angle_eq(t1, t2, 1),
                gen_seg_eq((t1[2],t1[0]),(t2[2],t2[0])),
            ],
        ])
        premises = pattern()
    else:
        # Random invalid: pick 3 non-corresponding elements
        choices = []
        # segment choices
        for i in range(3):
            for j in range(3):
                choices.append(("seg", i, j))
        # angle choices
        for i in range(3):
            choices.append(("angle", i, i))
        picks = _rnd.sample(choices, 3)
        premises = []
        for typ, pi, pj in picks:
            if typ == "seg":
                # Random segment (may not correspond)
                idx1 = (pi, (pi+1)%3)
                idx2 = (pj, (pj+1)%3)
                premises.append(gen_seg_eq(
                    (t1[idx1[0]],t1[idx1[1]]),
                    (t2[idx2[0]],t2[idx2[1]])))
            else:
                premises.append(gen_angle_eq(t1, t2, pi))
    
    # Build formula: (p1 ∧ p2 ∧ p3) → △≡△
    conclusion = gen_triangle_eq(t1, t2)
    if len(premises) >= 3:
        body = conj(conj(premises[0], premises[1]), premises[2])
    else:
        body = premises[0]
    return impl(body, conclusion)

print("=" * 60)
print("  GEME GO — Proof stream (multi-triangle, valid+invalid)")
print("=" * 60)

for exp_idx, (label, cap, rounds, valid_ratio) in enumerate([
    ("E1: mixed valid+invalid",   8, 30, 0.4),
    ("E2: mostly valid",         10, 30, 0.6),
    ("E3: mostly invalid",       8, 30, 0.2),
    ("E4: large mem",            12, 30, 0.4),
]):
    e = GEME(axioms=[], memory_cap=cap, merge_thresh=0.75)
    v = ProofViewer(e)
    total = 0
    for rnd in range(rounds):
        for _ in range(20):
            step = make_proof_step(valid_ratio > _rnd.random())
            e.process(step)
            total += 1
    
    cr = total / max(len(e.memory.frames), 1)
    path = v.save_run(OUT)
    
    print(f"\n  {label}")
    print(f"    input: {total}  output: {len(e.memory.frames)}  comp: {cr:.0f}:1")
    for i, f in enumerate(sorted(e.memory.frames, key=lambda x: x.weight, reverse=True)):
        s = f.src[:70].replace("\n","")
        print(f"    [{i}] w={f.weight:.1f}  {s}...")
    print(f"    -> {os.path.basename(path)}")
    print(f"    stress: {e.memory.stress:.4f}")

# ── Check which valid patterns were "discovered" ──
print("\n" + "=" * 60)
print("  VALID PATTERN DISCOVERY CHECK")
print("=" * 60)
# Run a dedicated discovery test
e = GEME(axioms=[], memory_cap=10, merge_thresh=0.75)
for _ in range(500):
    step = make_proof_step(0.35)  # 35% valid
    e.process(step)

print(f"\n  After 500 steps (35% valid):")
print(f"  Frames: {len(e.memory.frames)}  comp: {500/max(len(e.memory.frames),1):.0f}:1")
for i, f in enumerate(sorted(e.memory.frames, key=lambda x: x.weight, reverse=True)):
    s = f.src[:65].replace("\n","")
    # Categorize
    cat = "???"
    src = f.src
    has_seg = src.count("≡") >= 3
    has_angle = "∠" in src
    prems = src.split("→")[0] if "→" in src else src
    if "seg" in prems and "∠" in prems and has_seg:
        cat = "EDGE+ANGLE"
    elif has_seg and not has_angle:
        cat = "ALL-EDGES"
    else:
        cat = "OTHER"
    print(f"    [{i}] w={f.weight:.1f}  [{cat}]  {s}...")

print("\n" + "=" * 60)
print("  DONE")
print("=" * 60)
