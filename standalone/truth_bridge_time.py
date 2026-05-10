# Truth bridge with time windows: 'equals' and '=' co-exist in time
# English events and Math events interleaved, self-observation between
import sys, os, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, eq, fn, const, structural_signature

r = random.Random(42)
print("=== TRUTH BRIDGE IN TIME ===")
print("English 'equals' + Math '=' → self-observation creates temporal chain")
print()

# Each event = 50 inputs, then consolidate + self-observe
g = GEME(memory_cap=16, cooccur_window=80, cooccur_thresh=0.08, max_chains=10,
         time_window_size=50)
g.memory._chain_cooccur_thresh = 2

# Interleave English events and Math events
# T1: English "one and two equals three" (true) / "one and two equals four" (false)
# T2: Math "1+2=3" (true) / "1+2=4" (false)

nums_en = ["one","two","three","four","five"]
num_v = {"one":1,"two":2,"three":3,"four":4,"five":5}

for cycle in range(8):
    # English event: ~50 inputs
    for _ in range(25):
        x = r.choice(nums_en); y = r.choice(nums_en)
        z = num_v[x] + num_v[y]
        zs = [k for k,v in num_v.items() if v==z][0] if z<=5 else nums_en[-1]
        is_true = r.random() < 0.5
        if not is_true: zs = nums_en[(z+2)%5]
        tv = "t" if is_true else "f"
        f = eq(fn(tv, fn("eng", fn("x",const(x)), fn("eq_op",const("equals")),
                              fn("y",const(y)), fn("res",const(zs)))), const("yes"))
        g.process_sig(f, structural_signature(f))
    
    # Math event: ~50 inputs (triggers consolidation at 50)
    for _ in range(25):
        x = r.randint(1,5); y = r.randint(1,5)
        z = x + y
        is_true = r.random() < 0.5
        if not is_true: z += 1 if z < 9 else -1
        tv = "t" if is_true else "f"
        f = eq(fn(tv, fn("mth", fn("x",const(str(x))), fn("eq_op",const("=")),
                              fn("y",const(str(y))), fn("res",const(str(z))))), const("yes"))
        g.process_sig(f, structural_signature(f))

print(f"Cycles completed: {cycle+1}")
print(f"Total frames: {len(g.memory.frames)}")
assocs = [f for f in g.memory.frames if "──" in (f.sig_full or f.sig)]
chains = [f for f in g.memory.frames if "══" in (f.sig_full or f.sig)]
print(f"Associations: {len(assocs)}, Chains: {len(chains)}")
print(f"Self-observation count: {g.memory._self_observe_count}")

if chains:
    print(f"\nChains formed ({len(chains)}):")
    # Build fid->sig look-up
    fid_to_sig = {f.fid: (f.sig_full or f.sig) for f in g.memory.frames}
    for c in sorted(chains, key=lambda x: x.weight, reverse=True):
        sig = c.sig_full or c.sig
        # Extract fids from chain signature
        parts = sig.split("══")
        eng_mth = []
        for p in parts:
            if p.startswith("f") and p[1:].isdigit():
                fid = int(p[1:])
                frame_sig = fid_to_sig.get(fid, "?")
                if "eng" in frame_sig:
                    eng_mth.append("ENG")
                elif "mth" in frame_sig:
                    eng_mth.append("MTH")
                else:
                    eng_mth.append("??")
        bridge = "[ENG-MATH BRIDGE]" if "ENG" in eng_mth and "MTH" in eng_mth else ""
        print(f"  w={int(c.weight):4d} {sig[:55]} {'|'.join(eng_mth):12s} {bridge}")
    
    bridge_chains = sum(1 for c in chains if ("eng" in c.sig and "mth" in c.sig))
    print(f"\nEng-Math bridge chains: {bridge_chains}/{len(chains)}")
    if bridge_chains > 0:
        print("YES: 'equals' and '=' co-exist in time → temporal equivalence")
        print("The child discovered they are the same function")
        print("Not by structural position — by temporal co-presence in memory")
else:
    print("\nNo chains. Current frames:")
    for f in sorted(g.memory.frames, key=lambda x: x.weight, reverse=True)[:8]:
        sig = f.sig_full or f.sig
        t = "ASSOC" if "──" in sig else "FRAME"
        print(f"  [{t}] fid={f.fid} w={int(f.weight):4d} {sig[:40]}")
