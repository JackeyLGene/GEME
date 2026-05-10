"""
GEME GO — Generalization test + ProofStream visualization.
Train on SAS+SSS only. Test if ASA emerges spontaneously.
"""
import sys, os, random
sys.path.insert(0, r'G:\GEME\src')
from gira.phase3.language import *
from gira.phase6.geme_go import GEME

OUT = r'g:\GEME\docs\go_tri'
os.makedirs(OUT, exist_ok=True)
_rnd = random.Random()

TRI = [("A","B","C"),("D","E","F"),("P","Q","R"),("G","H","I"),("J","K","L")]
def _v(n): return var(n)

def seg_eq(t1,t2): return eq(fn("seg",_v(t1[0]),_v(t1[1])),fn("seg",_v(t2[0]),_v(t2[1])))
def ang_eq(t1,t2,i):
    pts1=(t1[(i+1)%3],t1[i],t1[(i+2)%3])
    pts2=(t2[(i+1)%3],t2[i],t2[(i+2)%3])
    return eq(fn("angle",_v(pts1[0]),_v(pts1[1]),_v(pts1[2])),
              fn("angle",_v(pts2[0]),_v(pts2[1]),_v(pts2[2])))
def tri_eq(t1,t2): return eq(fn("△",_v(t1[0]),_v(t1[1]),_v(t1[2])),fn("△",_v(t2[0]),_v(t2[1]),_v(t2[2])))

def make_step(t1,t2,pattern):
    """Build (p1∧p2∧p3)→△≡△ from pattern name."""
    P = {
        "SAS": lambda: [seg_eq((t1[0],t1[1]),(t2[0],t2[1])), ang_eq(t1,t2,0), seg_eq((t1[2],t1[0]),(t2[2],t2[0]))],
        "SSS": lambda: [seg_eq((t1[0],t1[1]),(t2[0],t2[1])), seg_eq((t1[1],t1[2]),(t2[1],t2[2])), seg_eq((t1[2],t1[0]),(t2[2],t2[0]))],
        "ASA": lambda: [ang_eq(t1,t2,0), seg_eq((t1[0],t1[1]),(t2[0],t2[1])), ang_eq(t1,t2,1)],
        "AAS": lambda: [ang_eq(t1,t2,0), ang_eq(t1,t2,1), seg_eq((t1[2],t1[0]),(t2[2],t2[0]))],
    }
    prems = P.get(pattern, P["SAS"])()
    body = conj(conj(prems[0],prems[1]),prems[2])
    return impl(body, tri_eq(t1,t2))

def gen_triple():
    t1 = _rnd.choice(TRI); t2 = _rnd.choice(TRI)
    while t2 == t1: t2 = _rnd.choice(TRI)
    return t1, t2

PAT_CODES = {"SAS":"S","SSS":"E","ASA":"A","AAS":"H"}

print("=" * 65)
print("  GEME GO — Generalization: train SAS+SSS, test ASA emergence")
print("=" * 65)

e = GEME(axioms=[], memory_cap=8, merge_thresh=0.75)
stream_log = []
generalization_test = False

# Phase 1: Train only SAS + SSS (no ASA, no AAS)
print("\n  Phase 1: Training SAS+SSS (1000 steps)")
print("  " + "-" * 60)
for step_i in range(1000):
    t1,t2 = gen_triple()
    pat = _rnd.choice(["SAS","SSS"])
    f = make_step(t1,t2,pat)
    r = e.process(f)
    
    # Log every 50th step
    if step_i % 50 == 0:
        from gira.phase6.geme_go import formula_source
        src_s = formula_source(f)[:55].replace("\n","")
        print(f"    step {step_i:4d} | {PAT_CODES[pat]} | mem={r['mem']} stress={r['stress']:.3f} | {src_s}...")

# Now check: has ASA emerged on its own?
print("\n  Phase 2: Generalization check — feed ASA")
print("  " + "-" * 60)
asa_appeared = False
for step_i in range(1000, 1100):
    t1,t2 = gen_triple()
    pat = "ASA"  # NEVER seen before!
    f = make_step(t1,t2,pat)
    r = e.process(f)
    
    if step_i % 20 == 0 or not asa_appeared:
        from gira.phase6.geme_go import formula_source
        src_s = formula_source(f)[:55].replace("\n","")
        # Check if ASA frame is in memory with high weight
        asa_w = 0
        for ff in e.memory.frames:
            if "∠" in ff.src and ff.weight > asa_w: asa_w = ff.weight
        status = "GENERALIZED!" if asa_w >= sorted([ff.weight for ff in e.memory.frames])[len(e.memory.frames)//2] else "learning..."
        if asa_w >= sorted([ff.weight for ff in e.memory.frames])[len(e.memory.frames)//2]:
            asa_appeared = True
        print(f"    step {step_i:4d} | ASA | mem={r['mem']} stress={r['stress']:.3f} asa_w={asa_w:.1f} [{status}]")

# Final memory
print("\n  Final memory state after generalization test:")
med = sorted(f.weight for f in e.memory.frames)[len(e.memory.frames)//2] if e.memory.frames else 0
for i,f in enumerate(sorted(e.memory.frames, key=lambda x:x.weight, reverse=True)):
    src_s = f.src[:60].replace("\n","")
    # Categorize: count seg vs angle elements
    has_seg = src_s.count("≡")
    has_ang = src_s.count("∠")
    if has_seg >= 3 and has_ang == 0: pat_type = "SSS"
    elif has_seg >= 2 and has_ang >= 1: pat_type = "SAS/ASA"
    elif has_ang >= 2: pat_type = "ANGLE-HEAVY"
    else: pat_type = "OTHER"
    em = "E" if f.weight >= med else " "
    print(f"  [{i}] [{em}] w={f.weight:6.1f} [{pat_type:10}] {src_s}...")

print(f"\n  Generalization: ASA={'YES (emerged)' if asa_appeared else 'NO (not emerged)'}")
print("=" * 65)

# Phase 3: Full generalization — test all pattern types
print("\n  Full pattern sweep (20 steps each):")
for pat in ["SAS","SSS","ASA","AAS"]:
    e2 = GEME(axioms=[], memory_cap=8, merge_thresh=0.75)
    # Train only SAS+SSS (like the main experiment)
    for _ in range(800):
        t1,t2 = gen_triple()
        e2.process(make_step(t1,t2,_rnd.choice(["SAS","SSS"])))
    # Now feed 20 test steps
    before = sorted(f.weight for f in e2.memory.frames)[len(e2.memory.frames)//2] if e2.memory.frames else 0
    for _ in range(20):
        t1,t2 = gen_triple()
        e2.process(make_step(t1,t2,pat))
    after = sorted(f.weight for f in e2.memory.frames)[len(e2.memory.frames)//2] if e2.memory.frames else 0
    # Check if this pattern has a high-weight frame
    max_w = max(f.weight for f in e2.memory.frames) if e2.memory.frames else 0
    med2 = sorted(f.weight for f in e2.memory.frames)[len(e2.memory.frames)//2] if e2.memory.frames else 0
    emerged = "EMERGED" if max_w >= med2 * 1.5 else "-"
    print(f"    {pat:4} | med={med2:.0f} max_w={max_w:.0f} | {emerged}")

print("\n" + "=" * 65)
print("  DONE")
print("=" * 65)
