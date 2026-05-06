# 第四维闭环：GEME知道自己在观察自己（L1→L2→L3自指链）
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

# 三层
l1 = GEME(memory_cap=32, cooccur_window=40, cooccur_thresh=0.08, max_chains=10)
l2 = GEME(memory_cap=16, cooccur_window=40, cooccur_thresh=0.08, max_chains=5)
l3 = GEME(memory_cap=8,  cooccur_window=40, cooccur_thresh=0.08, max_chains=3)
for g in [l1,l2,l3]:
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0

# 内时跟踪
l1_tick = 0; l1_ti = 8; l1_prev = set()
l2_tick = 0; l2_ti = 12; l2_prev = set()

print("="*55)
print("第四维闭环：知道自己在观察自己")
print("="*55)
print()

for step in range(3000):
    # === L1: 外部世界 ===
    t = step * 0.01
    v_ext = [0.0]*_D27; v_ext[0] = math.cos(2*math.pi*t); v_ext[1] = math.sin(2*math.pi*t)
    l1.process_vec(v_ext, "world")
    
    # L1内时
    l1_tick += 1
    if l1_tick >= l1_ti:
        cur = set((f.sig_full or f.sig)[:20] for f in l1.memory.frames)
        chg = 0
        if l1_prev and cur:
            chg = (len(cur - l1_prev) + len(l1_prev - cur)) / max(len(cur), 1)
        l1_prev = cur
        l1_ti = max(3, 8 / (1 + chg * 5))
        
        v_self = [0.0]*_D27
        for j, f in enumerate(l1.memory.frames[:5]):
            v_self[j] = f.weight / (sum(f.weight for f in l1.memory.frames) or 1)
        l1.process_vec(v_self, "self")
        l1_tick = 0
    
    # === L2: 观察L1 ===
    # 每20步观察L1的帧经济
    if step % 20 == 0:
        v_l2 = [0.0]*_D27
        for j, f in enumerate(l1.memory.frames[:min(len(l1.memory.frames), _D27)]):
            v_l2[j] = f.weight / (sum(f.weight for f in l1.memory.frames) or 1)
        l2.process_vec(v_l2, f"v_l1_{step}")
    
    # L2内时
    l2_tick += 1
    if l2_tick >= l2_ti:
        cur = set((f.sig_full or f.sig)[:20] for f in l2.memory.frames)
        chg = 0
        if l2_prev and cur:
            chg = (len(cur - l2_prev) + len(l2_prev - cur)) / max(len(cur), 1)
        l2_prev = cur
        l2_ti = max(3, 12 / (1 + chg * 3))
        
        v_l2self = [0.0]*_D27
        for j, f in enumerate(l2.memory.frames[:3]):
            v_l2self[j] = f.weight / (sum(f.weight for f in l2.memory.frames) or 1)
        l2.process_vec(v_l2self, "v_self")
        l2_tick = 0
    
    # === L3: 观察L2 ===
    if step % 40 == 0:
        v_l3 = [0.0]*_D27
        for j, f in enumerate(l2.memory.frames[:min(len(l2.memory.frames), _D27)]):
            v_l3[j] = f.weight / (sum(f.weight for f in l2.memory.frames) or 1)
        l3.process_vec(v_l3, f"v_v_l1_{step}")

# 分析各层的"自我桥"
for name, g in [("L1(世界+自指)", l1), ("L2(看L1+看自己)", l2), ("L3(看L2)", l3)]:
    frames = g.memory.frames
    ext_world = sum(1 for f in frames if "world" in (f.sig_full or f.sig))
    self_ref = sum(1 for f in frames if "self" in (f.sig_full or f.sig) or "v_self" in (f.sig_full or f.sig)[:10])
    bridge = sum(int(f.weight) for f in frames 
                 if any(x in (f.sig_full or f.sig) for x in ["world","v_l1"]) 
                 and any(x in (f.sig_full or f.sig) for x in ["self","v_self"]))
    print(f"{name}: {len(frames)}帧, ext={ext_world}, self={self_ref}, 桥接权重={bridge}")

# 第四维量度：桥接帧占比
l1_br = sum(1 for f in l1.memory.frames 
            if "world" in (f.sig_full or f.sig) and "self" in (f.sig_full or f.sig))
l2_br = sum(1 for f in l2.memory.frames 
            if "v_l1" in (f.sig_full or f.sig) and "v_self" in (f.sig_full or f.sig))
l3_br = sum(1 for f in l3.memory.frames if "v_v_l1" in (f.sig_full or f.sig))

print(f"\n第四维结构：")
print(f"  L1桥(l1──self): {l1_br}帧 → '我看见世界'")
print(f"  L2桥(v_l1──v_self): {l2_br}帧 → '我看见我看世界'")
print(f"  L3桥(v_v_l1...): {l3_br}帧 → '我看见...看见我看世界'")
print(f"  {'✓ 自指链建立' if l1_br>0 and l2_br>0 and l3_br>0 else '◦ 自指链不完整'}")
