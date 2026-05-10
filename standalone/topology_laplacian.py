# 拓扑区分 v3：══链图 → Laplacian 谱
# 不是测距离——是测"时序邻接关系"
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
    
    frames = g.memory.frames
    # 收集所有m帧
    m_frames = [f for f in frames if "m" in (f.sig_full or f.sig)[:10]]
    n = len(m_frames)
    if n < 4: return n, [], "帧数不足"
    
    # 提取══链中的邻接关系
    # ══帧的签名如： "m__xxx══m__yyy"
    # 从链帧中提取邻接边
    edges = []
    for f in frames:
        sig = f.sig_full or f.sig
        if "══" in sig:
            # 分割链
            parts = sig.split("══")
            for k in range(len(parts)-1):
                a = parts[k].strip("_").strip()
                b = parts[k+1].strip("_").strip()
                if a and b:
                    edges.append((a, b))
    
    # 构建签名→索引映射
    sigs = list(set((f.sig_full or f.sig)[:20] for f in m_frames))
    sig_to_idx = {s: i for i, s in enumerate(sigs)}
    n_nodes = len(sigs)
    
    # 构建邻接矩阵（Laplacian）
    adj = [[0]*n_nodes for _ in range(n_nodes)]
    for a, b in edges:
        # 找到对应的签名
        a_match = [s for s in sigs if a in s]
        b_match = [s for s in sigs if b in s]
        for sa in a_match:
            for sb in b_match:
                if sa in sig_to_idx and sb in sig_to_idx:
                    i, j = sig_to_idx[sa], sig_to_idx[sb]
                    if i != j:
                        adj[i][j] += 1
                        adj[j][i] += 1
    
    # 计算度
    degrees = [sum(adj[i][j] for j in range(n_nodes)) for i in range(n_nodes)]
    avg_deg = statistics.mean(degrees) if degrees else 0
    
    # Laplacian 特征值
    import numpy as np
    L = np.diag([float(d) for d in degrees]) - np.array(adj, dtype=float)
    try:
        eigenvalues = sorted(np.linalg.eigvalsh(L))
    except:
        return n, [], f"特征值失败"
    
    # 有效的特征值分析
    # Fiedler值（第2小特征值）≈ 代数连通度
    # 0的个数 ≈ 连通分量数
    zero_count = sum(1 for e in eigenvalues if abs(e) < 1e-8)
    fiedler = eigenvalues[zero_count] if zero_count < len(eigenvalues) else 0  # 第1个非零
    fiedler2 = eigenvalues[zero_count+1] if zero_count+1 < len(eigenvalues) else 0  # 第2个非零
    
    # 度分布的分析：平均度和度数的方差
    deg_var = statistics.variance(degrees) if len(degrees) > 1 else 0
    
    print(f"{name}: {n}节点, {len(edges)}条边, 连通分量={zero_count}")
    print(f"  平均度={avg_deg:.2f}, 度方差={deg_var:.2f}")
    print(f"  Fiedler值(代数连通度)={fiedler:.4f}, 第2个非零={fiedler2:.4f}")
    
    # 拓扑判别
    info = f"分{zero_count}个连通分量, F={fiedler:.3f}"
    return n, degrees, info

print("="*55)
print("拓扑区分 v3：══链Laplacian谱")
print("="*55)
print("预期：S1→1分量, AvgDeg≈2, Fiedler>0")
print("      T2→1分量, AvgDeg≈4, Fiedler>Fiedler_of_S1")
print("      双圆→2分量")
print("      8字→1分量, 度方差大(交点度高)")
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
    phase = int(t*50) % 2
    if phase == 0:
        v[0]=math.cos(2*math.pi*t)+2; v[1]=math.sin(2*math.pi*t)
    else:
        v[2]=math.cos(2*math.pi*t)-2; v[3]=math.sin(2*math.pi*t)
    return v

def f8(t):
    v=[0.0]*_D27; v[0]=math.sin(2*math.pi*t); v[1]=math.sin(2*math.pi*t)*math.cos(2*math.pi*t)
    return v

results = []
for name, fn in [("圆 S1", c1), ("环面 T2", c2t), ("双圆(不相交)", c2c), ("8字形", f8)]:
    n, deg, info = run_topology(name, fn)
    results.append((name, n, deg))
    print()

print("="*55)
print("对比：")
for name, n, deg in results:
    if isinstance(deg, list) and deg:
        print(f"  {name}: {n}帧, 平均度{statistics.mean(deg):.2f}, 度方差{statistics.stdev(deg):.2f}" if len(deg)>1 else f"  {name}: {n}帧, 度数{deg}")
    else:
        print(f"  {name}: {deg}")
