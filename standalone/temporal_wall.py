# The temporal wall: same input, different frequency → wall in time
# Signal A at high frequency (every 2-3 steps) → GEME forms frame
# Signal B at low frequency (every 50 steps) → GEME can't form stable frame
# Wall = the frequency boundary where the system can no longer track
import sys, os, random, math
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

r = random.Random(42)
_vec_r = random.Random(99)

def rand_vec():
    v = [0.0]*_VEC_DIM; v[_vec_r.randint(0, _VEC_DIM-1)] = 1.0; return v

# One signal: A (frequent)    A_A_A_A_A_A_A_A_A_A_A_A_A_A_A...
# Another signal: B (rare)    B_____________B_____________B...
# Third: C (intermediate)

g = GEME(memory_cap=32, cooccur_window=60, cooccur_thresh=0.08, max_chains=15)
g.memory._chain_cooccur_thresh = 2
g.memory._merge_thresh_val = 0.5
g.memory.preserve_sig = True

print("="*55)
print("时间壁实验")
print("="*55)
print("信号A: 每2-3步出现一次（高频）")
print("信号B: 每12-18步出现一次（中频）")
print("信号C: 每40-60步出现一次（低频）")
print("信号D: 每80-120步出现一次（极低频）")
print("壁 = 系统在时间中能跟踪的频率上限")
print()

va = rand_vec(); vb = rand_vec(); vc = rand_vec(); vd = rand_vec()

step_a = step_b = step_c = step_d = 0
freq_a = r.randint(2,3)
freq_b = r.randint(12,18)
freq_c = r.randint(40,60)
freq_d = r.randint(80,120)

for step in range(2000):
    step_a += 1; step_b += 1; step_c += 1; step_d += 1
    
    if step_a >= freq_a:
        g.process_vec(va, "sig_A")
        step_a = 0; freq_a = r.randint(2,3)
    if step_b >= freq_b:
        g.process_vec(vb, "sig_B")
        step_b = 0; freq_b = r.randint(12,18)
    if step_c >= freq_c:
        g.process_vec(vc, "sig_C")
        step_c = 0; freq_c = r.randint(40,60)
    if step_d >= freq_d:
        g.process_vec(vd, "sig_D")
        step_d = 0; freq_d = r.randint(80,120)

frames = g.memory.frames
print("【帧分析】")
for f in sorted(frames, key=lambda x: x.weight, reverse=True):
    sig = f.sig_full or f.sig
    t = "A" if "sig_A" in sig else ("B" if "sig_B" in sig else ("C" if "sig_C" in sig else ("D" if "sig_D" in sig else "?")))
    print(f"  sig_{t}: w={int(f.weight):4d}, {sig[:45]}")

# The wall: which signals formed stable frames?
print(f"\n【时间壁分析】")
for name, sig_marker in [("A(高频 2-3步)", "sig_A"),
                           ("B(中频 12-18步)", "sig_B"),
                           ("C(低频 40-60步)", "sig_C"),
                           ("D(极低频 80-120步)", "sig_D")]:
    f_count = sum(1 for f in frames if sig_marker in (f.sig_full or f.sig))
    weights = [int(f.weight) for f in frames if sig_marker in (f.sig_full or f.sig)]
    total_w = sum(weights)
    avg_w = total_w / max(f_count, 1)
    status = "✓ 帧稳定" if f_count > 0 and avg_w > 5 else "✗ 未形成"
    print(f"  {name}: {status} (帧数={f_count}, 平均权重={avg_w:.0f})")
    if f_count == 0 or avg_w <= 5:
        print(f"    → 壁：频率超出系统时间跟踪能力")

print(f"\n{'='*55}")
print("预期：A和B形成帧，C和D无法形成——这本身就是时间壁")
