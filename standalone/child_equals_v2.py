# Child discovers equals: English 'equals' and Math '=' in ONE economy
# Same structural position -> same frame at L1 -> discovery without teaching
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature

r = random.Random(42)

# TRUTH KEY: encode truth value IN the formula structure
# English: fn("eng", fn("true" or "false"), fn("x"), fn("equals"), fn("y"), fn("z"))
# Math:    fn("math", fn("true" or "false"), fn("x"), fn("="), fn("y"), fn("z"))
# structural_signature preserves: eng_true_x_equals_y_z vs eng_false_x_equals_y_z
#                                           vs math_true_x_equals_y_z vs math_false_x_equals_y_z

# If 'equals' and '=' appear in structurally identical frames, 
# GEME will form one association frame for both -> child discovered they're the same

nums = {"one":"1","two":"2","three":"3","four":"4","five":"5"}

def gen(n=400):
    out = []
    for _ in range(n):
        # English or Math
        is_eng = r.random() < 0.5
        a = r.randint(1,5); b = r.randint(1,5)
        z = a + b
        is_true = r.random() < 0.5
        if not is_true:
            z = z + 1 if z < 9 else z - 1
        
        if is_eng:
            en_a = [k for k,v in nums.items() if v==str(a)][0]
            en_b = [k for k,v in nums.items() if v==str(b)][0]
            en_z = [k for k,v in nums.items() if v==str(z)][0] if str(z) in nums.values() else str(z)
            tv = "true" if is_true else "false"
            f = eq(fn(tv, fn("eng", fn("x",const(en_a)), fn("eq",const("equals")),
                                  fn("y",const(en_b)), fn("z",const(en_z)))), const("yes"))
        else:
            tv = "true" if is_true else "false"
            f = eq(fn(tv, fn("math", fn("x",const(str(a))), fn("eq",const("=")),
                                  fn("y",const(str(b))), fn("z",const(str(z))))), const("yes"))
        out.append(f)
    return out

g = GEME(memory_cap=16, cooccur_window=60, cooccur_thresh=0.15, max_chains=10)
data = gen(400)
r.shuffle(data)
for f in data:
    g.process_sig(f, structural_signature(f))

print("=== CHILD DISCOVERS 'EQUALS': SINGLE ECONOMY ===")
print(f"Total frames: {len(g.memory.frames)}")
assocs = [f for f in g.memory.frames if "----" in f.sig]
chains = [f for f in g.memory.frames if "====" in f.sig]
print(f"Associations: {len(assocs)}, Chains: {len(chains)}")

top = sorted(g.memory.frames, key=lambda x: x.weight, reverse=True)[:8]
print(f"\nTop frames (truth economy L1):")
for f in top:
    sig = f.sig_full or f.sig
    t = "CHAIN" if "====" in sig else ("ASSOC" if "----" in sig else "FRAME")
    # Decode: does this frame link English 'equals' and Math '=' ?
    eq_link = "eng" in sig and "math" in sig
    marker = " <- EQUALS BRIDGE" if eq_link else ""
    print(f"  [{t}] w={int(f.weight):4d} {sig[:55]}{marker}")

# Check: did equals-bridge form?
eq_bridge = [f for f in g.memory.frames if "eng" in f.sig and "math" in f.sig]
print(f"\nEquals bridge frames (eng + math): {len(eq_bridge)}")
if eq_bridge:
    print("YES: Child discovered 'equals' and '=' are the same function")
    print("Both occupy the same structural position in truth economy")
else:
    print("No direct bridge - checking indirect associations...")
    # Check if eng and math frames share any patterns
    eng_sigs = [f.sig for f in g.memory.frames if "eng" in f.sig]
    math_sigs = [f.sig for f in g.memory.frames if "math" in f.sig]
    shared = [s for s in eng_sigs if s in math_sigs]
    print(f"Shared sigs: {len(shared)}; Eng: {len(eng_sigs)}, Math: {len(math_sigs)}")
