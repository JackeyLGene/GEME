# Grammar discovered through time: L1 clusters word vectors, L2 watches L1 change
# Each word = unit-time multi-dim vector
# Sentence = sequence of word vectors over time
# L1 forms categories, L2 sees sequence patterns = grammar
import sys, os, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

class GEME_Temporal(GEME):
    def observe_external(self, sigs, source="ext"):
        ft = self.memory._step_counter
        for sig in sigs:
            sig_id = f"{source}_{sig[:20]}"
            self.memory._window.append((sig_id, ft, (0.0,)*_VEC_DIM))
            if len(self.memory._window) > self.memory._win_max:
                self.memory._window.pop(0)

r = random.Random(42)

# Word set: 3 categories, 5 words each
nouns = ["cat","dog","bird","fish","ant"]
verbs = ["saw","chased","ate","found","bit"]
adjs = ["big","small","red","blue","fast"]
all_words = nouns + verbs + adjs
word_cat = {w:("N" if w in nouns else "V" if w in verbs else "A") for w in all_words}

# Generate word vectors: each word gets a random 5-dim vector (captures category similarity)
# Words in same category have SIMILAR vectors
r_vec = random.Random(123)
word_vec = {}
for w in nouns: word_vec[w] = [0.9 + r_vec.random()*0.2 for _ in range(5)] + [0]*22
for w in verbs: word_vec[w] = [0.3 + r_vec.random()*0.2 for _ in range(5)] + [0]*22
for w in adjs:  word_vec[w] = [0.6 + r_vec.random()*0.2 for _ in range(5)] + [0]*22

def gen_sentences(n=60):
    out = []
    for _ in range(n):
        n1 = r.choice(nouns); v = r.choice(verbs); n2 = r.choice(nouns)
        out.append((n1, v, n2))
    return [tuple([n1, v, n2]) for n1, v, n2 in out]

sentences = gen_sentences(60)

print("=== GRAMMAR DISCOVERED THROUGH TIME ===")
print("L1: word vectors -> category frames")
print("L2: observes L1's category changes over time -> grammar")
print()

# L1: word-level processing (time_window=1 per sentence = 3 words)
g1 = GEME_Temporal(memory_cap=16, cooccur_window=30, cooccur_thresh=0.08, max_chains=5, time_window_size=3)
g1.memory._chain_cooccur_thresh = 2

# L2: observes L1 (time_window=3 sentences)
g2 = GEME_Temporal(memory_cap=16, cooccur_window=30, cooccur_thresh=0.08, max_chains=5, time_window_size=9)
g2.memory._chain_cooccur_thresh = 2

for epoch in range(20):
    r.shuffle(sentences)
    for sent in sentences:
        for w in sent:
            vec = word_vec[w]
            sig = f"w_{word_cat[w]}"
            g1.process_sig(eq(fn("tk", const(w)), const("yes")), sig)
        
        # After each sentence, L2 observes L1's frame state
        l1_sigs = [f.sig_full or f.sig for f in g1.memory.frames if f.weight > 2]
        g2.observe_external(l1_sigs, "L1")
        
        # Also feed L2 the sentence pattern
        cats = "_".join(word_cat[w] for w in sent)
        g2.process_sig(eq(fn("pat", const(cats[:8])), const("yes")), f"p_{cats}")

print(f"L1 (word level):")
l1_frames = len(g1.memory.frames)
l1_chains = len([f for f in g1.memory.frames if "══" in (f.sig_full or f.sig)])
l1_assocs = len([f for f in g1.memory.frames if "──" in (f.sig_full or f.sig)])
print(f"  Frames: {l1_frames}, Assocs: {l1_assocs}, Chains: {l1_chains}")
print(f"  Self-observations: {g1.memory._self_observe_count}")

print(f"\nL2 (grammar level):")
l2_frames = len(g2.memory.frames)
l2_chains = len([f for f in g2.memory.frames if "══" in (f.sig_full or f.sig)])
l2_assocs = len([f for f in g2.memory.frames if "──" in (f.sig_full or f.sig)])
print(f"  Frames: {l2_frames}, Assocs: {l2_assocs}, Chains: {l2_chains}")

if l2_chains > 0:
    print(f"\nL2 chains (grammar discovered through time):")
    for c in sorted([f for f in g2.memory.frames if "══" in (f.sig_full or f.sig)], 
                    key=lambda x: x.weight, reverse=True):
        sig = c.sig_full or c.sig
        print(f"  w={int(c.weight):4d} {sig[:55]}")

# Show L1 frames
print(f"\nL1 frames (word categories):")
for f in sorted(g1.memory.frames, key=lambda x: x.weight, reverse=True)[:6]:
    sig = f.sig_full or f.sig
    t = "CHAIN" if "══" in sig else ("ASSOC" if "──" in sig else "FRAME")
    print(f"  [{t}] w={int(f.weight):3d} {sig[:40]}")

# Show L2 frames
print(f"\nL2 frames (grammar patterns):")
for f in sorted(g2.memory.frames, key=lambda x: x.weight, reverse=True)[:6]:
    sig = f.sig_full or f.sig
    t = "CHAIN" if "══" in sig else ("ASSOC" if "──" in sig else "FRAME")
    l1_ref = " [observes L1]" if "L1_" in sig else ""
    print(f"  [{t}] w={int(f.weight):3d} {sig[:40]}{l1_ref}")
