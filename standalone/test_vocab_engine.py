"""Test new GEME engine: character-level vocab discovery + L2 grammar."""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

SENTENCES = [
    "the cat sat on the mat","the dog chased the cat","a bird ate the fish",
    "the big cat saw the small dog","the red fish swam fast",
    "the small bird found the fish","the ant bit the dog",
    "a cat saw the red fish","the big dog ate the food",
    "the bird sat on the tree","the cat and the dog played",
    "a fish swam in the water","the small ant found food",
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

_chars = set("".join(SENTENCES))
_char_to_idx = {c:i for i,c in enumerate(sorted(_chars))}

def onehot(ch):
    v = [0.0]*_VEC_DIM
    idx = _char_to_idx.get(ch, 0) % _VEC_DIM
    v[idx] = 1.0
    return v

# ── L1: Characters → Words ──
g1 = GEME(memory_cap=64, cooccur_window=20, cooccur_thresh=0.08, max_chains=10)
g1.enable_vocab()

for epoch in range(15):
    random.shuffle(SENTENCES)
    for sent in SENTENCES:
        for ch in sent:
            g1.process_vec(onehot(ch), f"c{ord(ch):03d}")

print("=== L1: Character-level vocab discovery ===")
l1_frames = len(g1.memory.frames)
l1_assocs = len([f for f in g1.memory.frames if "──" in f.sig])
vocab = g1.get_vocab(min_weight=3)
print(f"Frames: {l1_frames}, Assocs: {l1_assocs}")
print(f"Vocabulary size: {len(vocab)}")
print(f"Discovered words: {sorted(vocab.keys())}")

# ── L2: Words → Grammar ──
g2 = GEME(memory_cap=16, cooccur_window=40, cooccur_thresh=0.12, max_chains=10)
for sent in SENTENCES:
    # Match against discovered vocabulary
    i = 0
    while i < len(sent):
        found = False
        for sz in [5,4,3,2]:
            if i+sz <= len(sent) and sent[i:i+sz] in vocab:
                g2.process_vec(onehot(sent[i]), f"w_{sent[i:i+sz]}")
                i += sz
                found = True
                break
        if not found:
            g2.process_vec(onehot(sent[i]), f"c{sent[i]}")
            i += 1

l2_frames = g2.memory.frames
l2_assocs = [f for f in l2_frames if "──" in f.sig]
l2_chains = [f for f in l2_frames if "══" in f.sig]

print(f"\n=== L2: Grammar from discovered vocabulary ===")
print(f"Frames: {len(l2_frames)}, Assocs: {len(l2_assocs)}, Chains: {len(l2_chains)}")
top = sorted(l2_frames, key=lambda x: x.weight, reverse=True)[:5]
for f in top:
    sig = f.sig_full if hasattr(f,'sig_full') and f.sig_full else f.sig
    t = "CHAIN" if "══" in sig else ("ASSOC" if "──" in sig else "FRAME")
    print(f"  [{t}] w={int(f.weight):4d} {sig[:55]}")
