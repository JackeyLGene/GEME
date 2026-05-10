# 拓扑区分 v2：扩散核 SVD（正确的方法）
# 不是"哪些帧共现"——而是"帧之间的距离结构"
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

def run_topology(name, make_vec, steps=5000, mem_cap=128):
    g = GEME(memory_cap=mem_cap, cooccur_window=60, cooccur_thresh=0.08, max_chains=20)
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    
    for i in range(steps):
        t = i * 0.01
        v = make_vec(t)
        g.process_vec(v, "m")
    
    # 收集所有m帧的重心向量和权重
    frames = [f for f in g.memory.frames if "m" in (f.sig_full or f.sig)[:10]]
    n = len(frames)
    if n < 3: return n, [], frames
    
    # 扩散核：核矩阵 K[i][j] = exp(-d_ij²/ε²)
    # ε = median of all distances (自适应尺度)
    vecs = [f.vec for f in frames]
    dists = []
    for i in range(n):
        for j in range(i+1, n):
            d = math.sqrt(sum((vecs[i][k]-vecs[j][k])**2 for k in range(_D27)))
            dists.append(d)
    
    if not dists: return n, [], frames
    # 局部自适应核宽度：取最近邻距离的中位数（而非全距离中位数）
    # 每个点取到其第5近邻的距离，取这些距离的中位数
    knn_dists = []
    for i in range(n):
        ds = sorted(math.sqrt(sum((vecs[i][k]-vecs[j][k])**2 for k in range(_D27))) for j in range(n) if j != i)
        if len(ds) >= 5: knn_dists.append(ds[min(4, len(ds)-1)])
    eps = statistics.median(knn_dists) if knn_dists else statistics.median(dists)
    eps = max(eps, 0.001)
    # 乘以一个小因子，使核更局部
    
    K = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            d = math.sqrt(sum((vecs[i][k]-vecs[j][k])**2 for k in range(_D27)))
            K[i][j] = math.exp(-d*d/(eps*eps))
    
    # 归一化扩散算子
    D = [sum(K[i][j] for j in range(n)) for i in range(n)]
    D = [max(d, 0.001) for d in D]
    # A = D^(-1/2) * K * D^(-1/2)  （对称归一化）
    # 直接算特征值
    import numpy as np
    K_np = np.array(K, dtype=float)
    D_inv_sqrt = np.diag([1.0/math.sqrt(d) for d in D])
    A = D_inv_sqrt @ K_np @ D_inv_sqrt
    
    try:
        eigenvalues = np.linalg.eigvalsh(A)
        # 从大到小排序
        eigenvalues = sorted(eigenvalues, reverse=True)
    except:
        return n, [], frames
    
    # 归一化到[0,1]
    ev_norm = [float(e)/eigenvalues[0] for e in eigenvalues] if eigenvalues[0] > 0 else eigenvalues
    
    # 统计扩散维度：λ_i > 0.1 且 λ_i/λ_{i-1} < 0.5 的个数
    # 更简单：找特征值间隙——第i个和第i+1个之间的大跳
    dim = 0
    for i in range(1, len(ev_norm)):
        if ev_norm[i] < 0.15:  # 截止阈值
            dim = i 
            break
    else:
        dim = len(ev_norm)
    
    print(f"{name}: {n}帧, 扩散维度≈{dim}")
    print(f"  特征值: [" + ", ".join(f"{e:.3f}" for e in ev_norm[:min(8, len(ev_norm))]) + "...]")
    
    return n, ev_norm, frames

print("="*55)
print("拓扑区分 v2：扩散核 SVD")
print("="*55)
print("预期：S1→1维  T2→2维  双圆→2分量  8字→2环")
print()

def c1(t):
    v=[0.0]*_D27; v[0]=math.cos(2*math.pi*t); v[1]=math.sin(2*math.pi*t)
    return v

def c2t(t):
    v=[0.0]*_D27
    v[0]=math.cos(2*math.pi*t); v[1]=math.sin(2*math.pi*t)
    v[2]=math.cos(2*math.pi*1.414*t); v[3]=math.sin(2*math.pi*1.414*t)
    return v

def c2c(t):
    v=[0.0]*_D27
    if int(t*10)%2==0:
        v[0]=math.cos(2*math.pi*t)+2; v[1]=math.sin(2*math.pi*t)
    else:
        v[2]=math.cos(2*math.pi*t)-2; v[3]=math.sin(2*math.pi*t)
    return v

def f8(t):
    v=[0.0]*_D27; v[0]=math.sin(2*math.pi*t); v[1]=math.sin(2*math.pi*t)*math.cos(2*math.pi*t)
    return v

results = []
for name, fn in [("圆 S1", c1), ("环面 T2", c2t), ("双圆 (不相交)", c2c), ("8字形", f8)]:
    n, ev, _ = run_topology(name, fn)
    results.append((name, n, ev))

print()
print("分析：")
for name, n, ev in results:
    ev_str = ", ".join(f"{e:.2f}" for e in ev[:4]) if ev else "[]"
    print(f"  {name}: 扩散维≈{sum(1 for e in ev if e>0.15) if ev else 0}")
