# Simple self-observation chain test with known association frames
import sys, os
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

g = GEME(memory_cap=16, cooccur_window=30, cooccur_thresh=0.1, max_chains=5)
g.memory._chain_cooccur_thresh = 2

# Feed inputs that will form associations (different signatures)
# swap with different numbers creates different signatures
import random
r = random.Random(42)

# Phase 1: Feed varied inputs to create association frames
print("Phase 1: building association frames...")
for _ in range(500):
    a = r.randint(1,9)
    b = r.randint(1,9)
    f = eq(fn("swap", const(str(a)), const(str(b))),
            fn("swap", const(str(b)), const(str(a))))
    g.process_sig(f, structural_signature(f))

# Phase 2: Feed different domain to create cross-domain associations
for _ in range(300):
    a = r.randint(1,9)
    f = eq(fn("succ", const("s"+str(a))), const("s"+str(a+1)))
    g.process_sig(f, structural_signature(f))

print(f"Frames: {len(g.memory.frames)}")
assocs = [f for f in g.memory.frames if "──" in (f.sig_full or f.sig)]
chains = [f for f in g.memory.frames if "══" in (f.sig_full or f.sig)]
print(f"Associations: {len(assocs)}, Chains: {len(chains)}")
print(f"Self-observation count: {g.memory._self_observe_count}")

if chains:
    print("\nChains formed:")
    for c in sorted(chains, key=lambda x: x.weight, reverse=True)[:5]:
        sig = c.sig_full or c.sig
        print(f"  w={int(c.weight):4d} {sig[:65]}")
else:
    print("\nNo chains. Co-occurrence counts:")
    # Debug: show co-occurrence for top frame pairs
    assoc_sigs = list(set(f.sig_full or f.sig for f in assocs[:4]))
    for a1 in assoc_sigs:
        for a2 in assoc_sigs:
            if a1 < a2:
                ckey = tuple(sorted([a1, a2]))
                cc = g.memory._cooccur.get(ckey, 0)
                print(f"  {a1[:30]} x {a2[:30]} = {cc} co-occurrences")
