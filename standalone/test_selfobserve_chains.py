# Test self-observation chain formation
import sys, os, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

r = random.Random(42)

def gen_eng_true(n=200):
    nums = ["one","two","three","four","five"]
    num_v = {"one":1,"two":2,"three":3,"four":4,"five":5}
    out = []
    for _ in range(n):
        x = r.choice(nums); y = r.choice(nums)
        z = num_v[x] + num_v[y]
        zs = [k for k,v in num_v.items() if v==z][0] if z<=5 else nums[-1]
        out.append(("eng", x, y, zs, True))
    return out

def gen_eng_false(n=200):
    nums = ["one","two","three","four","five"]
    num_v = {"one":1,"two":2,"three":3,"four":4,"five":5}
    out = []
    for _ in range(n):
        x = r.choice(nums); y = r.choice(nums)
        z = num_v[x] + num_v[y]
        wrong = nums[(z+1)%5]
        out.append(("eng", x, y, wrong, False))
    return out

def gen_math_true(n=200):
    return [(r.randint(1,5), r.randint(1,5), r.randint(2,9), True) for _ in range(n)]

def gen_math_false(n=200):
    out = []
    for _ in range(n):
        x = r.randint(1,5); y = r.randint(1,5)
        wrong = x+y+1 if x+y<10 else x+y-1
        out.append((x, y, wrong, False))
    return out

def encode_eng(x, y, z, is_true):
    t = "tr" if is_true else "fa"
    return eq(fn(t, fn("eng", fn("x",const(x)), fn("y",const(y)), fn("z",const(z)))), const("yes"))

def encode_math(x, y, z, is_true):
    t = "tr" if is_true else "fa"
    return eq(fn(t, fn("mth", fn("x",const(str(x))), fn("y",const(str(y))), fn("z",const(str(z))))), const("yes"))

print("=== SELF-OBSERVATION CHAIN TEST ===")
print()

g = GEME(memory_cap=16, cooccur_window=50, cooccur_thresh=0.12, max_chains=10)
g.memory._chain_cooccur_thresh = 2

data = gen_eng_true(200) + gen_eng_false(200) + gen_math_true(200) + gen_math_false(200)
r.shuffle(data)

for item in data:
    domain = item[0]
    if domain == "eng":
        _, x, y, z, is_true = item
        f = encode_eng(x, y, z, is_true)
    else:
        x, y, z, is_true = item
        f = encode_math(x, y, z, is_true)
    g.process_sig(f, structural_signature(f))

print(f"Total frames: {len(g.memory.frames)}")
assocs = [f for f in g.memory.frames if "----" in f.sig]
chains = [f for f in g.memory.frames if "====" in f.sig]
print(f"Associations: {len(assocs)}, Chains: {len(chains)}")

if chains:
    print(f"\nSelf-observation chains ({len(chains)}):")
    for c in sorted(chains, key=lambda x: x.weight, reverse=True)[:6]:
        sig = c.sig_full or c.sig
        print(f"  w={int(c.weight):4d} {sig[:65]}")
    bridge = [c for c in chains if "eng" in c.sig and "mth" in c.sig]
    print(f"\nEng-Math bridge chains: {len(bridge)}")
    if bridge:
        print("YES: Self-observation formed cross-domain chains")
else:
    print("\nNo chains formed. Self-observation needs tuning.")

print(f"\nSelf-observation count: {g.memory._self_observe_count}")
print("Chains = frames co-occurring in self-observation")
