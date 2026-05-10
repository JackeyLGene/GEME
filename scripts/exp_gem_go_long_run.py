"""
GEME GO — Long run, passive collection mode.
Translation layer acts as observer, no targeted intervention.
"""
import sys, os, random, datetime
sys.path.insert(0, r'G:\GEME\src')
from gira.phase3.language import *
from gira.phase6.geme_go import GEME
from gira.phase6.proof_viewer import ProofViewer

OUT = r'g:\GEME\docs\go_tri'; os.makedirs(OUT, exist_ok=True)
_rnd = random.Random(42)
A,B,C,D,E,F,G,H,I,J,K,L = [var(c) for c in "ABCDEFGHIJKL"]
tri_pool = [(A,B,C),(D,E,F),(G,H,I),(J,K,L)]

# Config
N_STEPS = 5000
e = GEME(axioms=[], memory_cap=15, merge_thresh=0.75,
         cooccur_window=120, cooccur_thresh=0.25)

print("=" * 55)
print("  GEME GO — Long Run (Passive Observation)")
print(f"  5000 discrete geometric assertions")
print("=" * 55)

snapshots = []  # periodic snapshots

for step_i in range(N_STEPS):
    t1,t2 = _rnd.choice(tri_pool), _rnd.choice(tri_pool)
    while t2 == t1: t2 = _rnd.choice(tri_pool)
    st = _rnd.choices(
        ["seg","angle","parallel","triangle","noise"],
        weights=[28,25,22,20,5]
    )[0]
    if st == "seg":
        i = _rnd.randint(0,2)
        f = eq(fn("seg",t1[i],t1[(i+1)%3]), fn("seg",t2[i],t2[(i+1)%3]))
    elif st == "angle":
        i = _rnd.randint(0,2)
        f = eq(fn("angle",t1[(i+1)%3],t1[i],t1[(i+2)%3]),
                fn("angle",t2[(i+1)%3],t2[i],t2[(i+2)%3]))
    elif st == "parallel":
        f = eq(fn("parallel",t1[0],t1[1]), fn("parallel",t2[0],t2[1]))
    elif st == "triangle":
        f = eq(fn("△",t1[0],t1[1],t1[2]), fn("△",t2[0],t2[1],t2[2]))
    else:
        f = eq(fn("seg",A,B), fn("seg",G,H))
    e.process(f)
    
    if step_i > 0 and step_i % 1000 == 0:
        assoc_count = sum(1 for ff in e.memory.frames 
                         if "──" in (ff.sig_full if hasattr(ff,'sig_full') and ff.sig_full else ff.sig))
        snapshots.append((step_i, len(e.memory.frames), e.memory.stress, assoc_count))
        print(f"  @{step_i:4d}: frames={len(e.memory.frames):2d} "
              f"stress={e.memory.stress:.4f}  assoc={assoc_count}")

# ── Final analysis ──
print(f"\n  @{N_STEPS}: FINAL")
print(f"  Frames: {len(e.memory.frames)}")
print(f"  Stress: {e.memory.stress:.4f}")

# Collect all associations
assoc_frames = [f for f in e.memory.frames 
                if "──" in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig)]
main_frames = [f for f in e.memory.frames if f not in assoc_frames]

print(f"  Main frames: {len(main_frames)}")
print(f"  Association frames: {len(assoc_frames)}")

# Print main frames (the "concept" frames)
print(f"\n  ── Stable Concepts (top 6) ──")
med = sorted(f.weight for f in e.memory.frames)[len(e.memory.frames)//2] if e.memory.frames else 0
for i, f in enumerate(sorted(main_frames, key=lambda x:x.weight, reverse=True)[:6]):
    src_s = f.src[:45]
    cat = "?"
    if "parallel" in src_s: cat = "∥"
    elif "∠" in src_s: cat = "∠"
    elif "△" in src_s: cat = "△"
    elif "seg" in src_s or "≡" in src_s: cat = "SEG"
    em = "E" if f.weight >= med else " "
    print(f"  [{i}] {em} [{cat:4}] w={f.weight:6.0f}  {src_s}...")

# Print association network
print(f"\n  ── Association Graph ──")
for f in sorted(assoc_frames, key=lambda x:x.weight, reverse=True):
    sig = f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
    parts = sig.split("──")
    def label(p):
        if "△" in p: return "△"
        if "parallel" in p: return "∥"
        if "angle" in p: return "∠"
        if "seg" in p: return "SEG"
        return p[:6]
    if len(parts) >= 2:
        print(f"    {label(parts[0]):4} ──({f.weight:.0f})── {label(parts[1]):4}")

# Discovery report
print(f"\n  ── Discovery Report ──")
# Full path from concept to concept
labels_present = set()
for f in main_frames:
    s = f.src
    if "parallel" in s: labels_present.add("∥")
    elif "∠" in s: labels_present.add("∠")
    elif "△" in s: labels_present.add("△")
    elif "seg" in s: labels_present.add("SEG")

# Check which paths exist
paths = {"SEG":["∠","∥","△"],"∠":["∥","△"],"∥":["△"]}
conns = {}
for f in assoc_frames:
    sig = f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
    p = sig.split("──")
    if len(p) >= 2:
        def abbr(s): return "△" if "△" in s else "∥" if "parallel" in s else "∠" if "angle" in s else "SEG" if "seg" in s else s
        conns[(abbr(p[0]),abbr(p[1]))] = f.weight

print(f"  Concepts found: {', '.join(sorted(labels_present, key=lambda x: -sum(1 for f in main_frames if x in f.src)))}")
print(f"  Total associations: {len(assoc_frames)}")
print(f"  Longest path fragments:")
for (a,b),w in sorted(conns.items(), key=lambda x:-x[1])[:5]:
    print(f"    {a} ──({w:.0f})── {b}")

# Save
v = ProofViewer(e)
path = v.save_run(OUT)
print(f"\n  -> {os.path.basename(path)}")
print("=" * 55)
