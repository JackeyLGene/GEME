# 匀速圆周运动：GEME学到什么
# 输入在2D平面匀速转动，GEME跟踪周期运动
import sys, math, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM

_r = random.Random(42)

def run_circle(freq, steps=3000, seed=42):
    """匀速圆周运动频率 f，steps步"""
    r = random.Random(seed)
    g = GEME(memory_cap=32, cooccur_window=60, cooccur_thresh=0.08, max_chains=10)
    g.memory.preserve_sig = True
    g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50
    g._induction_threshold = 2.0
    
    for i in range(steps):
        t = i * 0.01  # 时间推进
        theta = 2 * math.pi * freq * t  # 角度 = 2πft
        v = [0.0]*_VEC_DIM
        v[0] = math.cos(theta) * 0.8 + 0.1  # 归一化到[0,1)左右
        v[1] = math.sin(theta) * 0.8 + 0.1
        g.process_vec(v, f"circ")
    
    frames = g.memory.frames
    # 统计：有多少个独立的"位置帧"（circ帧的数量）
    circ_frames = [f for f in frames if "circ" in (f.sig_full or f.sig)]
    weights = sorted([int(f.weight) for f in circ_frames], reverse=True)
    
    # 均匀性：帧的角分布是否均匀（用帧数的标准差衡量）
    n_frames = len(circ_frames)
    n_unique = len(set((f.sig_full or f.sig).split("──")[0] for f in circ_frames))
    
    return n_frames, weights[:5] if weights else [], len(frames)

# 扫频：从慢到快
print("="*55)
print("匀速圆周运动：GEME学到什么")
print("="*55)
print()

for freq in [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
    n_f, top_w, total = run_circle(freq, 3000)
    period = 1/freq if freq > 0 else float('inf')
    w_str = ", ".join(str(w) for w in top_w[:3]) if top_w else "-"
    status = "帧集离散（完美跟踪）" if n_f > 10 else "墙：无法跟踪" if n_f <= 3 else ""
    print(f"频率 f={freq:4.1f} 周期 T={period:5.2f}: {n_f:2d}个位相帧 [{w_str}] {status}")

print()
print("解释：")
print("  f=0.1 (慢): GEME看到圆的每个角度 → 离散为多个帧 → 周期运动被跟踪")
print("  f=10 (快): GEME看到模糊的圆 → 所有角度合并为少数帧 → 时间壁")
print("  壁 = 角速度超过阈值自适应速度")
