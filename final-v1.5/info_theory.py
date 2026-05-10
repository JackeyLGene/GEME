"""Information-theoretic analysis of GEME frame compression."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature

def shannon_entropy(probs):
    return -sum(p * math.log2(p) for p in probs if p > 0)

def analyze(g, input_sigs, label=""):
    """Compute information-theoretic metrics for a GEME memory."""
    if not g.memory.frames: return
    # Input distribution
    total_in = len(input_sigs)
    sig_counts = {}
    for s in input_sigs:
        sig_counts[s] = sig_counts.get(s, 0) + 1
    input_probs = [c/total_in for c in sig_counts.values()]
    H_input = shannon_entropy(input_probs)
    
    # Frame distribution (by weight)
    total_w = g.memory.total_weight
    frame_sigs = list(set(f.sig for f in g.memory.frames))
    frame_w = {}
    for f in g.memory.frames:
        frame_w[f.sig] = frame_w.get(f.sig, 0) + f.weight
    frame_probs = [w/total_w for w in frame_w.values()]
    H_frames = shannon_entropy(frame_probs)
    
    # Compression ratio
    comp = g.memory.compression_ratio(total_in)
    
    # Entropy reduction: H_input vs H_frames
    if H_input > 0:
        red = (H_input - H_frames) / H_input * 100
    else: red = 0
    
    # Info preservation: fraction of input signatures preserved in frame sigs
    preserved = len([s for s in set(input_sigs) if s in frame_sigs]) / max(len(set(input_sigs)), 1)
    
    print(f"  {label}:")
    print(f"    H(input)={H_input:.2f} bits, H(frames)={H_frames:.2f} bits")
    print(f"    Entropy reduction: {red:.0f}%")
    print(f"    Compression: {comp:.0f}:1")
    print(f"    Signature preservation: {preserved*100:.0f}%")
    return {"H_in": H_input, "H_fr": H_frames, "red": red, "comp": comp, "pres": preserved}

SEED = 42
r = random.Random(SEED)
print("=== INFORMATION-THEORETIC ANALYSIS ===")
print()

# ── Exp 1: Commutativity ──
g = GEME(memory_cap=16, cooccur_window=60, cooccur_thresh=0.15)
sigs = []
for _ in range(600):
    a, b = r.randint(1,5), r.randint(1,5)
    f = eq(fn("swap", const(str(a)), const(str(b))),
           fn("swap", const(str(b)), const(str(a))))
    sig = structural_signature(f)
    g.process_sig(f, sig)
    sigs.append(sig)
a1 = analyze(g, sigs, "Exp 1 (commutativity, 600 inputs)")

# ── Exp 2: Godel wall ──
r = random.Random(SEED)
g = GEME(memory_cap=16, cooccur_window=60, cooccur_thresh=0.15)
sigs = []
for _ in range(400):
    a, b = "s"+str(r.randint(0,9)), "s"+str(r.randint(1,10))
    f = eq(fn("succ", const(a)), const(b))
    sig = structural_signature(f)
    g.process_sig(f, sig)
    sigs.append(sig)
a2 = analyze(g, sigs, "Exp 2 (Godel wall, 400 inputs)")

# ── Exp 3: Tarski wall ──
r = random.Random(SEED)
g = GEME(memory_cap=16, cooccur_window=60, cooccur_thresh=0.15)
sigs = []
for _ in range(400):
    pts = r.choice([["A","B","C"],["D","E","F"]])
    pairs = [(pts[0],pts[1]),(pts[1],pts[2])]
    if r.random() < 0.5: pairs.append((pts[2],pts[0]))
    for p,q in pairs:
        f = eq(fn("conn", const(p), const(q)), const("yes"))
        sig = structural_signature(f)
        g.process_sig(f, sig)
        sigs.append(sig)
a3 = analyze(g, sigs, "Exp 3 (Tarski wall, 400 inputs)")

print(f"\n{'='*55}")
print("Key finding: competitive memory reduces frame entropy")
print(f"(Exp 1: {a1['red']:.0f}% reduction, Exp 2: {a2['red']:.0f}%).")
print("Information compression = competitive survival.")
