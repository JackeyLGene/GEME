# GEME sees two numbers + their apples. L2 decides what "greater" means.
import sys, os, random, statistics
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

_av = random.Random(777)
num_vecs = {}
for n in range(1, 11):
    v = [0.0]*_VEC_DIM; v[_av.randint(0, _VEC_DIM-1)] = 2.0; num_vecs[n] = v

# 每个位置的苹果用不同向量（最多10个苹果）
_apv = random.Random(888)
apple_pos_vecs = {i: [0.0]*_VEC_DIM for i in range(1, 11)}
for i, v in apple_pos_vecs.items():
    v[_apv.randint(0, _VEC_DIM-1)] = 2.0

g1a = GEME_T(memory_cap=16, merge_thresh=0.1, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=2)
g1b = GEME_T(memory_cap=16, merge_thresh=0.1, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=2)
g2 = GEME_T(memory_cap=16, cooccur_window=30, cooccur_thresh=0.1, max_chains=10, time_window_size=6)
for g in [g1a,g1b,g2]: g.memory._chain_cooccur_thresh = 2

va = [0.0]*_VEC_DIM; va[0] = 1.0
vb = [0.0]*_VEC_DIM; vb[1] = 1.0

print("="*55)
print("让L2自己决定'大于'是什么")
print("="*55)
print()

for epoch in range(50):
    nums = list(range(1, 11))
    r.shuffle(nums)
    for i in range(0, len(nums)-1, 2):
        n1, n2 = nums[i], nums[i+1]  # e.g., 7 and 5
        
        # 同一时间窗口：输入两个数字
        for n in [n1, n2]:
            g1a.process_vec(num_vecs[n], f"vis_{n}")
            # L1b: 每个苹果不同向量+不同签名（苹果1, 苹果2...）
            for ai in range(n):
                g1b.process_vec(apple_pos_vecs[ai+1], f"apple_{ai+1}")
        
        # L2：A信号收到一次数字外形
        for f in g1a.memory.frames:
            s = f.sig_full or f.sig; g2.process_vec(va, f"A_{s[:15]}")
        # L2：B信号——每个苹果位置一个独立信号
        for f in g1b.memory.frames:
            s = f.sig_full or f.sig
            if "apple" in s:
                # 每个苹果位置用不同向量
                for ai in range(1, 11):
                    if f"apple_{ai}" in s:
                        v = [0.0]*_VEC_DIM
                        v[ai % _VEC_DIM] = 1.0
                        g2.process_vec(v, f"B_apple_{ai}")
                        break

print(f"L1a（外形）: {len(g1a.memory.frames)}帧")
print(f"L1b（质量）: {len(g1b.memory.frames)}帧, apple权重={int(sum(f.weight for f in g1b.memory.frames if 'apple' in (f.sig_full or f.sig)))}")
print(f"L2（概念）: {len(g2.memory.frames)}帧, {len([f for f in g2.memory.frames if '══' in (f.sig_full or f.sig)])}链")
print(f"L2自观察次数: {g2.memory._self_observe_count}")
print()

print("L2帧（让它自己说的）：")
for f in sorted(g2.memory.frames, key=lambda x: x.weight, reverse=True)[:10]:
    sig = f.sig_full or f.sig
    t = "CHAIN" if "══" in sig else ("ASSOC" if "──" in sig else "FRAME")
    is_a = "A_" in sig
    is_b = "B_" in sig
    tag = ""
    if is_a and is_b: tag = "← 跨域桥！"
    elif is_a: tag = "外形侧"
    elif is_b: tag = "质量侧"
    print(f"  [{t}] w={int(f.weight):5d} {sig[:50]} {tag}")

bridge = [f for f in g2.memory.frames if "A_" in (f.sig_full or f.sig) and "B_" in (f.sig_full or f.sig)]
if bridge:
    print(f"\n跨域桥数量: {len(bridge)}")
    print("L2自己建立了外形和质量的连接")
else:
    print(f"\nL2还没有跨域桥——它看到的是分离的外形和质量")

print(f"\n{'='*55}")
print("L2自由演化——不预测结果。这就是系统看到的。")
