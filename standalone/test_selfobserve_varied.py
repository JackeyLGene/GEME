# Self-observation with varied inputs → distinct association frames → chains
import sys, os, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

g = GEME(memory_cap=16, cooccur_window=60, cooccur_thresh=0.1, max_chains=10)
g.memory._chain_cooccur_thresh = 2

r = random.Random(42)

# Feed 3 distinct formula types to create 3 distinct association types
print("=== VARIED INPUT → ASSOCIATIONS → CHAINS ===")
for _ in range(800):
    a, b = str(r.randint(1,9)), str(r.randint(1,9))
    f = eq(fn("swap", const(a), const(b)), fn("swap", const(b), const(a)))
    g.process_sig(f, structural_signature(f))

for _ in range(800):
    a = str(r.randint(1,9))
    f = eq(fn("succ", const("s"+a)), const("s"+str(r.randint(2,9))))
    g.process_sig(f, structural_signature(f))

for _ in range(800):
    f = eq(fn("conn", const("P"), const("Q")), const("yes"))
    g.process_sig(f, structural_signature(f))

print(f"Frames: {len(g.memory.frames)}")
assocs = [f for f in g.memory.frames if "──" in (f.sig_full or f.sig)]
chains = [f for f in g.memory.frames if "══" in (f.sig_full or f.sig)]
print(f"Associations: {len(assocs)}, Chains: {len(chains)}")
print(f"Self-observation count: {g.memory._self_observe_count}")

if chains:
    print("\nChains formed (self-observation: 'I see both frames together'):")
    for c in sorted(chains, key=lambda x: x.weight, reverse=True)[:5]:
        sig = c.sig_full or c.sig
        print(f"  w={int(c.weight):4d} {sig[:60]}")
else:
    print("\nDebug: self-observed frames:")
    for f in g.memory.frames:
        sig = f.sig_full or f.sig
        if "──" in sig:
            print(f"  w={int(f.weight):3d} {sig[:40]}")
    print("\nCo-occurrence between any two distinct frames:")
    pairs = [(k,v) for k,v in g.memory._cooccur.items() if v >= 2]
    for k,v in pairs[:10]:
        print(f"  {k[0][:20]} x {k[1][:20]} = {v}")
