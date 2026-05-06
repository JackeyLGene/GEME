# 单位圆 x^2+y^2=1 匀速遍历——GEME学到什么
# 输入是纯二维标准化向量。GEME能"意识到"它们在同一个流形上吗？
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

g = GEME(memory_cap=64, cooccur_window=80, cooccur_thresh=0.08, max_chains=20)
g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0

# 单位圆匀速遍历
for i in range(5000):
    theta = 2 * math.pi * 1.0 * i * 0.01
    v = [0.0]*_D27
    v[0] = math.cos(theta)   # x
    v[1] = math.sin(theta)   # y
    # 其余维度保持0
    g.process_vec(v, f"u")

print("="*55)
print("单位圆 x^2+y^2=1 遍历——GEME学到了什么")
print("="*55)
print()

frames = g.memory.frames
print(f"总帧数: {len(frames)}")

# 分析帧类型
circ = [f for f in frames if "u" in (f.sig_full or f.sig)]
chain = [f for f in frames if "══" in (f.sig_full or f.sig)]
assoc = [f for f in frames if "──" in (f.sig_full or f.sig) and "══" not in (f.sig_full or f.sig)]
plain = [f for f in frames if not any(x in (f.sig_full or f.sig) for x in ["══", "──"])]

print(f"  圆形位置帧: {len(circ)}")
print(f"  链帧: {len(chain)}")
print(f"  关联帧: {len(assoc)}")
print(f"  孤立帧: {len(plain)}")

print(f"\n【前15帧】")
for f in sorted(frames, key=lambda x: x.weight, reverse=True)[:15]:
    s = f.sig_full or f.sig[:45]
    t = "○" if (s.count("──") + s.count("══")) == 0 else ("─" if "──" in s else "=")
    print(f"  {t} w={int(f.weight):5d} {s}")

# 检查：是否有"圆流形"帧？即所有位置帧的高阶关联
# 寻找是关联帧且包含多个不同u_xxx的帧
manifold_frames = [f for f in assoc if ("u" in (f.sig_full or f.sig))]
# 检查其中签名的复杂度（包含的u帧数量）
print(f"\n【流形帧分析】")
if len(manifold_frames) > 0:
    mf_top = sorted(manifold_frames, key=lambda x: x.weight, reverse=True)[:5]
    for f in mf_top:
        s = f.sig_full or f.sig
        # 统计s中包含多少个独立帧记号
        parts = s.replace("══", "─").split("─")
        unique = set(p.strip() for p in parts if p.strip())
        print(f"  w={int(f.weight):5d} [{len(unique)}个态] {s[:50]}")
else:
    print("  (无显式流形帧, 流形隐含在帧链结构中)")

# 每个帧的平均跨度（角覆盖）
if len(circ) > 1:
    angles = []
    for f in circ:
        s = f.sig_full or f.sig
        # 粗略估计：帧创建时的角度≈帧内第一次出现的位置
        i = int(s.split("_")[-1]) if "_" in s and s.split("_")[-1].isdigit() else 0
        angles.append(2 * math.pi * 1.0 * i * 0.01)
    angles.sort()
    gaps = [(angles[(i+1)%len(angles)] - angles[i]) % (2*math.pi) for i in range(len(angles))]
    print(f"\n帧间角距（平均）: {statistics.mean(gaps)*180/math.pi:.1f}° ± {statistics.stdev(gaps)*180/math.pi:.1f}°")
    print(f"帧数×角距 = {len(circ) * statistics.mean(gaps):.1f} (≈2π={2*math.pi:.1f})")
