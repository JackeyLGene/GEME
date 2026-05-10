# Three universes: different "constants" → different realities
# ℏ → VEC_DIM (spatial resolution)
# c → cooccur_window / merge_thresh (causal range)
# G → adaptive threshold slope (curvature response)
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _DEFAULT_DIM

_r = random.Random(42)

class GEME_U:
    """A universe: GEME with settable constants"""
    def __init__(self, name, dim, tau_over_delta=50, density_slope=1.5):
        self.name = name
        self.dim = dim  # "ℏ"
        self.tau_ratio = tau_over_delta  # "c"
        self.slope = density_slope  # "G"
        
        # Larger dim = finer spatial resolution = larger ℏ
        # Larger tau_ratio = faster max causal speed = larger c
        # Larger slope = stronger curvature response = larger G
        
        self.g = GEME(memory_cap=min(32, dim * 2), cooccur_window=tau_over_delta, 
                      cooccur_thresh=0.08, max_chains=10)
        self.g.memory.preserve_sig = True
        self.g.memory._chain_cooccur_thresh = 2
        self.g.memory._merge_dists = [density_slope * 0.5] * 50
        self.g.memory._merge_thresh_val = density_slope * 0.5
        self.g._induction_threshold = 2.0

    def feed(self, x, density, t):
        """Feed an input at position x with given density"""
        v = [0.0] * _DEFAULT_DIM
        v[x % self.dim] = density / (density + 1)
        self.g.process_vec(v, f"pos_{x % 20}")

    def analyze(self):
        pos_data = {}
        for f in self.g.memory.frames:
            s = f.sig_full or f.sig
            for p in range(20):
                if f"pos_{p}" in s:
                    if p not in pos_data: pos_data[p] = []
                    pos_data[p].append(f.weight)
        densities = []
        gen_rates = []
        for p, ws in pos_data.items():
            total_w = sum(ws)
            x = p * 5
            dens = 5.0 / (1 + x * 0.1)
            densities.append(dens)
            gen_rates.append(total_w / max(len(ws), 1))
        return densities, gen_rates

# Three universes with different "constants"
universes = [
    ("Classic (our universe)", _DEFAULT_DIM, 50, 1.5),
    ("Fine-grained (large h-bar)", _DEFAULT_DIM*2, 50, 1.5),
    ("Slow causal (small c)", _DEFAULT_DIM, 20, 1.5),
    ("Strong gravity (large G)", _DEFAULT_DIM, 50, 3.0),
]

print("="*55)
print("四个宇宙：不同常数→不同实在")
print("="*55)
print()

for name, dim, tau, slope in universes:
    u = GEME_U(name, dim, tau, slope)
    t = 0.0
    for _ in range(2000):
        t += 0.01
        for x in range(0, 100, 5):
            dens = 5.0 / (1 + x * 0.1)
            num = max(1, int(dens * _r.random() * 2))
            for _ in range(num):
                u.feed(x, dens, t)
    dens, rates = u.analyze()
    if dens and rates:
        high = [r for d, r in zip(dens, rates) if d > 2.0]
        low = [r for d, r in zip(dens, rates) if d < 1.0]
        if high and low:
            ratio = statistics.mean(high) / max(statistics.mean(low), 1)
            print(f"{name}:")
            print(f"  dim={dim} (ℏ), τ/δ={tau} (c), G-slope={slope}")
            print(f"  帧生成率比(高密度/低密度): {ratio:.3f}")
            print()
