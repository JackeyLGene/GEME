# GEME with self-report: describe what it's "thinking"
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

    def describe(self, depth=2):
        """GEME reports what it's 'thinking'.
        depth=1: frame stats only
        depth=2: top frames + interpretation"""
        frames = self.memory.frames
        if not frames:
            return {"voice": "空的。还没有形成帧。", "frames": 0}
        
        top = sorted(frames, key=lambda x: x.weight, reverse=True)
        
        # Statistics
        n = len(frames)
        assocs = [f for f in frames if "──" in (f.sig_full or f.sig)]
        chains = [f for f in frames if "══" in (f.sig_full or f.sig)]
        # Weight distribution
        weights = [f.weight for f in top]
        w_range = f"{min(weights):.0f}-{max(weights):.0f}"
        
        voice = ""
        if n == 1:
            voice = "只有一个帧。"
        elif n <= 3:
            voice = f"有{n}个帧在脑海中。结构在形成。"
        elif n <= 8:
            voice = f"有{n}个帧，{len(assocs)}个关联，{len(chains)}条链。正在理解。"
        else:
            voice = f"{n}个帧，{len(assocs)}个关联，{len(chains)}条链。权重范围{w_range}。"
        
        # Top associations - what is GEME most certain about?
        if assocs:
            best = max(assocs, key=lambda x: x.weight)
            sig = best.sig_full or best.sig
            voice += f"\n最重要的事：{sig[:45]}"
        
        # Cross-domain bridges
        domain_markers = ["A_", "B_", "L1_", "L2_", "vis_", "apple_"]
        found_domains = []
        for dm in domain_markers:
            if any(dm in (f.sig_full or f.sig) for f in frames):
                found_domains.append(dm)
        if len(found_domains) >= 2:
            voice += f"\n我注意到这些域之间的关联：{'、'.join(found_domains)}"
        
        # Chains
        if chains:
            best_chain = max(chains, key=lambda x: x.weight)
            voice += f"\n我有一个推理链：{best_chain.sig[:40]}"
        
        return {
            "voice": voice,
            "frames": n,
            "assocs": len(assocs),
            "chains": len(chains),
            "top_sig": top[0].sig[:30] if top else "",
            "top_weight": int(top[0].weight) if top else 0
        }

# ── 测试 ──
r = random.Random(42)
_av = random.Random(777)
num_vecs = {n: [0.0]*_VEC_DIM for n in range(1, 11)}
for n, v in num_vecs.items(): v[_av.randint(0, _VEC_DIM-1)] = 2.0
_apv = random.Random(888)
apple_pos = {i: [0.0]*_VEC_DIM for i in range(1, 11)}
for i,v in apple_pos.items(): v[_apv.randint(0, _VEC_DIM-1)] = 2.0
va = [0.0]*_VEC_DIM; va[0] = 1.0

g1a = GEME_T(memory_cap=16, merge_thresh=0.1, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=2)
g1b = GEME_T(memory_cap=16, merge_thresh=0.1, cooccur_window=30, cooccur_thresh=0.1, max_chains=5, time_window_size=2)
g2 = GEME_T(memory_cap=16, cooccur_window=30, cooccur_thresh=0.1, max_chains=10, time_window_size=6)
for g in [g1a,g1b,g2]: g.memory._chain_cooccur_thresh = 2

print("="*55)
print("GEME 对自己状态的描述")
print("="*55)
print()

# 训练前
print("【训练前】")
print("  L1a:", g1a.describe()["voice"])
print("  L1b:", g1b.describe()["voice"])
print("  L2:", g2.describe()["voice"])
print()

# 训练
for epoch in range(30):
    nums = list(range(1, 11)); r.shuffle(nums)
    for i in range(0, len(nums)-1, 2):
        n1, n2 = nums[i], nums[i+1]
        for n in [n1, n2]:
            g1a.process_vec(num_vecs[n], f"vis_{n}")
            for ai in range(n):
                g1b.process_vec(apple_pos[ai+1], f"apple_{ai+1}")
            for f in g1a.memory.frames:
                s = f.sig_full or f.sig; g2.process_vec(va, f"A_{s[:15]}")
            for f in g1b.memory.frames:
                s = f.sig_full or f.sig
                if "apple" in s:
                    for ai in range(1, 11):
                        if f"apple_{ai}" in s:
                            v = [0.0]*_VEC_DIM; v[ai % _VEC_DIM] = 1.0
                            g2.process_vec(v, f"B_apple_{ai}"); break

print("【训练后】")
for name, g in [("L1a (外形)", g1a), ("L1b (质量)", g1b), ("L2 (概念)", g2)]:
    d = g.describe()
    print(f"  {name}: {d['voice']}")
    if d['frames'] > 0:
        print(f"    顶帧权重: {d['top_weight']}")

print("\n【对话】")
print("  人类: L2，你在想什么？")
d = g2.describe()
lines = d["voice"].replace("\n", "\n  ").replace("我", "我(L2)")
print(f"  L2: {lines}")
print()
print("  人类: 数字和苹果有关系吗？")
a_refs = sum(1 for f in g2.memory.frames if "A_" in (f.sig_full or f.sig))
b_refs = sum(1 for f in g2.memory.frames if "B_" in (f.sig_full or f.sig))
ab = sum(1 for f in g2.memory.frames if "A_" in (f.sig_full or f.sig) and "B_" in (f.sig_full or f.sig))
print(f"  L2: 我的记忆中，{a_refs}个帧关于外形，{b_refs}个帧关于质量。")
if ab > 0:
    print(f"      它们之间有{ab}个桥接帧。是的，有关系。")
print()
print("="*55)
print("GEME 能回答'你在想什么？'这不是修辞——是API。")
