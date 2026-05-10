# 拓扑区分实验：共现矩阵 SVD → Betti 数估计
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

def run_topology(name, make_vec, steps=4000, mem_cap=128):
    g = GEME(memory_cap=mem_cap, cooccur_window=60, cooccur_thresh=0.08, max_chains=20)
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    
    # 记录每个时刻激活的帧ID
    active_history = []  # 每步: set of frame IDs
    
    for i in range(steps):
        t = i * 0.01
        v = make_vec(t)
        # 先记录当前帧集
        before = set(id(f) for f in g.memory.frames) if i > 0 else set()
        g.process_vec(v, "m")
        after = set(id(f) for f in g.memory.frames)
        # 记录当前有哪些"m"帧活动
        active = set(id(f) for f in g.memory.frames if "m" in (f.sig_full or f.sig)[:10])
        active_history.append(active)
    
    # 构建共现矩阵
    all_frames = [f for f in g.memory.frames if "m" in (f.sig_full or f.sig)[:10]]
    fid_to_idx = {id(f): i for i, f in enumerate(all_frames)}
    n = len(all_frames)
    if n == 0: return 0, []
    
    cooc = [[0]*n for _ in range(n)]
    for active in active_history:
        idxs = [fid_to_idx[fid] for fid in active if fid in fid_to_idx]
        for a in idxs:
            for b in idxs:
                cooc[a][b] += 1
    
    # SVD
    # 用纯Python SVD（简化版——对n≤100足够）
    # 计算协方差矩阵特征值
    import numpy as np
    mat = np.array(cooc, dtype=float)
    # 归一化
    row_sums = mat.sum(axis=1, keepdims=True)
    row_sums[row_sums==0] = 1
    mat_norm = mat / row_sums
    
    try:
        U, S, Vt = np.linalg.svd(mat_norm, full_matrices=False)
    except:
        return n, []
    
    # 归一化奇异值
    S_norm = S / S[0] if S[0] > 0 else S
    # 统计大于阈值的奇异值个数
    thresh = 0.1
    n_dominant = sum(1 for s in S_norm if s > thresh)
    
    print(f"{name}: {n}帧, 主奇异值={n_dominant}, 奇异值=[", end="")
    print(", ".join(f"{s:.3f}" for s in S_norm[:min(8, len(S_norm))]), end="")
    print("]")
    
    return n, S_norm.tolist()

print("="*55)
print("拓扑区分实验：共现矩阵 SVD")
print("="*55)
print("预期：S1→1个主奇异值, T2→2个, 双圆→2个, 8字→2个")
print()

# S1: 圆(一个周期)
def c1(t):
    v=[0.0]*_D27; v[0]=math.cos(2*math.pi*t); v[1]=math.sin(2*math.pi*t)
    return v

# T2: 环面(两个独立周期)
def c2t(t):
    v=[0.0]*_D27
    v[0]=math.cos(2*math.pi*t); v[1]=math.sin(2*math.pi*t)
    v[2]=math.cos(2*math.pi*1.414*t); v[3]=math.sin(2*math.pi*1.414*t)
    return v

# 两个不相交圆
def c2c(t):
    v=[0.0]*_D27
    if int(t)%2==0:
        v[0]=math.cos(2*math.pi*t)+2; v[1]=math.sin(2*math.pi*t)
    else:
        v[2]=math.cos(2*math.pi*t)-2; v[3]=math.sin(2*math.pi*t)
    return v

# 8字形
def f8(t):
    v=[0.0]*_D27; v[0]=math.sin(2*math.pi*t); v[1]=math.sin(2*math.pi*t)*math.cos(2*math.pi*t)
    return v

results = []
for name, fn in [("圆 S1", c1), ("环面 T2", c2t), ("双圆 (不相交)", c2c), ("8字形", f8)]:
    n, sv = run_topology(name, fn)
    results.append((name, n, sv))

print()
print("分析：")
for name, n, sv in results:
    dominant = sum(1 for s in sv if s > 0.1) if sv else 0
    print(f"  {name}: {n}帧, {dominant}个主奇异值", end="")
    if name == "圆 S1" and dominant == 1:
        print(" ✓ b₁=1")
    elif "环面" in name and dominant == 2:
        print(" ✓ b₁=2")
    elif "双圆" in name and dominant == 2:
        print(" ✓ b₀=2, 线性空间维=2")
    elif "8字" in name and dominant == 2:
        print(" ✓ b₁=2")
    else:
        print(" ? 与预期不一致")
