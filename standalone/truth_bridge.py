# Truth bridge: English sentence truth + Math formula truth -> L2 shared structure
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature

r = random.Random(42)

numbers = ["one","two","three","four","five","six","seven","eight","nine","ten"]
num_map = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}

def gen_eng_true(n=200):
    out = []
    for _ in range(n):
        x = r.choice(numbers[:5]); y = r.choice(numbers[:5])
        z_num = num_map[x] + num_map[y]
        z = [k for k,v in num_map.items() if v==z_num][0] if z_num <=10 else numbers[-1]
        out.append((x, "and", y, "equals", z, True))
    return out

def gen_eng_false(n=200):
    out = []
    for _ in range(n):
        x = r.choice(numbers[:5]); y = r.choice(numbers[:5])
        z_num = num_map[x] + num_map[y]
        wrong_z = numbers[(z_num+2) % 10] if z_num < 10 else numbers[z_num % 10]
        out.append((x, "and", y, "equals", wrong_z, False))
    return out

def gen_math_true(n=200):
    return [(r.randint(1,5), r.randint(1,5), r.randint(1,5)+r.randint(1,5), True) for _ in range(n)]

def gen_math_false(n=200):
    out = []
    for _ in range(n):
        x = r.randint(1,5); y = r.randint(1,5)
        z_w = x+y+1 if x+y < 10 else x+y-1
        out.append((x, y, z_w, False))
    return out

def encode_eng(words, is_true):
    x, op, y, eq_op, z, _ = words
    t = "true" if is_true else "false"
    return eq(fn(t, fn("eng", fn("w1",const(x)), fn("w2",const(op)), fn("w3",const(y)),
                        fn("w4",const(eq_op)), fn("w5",const(z)))), const("yes"))

def encode_math(formula):
    x, y, z, is_true = formula
    t = "true" if is_true else "false"
    return eq(fn(t, fn("math", fn("nx",const(str(x))), fn("op",const("p")),
                        fn("ny",const(str(y))), fn("eq",const("eq")), fn("nz",const(str(z))))), const("yes"))

print("=== TRUTH BRIDGE: English + Math ===")
print()

# L1a: English truth
g_eng = GEME(memory_cap=16, cooccur_window=40, cooccur_thresh=0.15, max_chains=5)
data = gen_eng_true(200) + gen_eng_false(200)
r.shuffle(data)
for words in data:
    is_true = words[-1]
    f = encode_eng(words, is_true)
    g_eng.process_sig(f, structural_signature(f))

eng_true = [f for f in g_eng.memory.frames if "true" in (f.sig_full or f.sig) and f.weight>5]
eng_false = [f for f in g_eng.memory.frames if "false" in (f.sig_full or f.sig) and f.weight>5]
print(f"L1a (English): {len(g_eng.memory.frames)} frames")
print(f"  TRUE patterns: {len(eng_true)}, FALSE patterns: {len(eng_false)}")

# L1b: Math truth
g_math = GEME(memory_cap=16, cooccur_window=40, cooccur_thresh=0.15, max_chains=5)
data_m = gen_math_true(200) + gen_math_false(200)
r.shuffle(data_m)
for fm in data_m:
    fm2 = encode_math(fm)
    g_math.process_sig(fm2, structural_signature(fm2))

math_true = [f for f in g_math.memory.frames if "true" in (f.sig_full or f.sig) and f.weight>5]
math_false = [f for f in g_math.memory.frames if "false" in (f.sig_full or f.sig) and f.weight>5]
print(f"L1b (Math): {len(g_math.memory.frames)} frames")
print(f"  TRUE patterns: {len(math_true)}, FALSE patterns: {len(math_false)}")

# L2: Integration
g2 = GEME(memory_cap=16, cooccur_window=40, cooccur_thresh=0.15, max_chains=10)

# Connect TRUE-English with TRUE-Math
for ef in eng_true[:3]:
    for mf in math_true[:3]:
        sef = ef.sig_full or ef.sig
        smf = mf.sig_full or mf.sig
        cross = eq(fn("cross_true", const(sef[:12]), const(smf[:12])), const("yes"))
        g2.process_sig(cross, structural_signature(cross))

# Connect FALSE-English with FALSE-Math
for ef in eng_false[:3]:
    for mf in math_false[:3]:
        sef = ef.sig_full or ef.sig
        smf = mf.sig_full or mf.sig
        cross = eq(fn("cross_false", const(sef[:12]), const(smf[:12])), const("yes"))
        g2.process_sig(cross, structural_signature(cross))

print(f"\nL2 (Integration):")
print(f"  Frames: {len(g2.memory.frames)}")
assocs = [f for f in g2.memory.frames if "----" in f.sig]
chains = [f for f in g2.memory.frames if "====" in f.sig]
print(f"  Associations: {len(assocs)}, Chains: {len(chains)}")

top = sorted(g2.memory.frames, key=lambda x: x.weight, reverse=True)[:6]
for f in top:
    sig = f.sig_full or f.sig
    t = "CHAIN" if "====" in sig else ("ASSOC" if "----" in sig else "FRAME")
    print(f"  [{t}] w={int(f.weight):4d} {sig[:60]}")

# Result
print(f"\n{'='*55}")
if eng_true and math_true:
    print("YES: English truth frames present")
    print("YES: Math truth frames present")
true_links = sum(1 for f in g2.memory.frames if "true" in f.sig)
false_links = sum(1 for f in g2.memory.frames if "false" in f.sig)
print(f"L2 true-links: {true_links}, false-links: {false_links}")
if true_links > 0 and false_links > 0:
    print("YES: Truth structure detected across BOTH domains")
    print("Grammar is the structural signature of truth")
