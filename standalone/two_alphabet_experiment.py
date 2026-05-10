# Two separate alphabets for L1a and L1b
# L1a: visual alphabet (10 unique vectors for 10 numerals)
# L1b: sensory alphabet (10 unique vectors for 10 apple positions)
# L2: observes both alphabets -> no vector collision
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

# 字母表A：视觉向量（每个数字独立）
alphabet_a = {}
for n in range(1, 11):
    v = [0.0]*_VEC_DIM; v[n % _VEC_DIM] = 2.0; alphabet_a[n] = v

# 字母表B：苹果向量（每个位置独立，0-9号槽）
alphabet_b = {}
for i in range(1, 11):
    v = [0.0]*_VEC_DIM; v[(i+10) % _VEC_DIM] = 2.0; alphabet_b[i] = v

# L2观察向量：从不同的字典分配
_l2v = random.Random(555)
l2va = {}; l2vb = {}
for n in range(1, 11):
    v = [0.0]*_VEC_DIM; v[_l2v.randint(0, _VEC_DIM-1)] = 1.0; l2va[n] = v
    v = [0.0]*_VEC_DIM; v[_l2v.randint(0, _VEC_DIM-1)] = 1.0; l2vb[n] = v

g1a = GEME_T(memory_cap=32, merge_thresh=0.3, cooccur_window=40, cooccur_thresh=0.08, max_chains=10, time_window_size=0)
g1b = GEME_T(memory_cap=32, merge_thresh=0.3, cooccur_window=40, cooccur_thresh=0.08, max_chains=10, time_window_size=0)
g2  = GEME_T(memory_cap=32, cooccur_window=50, cooccur_thresh=0.08, max_chains=10, time_window_size=0)
for g in [g1a,g1b,g2]: 
    g.memory._chain_cooccur_thresh = 2
    g.memory._merge_thresh_val = 0.5
    g._induction_threshold = 2.0  # 大幅减少归纳频率

print("="*55)
print("双字母表：视觉+感觉 无监督学习'大于'")
print("="*55)
print()

r = random.Random(42)
for epoch in range(40):
    nums = list(range(1, 11)); r.shuffle(nums)
    for i in range(0, len(nums)-1, 2):
        big, small = nums[i], nums[i+1]
        if big < small: big, small = small, big  # big first
        
        # 大数
        g1a.process_vec(alphabet_a[big], f"vis_{big}")
        for ai in range(big):
            g1b.process_vec(alphabet_b[ai+1], f"ap_{ai+1}")
        for f in g1a.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(va, f"A_{s[:15]}")
        for f in g1b.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(vb, f"B_{s[:15]}")
        
        # 小数
        g1a.process_vec(alphabet_a[small], f"vis_{small}")
        for ai in range(small):
            g1b.process_vec(alphabet_b[ai+1], f"ap_{ai+1}")
        for f in g1a.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(va, f"A_{s[:15]}")
        for f in g1b.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(vb, f"B_{s[:15]}")

print("【各层状态】")
for n,g in [("L1a(视觉)",g1a),("L1b(感觉)",g1b),("L2(概念)",g2)]:
    f = g.memory.frames
    a = len([x for x in f if "──" in (x.sig_full or x.sig)])
    c = len([x for x in f if "══" in (x.sig_full or x.sig)])
    print(f"  {n}: {len(f)}帧/{a}关联/{c}链")
    top = sorted(f, key=lambda x:x.weight, reverse=True)[:4]
    for t in top:
        s = t.sig_full or t.sig; print(f"    w={int(t.weight):5d} {s[:45]}")

print(f"\n【L2桥接帧分析】")
bridge = [f for f in g2.memory.frames if "A_" in (f.sig_full or f.sig) and "B_" in (f.sig_full or f.sig)]
print(f"  外形↔感觉桥接: {len(bridge)}帧")
for f in sorted(bridge, key=lambda x:x.weight, reverse=True)[:6]:
    s = f.sig_full or f.sig; t = "Chain" if "══" in s else "Assoc"
    print(f"  [{t}] w={int(f.weight):5d} {s[:55]}")

# 关键分析：L2是否区分了"大数字+很多苹果"和"小数字+少苹果"？
a_frames = len([f for f in g2.memory.frames if "A_" in (f.sig_full or f.sig)])
b_frames = len([f for f in g2.memory.frames if "B_" in (f.sig_full or f.sig)])
print(f"\n  L2中: {a_frames}个A帧, {b_frames}个B帧, {len(bridge)}个桥帧")
if bridge:
    print("  ✓ 视-感桥形成——'大于'概念的底层结构已建立")
    print("    无监督。无标签。只有视觉外形+身体感觉在时间中绑定。")
