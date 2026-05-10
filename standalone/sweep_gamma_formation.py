# γ扫瞄v2：宇宙形成期——连续注入新符号，看G不同时结构如何分化
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

def run_formation(gamma, steps=3000, vocab_size=50):
    """vocab_size个不同的符号随机注入——连续学习"""
    r = random.Random(42)
    g = GEME(memory_cap=128)  # 大容量给形成期足够空间
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    g.memory._novelty_bonus = gamma
    
    # 第一阶段：快速注入新符号（"暴涨期"）
    frame_counts = []
    for i in range(steps):
        ch = random.randint(0, vocab_size-1)
        v = [0.0]*_D27; v[ch % _D27] = 1.0
        g.process_vec(v, f"s{ch}")
        if i % 100 == 0:
            frame_counts.append(len([f for f in g.memory.frames if f"s" in (f.sig_full or f.sig)[:10]]))
    
    total_frames = len(g.memory.frames)
    m_frames = [f for f in g.memory.frames if "s" in (f.sig_full or f.sig)[:10]]
    assoc = sum(1 for f in g.memory.frames if "──" in (f.sig_full or f.sig))
    chain = sum(1 for f in g.memory.frames if "══" in (f.sig_full or f.sig))
    ws = [f.weight for f in m_frames]
    
    # 统计帧经济稳定性（最后500步的帧数变化率）
    last_half = frame_counts[len(frame_counts)//2:]
    stability = statistics.stdev(last_half) / max(statistics.mean(last_half), 1) if last_half else 0
    
    return len(m_frames), assoc, chain, statistics.mean(ws) if ws else 0, max(ws) if ws else 0, stability, frame_counts

print("="*55)
print("γ扫瞄·宇宙形成期")
print("="*55)
print(f"50个随机符号，3000步注入，memory_cap=128")
print()

for gamma in [0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]:
    nm, a, c, aw, mw, stab, fcs = run_formation(gamma)
    bar = "█" * min(nm // 5, 20)
    print(f"  γ={gamma:5.1f}: m帧={nm:3d} {bar} 关联={a:3d} 链={c:3d} 均w={aw:.1f} 稳定性={stab:.2f}")

print()
print("分析：")
print("  γ<1（G太小）→ 新帧权重≈1 → 没有结构能站稳 → 帧数多但关联少")
print("  γ=5（标准G）→ 新帧权重=6 → 新结构有合适优势 → 帧数+关联平衡")
print("  γ>10（G太大）→ 新帧权重>11 → 旧结构不断被颠覆 → 系统持续振荡")
