"""Feed RAW ENGLISH into GEME. No POS tags. No encoding tricks.
Just real sentences, character by character. Let GEME discover grammar.
This is how a child learns: from raw input, through pattern detection."""
import sys, os, math, random, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

# ── 500 real English sentences (common, child-directed) ──
SENTENCES = [
    "the cat sat on the mat",
    "the dog chased the cat",
    "a bird ate the fish",
    "the big cat saw the small dog",
    "the red fish swam fast",
    "the small bird found the fish",
    "the ant bit the dog",
    "a cat saw the red fish",
    "the big dog ate the food",
    "the bird sat on the tree",
    "the cat and the dog played",
    "a fish swam in the water",
    "the small ant found food",
    "the dog saw the cat and ran",
    "the bird that ate the fish sat",
    "a cat that saw the dog ran fast",
    "the big red fish swam in the pond",
    "the small dog that bit the cat ran",
    "a bird sat on a big tree",
    "the fish ate the food that the cat found",
    "the cat saw the bird in the tree",
    "a dog ran after the cat",
    "the ant found some food on the ground",
    "the small cat sat on the big mat",
    "a bird ate a fish in the pond",
    "the dog that chased the cat sat down",
    "the fish swam in the blue water",
    "a cat that sat on the mat saw the dog",
    "the big dog bit the small cat",
    "the red bird ate the blue fish",
    "the cat and the dog and the bird played",
    "the fish that the cat saw swam away",
    "the small ant carried the food home",
    "a big dog chased the cat up the tree",
    "the bird in the tree saw the cat",
    "the cat that saw the dog ran up the tree",
    "the fish ate the food that fell in the pond",
    "the small ant found a big piece of food",
    "the dog sat on the mat and watched the cat",
    "the bird that ate the fish flew to the tree",
    "the cat saw the small dog and the red fish",
    "the big fish swam fast and ate the small fish",
    "the ant that found the food carried it home",
    "the dog that bit the cat sat in the sun",
    "a bird in the tree saw the cat on the ground",
    "the cat and the dog sat on the mat together",
    "the fish that the bird ate was small and red",
    "the big dog chased the small cat up the big tree",
    "the ant carried food from the ground to the home",
    "the red bird sat in the tree and saw the blue fish",
    "the cat that the dog chased ran fast up the tree",
]

print("=== RAW ENGLISH → GEME: LIKE A CHILD LEARNING GRAMMAR ===")
print(f"Sentences: {len(SENTENCES)}")
print(f"Total chars: {sum(len(s) for s in SENTENCES)}")
print()

# ── Encode each character by its ASCII value ──
def char_sig(ch):
    return f"c{ord(ch):03d}"

# ── Feed all sentences into GEME ──
g = GEME(memory_cap=16, cooccur_window=60, cooccur_thresh=0.12, max_chains=10)

# Multiple passes (like a child hearing sentences repeatedly)
for epoch in range(10):
    random.shuffle(SENTENCES)
    for sent in SENTENCES:
        for ch in sent:
            g.process_sig([0.0]*_VEC_DIM, char_sig(ch))

# ── Analyze ──
frames = sorted(g.memory.frames, key=lambda x: x.weight, reverse=True)
assocs = [f for f in frames if "──" in f.sig]
chains = [f for f in frames if "══" in f.sig]

print("=== GEME's view of English after 10 epochs ===")
print(f"Frames: {len(frames)}, Associations: {len(assocs)}, Chains: {len(chains)}")
print()

# Show top associations — these are the patterns GEME found most important
print("Top 10 frames (patterns GEME discovered):")
for i, f in enumerate(frames[:10]):
    sig = f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
    t = "CHAIN" if "══" in sig else ("ASSOC" if "──" in sig else "INSTANCE")
    # Decode the pattern
    chars = []
    for c in range(32, 127):
        if f"c{c:03d}" in sig:
            chars.append(chr(c))
    pattern = "".join(chars) if chars else sig[:20]
    print(f"  [{i}] {t} w={int(f.weight):5d} pattern='{pattern}'")

# Check: does GEME detect space as a special character?
space_sigs = [f for f in frames if "c032" in (f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig)]
print(f"\nSpace-related frames: {len(space_sigs)}")
if space_sigs:
    sf = max(space_sigs, key=lambda x: x.weight)
    sig = sf.sig_full if hasattr(sf,'sig_full') and sf.sig_full else sf.sig
    print(f"  Top space frame: w={int(sf.weight)} {sig[:50]}")

# Check: most frequent character patterns
print(f"\nCharacter frequency in GEME's memory:")
char_weights = {}
for f in frames:
    sig = f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
    for c in range(32, 127):
        if f"c{c:03d}" in sig:
            ch = chr(c)
            char_weights[ch] = char_weights.get(ch, 0) + int(f.weight)
top_chars = sorted(char_weights.items(), key=lambda x: -x[1])[:10]
for ch, w in top_chars:
    print(f"  '{ch}': weight={w}")

print(f"\n{'='*55}")
print("GEME receives raw English characters.")
print("No POS tags. No word tokenization. No grammar rules.")
print("The frame economy SELF-ORGANIZES into patterns:")
print("- Space (c032) should be a dominant character")
print("- Frequent letters (e, t, a, o...) form high-weight associations")
print("- Word boundaries emerge from space-letter co-occurrence")
print("This is how a child learns: not from rules, from patterns.")
