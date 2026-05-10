# 语义 vs 随机：ext──self桥梁测试
import sys, random, math
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, _VEC_DIM as _D27

_r = random.Random(42)

def test_corpus(name, corpus_fn, steps=800):
    r = random.Random(42)
    g = GEME(memory_cap=64); g.memory.preserve_sig = True
    g.memory.quantum_mode = True
    g.memory._chain_cooccur_thresh = 2; g.memory._merge_dists = [0.3]*50
    g._induction_threshold = 3.0
    
    tick = 0; ti = 8; ls = set()
    
    for i in range(steps):
        chars = corpus_fn(i)
        for ch in chars[:3]:
            v = [0.0]*_D27; v[(ord(ch)-32) % _D27] = 1.0
            g.process_vec(v, "ext")
        
        tick += 1
        if tick >= ti:
            cur = set()
            for fl in g.memory.frames:
                cur.add((fl.sig_full or fl.sig)[:20])
            chg = 0
            if ls and cur:
                chg = (len(cur-ls) + len(ls-cur)) / max(len(cur), 1)
            ls = cur; ti = max(3, 8/(1+chg*5))
            v = [0.0]*_D27
            for j, f in enumerate(g.memory.frames[:5]):
                v[j] = f.weight / (sum(f.weight for f in g.memory.frames) or 1)
            g.process_vec(v, "self"); tick = 0
    
    bridge = sum(int(f.weight) for f in g.memory.frames
                 if "ext" in (f.sig_full or f.sig)
                 and "self" in (f.sig_full or f.sig))
    frames = len(g.memory.frames)
    self_only = sum(1 for f in g.memory.frames
                    if "self" in (f.sig_full or f.sig)
                    and "ext" not in (f.sig_full or f.sig))
    return bridge, frames, self_only

sentences = [
    "the cat sat on the mat",
    "a big black cat ran fast",
    "the cat likes milk and fish",
    "my cat is very cute today",
]

def semantic_fn(i):
    return sentences[i % len(sentences)]

def random_fn(i):
    chars = "thecatmatbigblackranfastmilkfishcute"
    d = len(sentences[i % len(sentences)])
    return "".join(random.Random(i+999).choice(chars) for _ in range(d))

def pure_random_fn(i):
    return "".join(chr(32 + random.Random(i+9999).randint(0, 25)) for _ in range(15))

for name, fn in [("语义句子", semantic_fn), ("随机字符(等长)", random_fn), ("纯随机", pure_random_fn)]:
    b, f, s = test_corpus(name, fn)
    has = "桥接形成" if b > 10 else "桥接未形成"
    print(f"{name}: 桥={b:4d}, 总帧={f}, self帧={s} — {has}")
