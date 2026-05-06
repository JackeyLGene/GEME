# 畴壁相变：ext密度扫瞄，测量ext──self桥接帧权重
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

def sweep_ext_density(ext_density, steps=800):
    """在给定ext输入密度下运行, 返回ext──self桥接帧权重"""
    g = GEME(memory_cap=64, cooccur_window=60, cooccur_thresh=0.08, max_chains=15)
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    
    # 内时模块（简化版嵌入）
    tick_interval = 8
    ticks = 0
    self_count = 0
    last_sigs = set()
    
    for i in range(steps):
        # 外部输入（按密度概率发送）
        if _r.random() < ext_density:
            t = i * 0.01
            v = [0.0]*_D27; v[0] = math.cos(t*2)*0.8+0.1; v[1] = math.sin(t*2)*0.8+0.1
            g.process_vec(v, "ext")
        
        # 内部心跳（固定间隔）
        ticks += 1
        if ticks >= tick_interval:
            cur = set()
            for f in g.memory.frames: cur.add((f.sig_full or f.sig)[:20])
            change = 0
            if last_sigs:
                add = len(cur - last_sigs) / max(len(cur), 1)
                rem = len(last_sigs - cur) / max(len(last_sigs), 1)
                change = add + rem
            last_sigs = cur
            tick_interval = max(3, 8 / (1 + change * 5))
            
            v = [0.0]*_D27
            for i2, f in enumerate(g.memory.frames[:5]):
                v[i2] = f.weight / (sum(f.weight for f in g.memory.frames) or 1)
            self_count += 1
            g.process_vec(v, "self")
            ticks = 0
    
    # 测量桥接帧
    bridge = 0
    for f in g.memory.frames:
        s = f.sig_full or f.sig
        if "ext" in s and "self" in s:
            bridge += int(f.weight)
    return bridge

print("="*55)
print("畴壁相变：ext──self桥接帧权重 vs ext输入密度")
print("="*55)
print()

densities = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]
results = []
for d in densities:
    w = sweep_ext_density(d)
    results.append(w)
    bar = "█" * min(w // 10, 30)
    print(f"  ext密度={d:.2f} → 桥接帧权重={w:4d} {bar}")

print()
print("曲线分析：")
if len(results) > 2:
    # 看有没有S形曲线——即中间某个密度点权重突然上升
    diffs = [results[i+1] - results[i] for i in range(len(results)-1)]
    max_diff_idx = diffs.index(max(diffs))
    print(f"  最大跃迁发生在密度 {densities[max_diff_idx]} → {densities[max_diff_idx+1]}")
    print(f"  跃迁幅度: {max(diffs)}")
    if max(diffs) > statistics.mean(diffs)*2:
        print(f"  ✓ S形曲线——畴壁相变存在")
        print(f"  临界密度 ≈ {densities[max_diff_idx]}")
    else:
        print(f"  - 曲线接近线性——无明确相变")
