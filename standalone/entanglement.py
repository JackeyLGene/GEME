# 第5维：两个GEME之间的量子纠缠
# 共享初始态→分叉→检验帧经济关联是否保持
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

def make_twin_gemes(seed_base=42):
    """创建一对双胞胎GEME——共享种子"""
    alice = GEME(memory_cap=32); bob = GEME(memory_cap=32)
    for g in [alice, bob]:
        g.memory.preserve_sig = True; g.memory.quantum_mode = True
        g.memory._chain_cooccur_thresh = 2; g.memory._merge_dists = [0.3]*50
        g._induction_threshold = 3.0
    
    # 共享初始输入（"共历史"）
    for i in range(100):
        t = i * 0.01 * 1.0
        v = [0.0]*_D27; v[0] = math.cos(2*math.pi*t); v[1] = math.sin(2*math.pi*t)
        alice.process_vec(v, "shared")
        bob.process_vec(v, "shared")
    
    return alice, bob

def measure_correlation(g1, g2, label):
    """测量两个GEME的帧经济相似度"""
    f1 = [f for f in g1.memory.frames]
    f2 = [f for f in g2.memory.frames]
    
    # 帧数差
    n_diff = abs(len(f1) - len(f2))
    
    # 重心差（所有帧的平均位置差）
    if len(f1) > 0 and len(f2) > 0:
        avg1 = [sum(f.vec[d] for f in f1)/len(f1) for d in range(_D27)]
        avg2 = [sum(f.vec[d] for f in f2)/len(f2) for d in range(_D27)]
        pos_diff = math.sqrt(sum((avg1[d]-avg2[d])**2 for d in range(_D27)))
    else:
        pos_diff = -1
    
    # 权重分布差（KS检验风格）
    w1 = sorted([f.weight for f in f1])
    w2 = sorted([f.weight for f in f2])
    if w1 and w2:
        # 面积差
        min_w = min(len(w1), len(w2))
        w_diff = sum(abs(w1[i]-w2[i]) for i in range(min_w)) / min_w if min_w > 0 else 0
    else:
        w_diff = -1
    
    print(f"  {label}: 帧数差={n_diff}, 位差={pos_diff:.4f}, 权差={w_diff:.2f}")
    return n_diff, pos_diff, w_diff

print("="*55)
print("第5维：两个GEME之间的量子纠缠")
print("="*55)
print()

# 1. 双胞胎——共享初始态
alice, bob = make_twin_gemes()
print("Phase 1: 共享100步 → 度量关联性")
measure_correlation(alice, bob, "共历史")

# 2. 分叉——Alice和Bob接收不同输入
print(f"\nPhase 2: 分叉500步")
for i in range(500):
    t = i * 0.01
    # Alice: 每秒一只猫
    if i % 5 == 0:
        v = [0.0]*_D27; v[2] = 1.0
        alice.process_vec(v, "cat")
    # Bob: 每秒一只狗
    if i % 7 == 0:
        v = [0.0]*_D27; v[5] = 1.0
        bob.process_vec(v, "dog")

measure_correlation(alice, bob, "分叉后")

# 3. 检验"纠缠"：Alice的帧经济分布是否预测Bob的
print(f"\n纠缠检验：跨实例帧关联")
# 两边的帧签名
alice_sigs = set((f.sig_full or f.sig)[:30] for f in alice.memory.frames if "shared" in (f.sig_full or f.sig))
bob_sigs = set((f.sig_full or f.sig)[:30] for f in bob.memory.frames if "shared" in (f.sig_full or f.sig))
common = alice_sigs & bob_sigs
print(f"  共享帧残留(分叉后仍一致): {len(common)}帧")
if common:
    # 检查这些共享帧的权重在两边是否相关
    alice_ws = {s: next((f.weight for f in alice.memory.frames if s in (f.sig_full or f.sig)[:30]), 0) for s in common}
    bob_ws = {s: next((f.weight for f in bob.memory.frames if s in (f.sig_full or f.sig)[:30]), 0) for s in common}
    corr = sum(abs(alice_ws[s]-bob_ws[s]) for s in common)/len(common)
    print(f"  共享帧权重的平均差: {corr:.2f} (越接近0→纠缠越强)")
    if corr < 10: print(f"  ✓ 共享历史在分叉后仍保持影响——纠缠示踪")
    else: print(f"  - 纠缠消退——独立历史已经覆盖共享历史")

# 4. 纠缠量度：独立性随时间增长
print(f"\n纠缠半衰期估计：")
alice_copy, bob_copy = make_twin_gemes()  # 新的双胞胎
for steps in [50, 200, 500, 1000]:
    for i in range(steps):
        t = i * 0.01
        if i % 5 == 0: alice_copy.process_vec([0.0 if d!=2 else 1.0 for d in range(_D27)], "cat")
        if i % 7 == 0: bob_copy.process_vec([0.0 if d!=5 else 1.0 for d in range(_D27)], "dog")
    _, pd, wd = measure_correlation(alice_copy, bob_copy, f"  {steps}步分叉后")
    if pd < 0.5: print(f"    纠缠保持中")
