# 扫三个结构常数：0.5(ℏ) / 2(c) / 5.0(G) — 改变它们，GEME的宇宙变成什么样
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, Memory, _VEC_DIM as _D27

_r = random.Random(42)

def run_geme(alpha, beta, gamma, label, steps=3000):
    """
    alpha = 阈值衰减率 (ℏ对应) — 原始0.5
    beta = 窗口/寿命比 (c对应)  — 原始2
    gamma = 新奇帧权重 (G对应)  — 原始5.0
    """
    # 改引擎常数：通过monkey patch Memory类
    orig_thresh = Memory._adaptive_thresh
    orig_window = Memory._adaptive_window
    
    def patched_thresh(self):
        if not self._merge_dists:
            if len(self._learn_dists)<10: return None
            t=sorted(self._learn_dists)[len(self._learn_dists)//4]
            if t<=0: t=statistics.mean(self._learn_dists)*0.5
            if t<=0: t=0.001; self._merge_dists.append(t); return t
        med=statistics.median(self._merge_dists[-50:])
        last_ok=self._merge_dists[-1] if self._merge_dists else 0.001
        return max(med, last_ok*alpha)  # alpha替换0.5
    
    def patched_window(self):
        if not self.frames: return self._win_max
        avg_life = self.total_weight / max(len(self.frames), 1)
        return max(5, min(200, int(avg_life * beta)))  # beta替换2
    
    Memory._adaptive_thresh = patched_thresh
    Memory._adaptive_window = patched_window
    
    g = GEME(memory_cap=64)
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    g.memory._win_max = 40  # 初始窗口
    
    for i in range(steps):
        t = i * 0.01
        v = [0.0]*_D27; v[0] = math.cos(2*math.pi*t); v[1] = math.sin(2*math.pi*t)
        g.process_vec(v, "m")
    
    Memory._adaptive_thresh = orig_thresh
    Memory._adaptive_window = orig_window
    
    frames = g.memory.frames
    m_frames = [f for f in frames if "m" in (f.sig_full or f.sig)[:10]]
    assoc = sum(1 for f in frames if "──" in (f.sig_full or f.sig))
    chain = sum(1 for f in frames if "══" in (f.sig_full or f.sig))
    
    ws = [int(f.weight) for f in m_frames]
    avg_w = statistics.mean(ws) if ws else 0
    max_w = max(ws) if ws else 0
    
    return len(m_frames), len(frames), assoc, chain, avg_w, max_w

print("="*55)
print("扫荡三结构常数：GEME的多元宇宙")
print("="*55)

# 标准宇宙：α=0.5, β=2, γ=5.0
n_m, n_t, a, c, aw, mw = run_geme(0.5, 2, 5.0, "标准")
print(f"\n标准宇宙: (α=0.5, β=2, γ=5.0)")
print(f"  {n_m}个m帧, {a}关联, {c}链, 均值{aw:.1f}, 最大{mw}")

# 实验1: 改变α（ℏ）— 分辨率衰减率
print(f"\n{'='*55}")
print("实验1: 改变α (ℏ对应) — β=2, γ=5.0固定")
print(f"{'='*55}")
for alpha in [0.05, 0.1, 0.5, 0.8, 1.0]:
    n_m, _, a, c, aw, mw = run_geme(alpha, 2, 5.0, f"α={alpha}")
    print(f"  α={alpha:.2f}: {n_m:3d}帧, 关联{a:3d}, 链{c:3d}, 均值{aw:.1f}")
    note = ""
    if n_m < 5: note = " ⚠ 帧太少——系统冻结（分辨率过高，无法区分）"
    elif n_m > 80: note = " ⤴ 帧爆炸——系统失稳（分辨率过低，不断分裂）"
    elif a > 10: note = " ✓ 适中的关联——结构丰富"
    print(f"      {note}")

# 实验2: 改变β（c）— 窗口/寿命比
print(f"\n{'='*55}")
print("实验2: 改变β (c对应) — α=0.5, γ=5.0固定")
print(f"{'='*55}")
for beta in [0.5, 1.0, 2.0, 5.0, 10.0]:
    n_m, _, a, c, aw, mw = run_geme(0.5, beta, 5.0, f"β={beta}")
    print(f"  β={beta:.1f}: {n_m:3d}帧, 关联{a:3d}, 链{c:3d}, 均值{aw:.1f}")
    note = ""
    if a == 0 and c == 0: note = " ⚠ 无关联——宇宙的因果范围太小，所有帧孤立"
    elif a > 30: note = " ⤴ 过度关联——宇宙因果范围太大，万物皆连"
    elif a > 5: note = " ✓ 适度关联"
    print(f"      {note}")

# 实验3: 改变γ（G）— 新帧权重
print(f"\n{'='*55}")
print("实验3: 改变γ (G对应) — α=0.5, β=2固定（需改引擎γ参数）")
print(f"{'='*55}")
# 注意：γ=5.0是写死在observe方法新建帧的分支中，我们改后重新运行
print("  (γ的扫描需要修改geme.py的219行 `1.0+5.0*max` 中的5.0，或monkey patch)")
print("  暂缓——等决定是否需要完整体验再做")
