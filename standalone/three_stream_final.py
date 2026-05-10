# 三流：视觉+触觉+真假 各用独立字母表
import sys, os, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM

class GEME_T(GEME):
    def describe(self):
        f = self.memory.frames
        if not f: return "空"
        top = sorted(f, key=lambda x: x.weight, reverse=True)
        a = len([x for x in f if "──" in (x.sig_full or x.sig)])
        c = len([x for x in f if "══" in (x.sig_full or x.sig)])
        return f"{len(f)}帧/{a}关联/{c}链 | 顶: w={int(top[0].weight)}"

r = random.Random(42)

# 三个字母表：使用不同维度区间，永不相交
# L1a (视觉): dim 0-9  (数字1-10)
# L1b (触觉): dim 10   (苹果 = 1)
# L1c (真假): dim 11-12 (真=11, 假=12)

alpha_a = {}
for n in range(1, 11):
    v = [0.0]*_VEC_DIM; v[n-1] = 1.0; alpha_a[n] = v  # dim 0-9

apple_vec = [0.0]*_VEC_DIM; apple_vec[10] = 1.0  # dim 10

true_vec = [0.0]*_VEC_DIM; true_vec[11] = 1.0   # dim 11
false_vec = [0.0]*_VEC_DIM; false_vec[12] = 1.0  # dim 12

# L2 字母表
va = [0.0]*_VEC_DIM; va[13] = 1.0  # 观察A
vb = [0.0]*_VEC_DIM; vb[14] = 1.0  # 观察B
vc = [0.0]*_VEC_DIM; vc[15] = 1.0  # 观察C

g1a = GEME_T(memory_cap=32, cooccur_window=40, cooccur_thresh=0.08, max_chains=10)
g1b = GEME_T(memory_cap=32, cooccur_window=40, cooccur_thresh=0.08, max_chains=10)
g1c = GEME_T(memory_cap=16, cooccur_window=40, cooccur_thresh=0.08, max_chains=5)
g2  = GEME_T(memory_cap=64, cooccur_window=50, cooccur_thresh=0.08, max_chains=10)
for g in [g1a,g1b,g1c,g2]:
    g.memory._chain_cooccur_thresh = 2
    g.memory._merge_thresh_val = 0.5
    g._induction_threshold = 2.0
g2._induction_threshold = 5.0  # L2需要更多时间积累跨域帧

print("="*55)
print("三流独立字母表")
print("  L1a [dim0-9] = 视觉 (vis_1..vis_10)")
print("  L1b [dim10]  = 触觉 (apple x N)")
print("  L1c [dim11-12] = 真假 (true/false)")
print("="*55)
print()

gt_pairs = [(7,5),(8,3),(9,4),(10,6)]
for epoch in range(20):
    r.shuffle(gt_pairs)
    for big, small in gt_pairs:
        g1a.process_vec(alpha_a[big], f"vis_{big}")
        g1a.process_vec(alpha_a[small], f"vis_{small}")
        for _ in range(big): g1b.process_vec(apple_vec, "apple")
        for _ in range(small): g1b.process_vec(apple_vec, "apple")
        g1c.process_vec(true_vec, "true")
        # FALSE
        g1a.process_vec(alpha_a[small], f"vis_{small}")
        g1a.process_vec(alpha_a[big], f"vis_{big}")
        for _ in range(big): g1b.process_vec(apple_vec, "apple")
        for _ in range(small): g1b.process_vec(apple_vec, "apple")
        g1c.process_vec(false_vec, "false")
    # 每轮结束后L2交错观察三层
    a_frames = list(g1a.memory.frames)
    b_frames = list(g1b.memory.frames)
    c_frames = list(g1c.memory.frames)
    max_len = max(len(a_frames), len(b_frames), len(c_frames))
    for idx in range(max_len):
        if idx < len(a_frames):
            s = a_frames[idx].sig_full or a_frames[idx].sig
            g2.process_vec(va, f"A_{s[:15]}")
        if idx < len(b_frames):
            s = b_frames[idx].sig_full or b_frames[idx].sig
            g2.process_vec(vb, f"B_{s[:15]}")
        if idx < len(c_frames):
            s = c_frames[idx].sig_full or c_frames[idx].sig
            g2.process_vec(vc, f"C_{s[:15]}")

print("【各层状态】")
for n,g in [("L1a(视觉)",g1a),("L1b(触觉)",g1b),("L1c(真假)",g1c),("L2(概念)",g2)]:
    print(f"  {n}: {g.describe()}")
    for t in sorted(g.memory.frames, key=lambda x:x.weight, reverse=True)[:4]:
        s = t.sig_full or t.sig; print(f"    w={int(t.weight):5d} {s[:45]}")

print(f"\n【L2桥接分析】")
all_f = g2.memory.frames
ab = [f for f in all_f if "A_" in (f.sig_full or f.sig) and "B_" in (f.sig_full or f.sig)]
ac = [f for f in all_f if "A_" in (f.sig_full or f.sig) and "C_" in (f.sig_full or f.sig)]
bc = [f for f in all_f if "B_" in (f.sig_full or f.sig) and "C_" in (f.sig_full or f.sig)]
abc = [f for f in all_f if "A_" in (f.sig_full or f.sig) and "B_" in (f.sig_full or f.sig) and "C_" in (f.sig_full or f.sig)]
print(f"  视觉↔触觉: {len(ab)}")
print(f"  视觉↔真假: {len(ac)}")
print(f"  触觉↔真假: {len(bc)}")
print(f"  三域全连: {len(abc)}")
if abc:
    print("\n  L2三域全连！'大于'概念完整涌现：")
    for f in sorted(abc, key=lambda x:x.weight, reverse=True):
        s = f.sig_full or f.sig; print(f"    w={int(f.weight):5d} {s[:60]}")
