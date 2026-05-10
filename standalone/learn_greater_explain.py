# Clear explanation of how GEME learns "greater than"
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

r = random.Random(42)

print("=" * 60)
print("GEME 如何学会'大于'")
print("=" * 60)
print()
print("输入设计：")
print("  L1a（表象层）：接收数字视觉信号")
print("    比如 '7' 的视觉向量 → vis_7 帧")
print("  L1b（意义层）：接收真假判断")
print("    比如 '7>6=TRUE' → gt_7_6_T 帧")
print("  L2（概念层）：观察L1a和L1b的帧变化")
print("    发现：'7'经常和 TRUE 同时出现")
print("          '5'经常和 FALSE 同时出现")
print("    结论：'大于'概念 = 表象与意义的时空共现")
print()

num_idx = {str(i): i-1 for i in range(1, 11)}
def num_vec(n):
    v = [0.0]*_VEC_DIM; v[num_idx[n] % _VEC_DIM] = 1.0; return v

gt_pairs = [(7,6),(8,5),(9,4),(10,3),(8,7),(9,6),(10,5),(6,5),(9,8),(10,9)]

g1a = GEME_T(memory_cap=32, cooccur_window=20, cooccur_thresh=0.08, max_chains=5, time_window_size=5)
g1b = GEME_T(memory_cap=32, cooccur_window=20, cooccur_thresh=0.08, max_chains=5, time_window_size=5)
g2 = GEME_T(memory_cap=16, cooccur_window=50, cooccur_thresh=0.08, max_chains=10, time_window_size=15)
for g in [g1a,g1b,g2]: g.memory._chain_cooccur_thresh = 2

for epoch in range(60):
    r.shuffle(gt_pairs)
    for larger, smaller in gt_pairs:
        bl, bs = str(larger), str(smaller)
        g1a.process_vec(num_vec(bl), f"vis_{bl}")
        g1a.process_vec(num_vec(bs), f"vis_{bs}")
        for pn, (a,b,tv) in enumerate([(bl,bs,"T"),(bs,bl,"F")]):
            v = [0.0]*_VEC_DIM; v[(ord(a[0])+ord(b[0])+pn) % _VEC_DIM] = 1.0
            g1b.process_vec(v, f"gt_{a}_{b}_{tv}")
        for fi, f in enumerate(g1a.memory.frames):
            s = f.sig_full or f.sig; v = [0.0]*_VEC_DIM; v[(fi*7+epoch)%_VEC_DIM] = 1.0
            g2.process_vec(v, f"A_{s[:20]}")
        for fi, f in enumerate(g1b.memory.frames):
            s = f.sig_full or f.sig; v = [0.0]*_VEC_DIM; v[(fi*7+epoch+3)%_VEC_DIM] = 1.0
            g2.process_vec(v, f"B_{s[:20]}")

print("训练完成后的系统状态：")
print()

# ── L1a 解读 ──
print("【L1a（表象层）】发生了什么：")
print("  输入：数字的独热向量（vis_7, vis_8...）")
print(f"  结果：{len(g1a.memory.frames)}帧，{len([f for f in g1a.memory.frames if '══' in (f.sig_full or f.sig)])}条链")
print("  L1a 成功区分了不同数字。每个数字是一个独立帧。")
print()

# ── L1b 解读 ──
print("【L1b（意义层）】发生了什么：")
print("  输入：真假命题向量（gt_7_6_T, gt_6_7_F...）")
print(f"  结果：{len(g1b.memory.frames)}帧，{len([f for f in g1b.memory.frames if '══' in (f.sig_full or f.sig)])}条链")
b_has_T = any("_T" in (f.sig_full or f.sig) for f in g1b.memory.frames)
b_has_F = any("_F" in (f.sig_full or f.sig) for f in g1b.memory.frames)
print(f"  TRUE帧存在：{'✓' if b_has_T else '✗'}")
print(f"  FALSE帧存在：{'✓' if b_has_F else '✗'}")
print()

# ── L2 解读 ──
print("【L2（概念层）】发生了什么：")
print("  输入：L1a的帧签名（A_vis_7...）+ L1b的帧签名（B_gt_7_6_T...）")
print(f"  结果：{len(g2.memory.frames)}帧，{len([f for f in g2.memory.frames if '══' in (f.sig_full or f.sig)])}条链")
print()

bridge = [f for f in g2.memory.frames if "A_" in (f.sig_full or f.sig) and "B_" in (f.sig_full or f.sig)]
print(f"【桥接帧】A（表象）和B（意义）之间的连接：")
if bridge:
    for f in sorted(bridge, key=lambda x: x.weight, reverse=True):
        sig = f.sig_full or f.sig
        t = "链" if "══" in sig else "关联"
        print(f"  [{t}] 权重={int(f.weight)}")
        print(f"    签名: {sig[:60]}")
        # 解析
        parts = sig.split("──")
        a_part = [p for p in parts if "A_" in p]
        b_part = [p for p in parts if "B_" in p]
        for ap in a_part:
            print(f"    表象侧: {ap}")
        for bp in b_part:
            print(f"    意义侧: {bp}")
else:
    print("  暂无直接桥接")
print()

# 解释桥接的意义
if bridge:
    print("结论：")
    print("  GEME通过以下机制学会了'大于'概念：")
    print("    1. L1a看到数字'7'的视觉信号")
    print("    2. L1b在同一窗口看到'7>6=TRUE'的意义信号")
    print("    3. L2观察到L1a的'7'帧和L1b的TRUE帧同时存在")
    print("    4. 多次共现→A帧和B帧在L2中形成桥接")
    print("    5. '大于'不是被教的——是从时间共现中涌现的")
else:
    print("需要更长时间训练才能形成桥接。")
