# L3对称 v2：相位锁定采样，整周期观察
import sys, math, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

l1 = GEME(memory_cap=32, cooccur_window=40, cooccur_thresh=0.08, max_chains=10)
l2 = GEME(memory_cap=32, cooccur_window=40, cooccur_thresh=0.08, max_chains=10)
l3 = GEME(memory_cap=32, cooccur_window=40, cooccur_thresh=0.08, max_chains=10)
for g in [l1,l2,l3]:
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 2.0

period = 100  # 整周期 = 100步（一圈）

for i in range(5000):
    t = i * 0.01
    v = [0.0]*_D27; v[0] = math.cos(2*math.pi*t); v[1] = math.sin(2*math.pi*t)
    l1.process_vec(v, "c")
    
    # 相位锁定：每整一圈观察L1
    if i % period == 0:
        v2 = [0.0]*_D27
        fl1 = l1.memory.frames
        for j, f in enumerate(fl1[:min(len(fl1), _D27)]):
            v2[j] = f.weight / (sum(f.weight for f in fl1) or 1)
        l2.process_vec(v2, "c")  # 注意：用"c"不用"l1_XXX"→签名一致→可合并
    
    # 每整2圈观察L2
    if i % (period * 2) == 0:
        v3 = [0.0]*_D27
        fl2 = l2.memory.frames
        for j, f in enumerate(fl2[:min(len(fl2), _D27)]):
            v3[j] = f.weight / (sum(f.weight for f in fl2) or 1)
        l3.process_vec(v3, "c")  # 同样用"c"→可合并

print("="*55)
print("L3对称 v2（相位锁定采样）")
print("="*55)
for name, g in [("L1(圆)", l1), ("L2(每圈看L1)", l2), ("L3(每2圈看L2)", l3)]:
    frames = g.memory.frames
    c_frames = [f for f in frames if "c" in (f.sig_full or f.sig)]
    print(f"\n{name}: {len(frames)}总帧, {len(c_frames)}圆帧")
    # 检查c帧权重分布
    if c_frames:
        top = sorted(c_frames, key=lambda x: x.weight, reverse=True)[:4]
        for f in top:
            w = int(f.weight); s = (f.sig_full or f.sig)[:40]
            print(f"  w={w:4d} {s}")

# 是否L3恢复了类似L1的圆形结构？
l3c = [f for f in l3.memory.frames if "c" in (f.sig_full or f.sig)]
l1c = [f for f in l1.memory.frames if "c" in (f.sig_full or f.sig)]
print(f"\n总结：")
print(f"  L1圆帧: {len(l1c)}个")
print(f"  L2圆帧: {len([...])}个")
print(f"  L3圆帧: {len(l3c)}个")
if len(l3c) >= len(l1c) * 0.5:
    print(f"  ✓ 圆结构在L3中恢复（层间对称性存在）")
else:
    print(f"  - 结构在层级中部分降解")
