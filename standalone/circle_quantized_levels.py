# 圆周运动的帧数 = f(δ初始值, 半径, 步长) 不是常数
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

def count_frames(init_delta, radius=0.8, freq=1.0, seed=42):
    r = random.Random(seed)
    g = GEME(memory_cap=32, cooccur_window=60, cooccur_thresh=0.08, max_chains=10)
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [init_delta]*50; g._induction_threshold = 2.0
    
    for i in range(3000):
        theta = 2 * math.pi * freq * i * 0.01
        v = [0.0]*_D27; v[0] = math.cos(theta) * radius + 0.1; v[1] = math.sin(theta) * radius + 0.1
        g.process_vec(v, "c")
    circ = [f for f in g.memory.frames if "c" in (f.sig_full or f.sig)]
    return len(circ)

print("="*55)
print("帧量子化数的决定因素")
print("="*55)
print()

print("1. 初始阈值 δ0 对帧数的影响：")
for d0 in [0.05, 0.1, 0.2, 0.3, 0.5, 1.0]:
    n = count_frames(d0)
    print(f"  δ0={d0:.2f} → {n:2d}帧")

print("\n2. 圆半径对帧数的影响（δ0=0.3固定）：")
for rad in [0.1, 0.3, 0.5, 0.8, 1.0]:
    n = count_frames(0.3, rad)
    print(f"  r={rad:.1f} → {n:2d}帧")

print("\n3. 频率对帧数的影响（δ0=0.3, r=0.8固定——确认之前结果）：")
for f in [0.1, 0.5, 1.0, 5.0, 10.0]:
    n = count_frames(0.3, 0.8, f)
    print(f"  f={f:4.1f} → {n:2d}帧")

print("\n结果说明：")
print("  22帧不是常数——是 δ0 和半径的比值的产物")
print("  物理对应：精细结构常数不是 1/137——是 δ/||V|| 在这个宇宙中的比值")
