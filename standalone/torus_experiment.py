# 拓扑感知实验：GEME能区分圆(S1)和环面(T2)吗？
# 圆：1个周期变量θ
# 环面：2个独立周期变量θ, φ
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

def run_manifold(name, signal_fn, steps=5000):
    g = GEME(memory_cap=64, cooccur_window=80, cooccur_thresh=0.08, max_chains=20)
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    
    for i in range(steps):
        t = i * 0.01
        v = signal_fn(t)
        g.process_vec(v, "m")
    
    frames = g.memory.frames
    m_frames = [f for f in frames if "m" in (f.sig_full or f.sig)]
    chain = [f for f in frames if "══" in (f.sig_full or f.sig)]
    assoc = [f for f in frames if "──" in (f.sig_full or f.sig)]
    
    # 链深度分析：链帧之间的连接度
    chain_depth = 0
    if chain:
        # 链的度数分布
        chain_sigs = [f.sig_full or f.sig for f in chain]
        degrees = []
        for s in chain_sigs:
            d = s.count("══")  # 链中的链接数
            degrees.append(d)
        chain_depth = statistics.mean(degrees) if degrees else 0
    
    # 关联密度
    assoc_density = len(assoc) / max(len(m_frames), 1)
    
    print(f"{name}: {len(m_frames)}位置帧, 链深度{chain_depth:.1f}, 关联密度{assoc_density:.2f}, 总{len(frames)}帧")
    top = sorted(m_frames, key=lambda x: x.weight, reverse=True)[:2]
    for t in top:
        w = int(t.weight); s = (t.sig_full or t.sig)[:40]
        print(f"  顶帧 w={w} {s}")
    return len(m_frames), chain_depth, assoc_density

print("="*55)
print("拓扑感知实验：GEME能区分不同拓扑吗？")
print("="*55)
print()

# 1. 单位圆 S1
def circle_signal(t):
    theta = 2 * math.pi * 1.0 * t
    v = [0.0]*_D27; v[0] = math.cos(theta); v[1] = math.sin(theta)
    return v

# 2. 环面 T2 (两个独立周期，不可通约频率→完全覆盖环面)
def torus_signal(t):
    theta = 2 * math.pi * 1.0 * t
    phi = 2 * math.pi * 1.414 * t  # √2不可通约
    v = [0.0]*_D27
    v[0] = math.cos(theta); v[1] = math.sin(theta)
    v[2] = math.cos(phi);   v[3] = math.sin(phi)
    return v

# 3. Möbius带 (一个方向周期，另一个方向有扭转)
def mobius_signal(t):
    theta = 2 * math.pi * 1.0 * t
    w = 0.3 * math.cos(theta/2)  # 宽度（扭转变换）
    v = [0.0]*_D27
    v[0] = math.cos(theta) * (1 + w)
    v[1] = math.sin(theta) * (1 + w)
    v[2] = 0.3 * math.sin(theta/2)  # 扭转方向
    return v

# 4. 8字形 (自交)
def figure8_signal(t):
    theta = 2 * math.pi * 1.0 * t
    v = [0.0]*_D27
    v[0] = math.sin(theta)
    v[1] = math.sin(theta) * math.cos(theta)
    return v

n_circ, dc, ac = run_manifold("圆 S1", circle_signal)
n_tor, dt, at = run_manifold("环面 T2", torus_signal)
n_mob, dm, am = run_manifold("Möbius带", mobius_signal)
n_fig, df, af = run_manifold("8字形", figure8_signal)

print()
print("拓扑区分分析：")
print(f"  链深度: 圆{dc:.1f} 环面{dt:.1f} Möbius{dm:.1f} 8字{df:.1f}")
print(f"  关联密度: 圆{ac:.2f} 环面{at:.2f} Möbius{am:.2f} 8字{af:.2f}")
if max(dt, dm, df) > dc * 1.2:
    print("  ✓ 链深度区分了不同拓扑")
else:
    print("  - 链深度不足以区分")
if max(at, am, af) > ac * 1.2:
    print("  ✓ 关联密度区分了不同拓扑")
else:
    print("  - 关联密度不足以区分")
