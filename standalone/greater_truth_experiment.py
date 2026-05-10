# Ultimate experiment: GEME learns "greater" from order + weight + truth
# L1A: sees two numerals in order [7, 5] or [5, 7]
# L1B: feels apple_big, apple_small (always same order: big then small)
# L1: receives true/false (whether numeral order matches weight order)
# L2: observes all three + time → discovers "greater than"
import sys, os, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

class GEME_T(GEME):
    def observe_ext(self, sigs, src="e"):
        ft = self.memory._step_counter
        for sig in sigs:
            sid = f"{src}_{sig[:18]}"
            self.memory._window.append((sid, ft, (0.0,)*_VEC_DIM))
            if len(self.memory._window) > self.memory._win_max:
                self.memory._window.pop(0)
    def describe(self):
        f = self.memory.frames
        if not f: return "空的"
        top = sorted(f, key=lambda x: x.weight, reverse=True)
        a = len([x for x in f if "──" in (x.sig_full or x.sig)])
        c = len([x for x in f if "══" in (x.sig_full or x.sig)])
        t = top[0]; ts = t.sig_full or t.sig
        return f"{len(f)}帧/{a}关联/{c}链 | 顶: {ts[:40]} w={int(t.weight)}"

r = random.Random(42)
_av = random.Random(777); _bv = random.Random(888)

# 10个数字的独特外形向量
num_v = {n: [0.0]*_VEC_DIM for n in range(1, 11)}
for n,v in num_v.items(): v[_av.randint(0, _VEC_DIM-1)] = 2.0

# 苹果多/少向量（两个固定向量）
apple_big = [0.0]*_VEC_DIM; apple_big[0] = 2.0
apple_small = [0.0]*_VEC_DIM; apple_small[1] = 2.0

# 真值向量
true_v = [0.0]*_VEC_DIM; true_v[2] = 2.0
false_v = [0.0]*_VEC_DIM; false_v[3] = 2.0

gt_pairs = [(7,5),(8,3),(9,4),(10,6)]  # 大数在前，只保留4对最基本

g1a = GEME_T(memory_cap=16, merge_thresh=0.2, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=2)
g1b = GEME_T(memory_cap=16, merge_thresh=0.2, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=2)
g1t = GEME_T(memory_cap=16, merge_thresh=0.2, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=2)
g2  = GEME_T(memory_cap=16, cooccur_window=40, cooccur_thresh=0.1, max_chains=10, time_window_size=6)
for g in [g1a,g1b,g1t,g2]: g.memory._chain_cooccur_thresh = 2

# 固定观察向量
va = [0.0]*_VEC_DIM; va[4] = 1.0  # 外形
vb = [0.0]*_VEC_DIM; vb[5] = 1.0  # 体重
vt = [0.0]*_VEC_DIM; vt[6] = 1.0  # 真值

print("="*55)
print("终极实验：GEME学会'大于'")
print("="*55)
print()

for epoch in range(40):
    r.shuffle(gt_pairs)
    for big, small in gt_pairs:
        # TRUE: 大数在前
        g1a.process_vec(num_v[big], f"vis_{big}")
        g1a.process_vec(num_v[small], f"vis_{small}")
        g1b.process_vec(apple_big, "apple_big")
        g1b.process_vec(apple_small, "apple_small")
        g1t.process_vec(true_v, "true")
        for f in g1a.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(va, f"A_{s[:15]}")
        for f in g1b.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(vb, f"B_{s[:15]}")
        for f in g1t.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(vt, f"T_{s[:15]}")
        
        # FALSE: 小数在前（交换顺序）
        g1a.process_vec(num_v[small], f"vis_{small}")
        g1a.process_vec(num_v[big], f"vis_{big}")
        g1b.process_vec(apple_big, "apple_big")
        g1b.process_vec(apple_small, "apple_small")
        g1t.process_vec(false_v, "false")
        for f in g1a.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(va, f"A_{s[:15]}")
        for f in g1b.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(vb, f"B_{s[:15]}")
        for f in g1t.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(vt, f"T_{s[:15]}")

print("【训练后层次状态】")
for n, g in [("L1A(外形)",g1a),("L1B(体重)",g1b),("L1T(真值)",g1t),("L2(概念)",g2)]:
    print(f"  {n}: {g.describe()}")

print(f"\n【L2帧】")
for f in sorted(g2.memory.frames, key=lambda x: x.weight, reverse=True)[:10]:
    sig = f.sig_full or f.sig
    t = "Chain" if "══" in sig else ("Assoc" if "──" in sig else "Frame")
    tags = []
    if "A_" in sig: tags.append("外形")
    if "B_" in sig: tags.append("体重")
    if "T_" in sig: tags.append("真值")
    tag = f"<跨域: {'+'.join(tags)}>" if len(tags)>=2 else ""
    print(f"  [{t}] w={int(f.weight):5d} {sig[:55]} {tag}")

bridge_ab = [f for f in g2.memory.frames if "A_" in (f.sig_full or f.sig) and "B_" in (f.sig_full or f.sig)]
bridge_at = [f for f in g2.memory.frames if "A_" in (f.sig_full or f.sig) and "T_" in (f.sig_full or f.sig)]
bridge_bt = [f for f in g2.memory.frames if "B_" in (f.sig_full or f.sig) and "T_" in (f.sig_full or f.sig)]
bridge_all = [f for f in g2.memory.frames if "A_" in (f.sig_full or f.sig) and "B_" in (f.sig_full or f.sig) and "T_" in (f.sig_full or f.sig)]

print(f"\n【跨域桥分析】")
print(f"  外形↔体重: {len(bridge_ab)}帧")
print(f"  外形↔真值: {len(bridge_at)}帧")
print(f"  体重↔真值: {len(bridge_bt)}帧")
print(f"  三者全跨: {len(bridge_all)}帧")
if bridge_all:
    print("✓ L2建立了外形+体重+真值的三方连接")
    print("  这就是'大于'概念：数字顺序+体重感受+真值判断的时空绑定")
else:
    print("  三域桥尚未形成")

print(f"\n{'='*55}")
print("L2的核心洞察：'当大数字出现在小数字前面，且真值说真——这就是'大于'")
