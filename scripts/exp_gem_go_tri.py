"""
GEME GO — Triangle space random proposition stream.
Measures compression efficiency as emergence signal.
No pre-coded targets. System discovers valid triangle congruence patterns.
"""
import sys, os, random, datetime, statistics
sys.path.insert(0, r'G:\GEME\src')
from gira.phase3.language import *
from gira.phase6.geme_go import GEME
from gira.phase6.proof_viewer import ProofViewer

A,B,C,D,E,F,G,H = [var(c) for c in "ABCDEFGH"]
P,Q,R,S,T,U = [var(c) for c in "PQRSTU"]

OUT_DIR = r'g:\GEME\docs\go_tri'
os.makedirs(OUT_DIR, exist_ok=True)

# ── Triangle-pool: all valid congruence patterns ──
# Valid: 3 specific element pairs → △≡△
# Invalid: 3 random pairs → may not correspond to triangle
ELEMENTS = [
    ("seg", "AB","DE"), ("seg", "BC","EF"), ("seg", "CA","FD"),
    ("angle","A","D"), ("angle","B","E"), ("angle","C","F"),
]
ELEM_DICT = {i:e for i,e in enumerate(ELEMENTS)}

VALID_TRIPLES = [
    # SAS: seg(A), angle(A), seg(C)
    (("seg","AB","DE"), ("angle","A","D"), ("seg","CA","FD")),
    # ASA: angle(A), seg(A), angle(B)
    (("angle","A","D"), ("seg","AB","DE"), ("angle","B","E")),
    # SSS: all three segs
    (("seg","AB","DE"), ("seg","BC","EF"), ("seg","CA","FD")),
    # AAS: angle(A), angle(B), seg(C)
    (("angle","A","D"), ("angle","B","E"), ("seg","CA","FD")),
]

def make_prop(triple):
    """Convert a triple of (type, p1, p2) into formula."""
    conds = []
    for typ, p1, p2 in triple:
        if typ == "seg":
            a,b = var(p1[0]), var(p1[1])
            c,d = var(p2[0]), var(p2[1])
            conds.append(eq(fn("seg",a,b), fn("seg",c,d)))
        elif typ == "angle":
            a = var(p1); d = var(p2)
            conds.append(eq(fn("angle",a), fn("angle",d)))
    
    if not conds: return None
    premise = conds[0]
    for c in conds[1:]:
        premise = conj(premise, c)
    
    triangles = eq(fn("△",A,B,C), fn("△",D,E,F))
    return impl(premise, triangles)

_rnd = random.Random()

def gen_random_props(n=20, valid_ratio=0.4):
    """Generate n random triangle propositions."""
    props = []
    for _ in range(n):
        if _rnd.random() < valid_ratio:
            triple = _rnd.choice(VALID_TRIPLES)
        else:
            # Random pick 3 from 6 elements (may be invalid)
            triple = tuple(ELEM_DICT[i] for i in _rnd.sample(range(6), 3))
        p = make_prop(triple)
        if p: props.append(p)
    return props

# ── Run ──
print("=" * 60)
print("  GEME GO — Triangle space (no pre-coded targets)")
print("=" * 60)

for exp_idx, (label, cap, rounds, noise_level) in enumerate([
    ("E1: medium noise", 8, 20, 0.4),
    ("E2: low noise",    10, 30, 0.6),
    ("E3: high noise",   8, 30, 0.2),
    ("E4: large memory", 12, 30, 0.4),
]):
    e = GEME(axioms=[], memory_cap=cap, merge_thresh=0.75)
    v = ProofViewer(e)
    
    stats = {"frames_in": 0, "frames_out": 0, "inductions": 0}
    
    for rnd in range(rounds):
        props = gen_random_props(20, noise_level)
        stats["frames_in"] += len(props)
        for p in props:
            r = e.process(p)
            if r["induction"]: stats["inductions"] += 1
        stats["frames_out"] = len(e.memory.frames)
    
    # Compression ratio
    comp_ratio = stats["frames_in"] / max(stats["frames_out"], 1)
    
    path = v.save_run(OUT_DIR)
    
    print(f"\n  {label}")
    print(f"    frames in: {stats['frames_in']:4d}  out: {stats['frames_out']}  "
          f"inductions: {stats['inductions']}")
    print(f"    compression ratio: {comp_ratio:.1f}:1  "
          f"stress: {e.memory.stress:.4f}")
    print(f"    memory frames:")
    for i, f in enumerate(sorted(e.memory.frames, key=lambda x: x.weight, reverse=True)):
        print(f"      [{i}] w={f.weight:.1f}  {f.src[:50]}...")
    print(f"    → {os.path.basename(path)}")

print("\n" + "=" * 60)
print("  DONE")
print("=" * 60)
