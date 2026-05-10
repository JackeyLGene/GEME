# 拓扑区分 v4：时序合并邻接
# 每步输入合并到的帧ID → 相邻步的帧ID不同 → 在它们之间加一条边
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

def run_topology(name, make_vec, steps=5000, mem_cap=128):
    g = GEME(memory_cap=mem_cap, cooccur_window=60, cooccur_thresh=0.08, max_chains=20)
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    
    # 记录每步合并到哪个帧ID
    merge_history = []  # 每步: fid of merged-to frame
    step_fids = []
    
    for i in range(steps):
        t = i * 0.01
        v = make_vec(t)
        # 记录合并前的帧数/ID，用于判断合并到哪个
        before_fids = set(id(f) for f in g.memory.frames)
        g.process_vec(v, "m")
        after_fids = set(id(f) for f in g.memory.frames)
        
        # 判断合并或新建
        new_fids = after_fids - before_fids
        if new_fids:
            fid = list(new_fids)[0]  # 新建帧
        else:
            # 找到权重增加的帧
            # 简单处理：取最近合并记录（GEME内部有merge_dists）
            # 用最简办法：帧数量不变，找fid出现的变化
            # 实际上难以精确定位——用g.memory._merge_dists最后一条作为合并发生的标志
            # 如果合并，取最近一次process_vec中更新的帧
            # 退一步：取前后共有的帧中权重增加的那个
            pass
        
        # 简化：记录所有当前帧的fid
        merge_history.append([id(f) for f in g.memory.frames])
    
    # 收集m帧（过滤出带"m"签名的）
    m_frames = [f for f in g.memory.frames if "m" in (f.sig_full or f.sig)[:10]]
    m_fids = set(id(f) for f in m_frames)
    
    # 构建时序邻接：step t的活动帧集 vs step t+1的活动帧集
    # 如果两个fid在相邻步中都出现，且它们不同，加一条边
    edges = {}
    for t in range(len(merge_history)-1):
        cur = [f for f in merge_history[t] if f in m_fids]
        nxt = [f for f in merge_history[t+1] if f in m_fids]
        for a in cur:
            for b in nxt:
                if a != b:
                    key = (min(a,b), max(a,b))
                    edges[key] = edges.get(key, 0) + 1
    
    # 构建图
    fids_list = list(m_fids)
    fid_to_idx = {fid: i for i, fid in enumerate(fids_list)}
    n = len(fids_list)
    
    adj = [[0]*n for _ in range(n)]
    for (a, b), w in edges.items():
        if a in fid_to_idx and b in fid_to_idx:
            i, j = fid_to_idx[a], fid_to_idx[b]
            adj[i][j] += w
            adj[j][i] += w
    
    degrees = [sum(adj[i][j] for j in range(n)) for i in range(n)]
    
    # 连通分量（BFS）
    visited = [False]*n
    components = []
    for start in range(n):
        if visited[start]: continue
        queue = [start]; visited[start] = True; comp = []
        while queue:
            v = queue.pop(0); comp.append(v)
            for u in range(n):
                if adj[v][u] > 0 and not visited[u]:
                    visited[u] = True; queue.append(u)
        components.append(comp)
    
    n_comp = len(components)
    avg_deg = statistics.mean(degrees) if degrees else 0
    deg_var = statistics.variance(degrees) if len(degrees) > 1 else 0
    
    print(f"{name}: {n}个m帧, {len(edges)}条时序边, {n_comp}个连通分量")
    print(f"  平均度={avg_deg:.2f}, 度方差={deg_var:.2f}")
    
    # 拓扑判别
    if n_comp == 2:
        label = "2个分离结构（如：两个圆）"
    elif n_comp == 1 and deg_var < avg_deg:
        label = "均匀环（圆 S1）"
    elif n_comp == 1 and deg_var > avg_deg * 2:
        label = "不均匀（有交叉点——8字形/F8）"
    else:
        label = f"待判({n_comp}分, deg方差{deg_var:.1f})"
    print(f"  判别: {label}")
    print()
    
    return n, degrees, n_comp

print("="*55)
print("拓扑区分 v4：时序合并邻接图")
print("="*55)
print()

def c1(t):
    v=[0.0]*_D27; v[0]=math.cos(2*math.pi*t); v[1]=math.sin(2*math.pi*t); return v

def c2t(t):
    v=[0.0]*_D27; v[0]=math.cos(2*math.pi*t); v[1]=math.sin(2*math.pi*t)
    v[2]=math.cos(2*math.pi*1.414*t); v[3]=math.sin(2*math.pi*1.414*t); return v

def c2c(t):
    v=[0.0]*_D27
    if int(t*50)%2==0: v[0]=math.cos(2*math.pi*t)+2; v[1]=math.sin(2*math.pi*t)
    else: v[2]=math.cos(2*math.pi*t)-2; v[3]=math.sin(2*math.pi*t)
    return v

def f8(t):
    v=[0.0]*_D27; v[0]=math.sin(2*math.pi*t); v[1]=math.sin(2*math.pi*t)*math.cos(2*math.pi*t)
    return v

for name, fn in [("圆 S1", c1), ("环面 T2", c2t), ("双圆(不相交)", c2c), ("8字形 F8", f8)]:
    run_topology(name, fn)
