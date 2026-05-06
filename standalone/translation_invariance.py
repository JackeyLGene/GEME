# 翻译不变性测试：同一意义的不同语言 → 相同帧结构？
import sys, random, math, statistics
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

def test_lang(name, sentences, steps=800):
    r = random.Random(42)
    g = GEME(memory_cap=64); g.memory.preserve_sig = True
    g.memory.quantum_mode = True
    g.memory._chain_cooccur_thresh = 2; g.memory._merge_dists = [0.3]*50
    g._induction_threshold = 3.0
    
    for i in range(steps):
        chars = sentences[i % len(sentences)]
        for ch in chars[:3]:
            v = [0.0]*_D27; v[(ord(ch)-32) % _D27] = 1.0
            g.process_vec(v, "ext")
    
    frames = g.memory.frames
    
    # 测量指标
    n = len(frames)
    assoc = sum(1 for f in frames if "──" in (f.sig_full or f.sig))
    chain = sum(1 for f in frames if "══" in (f.sig_full or f.sig))
    # 同符号关联（语义核心度量）
    same_word = sum(1 for f in frames if "ext" in (f.sig_full or f.sig) and "──" in (f.sig_full or f.sig))
    
    print(f"{name}: {n:2d}帧, 关联={assoc:3d}, 链={chain:3d}")
    return assoc, chain

# 中文
cn = [
    "猫坐在垫子上",
    "大黑猫跑得很快",
    "猫喜欢牛奶和鱼",
    "我的猫今天真可爱",
]

# 英文（相同意义）
en = [
    "the cat sat on the mat",
    "a big black cat ran fast",
    "the cat likes milk and fish",
    "my cat is very cute today",
]

# 日文罗马音（问句）
jp = [
    "neko wa matto ni suwatta",
    "ookina kuro neko ga hayaku hashitta",
    "neko wa miruku to sakana ga suki",
    "watashi no neko wa kyou kawaii",
]

print("="*55)
print("翻译不变性测试")
print("="*55)
print()
ac, cc = test_lang("中文", cn, 600)
ae, ce = test_lang("英文", en, 600)
aj, cj = test_lang("日文", jp, 600)
print()
print("分析：")
# 关联度差异：语义相同→关联数应接近
max_diff = max(abs(ac-ae), abs(ac-aj), abs(ae-aj))
avg = statistics.mean([ac, ae, aj])
print(f"  关联帧: 中{ac} 英{ae} 日{aj} (平均{avg:.0f}, 极差{max_diff})")
if max_diff / max(avg, 1) < 0.3:
    print(f"  ✓ 翻译不变性成立——关联结构跨语言一致")
else:
    print(f"  - 差异较大——可能是符号统计而非语义")
