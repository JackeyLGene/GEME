"""
GEME GO — Extract proof from stable association network.
Traverse: seg → angle → parallel → triangle → △
Each step = one association link in the network.
"""
import sys, os, random
sys.path.insert(0, r'G:\GEME\src')
from gira.phase3.language import *
from gira.phase6.geme_go import GEME, formula_source
from gira.phase6.proof_viewer import ProofViewer

OUT = r'g:\GEME\docs\go_tri'
os.makedirs(OUT, exist_ok=True)
_rnd = random.Random(42)
A,B,C,D,E,F,G,H,I,J,K,L = [var(c) for c in "ABCDEFGHIJKL"]

# ── Train the system ──
e = GEME(axioms=[], memory_cap=12, merge_thresh=0.75,
         cooccur_window=80, cooccur_thresh=0.30)
v = ProofViewer(e)

print("=" * 65)
print("  GEME GO — Proof Extraction from Association Network")
print("=" * 65)

# Feed 2500 discrete geometric assertions
tri_pool = [(A,B,C),(D,E,F),(G,H,I),(J,K,L)]
for step_i in range(2500):
    t1 = _rnd.choice(tri_pool)
    t2 = _rnd.choice(tri_pool)
    while t2 == t1: t2 = _rnd.choice(tri_pool)
    sig_type = _rnd.choices(
        ["seg","angle","parallel","triangle","noise"],
        weights=[30,25,20,20,5]
    )[0]
    if sig_type == "seg":
        i = _rnd.randint(0,2)
        f = eq(fn("seg",t1[i],t1[(i+1)%3]), fn("seg",t2[i],t2[(i+1)%3]))
    elif sig_type == "angle":
        i = _rnd.randint(0,2)
        f = eq(fn("angle",t1[(i+1)%3],t1[i],t1[(i+2)%3]),
                fn("angle",t2[(i+1)%3],t2[i],t2[(i+2)%3]))
    elif sig_type == "parallel":
        f = eq(fn("parallel",t1[0],t1[1]), fn("parallel",t2[0],t2[1]))
    elif sig_type == "triangle":
        f = eq(fn("△",t1[0],t1[1],t1[2]), fn("△",t2[0],t2[1],t2[2]))
    else:
        f = eq(fn("seg",A,F), fn("seg",G,L))
    e.process(f)

# ── Extract Proof ──
# Step 1: identify main frames and association frames
main_frames = [f for f in e.memory.frames if "──" not in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig)]
assoc_frames = [f for f in e.memory.frames if "──" in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig)]

# Categorize main frames
def categorize(src):
    if "parallel" in src: return "∥"
    if "∠" in src: return "∠"
    if "△" in src: return "△"
    if "seg" in src or "≡" in src: return "SEG"
    return "?"

def extract_short_sig(assoc_sig):
    parts = assoc_sig.split("──")
    return [p[:15] for p in parts]

print("\n  ── Association Network (Proof Structure) ──")
print()
# Print the network as a graph
for f in sorted(assoc_frames, key=lambda x:x.weight, reverse=True):
    sig_full = f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
    p1,p2 = extract_short_sig(sig_full)
    # Map sig parts to human labels
    def to_label(p):
        if "parallel" in p: return "∥"
        if "angle" in p: return "∠"
        if "seg" in p: return "SEG"
        if "triangle" in p or "△" in p: return "△"
        return p
    l1,l2 = to_label(p1), to_label(p2)
    print(f"    {l1:4} ──({f.weight:.0f})── {l2}")

# Print as adjacency table
labels = ["SEG","∠","∥","△"]
print("\n  ── Adjacency Matrix (weight) ──")
print(f"     {'':4} {'SEG':6} {'∠':6} {'∥':6} {'△':6}")
print("     " + "-" * 28)
weights = {}
for f in assoc_frames:
    sig = f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
    p1,p2 = extract_short_sig(sig)
    l1,l2 = to_label(p1), to_label(p2)
    weights[(l1,l2)] = f.weight
    weights[(l2,l1)] = f.weight
for l1 in labels:
    row = f"     {l1:4}"
    for l2 in labels:
        if l1 == l2:
            row += f" {'--':6}"
        else:
            w = weights.get((l1,l2), 0)
            row += f" {w:6.0f}"
    print(row)

# Step 3: Extract proof path
print("\n  ── Proof Path: seg → angle → parallel → triangle ──")
path = ["SEG","∠","∥","△"]
for i in range(len(path)-1):
    a,b = path[i], path[i+1]
    w = weights.get((a,b), 0)
    arrow = "→" if w > 20 else "?>"
    print(f"    {a} {arrow} {b}  (association weight: {w:.0f})")

# Step 4: Show stability of associations over time from chain snapshots
print("\n  ── Weight History from Snapshots ──")
snaps = e.chain.sections
if len(snaps) >= 2:
    print(f"   {len(snaps)} snapshots recorded:")
    for snap in snaps[-3:]:
        print(f"    @frame {snap.frame}: {len(snap.items)} frames")
        for src,w in sorted(snap.items, key=lambda x:x[1], reverse=True)[:3]:
            print(f"      w={w:.0f}  {src[:40]}")

# Save
path = v.save_run(OUT)
print(f"\n  -> {os.path.basename(path)}")
print("=" * 65)
