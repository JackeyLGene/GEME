# GEME learns "greater than": appearance + meaning → temporal concept
# L1a (appearance): receives visual numeral "7" "6" "5" etc.
# L1b (meaning): receives "7>6 TRUE" "6>7 FALSE" etc.
# L2: observes both over time → 7 correlates with TRUE, 6 with FALSE
import sys, os, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

class GEME_T(GEME):
    def observe_ext(self, sigs, src="e"):
        ft = self.memory._step_counter
        for sig in sigs:
            sid = f"{src}_{sig[:18]}"
            self.memory._window.append((sid, ft, (0.0,)*_VEC_DIM))
            if len(self.memory._window) > self.memory._win_max:
                self.memory._window.pop(0)

r = random.Random(42)

# Each numeral: unique one-hot vector + unique formula signature
num_idx = {str(i): i-1 for i in range(1, 11)}
def num_vec(n):
    v = [0.0]*_VEC_DIM
    v[num_idx[n] % _VEC_DIM] = 1.0
    return v

gt_pairs = [(7,6),(8,5),(9,4),(10,3),(8,7),(9,6),(10,5),(6,5),(9,8),(10,9)]

print("=== GEME LEARNS 'GREATER THAN' ===")
print()

# L1a (appearance) and L1b (meaning) in parallel
g1a = GEME_T(memory_cap=32, cooccur_window=20, cooccur_thresh=0.08, max_chains=5, time_window_size=5)
g1b = GEME_T(memory_cap=32, cooccur_window=20, cooccur_thresh=0.08, max_chains=5, time_window_size=5)
# L2 observes both
g2 = GEME_T(memory_cap=16, cooccur_window=50, cooccur_thresh=0.08, max_chains=10, time_window_size=15)
for g in [g1a,g1b,g2]: g.memory._chain_cooccur_thresh = 2

for epoch in range(60):
    r.shuffle(gt_pairs)
    for larger, smaller in gt_pairs:
        bl = str(larger); bs = str(smaller)
        
        # Feed appearance to L1a (process_vec with unique vectors)
        g1a.process_vec(num_vec(bl), f"vis_{bl}")
        g1a.process_vec(num_vec(bs), f"vis_{bs}")
        
        # Feed meaning to L1b: process_vec with unique vectors per proposition
        for prop_n, (a, b, tv) in enumerate([(bl, bs, "T"), (bs, bl, "F")]):
            v = [0.0]*_VEC_DIM
            v[(ord(a[0]) + ord(b[0]) + prop_n) % _VEC_DIM] = 1.0
            g1b.process_vec(v, f"gt_{a}_{b}_{tv}")
        
        # L2 processes observed L1 frames with unique vectors
        for fi, f in enumerate(g1a.memory.frames):
            s = f.sig_full or f.sig
            v = [0.0]*_VEC_DIM
            v[(fi * 7 + epoch) % _VEC_DIM] = 1.0
            g2.process_vec(v, f"A_{s[:20]}")
        for fi, f in enumerate(g1b.memory.frames):
            s = f.sig_full or f.sig
            v = [0.0]*_VEC_DIM
            v[(fi * 7 + epoch + 3) % _VEC_DIM] = 1.0
            g2.process_vec(v, f"B_{s[:20]}")

print(f"L1a (appearance): {len(g1a.memory.frames)} frames, "
      f"{len([f for f in g1a.memory.frames if '══' in (f.sig_full or f.sig)])} chains")
print(f"L1b (meaning): {len(g1b.memory.frames)} frames, "
      f"{len([f for f in g1b.memory.frames if '══' in (f.sig_full or f.sig)])} chains")
print(f"L2 (concept): {len(g2.memory.frames)} frames, "
      f"{len([f for f in g2.memory.frames if '══' in (f.sig_full or f.sig)])} chains")

print(f"\nL2 top frames (the concept of 'greater'):")
for f in sorted(g2.memory.frames, key=lambda x: x.weight, reverse=True)[:10]:
    sig = f.sig_full or f.sig
    t = "C" if "══" in sig else ("A" if "──" in sig else "F")
    ext = ""
    if "A_" in sig: ext += " [APPEARANCE]"
    if "B_" in sig: ext += " [MEANING]"
    print(f"  [{t}] w={int(f.weight):5d} {sig[:55]}{ext}")

# Check: does L2 link appearance with meaning?
a_frames = [f for f in g2.memory.frames if "A_" in (f.sig_full or f.sig)]
b_frames = [f for f in g2.memory.frames if "B_" in (f.sig_full or f.sig)]
ab_bridge = [f for f in g2.memory.frames if "A_" in (f.sig_full or f.sig) and "B_" in (f.sig_full or f.sig)]

print(f"\nL2 references appearance: {len(a_frames)}")
print(f"L2 references meaning: {len(b_frames)}")
print(f"L2 bridges A+B: {len(ab_bridge)}")
if ab_bridge:
    print("YES: GEME learned 'greater' by temporal co-occurrence")
    print("7's appearance + TRUE meaning → temporal frame → concept of '>'")
else:
    print("Bridge not yet formed. Need longer training.")
