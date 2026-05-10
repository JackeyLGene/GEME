"""Direct chain test: feed pairs that share elements.
If GEME can form chains, this will show them."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature

g = GEME(memory_cap=16, cooccur_window=60, cooccur_thresh=0.1, max_chains=10)

# Feed two PAIRS that share "V":
# Pair 1: N──V (noun followed by verb)
# Pair 2: V──N (verb followed by noun)
# If they share V, GEME should form chain: N──V══V──N

print("=== DIRECT CHAIN TEST ===")
print("Feeding pairs: N-V and V-N (share 'V')")
for _ in range(100):
    g.process_sig(eq(fn("rule", const("NV")), const("yes")), "rule_N_V")
    g.process_sig(eq(fn("rule", const("VN")), const("yes")), "rule_V_N")
    # Also feed their combination
    g.process_sig(eq(fn("combo", const("NV"), const("VN")), const("yes")), "combo_NV_VN")

print(f"Frames: {len(g.memory.frames)}")
assocs = [f for f in g.memory.frames if "──" in f.sig]
chains = [f for f in g.memory.frames if "══" in f.sig]
print(f"Associations: {len(assocs)}")
print(f"Chains: {len(chains)}")

for f in sorted(g.memory.frames, key=lambda x: x.weight, reverse=True)[:5]:
    sig = f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
    t = "CHAIN" if "══" in sig else ("ASSOC" if "──" in sig else "FRAME")
    print(f"  [{t}] w={int(f.weight)} {sig[:50]}")

print(f"\n{'='*55}")
print(f"Chain count: {chains}")
