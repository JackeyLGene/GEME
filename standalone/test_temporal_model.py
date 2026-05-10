# Comprehensive test of temporal GEME
# Single-file test: closure detection across many seeds
import sys, os, random, statistics, math
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

def run_trial(seed, noise_level=0.0):
    r = random.Random(seed)
    pts = ["A","B","C","D","E","F","G","H"]
    
    g0 = GEME_T(memory_cap=12, merge_thresh=0.001, cooccur_window=20, cooccur_thresh=0.08, max_chains=5, time_window_size=5)
    g1 = GEME_T(memory_cap=16, cooccur_window=30, cooccur_thresh=0.1, max_chains=10, time_window_size=10)
    g2 = GEME_T(memory_cap=16, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=8)
    for g in [g0,g1,g2]: g.memory._chain_cooccur_thresh = 2
    
    closed_count = 0
    for epoch in range(30):
        r.shuffle(pts)
        for i in range(0, len(pts)-2, 2):
            a,b,c = pts[i], pts[i+1], pts[i+2]
            # Closed triangle
            for p in [a,b,c]: g0.process_sig(eq(fn("pt",const(p)),const("y")),f"p{p}")
            g1.process_sig(eq(fn("s",const(f"{a}{b}")),const("y")),f"s{a}{b}")
            g1.process_sig(eq(fn("s",const(f"{b}{c}")),const("y")),f"s{b}{c}")
            g1.process_sig(eq(fn("s",const(f"{c}{a}")),const("y")),f"s{c}{a}")
            closed_count += 1
            
            # Noise: occasionally add random segments
            if noise_level > 0 and r.random() < noise_level:
                x = r.choice(pts); y = r.choice(pts)
                g1.process_sig(eq(fn("s",const(f"{x}{y}")),const("y")),f"s{x}{y}")
            
            for _ in range(3):
                l1s = list(set(f.sig_full or f.sig for f in g1.memory.frames if f.weight>2))
                g2.observe_ext(l1s,"L1")
                g2.process_sig(eq(fn("v",const("c")),const("y")),"v_closed")
            
            # Open chain (2 segs, no closure)
            a,b,c = pts[(i+1)%8], pts[(i+2)%8], pts[(i+3)%8]
            for p in [a,b,c]: g0.process_sig(eq(fn("pt",const(p)),const("y")),f"p{p}")
            g1.process_sig(eq(fn("s",const(f"{a}{b}")),const("y")),f"s{a}{b}")
            g1.process_sig(eq(fn("s",const(f"{b}{c}")),const("y")),f"s{b}{c}")
            for _ in range(2):
                l1s = list(set(f.sig_full or f.sig for f in g1.memory.frames if f.weight>2))
                g2.observe_ext(l1s,"L1")
                g2.process_sig(eq(fn("v",const("o")),const("y")),"v_open")
    
    # Metrics
    l2_frames = g2.memory.frames
    closure_detected = any("closed" in (f.sig_full or f.sig) for f in l2_frames)
    open_ignored = not any("open" in (f.sig_full or f.sig) for f in l2_frames)
    l1_ref = len([f for f in l2_frames if "L1_" in (f.sig_full or f.sig)])
    l2_chains = len([f for f in l2_frames if "══" in (f.sig_full or f.sig)])
    
    return {
        "closure": closure_detected,
        "open_ignored": open_ignored,
        "l1_ref": l1_ref,
        "chains": l2_chains,
        "frames": len(l2_frames)
    }

print("=== TEMPORAL MODEL COMPREHENSIVE TEST ===")
print()

# Test 1: Clean data, 20 seeds
print("Test 1: Clean closure detection (20 seeds)...")
results = [run_trial(s, 0.0) for s in range(42, 62)]
clo = sum(1 for r in results if r["closure"])
opi = sum(1 for r in results if r["open_ignored"])
l1 = statistics.mean(r["l1_ref"] for r in results)
ch = statistics.mean(r["chains"] for r in results)
fr = statistics.mean(r["frames"] for r in results)
print(f"  Closure detected: {clo}/20")
print(f"  Open NOT framed: {opi}/20")
print(f"  Avg L2 frames: {fr:.0f}, L1 refs: {l1:.1f}, chains: {ch:.1f}")

# Test 2: Noise robustness (5 seeds each noise level)
print(f"\nTest 2: Noise robustness...")
for noise in [0.1, 0.2, 0.3]:
    r_noise = [run_trial(s, noise) for s in range(72, 77)]
    cl = sum(1 for r in r_noise if r["closure"])
    print(f"  Noise {noise*100:.0f}%: closure={cl}/5")

# Test 3: Non-temporal comparison (no time_window_size)
print(f"\nTest 3: Non-temporal baseline (no time windows)...")
def run_nontemporal(seed):
    r = random.Random(seed)
    g = GEME(memory_cap=16, cooccur_window=50, cooccur_thresh=0.1)
    pts = ["A","B","C","D","E","F"]
    for epoch in range(30):
        r.shuffle(pts)
        for i in range(len(pts)-2):
            a,b,c = pts[i], pts[i+1], pts[i+2]
            if r.random() < 0.5:
                g.process_sig(eq(fn("triangle",const("closed")),const("y")), "tri_closed")
            else:
                g.process_sig(eq(fn("triangle",const("open")),const("y")), "tri_open")
    has = any("closed" in (f.sig_full or f.sig) for f in g.memory.frames)
    return has

nt = [run_nontemporal(s) for s in range(42, 52)]
print(f"  Closure detected: {sum(1 for r in nt if r)}/10")

binom = lambda n,t: sum(math.comb(t,k)*0.5**t for k in range(n,t+1))
p_clo = binom(clo, 20)
p_nt = binom(sum(1 for r in nt if r), 10)

print(f"\n{'='*55}")
print(f"TEMPORAL MODEL VERIFICATION:")
print(f"  Temporal closure: {clo}/20 (p~{p_clo:.2e})")
print(f"  Non-temporal: {sum(1 for r in nt if r)}/10 (p~{p_nt:.2f})")
if p_clo < 0.001:
    print("*** TEMPORAL MODEL PASSED ***")
    print("Closure detection is statistically significant")
