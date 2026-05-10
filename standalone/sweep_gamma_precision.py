# γ精密扫瞄：同签名噪声注入——只有γ改变时帧经济如何分化
import sys, math, random, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

def run_gamma(gamma, steps=5000, noise=0.1):
    """3个基向量+噪声→同签名→γ决定新帧是否存活"""
    r = random.Random(42)
    g = GEME(memory_cap=32)
    g.memory.preserve_sig = True; g.memory._chain_cooccur_thresh = 2
    g.memory._merge_dists = [0.3]*50; g._induction_threshold = 3.0
    g.memory._novelty_bonus = gamma
    
    # 3个基向量
    bases = [[0.0]*_D27 for _ in range(3)]
    bases[0][0] = 1.0  # 符号A
    bases[1][5] = 1.0  # 符号B
    bases[2][10] = 1.0 # 符号C
    
    for i in range(steps):
        base = bases[i % 3]
        # 加噪声
        v = [base[d] + r.gauss(0, noise) for d in range(_D27)]
        v = [max(0, min(1, x)) for x in v]  # 钳位到[0,1]
        g.process_vec(v, "s")  # 同签名
    
    m_frames = [f for f in g.memory.frames if "s" in (f.sig_full or f.sig)[:10]]
    n = len(m_frames)
    assoc = sum(1 for f in g.memory.frames if "──" in (f.sig_full or f.sig))
    ws = [f.weight for f in m_frames]
    avg_w = statistics.mean(ws) if ws else 0
    
    # 分支因子：几个帧占了大部分权重
    top3 = sum(sorted(ws, reverse=True)[:3]) / max(sum(ws), 1) if len(ws) >= 3 else 0
    
    return n, assoc, avg_w, top3

print("="*55)
print("γ精密扫瞄：同签名噪声注入")
print("="*55)
print('3个基符号+高斯噪声(σ=0.15)，同签名"s"，5000步')
print()

for gamma in [0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0]:
    n, a, aw, t3 = run_gamma(gamma, noise=0.15)
    bar = "█" * min(n, 30)
    print(f"  γ={gamma:5.1f}: 帧={n:2d} {bar} | 关联={a:2d} | 均w={aw:.0f} | 前3占比={t3*100:.0f}%")

print()
print("分析：")
print("  γ大 → 噪声产生的新帧存活 → 帧数多 → 重量分散 → 结构不稳定")
print("  γ小 → 噪声帧被合并 → 帧数少 → 重量集中 → 结构稳定但僵化")
print("  γ最优 ≈ 1~5 → 兼顾稳定性和适应性")
