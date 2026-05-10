# Time as a vector dimension: not a counter, part of the data
# Each input gets a 28-dim vector: 27 data + 1 time
# Same time → same vector in time dim → merge
# Different time → different vector → separate
# Wall = temporal resolution limit
import sys, math
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM

# GEME uses 27-dimensional vectors. 
# We extend: time is embedded in the vector itself.
# All data inputs use the same 27-dim vector; only time dimension differs.

data_vec = [0.0] * _VEC_DIM  # neutral data vector

def time_vec(t, time_scale=1.0):
    """Create a vector with time embedded as a monotonic dimension.
    t: time position. time_scale: resolution.
    v[0] = t/(t+1) — monotonic, bounded [0,1), increases with time."""
    v = data_vec[:]
    v[0] = (t * time_scale) / (t * time_scale + 1)  # [0,1), monotonic
    return v

# Test: two signals at varying time distances
# Show how L2 distance grows with time distance

import random
r = random.Random(42)

print("="*55)
print("时间作为向量维度")
print("="*55)
print()
print("时间距离 vs 向量距离（单调编码，v[0]=t/(t+1)）：")
for dt in [0, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0]:
    v1 = time_vec(0)
    v2 = time_vec(dt)
    d = math.sqrt(sum((v1[i]-v2[i])**2 for i in range(_VEC_DIM)))
    print(f"  dt={dt:5.1f} → 向量距离={d:.4f}")
print()

# Now: feed periodic signals at different frequencies
# High freq (short time gap) → same time vec → merge
# Low freq (long time gap) → different time vec → separate → wall

g = GEME(memory_cap=16, merge_thresh=0.01, cooccur_window=80, cooccur_thresh=0.08, max_chains=10)
g.memory.preserve_sig = True

# Merge threshold: 0.2 means time diff < ~0.15 merge, > 0.2 separate
g.memory._merge_thresh_val = 0.2
g._induction_threshold = 2.0

# Three signals at different frequencies (TIME resolution: scale=5.0)
# A: period 0.05 (very fast, every 0.05 time units) → dt~0 → merge
# B: period 0.25 (medium)
# C: period 2.0 (slow) → dt~0.67 → separate → temporal wall

print("输入流（时间尺度=5.0, 合并阈值=0.2）:")
print("  A: 周期 0.05 (超高频) → dt~0 → 总是合并")
print("  B: 周期 0.25 (中频)")
print("  C: 周期 2.0 (低频) → dt~0.67 → 不合并 → 时间壁")
print()

t = 0.0
tA = tB = tC = 0.0
for _ in range(10000):
    t += 0.01
    
    if t - tA >= 0.05:
        g.process_vec(time_vec(t, 5.0), "sig_A")
        tA = t
    if t - tB >= 0.25:
        g.process_vec(time_vec(t, 5.0), "sig_B")
        tB = t
    if t - tC >= 2.0:
        g.process_vec(time_vec(t, 5.0), "sig_C")
        tC = t

print("【训练完成】")
for f in sorted(g.memory.frames, key=lambda x: x.weight, reverse=True):
    sig = f.sig_full or f.sig
    t = "A" if "sig_A" in sig else ("B" if "sig_B" in sig else ("C" if "sig_C" in sig else "?"))
    print(f"  {t}: w={int(f.weight):4d} {sig[:45]}")

a_w = sum(f.weight for f in g.memory.frames if "sig_A" in (f.sig_full or f.sig))
b_w = sum(f.weight for f in g.memory.frames if "sig_B" in (f.sig_full or f.sig))
c_w = sum(f.weight for f in g.memory.frames if "sig_C" in (f.sig_full or f.sig))
a_f = sum(1 for f in g.memory.frames if "sig_A" in (f.sig_full or f.sig))
b_f = sum(1 for f in g.memory.frames if "sig_B" in (f.sig_full or f.sig))
c_f = sum(1 for f in g.memory.frames if "sig_C" in (f.sig_full or f.sig))

print(f"\n【时间壁】")
print(f"  A(周期0.1): {a_f}帧, 权重={a_w:.0f} {'✓' if a_f>0 and a_w>50 else '✗'}")
print(f"  B(周期0.5): {b_f}帧, 权重={b_w:.0f} {'✓' if b_f>0 and b_w>50 else '✗'}")
print(f"  C(周期3.0): {c_f}帧, 权重={c_w:.0f} {'✓' if c_f>0 and c_w>50 else '✗'}")
if c_f == 0 or c_w < 50:
    print("  C被时间壁阻挡——周期过长，时间距离超过分辨率")
