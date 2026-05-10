"""
GEME GO — Ultimate test: feed DISCRETE geometric information.
No pre-bundled propositions. Individual signals: seg, angle, parallel, triangle.
System must ORGANIZE them into meaningful structures.
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

print("=" * 65)
print("  GEME GO — Discrete geometric information stream")
print("=" * 65)

e = GEME(axioms=[], memory_cap=12, merge_thresh=0.75,
         cooccur_window=80, cooccur_thresh=0.30)
v = ProofViewer(e)

total = 0
step_types = {"seg":0,"angle":0,"parallel":0,"triangle":0,"noise":0}

# Phase 1: feed 2000 individual geometric assertions
for step_i in range(2000):
    # Randomly pick one of 4 signal types
    sig_type = _rnd.choices(
        ["seg","angle","parallel","triangle","noise"],
        weights=[30,25,20,20,5]
    )[0]
    step_types[sig_type] += 1
    
    # Pick two random triangles
    tri_pool = [(A,B,C),(D,E,F),(G,H,I),(J,K,L)]
    t1 = _rnd.choice(tri_pool)
    t2 = _rnd.choice(tri_pool)
    while t2 == t1: t2 = _rnd.choice(tri_pool)
    
    if sig_type == "seg":
        # Individual segment equality
        i = _rnd.randint(0,2)
        a1,b1 = t1[i], t1[(i+1)%3]
        a2,b2 = t2[i], t2[(i+1)%3]
        f = eq(fn("seg",a1,b1), fn("seg",a2,b2))
    elif sig_type == "angle":
        # Individual angle equality (3-point form)
        i = _rnd.randint(0,2)
        f = eq(fn("angle",t1[(i+1)%3],t1[i],t1[(i+2)%3]),
                fn("angle",t2[(i+1)%3],t2[i],t2[(i+2)%3]))
    elif sig_type == "parallel":
        # Two random lines are parallel
        p1,q1 = _rnd.choice(t1[:2]), _rnd.choice(t1[1:])
        p2,q2 = _rnd.choice(t2[:2]), _rnd.choice(t2[1:])
        while p1==q1: q1 = _rnd.choice(t1[1:])
        while p2==q2: q2 = _rnd.choice(t2[1:])
        f = eq(fn("parallel",p1,q1), fn("parallel",p2,q2))
    elif sig_type == "triangle":
        # Triangle congruence statement
        f = eq(fn("△",t1[0],t1[1],t1[2]),
               fn("△",t2[0],t2[1],t2[2]))
    else:  # noise
        f = eq(fn("seg",A,F), fn("seg",G,L))
    
    e.process(f)
    total += 1

# Phase 2: test with bundled propositions (check chain understanding)
print("\n  Training: 2000 discrete geometric assertions")
print(f"    {step_types}")
print(f"    Memory frames: {len(e.memory.frames)}")
print(f"    Associations created: {e.memory._assoc_frames}")

# Print final memory
med = sorted(f.weight for f in e.memory.frames)[len(e.memory.frames)//2] if e.memory.frames else 0
print(f"\n  Final memory (median weight = {med:.0f}):")
for i,f in enumerate(sorted(e.memory.frames, key=lambda x:x.weight, reverse=True)):
    is_assoc = "──" in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig)
    cat = "⇄" if is_assoc else " "
    em = "E" if f.weight >= med else " "
    s = f.src[:50]
    t = "ASSOC" if is_assoc else ("SEG" if "seg" in s else "∠" if "∠" in s else "∥" if "parallel" in s else "△" if "△" in s else "?")
    print(f"  [{i}] {em} {cat} [{t:5}] w={f.weight:6.1f}  {s}")

# Phase 3: Test chain understanding — feed SSS bundled and check evaluation
print("\n  Phase 3: Chain understanding test")
# Build a SSS proposition
SSS_prop = impl(
    conj(conj(eq(fn("seg",A,B),fn("seg",D,E)),
              eq(fn("seg",B,C),fn("seg",E,F))),
         eq(fn("seg",C,A),fn("seg",F,D))),
    eq(fn("△",A,B,C),fn("△",D,E,F)))
e.process(SSS_prop)

# Check: did the SSS proposition match any existing frame?
print(f"  SSS evaluate: S{e.evaluate(SSS_prop)} (S2=emerged)")
for f in sorted(e.memory.frames, key=lambda x:x.weight, reverse=True)[:3]:
    if "seg" in f.src and "△" in f.src:
        print(f"    matched: w={f.weight:.1f}  {f.src[:50]}")

# Phase 4: Association network summary
print(f"\n  Phase 4: Association network")
assoc_frames = [f for f in e.memory.frames if "──" in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig)]
print(f"    Live associations: {len(assoc_frames)}")
for f in sorted(assoc_frames, key=lambda x:x.weight, reverse=True):
    parts = (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig).split("──")
    print(f"    w={f.weight:.1f}  {parts[0][:20]} ←→ {parts[1][:20] if len(parts)>1 else '?'}")

path = v.save_run(OUT)
print(f"\n  -> {os.path.basename(path)}")
print("=" * 65)
