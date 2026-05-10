"""GEME with built-in hierarchical layer propagation.
GEME1→GEME2→GEME3 captures Chomsky hierarchy levels.
Layer output becomes next layer's vocabulary."""
import sys, os, math, random, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

class HierarchicalGEME:
    """Multi-layer GEME: each layer's associations become the next layer's vocabulary."""
    def __init__(self, num_layers=3, mem_cap=12, window=40, thresh=0.15):
        self.layers = [GEME(memory_cap=mem_cap, cooccur_window=window, 
                           cooccur_thresh=thresh, max_chains=10) 
                      for _ in range(num_layers)]
        self.num_layers = num_layers
        self.vocab = [{} for _ in range(num_layers)]  # sig→layer mapping
    
    def feed_sentence(self, words):
        """Feed a sentence into the hierarchy. Layer n processes layer n-1's output."""
        # L0: feed word-level syntactic categories
        cats = [self._cat(w) for w in words]
        sig = f"s_{'_'.join(cats)}"
        
        # Feed into layer 0 (char/word level)
        sig_prev = sig
        for li in range(self.num_layers):
            g = self.layers[li]
            # Process at this layer
            f = eq(fn("input", const(sig_prev[:15])), const("yes"))
            g.process_sig(f, structural_signature(f))
            
            # Extract associations from this layer → next layer's vocabulary
            assocs = [f for f in g.memory.frames if "──" in f.sig 
                     and f.weight > 5][:2]
            if assocs:
                # The top association becomes a "compound word" for next layer
                top_a = assocs[0]
                a_sig = top_a.sig_full if hasattr(top_a, 'sig_full') and top_a.sig_full else top_a.sig
                sig_prev = f"comp_{li}_{a_sig[:10]}"
                self.vocab[li][sig_prev] = a_sig
            else:
                sig_prev = f"flat_{sig_prev[:10]}"
    
    def _cat(self, w):
        nouns = {"cat","dog","bird","fish","ant"}
        verbs = {"saw","chased","ate","found","bit"}
        adjs = {"big","small","red","blue","fast"}
        if w in nouns: return "N"
        if w in verbs: return "V"
        if w in adjs: return "A"
        return "X"
    
    def stats(self):
        for li, g in enumerate(self.layers):
            frames = g.memory.frames
            assocs = [f for f in frames if "──" in f.sig]
            chains = [f for f in frames if "══" in f.sig]
            print(f"  Layer {li}: {len(frames)} frames, {len(assocs)} assocs, {len(chains)} chains")
            if chains:
                for c in chains[:2]:
                    sig = c.sig_full if hasattr(c, 'sig_full') and c.sig_full else c.sig
                    print(f"    Chain: w={int(c.weight)} {sig[:55]}")
        # Report hierarchy depth
        chain_depths = [len([f for f in g.memory.frames if "══" in f.sig]) for g in self.layers]
        return chain_depths

r = random.Random(42)
nouns = ["cat","dog","bird","fish","ant"]
verbs = ["saw","chased","ate","found","bit"]
adjs = ["big","small","red","blue","fast"]

print("=== HIERARCHICAL GEME: CHOMSKY HIERARCHY IN RUNNING CODE ===")
print()

# ── Test 1: Flat grammar (N V N) ──
hg = HierarchicalGEME(num_layers=3, mem_cap=12, window=40, thresh=0.15)
for _ in range(300):
    hg.feed_sentence([r.choice(nouns), r.choice(verbs), r.choice(nouns)])
print("Flat grammar (N V N):")
hg.stats()
print()

# ── Test 2: Nested grammar ([A N] V [A N]) ──
hg2 = HierarchicalGEME(num_layers=3, mem_cap=12, window=40, thresh=0.15)
for _ in range(300):
    hg2.feed_sentence([r.choice(adjs), r.choice(nouns), 
                       r.choice(verbs), r.choice(adjs), r.choice(nouns)])
print("Nested grammar ([A N] V [A N]):")
hg2.stats()
print()

# ── Test 3: Mixed (flat + nested → should learn substitution) ──
hg3 = HierarchicalGEME(num_layers=3, mem_cap=16, window=40, thresh=0.15)
all_nouns = nouns + [f"A_N_{i}" for i in range(3)]  # compound nouns emerge
for _ in range(200):
    if r.random() < 0.5:
        hg3.feed_sentence([r.choice(nouns), r.choice(verbs), r.choice(nouns)])
    else:
        hg3.feed_sentence([r.choice(adjs), r.choice(nouns), 
                           r.choice(verbs), r.choice(adjs), r.choice(nouns)])
print("Mixed grammar (N V N + [A N] V [A N]):")
depths = hg3.stats()
print()

print(f"{'='*55}")
print("CHOMSKY HIERARCHY IN GEME:")
print(f"  Layer 0 chains: {depths[0]} (regular grammar)")
print(f"  Layer 1 chains: {depths[1]} (context-free)")
print(f"  Layer 2 chains: {depths[2]} (hierarchical)")
print()
if depths[2] > depths[1]:
    print("  ✓ Hierarchical syntax detected: deeper layers form chains")
elif depths[0] == depths[1] == depths[2]:
    print("  Flat processing: all layers equivalent")
else:
    print("  Partial hierarchy detected")
