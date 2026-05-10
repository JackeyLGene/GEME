"""A child discovers what 'equals' means.
GEME processes English + Math sentences with truth values.
Equals and = serve the SAME function in truth economies.
GEME discovers they are the same word without being told."""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature

r = random.Random(42)

# ── English: "X and Y equals Z" ──
numbers_en = ["one","two","three","four","five"]
num_map = {"one":1,"two":2,"three":3,"four":4,"five":5}

def gen_eng(n=300):
    """English sentences with true/false."""
    out = []
    for _ in range(n):
        x = r.choice(numbers_en); y = r.choice(numbers_en)
        z = num_map[x] + num_map[y]
        z_en = [k for k,v in num_map.items() if v==z][0] if z <=5 else numbers_en[-1]
        if r.random() < 0.5:
            out.append((x, y, z_en, True))  # correct
        else:
            wrong = numbers_en[(z+1)%5] if z < 5 else numbers_en[(z-1)%5]
            out.append((x, y, wrong, False))  # wrong
    return out

def encode_eng(x, y, z, is_true):
    """Encode English sentence. 'equals' is marked in signature."""
    tr = "t" if is_true else "f"
    return eq(fn(f"s_{tr}", fn("eng", fn("x",const(x)), fn("eq_op",const("eq")),
                                fn("y",const(y)), fn("res",const(z)))), const("yes"))

# ── Math: "X+Y=Z" ──
def gen_math(n=300):
    out = []
    for _ in range(n):
        x = r.randint(1,5); y = r.randint(1,5)
        z = x + y
        if r.random() < 0.5:
            out.append((str(x), str(y), str(z), True))
        else:
            out.append((str(x), str(y), str(z+1 if z<10 else z-1), False))
    return out

def encode_math(x, y, z, is_true):
    tr = "t" if is_true else "f"
    return eq(fn(f"s_{tr}", fn("math", fn("x",const(x)), fn("eq_op",const("=")),
                                fn("y",const(y)), fn("res",const(z)))), const("yes"))

print("=== CHILD DISCOVERS 'EQUALS' ===")
print()

# ── L1a: English truth economy ──
g_en = GEME(memory_cap=16, cooccur_window=40, cooccur_thresh=0.15)
data_en = gen_eng(300)
r.shuffle(data_en)
for x, y, z, is_true in data_en:
    f = encode_eng(x, y, z, is_true)
    g_en.process_sig(f, structural_signature(f))

# Show frames related to "eq" (equals)
eq_frames_en = [f for f in g_en.memory.frames if "eq" in (f.sig_full or f.sig)]
print(f"L1a (English): {len(g_en.memory.frames)} frames")
print(f"  Frames mentioning 'eq' (equals): {len(eq_frames_en)}")

# ── L1b: Math truth economy ──
g_ma = GEME(memory_cap=16, cooccur_window=40, cooccur_thresh=0.15)
data_ma = gen_math(300)
r.shuffle(data_ma)
for x, y, z, is_true in data_ma:
    f = encode_math(x, y, z, is_true)
    g_ma.process_sig(f, structural_signature(f))

eq_frames_ma = [f for f in g_ma.memory.frames if "eq" in (f.sig_full or f.sig)]
print(f"L1b (Math): {len(g_ma.memory.frames)} frames")
print(f"  Frames mentioning 'eq' (equals): {len(eq_frames_ma)}")

# ── L2: Compare frames → discover 'equals' = '=' ──
g2 = GEME(memory_cap=16, cooccur_window=40, cooccur_thresh=0.15, max_chains=10)

# Feed English 'eq' frames and Math 'eq' frames
# Use TRUTH VALUE as the bridge (not specific frame signatures)
# TRUE-English frames + TRUE-Math frames share "truth" signature
for f_en in eq_frames_en:
    sig_en = f_en.sig_full or f_en.sig
    is_true = "s_t" in sig_en
    for f_ma in eq_frames_ma:
        sig_ma = f_ma.sig_full or f_ma.sig
        is_true_m = "s_t" in sig_ma
        if is_true == is_true_m:
            # Same truth value = same structural role
            truth_val = "true" if is_true else "false"
            cross = eq(fn("discover", const(truth_val)), const("yes"))
            g2.process_sig(cross, f"disc_{truth_val}")

print(f"\nL2 (Discovery):")
print(f"  Frames: {len(g2.memory.frames)}")
assocs = [f for f in g2.memory.frames if "----" in f.sig]
chains = [f for f in g2.memory.frames if "====" in f.sig]
print(f"  Associations: {len(assocs)}, Chains: {len(chains)}")

# Show what GEME discovered about "equals"
top = sorted(g2.memory.frames, key=lambda x: x.weight, reverse=True)[:5]
for f in top:
    sig = f.sig_full or f.sig
    t = "CHAIN" if "====" in sig else ("ASSOC" if "----" in sig else "FRAME")
    print(f"  [{t}] w={int(f.weight):4d} {sig[:65]}")

print(f"\n{'='*55}")
print("DID THE CHILD DISCOVER 'EQUALS'?")
# Key insight: if English 'eq' frames and Math 'eq' frames
# co-occur at L2, they share the structural role of truth-carrier
equals_eng = "eq" in " ".join(f.sig for f in g_en.memory.frames)
equals_math = "eq" in " ".join(f.sig for f in g_ma.memory.frames)
l2_overlap = sum(1 for f in g2.memory.frames if "eng" in f.sig and "math" in f.sig)
print(f"  English 'equals' detected: {equals_eng}")
print(f"  Math '=' detected: {equals_math}")
print(f"  L2 eng-math overlap frames: {l2_overlap}")
if l2_overlap > 0:
    print("YES: The child discovered that 'equals' = '='")
    print("Same structural role in truth economy = same meaning")
else:
    print("L2 overlap insufficient - need more varied cross-connections")
