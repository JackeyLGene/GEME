# L3对称测试：GEME能否从自观察中恢复圆的结构？
# L1直接看圆 → L2看L1 → L3看L2 → L3是否恢复圆的帧结构？
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

# 三层
l1 = GEME(memory_cap=32, cooccur_window=40, cooccur_thresh=0.08, max_chains=10)
l2 = GEME(memory_cap=32, cooccur_window=40, cooccur_thresh=0.08, max_chains=10)
l3 = GEME(memory_cap=32, cooccur_window=40, cooccur_thresh=0.08, max_chains=10)
for g in [l1,l2,l3]:
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 2.0

# 运行
for i in range(3000):
    t = i * 0.01
    # L1: 圆输入
    v1 = [0.0]*_D27; v1[0] = math.cos(2*math.pi*t); v1[1] = math.sin(2*math.pi*t)
    l1.process_vec(v1, "c")
    
    # L2: 每20步观察一次L1的帧经济
    if i % 20 == 0:
        v2 = [0.0]*_D27
        frames = l1.memory.frames
        for j, f in enumerate(frames[:min(len(frames), _D27)]):
            v2[j] = f.weight / (sum(f.weight for f in frames) or 1)
        l2.process_vec(v2, f"l1_{i}")
    
    # L3: 每40步观察一次L2的帧经济
    if i % 40 == 0:
        v3 = [0.0]*_D27
        frames = l2.memory.frames
        for j, f in enumerate(frames[:min(len(frames), _D27)]):
            v3[j] = f.weight / (sum(f.weight for f in frames) or 1)
        l3.process_vec(v3, f"l2_{i}")

print("="*55)
print("L3对称测试")
print("="*55)
print()

for name, g in [("L1(直接看圆)", l1), ("L2(看L1)", l2), ("L3(看L2)", l3)]:
    frames = g.memory.frames
    n = len(frames)
    # 统计帧分布
    sigs = [(f.sig_full or f.sig)[:35] for f in sorted(frames, key=lambda x: x.weight, reverse=True)[:5]]
    print(f"{name}: {n}帧")
    for f in sorted(frames, key=lambda x: x.weight, reverse=True)[:4]:
        w = int(f.weight); s = (f.sig_full or f.sig)[:40]
        print(f"  w={w:4d} {s}")

# 检验：L3是否恢复了类似L1的帧结构
l3_frames = l3.memory.frames
n_l3 = len(l3_frames)
if n_l3 >= 10:
    print(f"\nL3有{n_l3}帧 → 自观察保留了帧经济结构")
else:
    print(f"\nL3仅{n_l3}帧 → 结构在层级中降解")
