"""True emergence: feed premise-triples WITHOUT triangle conclusion.
System must ORGANIZE premises into theorems by co-occurrence."""
import sys,os,random
sys.path.insert(0,r'G:\GEME\src')
from gira.phase3.language import *
from gira.phase6.geme_go import GEME
from gira.phase6.proof_viewer import ProofViewer

A,B,C,D,E,F = [var(c) for c in "ABCDEF"]
OUT = r'g:\GEME\docs\go_tri'
os.makedirs(OUT,exist_ok=True)

# Premise pool: individual edge/angle equalities
PREMS = {
    "S1": eq(fn("seg",A,B),fn("seg",D,E)),
    "S2": eq(fn("seg",B,C),fn("seg",E,F)),
    "S3": eq(fn("seg",C,A),fn("seg",F,D)),
    "A1": eq(fn("angle",A),fn("angle",D)),
    "A2": eq(fn("angle",B),fn("angle",E)),
    "A3": eq(fn("angle",C),fn("angle",F)),
}

# Valid triples: SSS, SAS, ASA, AAS
VALID = [
    ("SSS", ["S1","S2","S3"]),
    ("SAS", ["S1","A1","S3"]),
    ("ASA", ["A1","S1","A2"]),
    ("AAS", ["A1","A2","S3"]),
]

_rnd = random.Random()

def gen_triple(valid_ratio=0.4):
    """Generate a conjunction of 3 premises. No triangle conclusion."""
    if _rnd.random() < valid_ratio:
        name,keys = _rnd.choice(VALID)
        prems = [PREMS[k] for k in keys]
    else:
        keys = _rnd.sample(list(PREMS.keys()),3)
        prems = [PREMS[k] for k in keys]
    # Return a conjunction of 3 premises (NO implication)
    if len(prems) >= 3:
        return conj(conj(prems[0],prems[1]),prems[2])
    return conj(prems[0],prems[1])

for exp_idx,(label,cap,rounds,noise) in enumerate([
    ("E1: SSS-heavy",8,30,0.5),
    ("E2: standard",10,30,0.4),
    ("E3: high noise",8,30,0.2),
    ("E4: large mem",12,30,0.5),
]):
    e = GEME(axioms=[],memory_cap=cap,merge_thresh=0.75)
    v = ProofViewer(e)
    total=0
    for rnd in range(rounds):
        for _ in range(20):
            f = gen_triple(noise)
            e.process(f)
            total+=1
    cr = total/max(len(e.memory.frames),1)
    
    path = v.save_run(OUT)
    print(f"\n  {label}")
    print(f"    input: {total}  output: {len(e.memory.frames)}  comp: {cr:.0f}:1")
    for i,f in enumerate(sorted(e.memory.frames,key=lambda x:x.weight,reverse=True)):
        # Show which premises compose this frame
        src_short = f.src[:60].replace("\n","")
        print(f"    [{i}] w={f.weight:.1f}  {src_short}...")
    print(f"    -> {os.path.basename(path)}")

print("\n  SSS discovery check:")
print("  If (S1∧S2∧S3) or (S1∧A1∧S3) etc. appear as top frames -> emergence real")
