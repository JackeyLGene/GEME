# 模拟宇宙：输入密度 = 质量 → 时间膨胀
# 高密度区域：阈值更细，帧生成率更高 → 时间变慢
# 低密度区域：阈值更粗，帧生成率更低 → 时间变快
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM

_r = random.Random(42)

# ── 空间设定 ──
# 一维线：左端高密度（质量M），右端低密度（无质量）
# 坐标x从0-100。密度函数ρ(x) = M / (1 + x)
M = 5.0  # "质量"

def density(x):
    return M / (1 + x * 0.1)

def signal_id_from_x(x, t):
    """从空间位置和时间生成信号"""
    return f"evt_{int(x)}_{int(t*10)}"

# ── 生成输入流 ──
# 高密度处产生更多输入
inputs = []
for t in range(1000):  # 1000个"系统时间步"
    for x in range(0, 100, 5):  # 每5个单位采样一次
        dens = density(x)
        # 当前空间位置的输入数量正比于密度
        num_inputs = max(1, int(dens * _r.random() * 2))
        for _ in range(num_inputs):
            vec = [0.0]*_VEC_DIM
            vec[x % _VEC_DIM] = dens  # 位置和密度编码在向量中
            inputs.append((x, dens, vec))

_r.shuffle(inputs)  # 时序混合——就像真实的时空

print("="*55)
print("模拟宇宙：密度驱动的时间膨胀")
print("="*55)
print(f"质量 M={M}")
print(f"输入总数: {len(inputs)}")
print()

# ── GEME ──
g = GEME(memory_cap=32, cooccur_window=60, cooccur_thresh=0.08, max_chains=10)
g.memory.preserve_sig = True
g._induction_threshold = 2.0

for x, dens, vec in inputs:
    sig = f"x_{x//5 * 5}"  # 按25个空间位置分桶
    g.process_vec(vec, sig)

# ── 分析：每个空间位置的帧生成率 ──
frames = g.memory.frames
position_data = {}

for bucket in range(0, 100, 5):
    bucket_sig = f"x_{bucket}"
    bucket_frames = [f for f in frames if f"x_{bucket}" in (f.sig_full or f.sig)]
    total_w = sum(f.weight for f in bucket_frames)
    count = len(bucket_frames)
    pos_x = bucket + 2.5  # 中间点
    dens = density(pos_x)
    position_data[pos_x] = {
        "density": dens,
        "frames": count,
        "total_weight": total_w,
        "weight_per_frame": total_w / max(count, 1),
    }

print("空间位置 | 密度 | 帧数 | 总权重 | 每帧权重 (帧生成率)")
print("-"*55)
for x in sorted(position_data.keys()):
    d = position_data[x]
    bar = "█" * min(int(d["weight_per_frame"]/50), 20)
    print(f" x={x:4.0f}  | ρ={d['density']:.2f} | {d['frames']:2d}帧 | {d['total_weight']:6.0f} | {d['weight_per_frame']:6.0f} {bar}")

# ── 时间膨胀效应 ──
print(f"\n{'='*55}")
print("时间膨胀分析：")
high_d = [d for x,d in position_data.items() if d['density'] > 2.0]
low_d = [d for x,d in position_data.items() if d['density'] < 1.0]
if high_d and low_d:
    h_avg = statistics.mean(d['weight_per_frame'] for d in high_d)
    l_avg = statistics.mean(d['weight_per_frame'] for d in low_d)
    ratio = h_avg / max(l_avg, 0.001)
    print(f"  高密度区(ρ>2): 平均每帧权重={h_avg:.0f}")
    print(f"  低密度区(ρ<1): 平均每帧权重={l_avg:.0f}")
    print(f"  帧生成率比(高/低) = {ratio:.2f}")
    if ratio > 1.3:
        print("  ✓ 高密度区的帧生成率更高——时间在高密度区流动更慢")
        print("  ✓ GEME展示了密度-时间膨胀的定性对应")
    else:
        print("  - 时间膨胀效应不显著——需要更大质量M或更多输入")
