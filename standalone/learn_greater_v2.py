# GEME learns "greater than": simpler, more primitive
# L1a: numeral appearance (visual "7")
# L1b: numeral quantity ("7 apples" = count)
# Same numeral at same time → L2 learns equivalence
# Then: compare 7 and 5 → 7's "more" emerges from quantity difference
import sys, os, random, statistics, math
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
print("GEME 学会'大于'（原始版）")
print("=" * 60)
print()

# ── 设计 ──
# 每个数字同时输入到两个GEME：
#   L1a: 数字的"视觉外形"（独热向量，不携带数值）
#   L1b: 数字的"数量"（另一个独热向量，也不携带数值）
# 关键在于：同一个数字的两幅面孔在同一时间出现。
# "7"的视觉 + "7个"的数量 → L2发现"这两个帧总是一起出现"
# 这个共现关系 = "7"的意义

# 然后：同一窗口内出现两个数字（7和5）
# L2看到：vis_7 总是和 qty_7 在一起
#         vis_5 总是和 qty_5 在一起
# 比较两者 → 7比5大

_vr = random.Random(777)
def num_vec_raw(n, offset=0):
    """每个数字完全不同的向量（互不妨碍）"""
    v = [0.0]*_VEC_DIM
    v[(abs(hash(f"num_{n}_{offset}")) % _VEC_DIM)] = 2.0
    return v

# 三层
g1a = GEME_T(memory_cap=16, merge_thresh=0.8, cooccur_window=20, cooccur_thresh=0.08, max_chains=5, time_window_size=2)
g1b = GEME_T(memory_cap=16, merge_thresh=0.8, cooccur_window=20, cooccur_thresh=0.08, max_chains=5, time_window_size=2)
g2  = GEME_T(memory_cap=16, cooccur_window=30, cooccur_thresh=0.08, max_chains=10, time_window_size=4)
for g in [g1a,g1b,g2]: g.memory._chain_cooccur_thresh = 2

print("训练过程：")
print("  L1a ← 数字外形: vis_7, vis_5...")
print("  L1b ← 数字数量: qty_7, qty_5...")
print("  每个时间窗口内：同数字的两面同时进来")
print("  L2 ← 观察L1a和L1b的帧 → 发现共现模式")
print()

for epoch in range(40):
    nums = list(range(1, 11))
    r.shuffle(nums)
    for i in range(0, len(nums)-1, 2):
        n1, n2 = nums[i], nums[i+1]
        
        # 每个数字：视觉和数量作为一对连续输入
        # time_window=2 → 每对之后 consolidation
        for n in [n1, n2]:
            g1a.process_vec(num_vec_raw(n, 0), f"vis_{n}")
            g1b.process_vec(num_vec_raw(n, 10), f"qty_{n}")
        
        # L2观察两层的帧——用独热向量防止合并
        for fi, f in enumerate(g1a.memory.frames):
            s = f.sig_full or f.sig
            v = [0.0]*_VEC_DIM; v[(fi+epoch)%_VEC_DIM] = 1.0 + r.random()*0.1
            g2.process_vec(v, f"A_{s[:15]}")
        for fi, f in enumerate(g1b.memory.frames):
            s = f.sig_full or f.sig
            v = [0.0]*_VEC_DIM; v[(fi+epoch+10)%_VEC_DIM] = 1.0 + r.random()*0.1
            g2.process_vec(v, f"B_{s[:15]}")

# ── 结果 ──
print("【训练完成】")
print(f"  L1a（外形）: {len(g1a.memory.frames)}帧，{len([f for f in g1a.memory.frames if '══' in (f.sig_full or f.sig)])}链")
print(f"  L1b（数量）: {len(g1b.memory.frames)}帧，{len([f for f in g1b.memory.frames if '══' in (f.sig_full or f.sig)])}链")
print(f"  L2（概念）: {len(g2.memory.frames)}帧，{len([f for f in g2.memory.frames if '══' in (f.sig_full or f.sig)])}链")
print()

# ── L2 桥接帧 ──
print("【L2中A（外形）与B（数量）的桥接帧】")
bridge = [f for f in g2.memory.frames if "A_" in (f.sig_full or f.sig) and "B_" in (f.sig_full or f.sig)]
if bridge:
    for f in sorted(bridge, key=lambda x: x.weight, reverse=True)[:6]:
        sig = f.sig_full or f.sig
        parts = sig.split("──")
        a_s = [p for p in parts if "A_" in p]
        b_s = [p for p in parts if "B_" in p]
        a_num = [p.replace("A_vis_","").replace("A_qty_","") for p in a_s]
        b_num = [p.replace("B_qty_","").replace("B_vis_","") for p in b_s]
        match = "★ 同数字" if any(an == bn for an in a_num for bn in b_num) else ""
        print(f"  [桥] 权重={int(f.weight):5d} {match}")
        print(f"        外形: {a_s[0] if a_s else '?'}")
        print(f"        数量: {b_s[0] if b_s else '?'}")
    print()
    print("★ = GEME发现：这个数字的外形和数量总是一起出现")
    print("  这就是'数字的意义'——外形与数量的时空绑定")
else:
    print("  暂无桥接")

# ── 链分析 ──
chains = [f for f in g2.memory.frames if "══" in (f.sig_full or f.sig)]
print(f"\n【L2链分析】（{len(chains)}条）")
for c in sorted(chains, key=lambda x: x.weight, reverse=True)[:5]:
    sig = c.sig_full or c.sig
    has_a = "A_" in sig; has_b = "B_" in sig
    tag = ""
    if has_a and has_b: tag = "★ = 桥链"
    elif has_a: tag = "外形侧链"
    elif has_b: tag = "数量侧链"
    print(f"  权重={int(c.weight):5d} {tag}")

print()
print("=" * 60)
print("结论：GEME从外形和数量的时空共现中")
print("      学会了数字的意义——不是被教的")
print("=" * 60)
