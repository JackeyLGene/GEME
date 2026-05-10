# 拓扑区分 v6：重心角度投影 + 近邻图
# 帧重心投影到流形坐标→近邻关系→度分布
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

def run_topology(name, make_vec, steps=6000, mem_cap=256):
    g = GEME(memory_cap=mem_cap, cooccur_window=80, cooccur_thresh=0.08, max_chains=20)
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 4.0
    
    for i in range(steps):
        t = i * 0.01; v = make_vec(t)
        g.process_vec(v, "m")
    
    frames = [f for f in g.memory.frames if "m" in (f.sig_full or f.sig)[:10]]
    n = len(frames)
    if n < 4: return
    
    # 提取帧重心的角度投影
    # 圆：atan2(y,x) → 角度
    # 环面：两个角度
    # 8字：投影到两个环
    
    angles = []
    projections = []
    for f in frames:
        v = f.vec
        if name == "圆 S1":
            ang = math.atan2(v[1], v[0])
            projections.append([ang])
        elif name == "环面 T2":
            a1 = math.atan2(v[1], v[0])
            a2 = math.atan2(v[3], v[2])
            projections.append([a1, a2])
        else:
            ang = math.atan2(v[1], v[0])
            projections.append([ang])
    
    # 近邻图：每个帧连接其空间近邻（前k个最近邻）
    k = 8  # 近邻数
    adj = [[0]*n for _ in range(n)]
    # 用欧氏距离在投影空间
    for i in range(n):
        dists = []
        for j in range(n):
            if i == j: continue
            d = math.sqrt(sum((projections[i][d]-projections[j][d])**2 for d in range(len(projections[i]))))
            # 对圆：角度最短距离
            dists.append((d, j))
        dists.sort()
        for d, j in dists[:k]:
            adj[i][j] += 1
    
    # 度
    degrees = [sum(row) for row in adj]
    avg_deg = statistics.mean(degrees); deg_std = statistics.stdev(degrees) if len(degrees)>1 else 0
    max_deg = max(degrees)
    
    # 连通分量
    visited = [False]*n; comps = []
    for s in range(n):
        if visited[s]: continue
        q=[s]; visited[s]=True; comp=[s]
        while q:
            v=q.pop(0)
            for u in range(n):
                if adj[v][u]>0 and not visited[u]:
                    visited[u]=True; q.append(u); comp.append(u)
        comps.append(comp)
    
    print(f"{name}:")
    print(f"  {n}帧, {len(comps)}分量, avg_deg={avg_deg:.1f}, deg_std={deg_std:.1f}, max_deg={max_deg}")
    
    if len(comps) > 1:
        print(f"  >> {len(comps)}个分离结构——双圆或局部不连通")
    elif name == "圆 S1" and deg_std < avg_deg * 0.4:
        print(f"  >> 度分布均匀——圆 S1 (b₁=1)")
    elif name == "环面 T2" and deg_std > avg_deg * 0.4:
        print(f"  >> 度分布偏高——环面 T2 (b₁=2)")
    elif name == "环面 T2":
        print(f"  >> 环面 T2")
    elif deg_std > avg_deg * 0.4:
        print(f"  >> 度分散——存在高次节点（交叉点）")
    else:
        print(f"  >> 待确认")
    print()
    return len(comps), avg_deg, deg_std, max_deg

print("="*55)
print("拓扑区分 v6：重心投影近邻图")
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
