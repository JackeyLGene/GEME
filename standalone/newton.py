# 牛顿三定律在 GEME 中的对应
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM

print("="*55)
print("GEME 中的牛顿三定律")
print("="*55)
print()

# ── 第一定律：惯性 ──
print("第一定律（惯性）：匀速运动帧")
print("-"*45)

g = GEME(memory_cap=32); g.memory.preserve_sig = True
g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0

# 匀速输入：每步位置+0.02（在dim0上匀速运动）
positions = []
for i in range(500):
    v = [0.0]*_VEC_DIM; v[0] = i * 0.02
    g.process_vec(v, "m")

# 查看帧重心——是否形成均匀间距的链？
mframes = [f for f in g.memory.frames if "m" in (f.sig_full or f.sig)[:10]]
if mframes:
    centroids = sorted([f.vec[0] for f in mframes])
    if len(centroids) > 2:
        gaps = [centroids[i+1]-centroids[i] for i in range(len(centroids)-1)]
        avg_gap = statistics.mean(gaps); std_gap = statistics.stdev(gaps)
        print(f"  匀速输入 {len(mframes)}帧, 帧间距 {avg_gap:.4f}±{std_gap:.4f}")
        print(f"  均匀度: {std_gap/avg_gap:.2f} {'均匀(惯性成立)' if std_gap/avg_gap<0.3 else '不均匀'}")

# ── 第二定律：F=ma ──
print(f"\n第二定律（F=ma）：质量×加速度=力")
print("-"*45)

def test_inertia(mass, accel, label):
    """相同加速输入，不同质量帧看位移量"""
    g = GEME(memory_cap=10); g.memory.preserve_sig = True
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    
    # 创建有质量(weight)的帧
    from geme import Frame
    f = Frame([0.0]*_VEC_DIM, mass, "obj")
    g.memory.frames = [f]; g.memory.total_weight = mass
    
    # 加速推动
    disp = 0
    for step in range(200):
        disp += accel * step * 0.001  # 位移 = ½at²
        if step < 3: continue  # 跳过初始不稳定
        v = [0.0]*_VEC_DIM; v[0] = disp
        g.process_vec(v, "obj")
    
    # 看帧最终位置
    final_pos = g.memory.frames[0].vec[0] if g.memory.frames else 0
    return final_pos

# 固定力：质量不同→位移应当不同
masses = [1, 5, 10, 20]
positions_ms = [(m, test_inertia(m, 0.5, f"m={m}")) for m in masses]
for m, p in positions_ms:
    print(f"  质量={m:3d}, 位移={p:.6f}, 位移×质量={p*m:.4f}")

# 如果 F=ma，则位移×质量应该≈常数
if len(positions_ms)>1:
    products = [p*m for m, p in positions_ms]
    avg_p = statistics.mean(products); std_p = statistics.stdev(products)
    print(f"  位移×质量 = {avg_p:.4f}±{std_p:.4f} ({std_p/avg_p*100:.0f}% 误差)")
    print(f"  {'✓ F=ma成立' if std_p/avg_p<0.3 else '✗ F=ma不显著'}")
