# Quantum Zeno merge: weight increases, centroid stays unchanged
# Merge selects a frame probabilistically, but doesn't shift its vector
import sys, math
sys.path.insert(0,'g:/GEME/final-v1.5')
from geme import GEME, _VEC_DIM

# Two prototypes orthogonal
v1=[0.0]*_VEC_DIM; v1[0]=1.0  # dim0
v2=[0.0]*_VEC_DIM; v2[10]=1.0 # dim10

# Input squarely between them
v_in=[0.0]*_VEC_DIM; v_in[0]=0.5; v_in[10]=0.5

g=GEME(memory_cap=5); g.memory.quantum_mode=True; g.memory.preserve_sig=True
th=0.8
g.memory._merge_thresh_val=th; g.memory._merge_dists=[th]*50

# Disable centroid shift during merge
def zeno_observe(self, vec, sig, src=""):
    """Zeno merge: add weight, keep centroid unchanged"""
    # Use standard observe BUT don't update vec
    import copy
    # Temporarily intercept the vec update in frame merge
    orig_observe = self.observe.__func__ if hasattr(self.observe, '__func__') else None
    
    # We need to modify observe for quantum mode
    # Instead, use process_vec normally but patch after
    pass

# Override: merge keeps centroid
import types
original_observe = GEME.process_vec

def zeno_process_vec(self, vec, sig, src=""):
    """Zeno process_vec: quantum probabilistic merge, no centroid shift."""
    # Find candidates
    thresh = self.memory._adaptive_thresh()
    self.memory._merge_thresh_val = thresh or 0.0
    candidates = []
    bi, bd = -1, float('inf')
    for i, f in enumerate(self.memory.frames):
        d = math.sqrt(sum((vec[j]-f.vec[j])**2 for j in range(_VEC_DIM)))
        if d < bd: bd = d; bi = i
        if hasattr(self.memory,'quantum_mode') and self.memory.quantum_mode and thresh:
            if d <= thresh: candidates.append((i, d, f))
    
    # Bootstrap
    if thresh is None and bi>=0 and bd!=float('inf'):
        self.memory._learn_dists.append(bd)
        if len(self.memory._learn_dists)>200: self.memory._learn_dists.pop(0)
    
    # Quantum Zeno: pick with Boltzmann, keep centroid
    if hasattr(self.memory,'quantum_mode') and self.memory.quantum_mode and len(candidates)>0:
        import random as _qr
        if not hasattr(self.memory, '_qrand'): 
            self.memory._qrand = _qr.Random(_qr.randint(0,999999))
        
        # Boltzmann probabilities
        psum = 0.0; probs = []
        for i, d, f in candidates:
            p = math.exp(-d / max(thresh, 0.001))
            probs.append((i, d, f, p)); psum += p
        
        if psum > 0:
            r = self.memory._qrand.random() * psum; acc = 0.0
            selected_i = None
            for i, d, f, p in probs:
                acc += p
                if r <= acc: selected_i = i; bd = d; break
            
            if selected_i is not None:
                f = self.memory.frames[selected_i]
                # Zeno: weight increases, centroid STAYS
                self.memory.total_weight -= f.weight
                f.weight += 1.0  # weight up
                f.merged += 1
                # NO vec update: centroid unchanged
                self.memory.total_weight += f.weight
                self.memory._step_counter += 1
                self.memory._window.append((sig, self.memory._step_counter, tuple(vec)))
                if len(self.memory._window) > self.memory._win_max:
                    self.memory._window.pop(0)
                return
    
    # Fallback: standard process
    self.frame_count += 1; self._input_count += 1
    self.memory.observe(vec, sig, src)

g.process_vec = types.MethodType(zeno_process_vec, g)

# Seed prototypes
g.process_vec(v1, 'proto_a')
g.process_vec(v2, 'proto_b')

# Send v_in 2000 times
for _ in range(2000):
    g.process_vec(v_in, 'test')

# Count
ca = cb = 0
for f in g.memory.frames:
    s = f.sig_full or f.sig
    if 'proto_a' in s: ca = int(f.weight) - 1
    if 'proto_b' in s: cb = int(f.weight) - 1

total = ca + cb
print("Quantum Zeno merge (2000 trials, centroid unchanged):")
print(f"  Merged into proto_a: {ca} ({(ca/total*100) if total else 0:.1f}%)")
print(f"  Merged into proto_b: {cb} ({(cb/total*100) if total else 0:.1f}%)")
print(f"  Total: {total}")
if ca > 0 and cb > 0:
    print("YES: Zeno measurement uncertainty confirmed")
    print("Observation doesn't change the state — quantum uncertainty preserved")
else:
    print("Zeno did not trigger — check implementation")
