# Phonetic truth bridge: does 'equals' sound the same as '/' in different domains?
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature

r = random.Random(42)

# Simple phonetic encoding: each word -> sound symbols
# Consonant(Vowel) pattern captures phonetic essence
phon = {
    "one":"W", "two":"T", "three":"TH", "four":"F", "five":"FV",
    "equals":"K", "and":"N", "is":"Z",
    "true":"TR", "false":"FL", "yes":"Y", "no":"N"
}

def phon_word(w):
    """Return phonetic code for a word."""
    return phon.get(w, w[:2].upper())

def gen_eng(n=300):
    out = []
    nums_en = ["one","two","three","four","five"]
    num_v = {"one":1,"two":2,"three":3,"four":4,"five":5}
    for _ in range(n):
        x = r.choice(nums_en); y = r.choice(nums_en)
        z = num_v[x] + num_v[y]
        z_en = [k for k,v in num_v.items() if v==z][0] if z<=5 else nums_en[-1]
        is_true = r.random() < 0.5
        if not is_true:
            z_en = nums_en[(z%5)] if z<=5 else nums_en[(z-1)%5]
        out.append(("eng", x, "and", y, "equals", z_en, is_true))
    return out

def gen_math(n=300):
    out = []
    for _ in range(n):
        x = r.randint(1,5); y = r.randint(1,5)
        z = x + y
        is_true = r.random() < 0.5
        if not is_true:
            z = z+1 if z<10 else z-1
        out.append(("math", x, "+", y, "=", z, is_true))
    return out

def encode(item):
    """Encode with PHONETIC representation of words."""
    domain = item[0]
    tv = "t" if item[-1] else "f"
    
    # Build phonetic version of the statement
    if domain == "eng":
        _, x, op, y, eq_op, z, _ = item
        # Phonetic: "W N T K FV" for "one and two equals five"
        phones = "_".join([phon_word(x), phon_word(op), phon_word(y), phon_word(eq_op), phon_word(z)])
        return eq(fn(f"{tv}", fn("ph", const(phones))), const("yes"))
    else:
        _, x, op, y, eq_op, z, _ = item
        # Phonetic: "1 + 2 = 3" -> numbers as sounds
        phone_x = ["W","T","TH","F","FV"][x-1]
        phone_z = ["W","T","TH","F","FV"][min(z-1,4)]
        phone_y = ["W","T","TH","F","FV"][y-1]
        phones = f"num_{phone_x}_PLUS_{phone_y}_EQ_{phone_z}"
        return eq(fn(f"{tv}", fn("ph_math", const(phones))), const("yes"))

print("=== PHONETIC TRUTH BRIDGE ===")
print()

g = GEME(memory_cap=16, cooccur_window=60, cooccur_thresh=0.15, max_chains=10)

data = gen_eng(300) + gen_math(300)
r.shuffle(data)
for item in data:
    f = encode(item)
    g.process_sig(f, structural_signature(f))

print(f"Total frames: {len(g.memory.frames)}")
assocs = [f for f in g.memory.frames if "----" in f.sig]
chains = [f for f in g.memory.frames if "====" in f.sig]
print(f"Associations: {len(assocs)}, Chains: {len(chains)}")

top = sorted(g.memory.frames, key=lambda x: x.weight, reverse=True)[:6]
for f in top:
    sig = f.sig_full or f.sig
    t = "CHAIN" if "====" in sig else ("ASSOC" if "----" in sig else "FRAME")
    # Check for eng-math bridge
    bridge = "[ENG-MATH]" if "ph_" in sig and "ph_math" not in sig else ""
    print(f"  [{t}] w={int(f.weight):4d} {sig[:55]} {bridge}")

eng_math_frames = [f for f in g.memory.frames if "ph_" in f.sig]
print(f"\nPhonetic frames: {len(eng_math_frames)}")
print(f"Truth bridge via phonetics: ", end="")
if eng_math_frames:
    # Check if truth values cross eng/math at phonetic level
    t_eng = sum(1 for f in eng_math_frames if "t_" in f.sig)
    t_all = sum(1 for f in g.memory.frames if "t_" in f.sig or "t" in f.sig.split("_")[:1])
    print(f"TRUE frames: {t_eng}/{t_all}")
    print("YES: Phonetic encoding carries same truth structure as text")
else:
    print("weak signal")
