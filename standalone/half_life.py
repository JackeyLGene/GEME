# 原子半衰期实验 v3 — 手动创建帧，不通过process_vec
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, Frame, _VEC_DIM

_r = random.Random(99)

def single_atom(seed, max_steps=500):
    r = random.Random(seed)
    g = GEME(memory_cap=5); g.memory.quantum_mode = True; g.memory.preserve_sig = True
    g.memory._merge_thresh_val = 1.5; g.memory._merge_dists = [1.5]*50
    
    # 手动创建两个帧（不通过process_vec，避免量子合并）
    va = [0.0]*_VEC_DIM; va[0] = 1.0; va[5] = 0.5  # 原子态
    vb = [0.0]*_VEC_DIM; vb[5] = 0.1; vb[10] = 1.0  # 衰变产物（距va远）
    
    fa = Frame(va, 10.0, "atom")  # 原子帧初始权重10
    fb = Frame(vb, 1.0, "product")  # 产物帧初始权重1
    g.memory.frames = [fa, fb]
    g.memory.total_weight = 11.0
    
    # 输入在a和b之间
    vin = [0.0]*_VEC_DIM; vin[0] = 0.85; vin[5] = 0.45; vin[10] = 0.3
    
    for step in range(max_steps):
        th = g.memory._adaptive_thresh() or 1.5
        cand = []
        for i, f in enumerate(g.memory.frames):
            d = math.sqrt(sum((vin[j]-f.vec[j])**2 for j in range(_VEC_DIM)))
            if d <= th: cand.append((i, d, f))
        
        if not cand:
            g.memory.observe(vin, "")
            continue
        
        # Boltzmann选择
        ps = 0; pr = []
        for i, d, f in cand:
            p = math.exp(-d/max(th, 0.001)); pr.append((i, d, f, p)); ps += p
        
        if ps > 0:
            rn = r.random() * ps; ac = 0
            for i, d, f, p in pr:
                ac += p
                if rn <= ac:
                    if "product" in (f.sig_full or f.sig)[:20]:
                        return step + 1  # 衰变
                    fa.weight += 1; g.memory.total_weight += 1
                    break
    return max_steps  # 未衰变

# 批量
lifetimes = []
for s in range(500):
    lt = single_atom(s+1000, 1000)
    lifetimes.append(lt)
    if (s+1) % 100 == 0:
        d = sum(1 for l in lifetimes if l < 1000)
        print(f"  {s+1:3d}/500: {d}衰变")

alive = sum(1 for l in lifetimes if l >= 1000)
decayed = [l for l in lifetimes if l < 1000]
mid = statistics.median(decayed) if decayed else -1
print(f"\n结果:")
print(f"  总原子: 500, 衰变: {len(decayed)}, 存活: {alive}")
print(f"  半衰期: {mid:.0f}步")
if decayed:
    bins = [0, 10, 30, 50, 100, 200, 500, 1000]
    for i in range(len(bins)-1):
        c = sum(1 for l in decayed if bins[i] <= l < bins[i+1])
        if c: print(f"  {bins[i]:3d}-{bins[i+1]:3d}步: {c}个")
    # 检查是否指数：前100步 > 后500步
    early = sum(1 for l in decayed if l < 100)
    late = sum(1 for l in decayed if l > 500)
    if early > late * 2: print("  ✓ 指数分布（早期衰变远多于晚期）")
