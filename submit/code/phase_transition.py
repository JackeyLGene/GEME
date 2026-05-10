"""
Phase transition experiment v4: self-observation frequency as control parameter.

v2: adaptive threshold acts as homeostat → no phase transition in (d,g) space.
v3: fixed threshold, cyclic input → input structure dominates, no phase transition.

v4 hypothesis: the TRUE phase transition in GEME is between two dynamical regimes:
  - EXTERNALLY-DRIVEN: system tracks input, self_observe is a minor perturbation
  - SELF-DRIVEN: self_observe feedback loop dominates, system ignores external input

Control parameter: k = self_observe interval (steps between self-observations)
  - k large (infrequent self-obs) → system tracks external world
  - k small (frequent self-obs) → feedback loop amplifies → system enters
    self-referential regime where centroid dominates over external input

This would be a genuine dynamical bifurcation — the system spontaneously transitions
from one attractor to another as k crosses a critical value k_c.

Key measurements:
  1. Order parameter: fraction of frames sourced from self_obs vs external input
  2. Bifurcation diagram: frame count vs k (look for sudden jump)
  3. Critical fluctuations: variance peaks near k_c
  4. Hysteresis: sweep k up then down
"""
import sys, math
sys.path.insert(0, '.')
from geme import _VEC_DIM, DELTA, GAMMA, TAU, Frame
import random


class SelfObsMemory:
    """Memory where self-observation frequency k is the control parameter.
    d=DELTA (fixed at original 0.19), g=GAMMA (fixed at 0.05).
    Only k varies: how many external inputs between each self_observe."""

    def __init__(self, k_self_obs, capacity=16):
        self.frames = []
        self.capacity = max(capacity, 1)
        self.total_weight = 0.0
        self._step_counter = 0
        self._k = k_self_obs
        self._frame_id = 0
        self._merge_dists = []
        self._learn_dists = []
        # Tracking
        self.n_self_obs_frames = 0    # frames whose source is self_obs
        self.n_external_frames = 0     # frames whose source is external input

    def _adaptive_thresh(self):
        if not self._merge_dists:
            if len(self._learn_dists) < 10:
                return None
            t = sorted(self._learn_dists)[len(self._learn_dists) // 4]
            if t <= 0:
                t = 0.001
            self._merge_dists.append(t)
            return t
        med = sorted(self._merge_dists[-50:])[len(self._merge_dists[-50:]) // 2] if self._merge_dists else 0.001
        last = self._merge_dists[-1] if self._merge_dists else 0.001
        return max(med, last * 0.5)

    def observe(self, vec, source="ext"):
        if not vec:
            return
        thresh = self._adaptive_thresh()
        bi, bd = -1, float('inf')
        for i, f in enumerate(self.frames):
            d = math.sqrt(sum((a - b) ** 2 for a, b in zip(vec, f.vec)))
            if d < bd:
                bd, bi = d, i
        if thresh is None and bi >= 0 and bd != float('inf'):
            self._learn_dists.append(bd)
            if len(self._learn_dists) > 200:
                self._learn_dists.pop(0)
        if thresh is not None and bi >= 0 and bd <= thresh:
            self._merge_dists.append(bd)
            if len(self._merge_dists) > 100:
                self._merge_dists.pop(0)
            f = self.frames[bi]
            self.total_weight -= f.weight
            f.vec = tuple((f.vec[j] * f.weight + vec[j]) / (f.weight + 1) for j in range(len(vec)))
            f.weight += 1.0
            f.merged += 1
            self.total_weight += f.weight
        else:
            if len(self.frames) >= self.capacity:
                self.frames.sort(key=lambda x: x.weight)
                removed = self.frames.pop(0)
                self.total_weight -= removed.weight
            nf = Frame(vec, 1.0)
            nf.fid = self._frame_id
            self._frame_id += 1
            self.frames.append(nf)
            self.total_weight += 1.0
            if source == "self_obs":
                self.n_self_obs_frames += 1
            else:
                self.n_external_frames += 1
        self._step_counter += 1

    def self_observe(self):
        active = [f for f in self.frames if f.weight > 2]
        if not active:
            return None
        total_w = sum(f.weight for f in active)
        dim = len(active[0].vec)
        centroid = tuple(
            sum(f.vec[j] * f.weight for f in active) / total_w
            for j in range(dim)
        )
        self.observe(centroid, source="self_obs")
        return centroid

    def induction_clean(self):
        self.self_observe()
        for f in self.frames:
            self.total_weight -= f.weight
            if f.merged == 0:
                f.weight *= math.exp(-GAMMA / 0.25)
            elif f.merged < 3:
                f.weight *= math.exp(-GAMMA)
            f.weight = max(1.0, f.weight)
            self.total_weight += f.weight
            f.age += 1
        self.frames.sort(key=lambda x: x.weight - x.age * GAMMA, reverse=True)
        half = max(1, len(self.frames) // 2)
        for f in self.frames[half:]:
            self.total_weight -= f.weight
        self.frames = self.frames[:half]

    def gini(self):
        if not self.frames or self.total_weight <= 0:
            return 0.0
        w = sorted([f.weight for f in self.frames])
        n = len(w)
        total = sum(w)
        if total <= 0:
            return 0.0
        numerator = sum((i + 1) * w[i] for i in range(n))
        return max(0.0, (2.0 * numerator - (n + 1) * total) / (n * total))

    def self_obs_ratio(self):
        total = self.n_self_obs_frames + self.n_external_frames
        if total == 0:
            return 0.0
        return self.n_self_obs_frames / total


# ============================================================
# Experiment 1: BIFURCATION DIAGRAM — sweep k
# ============================================================
def bifurcation_sweep(k_values, steps=1000, trials=3):
    """For each k, run multiple trials and record order parameters.
    k = number of external inputs between each self_observe.
    k=1: self_observe after every external input (maximum feedback)
    k=10: self_observe every 10 inputs (moderate feedback)
    k=50: self_observe every 50 inputs (weak feedback)
    k=inf: no self_observe at all (only induction_clean calls it)"""
    results = []
    for k in k_values:
        trial_data = []
        for seed in range(trials):
            rng = random.Random(seed * 100 + k)
            mem = SelfObsMemory(k_self_obs=k, capacity=16)
            mem._merge_dists = [DELTA] * 50

            for s in range(steps):
                # External input
                idx = s % 6
                v = [0.0] * _VEC_DIM
                v[idx] = 1.0
                v[(idx + 2) % _VEC_DIM] = 0.3
                mem.observe(v, source="ext")

                # Self-observe at interval k
                if k > 0 and s % k == (k - 1):
                    mem.self_observe()

                # Periodic induction
                if s % 20 == 19:
                    mem.induction_clean()

            trial_data.append({
                'gini': mem.gini(),
                'n_frames': len(mem.frames),
                'self_obs_ratio': mem.self_obs_ratio(),
            })

        avg_gini = sum(d['gini'] for d in trial_data) / len(trial_data)
        avg_nf = sum(d['n_frames'] for d in trial_data) / len(trial_data)
        avg_ratio = sum(d['self_obs_ratio'] for d in trial_data) / len(trial_data)
        std_gini = (sum((d['gini'] - avg_gini)**2 for d in trial_data) / len(trial_data)) ** 0.5
        std_ratio = (sum((d['self_obs_ratio'] - avg_ratio)**2 for d in trial_data) / len(trial_data)) ** 0.5

        results.append({
            'k': k,
            'gini': avg_gini,
            'gini_std': std_gini,
            'n_frames': avg_nf,
            'self_obs_ratio': avg_ratio,
            'ratio_std': std_ratio,
            'raw_gini': [d['gini'] for d in trial_data],
        })

    return results


# ============================================================
# Experiment 2: HYSTERESIS — sweep k up then down
# ============================================================
def hysteresis_k(k_range, steps_per=600):
    forward = []
    backward = []

    # Forward: k increasing (feedback DECREASING)
    mem = SelfObsMemory(k_self_obs=k_range[0], capacity=16)
    mem._merge_dists = [DELTA] * 50
    rng = random.Random(99)
    for k in k_range:
        mem._k = k
        for s in range(steps_per):
            idx = s % 6
            v = [0.0] * _VEC_DIM
            v[idx] = 1.0
            v[(idx + 2) % _VEC_DIM] = 0.3
            mem.observe(v, source="ext")
            if k > 0 and s % k == (k - 1):
                mem.self_observe()
            if s % 20 == 19:
                mem.induction_clean()
        forward.append((k, len(mem.frames), mem.gini(), mem.self_obs_ratio()))

    # Backward: k decreasing (feedback INCREASING)
    for k in reversed(k_range):
        mem._k = k
        for s in range(steps_per):
            idx = s % 6
            v = [0.0] * _VEC_DIM
            v[idx] = 1.0
            v[(idx + 2) % _VEC_DIM] = 0.3
            mem.observe(v, source="ext")
            if k > 0 and s % k == (k - 1):
                mem.self_observe()
            if s % 20 == 19:
                mem.induction_clean()
        backward.append((k, len(mem.frames), mem.gini(), mem.self_obs_ratio()))

    return forward, backward


# ============================================================
# Experiment 3: BISTABILITY — many runs at critical k
# ============================================================
def bistability_k(k, n_runs=20, steps=1200):
    ginis = []
    ratios = []
    for seed in range(n_runs):
        rng = random.Random(seed * 77 + k * 3)
        mem = SelfObsMemory(k_self_obs=k, capacity=16)
        mem._merge_dists = [DELTA] * 50
        for s in range(steps):
            idx = s % 6
            v = [0.0] * _VEC_DIM
            v[idx] = 1.0
            v[(idx + 2) % _VEC_DIM] = 0.3
            mem.observe(v, source="ext")
            if k > 0 and s % k == (k - 1):
                mem.self_observe()
            if s % 20 == 19:
                mem.induction_clean()
        ginis.append(mem.gini())
        ratios.append(mem.self_obs_ratio())
    return ginis, ratios


# ============================================================
# Run
# ============================================================
if __name__ == "__main__":
    print("=" * 70)
    print("PHASE TRANSITION v4: Self-Observation Frequency as Control Parameter")
    print("Question: does the system bifurcate from externally-driven to")
    print("self-driven regime as k (self-obs interval) crosses a critical value?")
    print("=" * 70)

    # --- Bifurcation Diagram ---
    k_vals = [0, 1, 2, 3, 4, 5, 7, 10, 15, 20, 30, 50]
    print("\n--- BIFURCATION DIAGRAM ---")
    print(f"{'k':>4} {'Gini':>8} {'std':>8} {'N_frames':>10} {'self_obs%':>12} {'std%':>8}  Distribution")
    print("-" * 75)
    results = bifurcation_sweep(k_vals, steps=1000, trials=5)
    for r in results:
        k = r['k']
        g = r['gini']
        gs = r['gini_std']
        nf = r['n_frames']
        ratio = r['self_obs_ratio']
        rs = r['ratio_std']
        # Visual distribution
        raw = r['raw_gini']
        bar = ""
        for gi in sorted(raw):
            if gi < 0.2:
                bar += "."
            elif gi < 0.5:
                bar += "o"
            elif gi < 0.7:
                bar += "O"
            else:
                bar += "@"
        print(f"{k:4d} {g:8.4f} {gs:8.4f} {nf:10.1f} {ratio:11.4f} {rs:8.4f}  [{bar}]")

    # --- Hysteresis ---
    print("\n" + "=" * 70)
    print("HYSTERESIS SWEEP (k forward then backward)")
    k_hyst = [1, 2, 3, 4, 5, 7, 10, 15, 20, 30, 50]
    fwd, bwd = hysteresis_k(k_hyst, steps_per=400)
    print(f"\n{'k':>4} {'N_fwd':>6} {'Gini_fwd':>10} {'ratio_fwd':>10} | {'N_bwd':>6} {'Gini_bwd':>10} {'ratio_bwd':>10}")
    print("-" * 65)
    for i, (k, nf, gf, rf) in enumerate(fwd):
        _, nb, gb, rb = bwd[i]
        dg = gf - gb
        flag = " <--" if abs(dg) > 0.03 else ""
        print(f"{k:4d} {nf:6d} {gf:10.4f} {rf:10.4f} | {nb:6d} {gb:10.4f} {rb:10.4f}{flag}")

    # --- Bistability ---
    print("\n" + "=" * 70)
    print("BISTABILITY TEST (20 runs each at critical k)")
    for k_test in [1, 2, 3, 5, 10, 30]:
        ginis, ratios = bistability_k(k_test, n_runs=20, steps=1200)
        avg_g = sum(ginis) / len(ginis)
        std_g = (sum((x - avg_g)**2 for x in ginis) / len(ginis)) ** 0.5
        mn, mx = min(ginis), max(ginis)
        span = mx - mn
        unique = len(set(round(x, 3) for x in ginis))
        mode = "MULTIMODAL!" if unique > 5 else ("BIMODAL!" if unique > 2 else "unimodal")
        print(f"  k={k_test:2d}: Gini={avg_g:.4f}+/-{std_g:.4f} range=[{mn:.4f},{mx:.4f}] "
              f"span={span:.4f} {unique} unique → {mode}")

    print("\n" + "=" * 70)
    print("INTERPRETATION:")
    print("  k=1: maximum feedback — self_obs after EVERY external input")
    print("  k=50: minimum feedback — self_obs every 50 inputs")
    print("  k=0: no self_obs between inductions (baseline)")
    print("  If bifurcation exists: order parameter should JUMP at some k_c")
    print("  If crossover: smooth change across all k")
    print("=" * 70)
