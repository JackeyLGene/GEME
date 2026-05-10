# Same input stream, different merge thresholds → different realities
# threshold = resolution of generated reality
import sys, math, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM

_r = random.Random(42)

# Fixed 27-dim sinusoidal time vector (same for all runs)
def tv(t):
    v = [0.0]*_VEC_DIM
    v[0] = t/(t+1)
    return v

# Fixed input stream: 4 signals at different frequencies
# A (fast, period 0.02), B (med, 0.1), C (slow, 0.5), D (very slow, 2.0)
# Same stream, fed to 4 different GEMEs with different thresholds
signals = []
t = 0.0; tA=tB=tC=tD=0.0
while t < 10.0:
    t += 0.001
    if t-tA >= 0.02:
        signals.append((t, "A")); tA = t
    if t-tB >= 0.1:
        signals.append((t, "B")); tB = t
    if t-tC >= 0.5:
        signals.append((t, "C")); tC = t
    if t-tD >= 2.0:
        signals.append((t, "D")); tD = t

print("="*55)
print("合并阈值 = 实在的分辨率")
print("固定输入流：A(0.02) B(0.1) C(0.5) D(2.0)")
print("="*55)

for thresh in [0.05, 0.1, 0.2, 0.5, 1.0]:
    g = GEME(memory_cap=16, cooccur_window=60, cooccur_thresh=0.08, max_chains=10)
    g.memory.preserve_sig = True
    g.memory._merge_thresh_val = thresh
    g.memory._merge_dists = [thresh]*50   # 自适应返回=thresh
    g._induction_threshold = 2.0
    
    for _t, sig in signals:
        g.process_vec(tv(_t), f"sig_{sig}")
    
    # Analyze: count frames per signal type
    a = sum(1 for f in g.memory.frames if "sig_A" in (f.sig_full or f.sig))
    b = sum(1 for f in g.memory.frames if "sig_B" in (f.sig_full or f.sig))
    c = sum(1 for f in g.memory.frames if "sig_C" in (f.sig_full or f.sig))
    d = sum(1 for f in g.memory.frames if "sig_D" in (f.sig_full or f.sig))
    total = len(g.memory.frames)
    
    # Dominant frame
    top = sorted(g.memory.frames, key=lambda x: x.weight, reverse=True)
    top_str = f"{top[0].sig[:30]} w={int(top[0].weight)}" if top else "-"
    
    print(f"\n阈值={thresh:4.2f} → {total}帧")
    print(f"  A帧:{a} B帧:{b} C帧:{c} D帧:{d}")
    print(f"  主帧: {top_str}")
    
    # Reality interpretation
    if a == total or total <= 2:
        print(f"  实在: 非常粗糙——只有高频信号能被区分")
    elif a > 0 and b > 0 and c == 0 and d == 0:
        print(f"  实在: 中频——A和B存在，C和D被噪声化")
    elif a > 0 and b > 0 and c > 0 and d == 0:
        print(f"  实在: 较细——A,B,C独立存在，D坍缩进C的阴影")
    elif a > 0 and b > 0 and c > 0 and d > 0:
        print(f"  实在: 最细——所有信号独立存在")
        print(f"  但D只有{d}帧，频率太低，权重无法维持")

print(f"\n{'='*55}")
print("同一输入流。不同阈值→不同实在。")
print("阈值不是参数——是实在的分辨率。")
