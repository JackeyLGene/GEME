# 高→低投影：GEME的自由能对应
# L3的意义拓扑 → L1的合并阈值调制
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, Frame, _VEC_DIM as _D27

_r = random.Random(42)

print("="*55)
print("高→低投影：GEME的自由能机制")
print("="*55)
print("原理：高层的意义帧→低层帧的预测偏差→调制合并阈值")
print()

g = GEME(memory_cap=20); g.memory.preserve_sig = True
g.memory._chain_cooccur_thresh = 2; g.memory._merge_dists = [0.3]*50
g._induction_threshold = 3.0

# 预先建立三帧代表"猫"概念
vcat=[0.0]*_D27; vcat[0]=1.0; vcat[2]=0.5  # 猫
vmat=[0.0]*_D27; vmat[2]=0.5; vmat[5]=1.0  # 垫
vmilk=[0.0]*_D27; vmilk[0]=0.5; vmilk[5]=1.0  # 奶

for _ in range(500):
    g.process_vec(vcat, "cat")
    g.process_vec(vmat, "mat")
    g.process_vec(vmilk, "milk")

# 计算L2的意义拓扑（哪些──关联最稳定）
top_frames = [f for f in g.memory.frames if "──" in (f.sig_full or f.sig)]
print(f"建立的意义关联: {len(top_frames)}个")
for f in sorted(top_frames, key=lambda x: x.weight, reverse=True)[:3]:
    s=(f.sig_full or f.sig)[:40]; w=int(f.weight)
    print(f"  w={w:3d} {s}")

# 高→低投影：L2帧的重心→L1的阈值调制
proj = [0.0]*_D27  # 投影向量（L2对L1的"期待"）
for f in top_frames:
    for d in range(_D27):
        proj[d] += f.vec[d] * f.weight
total_w = sum(f.weight for f in top_frames) or 1
proj = [p/total_w for p in proj]

# 预测偏差：每个L1帧与L2投影的距离
print(f"\n投影分配到L1帧(预测偏差=帧重心-投影距离):")
for i, f in enumerate(g.memory.frames[:5]):
    s=(f.sig_full or f.sig)[:15]; w=int(f.weight)
    pred_err = math.sqrt(sum((f.vec[d]-proj[d])**2 for d in range(_D27)))
    # 预测偏差大→高"意外"→应该降低阈值（更细分辨）
    # 预测偏差小→低"意外"→应该提高阈值（更平滑处理）
    threshold_mod = 1.0 / max(0.1, pred_err)
    print(f"  帧{i}: sig={s:15s} w={w:3d} 预测误差={pred_err:.3f} 阈值调制×{threshold_mod:.2f}")

print(f"\n自由能解释:")
print(f"  预测误差大的帧→阈值降低→感知变细→注意意外发生")
print(f"  预测误差小的帧→阈值提高→感知变粗→一切如常，节约能量")
print(f"  这就是Friston自由能原理在GEME中的计算对应")
