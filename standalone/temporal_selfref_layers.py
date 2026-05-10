# Temporal self-reference: each layer observes the layer below's evolution
# L0: character-level processing
# L1: observes L0's frame changes over time
# L2: observes L1's frame changes over time
import sys, os, random
sys.path.insert(0, r"g:\GEME\final-v1.5")
from geme import GEME, eq, fn, const, structural_signature, _VEC_DIM

class GEME_Temporal(GEME):
    """Extended GEME: can observe external frame signatures."""
    def observe_external(self, external_sigs, source="ext"):
        """Feed external frame signatures into self-observation window.
        This lets this GEME 'see' what another GEME is doing."""
        feed_time = self.memory._step_counter
        for sig in external_sigs:
            safe = sig[:25]
            sig_id = f"{source}_{safe}"
            self.memory._window.append((sig_id, feed_time, (0.0,)*_VEC_DIM))
            if len(self.memory._window) > self.memory._win_max:
                self.memory._window.pop(0)

r = random.Random(42)

# L0: character processor (simulated: word tokens)
# L1: word pattern observer (looks at L0's frames over time)
# L2: grammar observer (looks at L1's frames over time)

token_map = {
    "cat": "N", "dog": "N", "bird": "N",
    "saw": "V", "chased": "V", "ate": "V",
    "big": "A", "small": "A", "the": "D", "a": "D",
}

# Generate sentences
sentences = [
    ("the", "cat", "saw", "the", "dog"),
    ("a", "dog", "chased", "a", "cat"),
    ("the", "big", "cat", "saw", "the", "small", "dog"),
    ("a", "bird", "ate", "the", "fish"),
    ("the", "cat", "chased", "a", "bird"),
    ("a", "small", "dog", "saw", "the", "cat"),
]

def sent_to_sigs(sent):
    return [f"tok_{token_map.get(w, 'X')}" for w in sent]

print("=== TEMPORAL SELF-REFERENCE: LAYERS OBSERVING LAYERS ===")
print()

# L0 + L1 + L2
g0 = GEME_Temporal(memory_cap=12, cooccur_window=40, cooccur_thresh=0.1, max_chains=3, time_window_size=20)
g1 = GEME_Temporal(memory_cap=12, cooccur_window=40, cooccur_thresh=0.1, max_chains=3, time_window_size=20)
g2 = GEME_Temporal(memory_cap=12, cooccur_window=40, cooccur_thresh=0.1, max_chains=3, time_window_size=20)

# Set chain thresholds
for g in [g0, g1, g2]:
    g.memory._chain_cooccur_thresh = 2

# Run temporal simulation
for epoch in range(10):
    r.shuffle(sentences)
    for sent in sentences:
        # L0 processes tokens
        for tok in sent_to_sigs(sent):
            g0.process_sig(eq(fn("tok", const(tok)), const("yes")), f"tok_{tok}")
        
        # L1 observes L0's current frame signatures
        g1.observe_external(
            [f.sig_full or f.sig for f in g0.memory.frames if f.weight > 2],
            "L0"
        )
        
        # L1 also processes its own input (abstract patterns)
        cats = "_".join(token_map.get(w, "X") for w in sent)
        g1.process_sig(eq(fn("pat", const(cats[:10])), const("yes")), f"pat_{cats}")
        
        # L2 observes L1's current frame signatures
        g2.observe_external(
            [f.sig_full or f.sig for f in g1.memory.frames if f.weight > 2],
            "L1"
        )
        g2.process_sig(eq(fn("meta", const(cats[:6])), const("yes")), f"meta_{cats}")

print(f"L0: {len(g0.memory.frames)} frames, "
      f"{len([f for f in g0.memory.frames if '══' in (f.sig_full or f.sig)])} chains")
print(f"L1: {len(g1.memory.frames)} frames, "
      f"{len([f for f in g1.memory.frames if '══' in (f.sig_full or f.sig)])} chains "
      f"(self-obs: {g1.memory._self_observe_count})")
print(f"L2: {len(g2.memory.frames)} frames, "
      f"{len([f for f in g2.memory.frames if '══' in (f.sig_full or f.sig)])} chains "
      f"(self-obs: {g2.memory._self_observe_count})")

# Analyze: does L1 have chains that reference L0?
l0_ref = [f for f in g1.memory.frames if "L0_" in (f.sig_full or f.sig)]
print(f"\nL1 frames referencing L0: {len(l0_ref)}")
l1_ref = [f for f in g2.memory.frames if "L1_" in (f.sig_full or f.sig)]
print(f"L2 frames referencing L1: {len(l1_ref)}")

# Temporal self-reference: L1 sees L0 changing, L2 sees L1 changing
print(f"\nTemporal self-reference chain:")
print(f"  L0 -> L0 changes -> L1 observes L0 -> L1 chains")
print(f"  L1 -> L1 changes -> L2 observes L1 -> L2 chains")
print(f"  The system sees itself in time")
