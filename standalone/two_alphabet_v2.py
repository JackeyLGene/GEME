# 真正的双字母表：L1a用27维视觉、L1b用2维二进制 {0,1}
import sys, os, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

class GEME_T(GEME):
    def observe_ext(self, sigs, src="e"):
        ft = self.memory._step_counter
        for sig in sigs:
            sid = f"{src}_{sig[:18]}"
            self.memory._window.append((sid, ft, (0.0,)*_VEC_DIM))

# 字母表A（视觉）：10个数字用10个不同向量
alpha_a = {}
for n in range(1, 11):
    v = [0.0]*_VEC_DIM; v[n % _VEC_DIM] = 1.0; alpha_a[n] = v

# 字母表B（二进制）：只有"有"和"无"
# 有苹果 = [1, 0, 0, ...]
# 无苹果 = [0, 0, 0, ...]
apple_yes = [1.0] + [0.0]*(_VEC_DIM-1)
apple_no  = [0.0]*_VEC_DIM

# L2的向量：兼顾观测A和B时需要区分
# 但实际上L2不应该直接看L1b的帧——L2应该看"数量"编码
# 最简单：L2直接收到（外形向量+数量值）

g1a = GEME_T(memory_cap=32, merge_thresh=0.3, cooccur_window=40, cooccur_thresh=0.08, max_chains=10)
g1b = GEME_T(memory_cap=2,  merge_thresh=0.3, cooccur_window=40, cooccur_thresh=0.08, max_chains=2)  # memory_cap=2就够了
g2  = GEME_T(memory_cap=32, cooccur_window=50, cooccur_thresh=0.08, max_chains=10)
for g in [g1a,g1b,g2]:
    g.memory._chain_cooccur_thresh = 2
    g.memory._merge_thresh_val = 0.5
    g._induction_threshold = 2.0

r = random.Random(42)
print("="*55)
print("真正的双字母表")
print("  L1a: 27维视觉向量（10种数字）")
print("  L1b: 2维二进制向量 [1,0]=有苹果, [0,0]=无")
print("  L2: 同时观察两侧时间绑定")
print("="*55)
print()

for epoch in range(30):
    nums = list(range(1, 11)); r.shuffle(nums)
    for i in range(0, len(nums)-1, 2):
        big, small = nums[i], nums[i+1]
        if big < small: big, small = small, big
        
        # 大数
        g1a.process_vec(alpha_a[big], f"vis_{big}")
        for _ in range(big):
            g1b.process_vec(apple_yes, "apple")
        g1b.process_vec(apple_no, "apple")  # 结束标记
        
        # L2观察两侧（用不同向量避免合并）
        va = [0.0]*_VEC_DIM; va[0] = 1.0
        vb = [0.0]*_VEC_DIM; vb[1] = 1.0
        for f in g1a.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(va, f"A_{s[:15]}")
        for f in g1b.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(vb, f"B_{s[:15]}")
        
        # 小数
        g1a.process_vec(alpha_a[small], f"vis_{small}")
        for _ in range(small):
            g1b.process_vec(apple_yes, "apple")
        g1b.process_vec(apple_no, "apple")
        for f in g1a.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(va, f"A_{s[:15]}")
        for f in g1b.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(vb, f"B_{s[:15]}")

print("【训练结果】")
for n,g in [("L1a(视觉)",g1a),("L1b(二进制)",g1b),("L2(概念)",g2)]:
    f = g.memory.frames
    a = len([x for x in f if "──" in (x.sig_full or x.sig)])
    c = len([x for x in f if "══" in (x.sig_full or x.sig)])
    print(f"  {n}: {len(f)}帧/{a}关联/{c}链")
    for t in sorted(f, key=lambda x:x.weight, reverse=True)[:3]:
        s = t.sig_full or t.sig; print(f"    w={int(t.weight):5d} {s[:45]}")

bridge = [x for x in g2.memory.frames if "A_" in (x.sig_full or x.sig) and "B_" in (x.sig_full or x.sig)]
print(f"\n跨域桥: {len(bridge)}帧")
for f in sorted(bridge, key=lambda x:x.weight, reverse=True)[:4]:
    s = f.sig_full or f.sig; t = "C" if "══" in s else "A"
    print(f"  [{t}] w={int(f.weight):5d} {s[:50]}")

print(f"\n{'='*55}")
print("L2各帧签名：")
for f in sorted(g2.memory.frames, key=lambda x:x.weight, reverse=True):
    s = f.sig_full or f.sig
    tags = []
    if "A_" in s: tags.append("A")
    if "B_" in s: tags.append("B")
    print(f"  w={int(f.weight):5d} {s[:50]} [{'+'.join(tags) if tags else ''}]")
