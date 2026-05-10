"""
Effective Memory Window experiment.
Tests whether a single composite parameter P = f(delta, gamma, tau)
predicts the system's stable frame count N_eq.

Hypothesis: N_eq is determined not by C (hard capacity) alone, but by the
interplay of merge tolerance (delta), forgetting rate (gamma), and
induction threshold (tau). These define an "effective memory window" —
how many distinct inputs can coexist in the frame economy before the
oldest are forgotten faster than they are validated.

Candidate composites:
  P1 = delta / gamma          merge tolerance per forgetting timescale
  P2 = delta / (gamma * tau)  ... per induction cycle
  P3 = 1 / (gamma * tau)      forgetting-induction interaction (delta-invariant)
  P4 = delta * tau / gamma    alternative parameterization

If N_eq = f(P) for some P, then varying (d,g,t) while keeping P constant
should produce the same N_eq — confirming that the three constants
collapse to a single degree of freedom in determining capacity.
"""
import sys, math
sys.path.insert(0, '.')
from geme import _VEC_DIM, Frame, GAMMA as G0, TAU as T0, DELTA as D0
import random


class ParamMemory:
    """Memory with independently settable delta, gamma, tau, capacity."""

    def __init__(self, delta, gamma, tau, capacity=32):
        self.frames = []
        self.capacity = max(capacity, 1)
        self.total_weight = 0.0
        self._step_counter = 0
        self._merge_dists = []
        self._learn_dists = []
        self._delta = delta
        self._gamma = gamma
        self._tau = tau
        self._frame_id = 0
        self._stress_accum = 0.0

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

    def observe(self, vec):
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
        self._step_counter += 1

    def induction_clean(self):
        for f in self.frames:
            self.total_weight -= f.weight
            if f.merged == 0:
                f.weight *= math.exp(-self._gamma / 0.25)
            elif f.merged < 3:
                f.weight *= math.exp(-self._gamma)
            f.weight = max(1.0, f.weight)
            self.total_weight += f.weight
            f.age += 1
        self.frames.sort(key=lambda x: x.weight - x.age * self._gamma, reverse=True)
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


def measure_N_eq(delta, gamma, tau, n_patterns=20, steps=1500, capacity=32, trials=3):
    """Measure stable frame count for given (delta, gamma, tau).
    Uses n_patterns distinct inputs to ensure the system is not
    input-limited — the convergence value reflects internal dynamics."""
    n_frames_list = []
    for seed in range(trials):
        rng = random.Random(seed * 419 + int(delta * 10000 + gamma * 1000 + tau * 100))
        mem = ParamMemory(delta=delta, gamma=gamma, tau=tau, capacity=capacity)
        mem._merge_dists = [delta] * 50

        for t in range(steps):
            idx = t % n_patterns
            v = [0.0] * _VEC_DIM
            v[idx] = 1.0
            v[(idx + int(delta * 100)) % _VEC_DIM] = 0.3  # slight variation
            mem.observe(v)

            # Stress-based induction
            stress = min(1.0, len(mem.frames) / capacity) * (1.0 - mem.gini())
            mem._stress_accum += stress * 0.1
            if mem._stress_accum > tau and t > 50:
                mem.induction_clean()
                mem._stress_accum = 0.0
                mem._merge_dists = mem._merge_dists[-30:] if mem._merge_dists else [delta] * 30

        n_frames_list.append(len(mem.frames))

    return sum(n_frames_list) / len(n_frames_list)


def composite(delta, gamma, tau, form):
    """Compute composite parameter."""
    if form == 'P1':  # delta / gamma
        return delta / max(gamma, 0.001)
    elif form == 'P2':  # delta / (gamma * tau)
        return delta / max(gamma * tau, 0.0001)
    elif form == 'P3':  # 1 / (gamma * tau)
        return 1.0 / max(gamma * tau, 0.0001)
    elif form == 'P4':  # delta * tau / gamma
        return delta * tau / max(gamma, 0.001)
    elif form == 'P5':  # delta / gamma * exp(-tau)
        return delta / max(gamma, 0.001) * math.exp(-tau)
    elif form == 'P6':  # tau / gamma (induction timescale)
        return tau / max(gamma, 0.001)
    else:
        return 0.0


if __name__ == '__main__':
    print("=" * 70)
    print("Effective Memory Window Experiment")
    print("Testing: does N_eq = f(P) for some composite P(delta, gamma, tau)?")
    print("=" * 70)

    # ---- Part 1: Vary each constant independently ----
    print("\n--- Part 1: Independent variation ---")

    # Vary delta
    print("\n  N_eq vs delta (gamma=0.05, tau=0.60):")
    for d in [0.05, 0.10, 0.15, 0.19, 0.25, 0.30, 0.40, 0.50]:
        neq = measure_N_eq(d, G0, T0, n_patterns=20, steps=1000, trials=3)
        bar = "#" * int(neq)
        print(f"    delta={d:.2f}  N_eq={neq:.1f}  {bar}")

    # Vary gamma
    print("\n  N_eq vs gamma (delta=0.19, tau=0.60):")
    for g in [0.01, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20, 0.30]:
        neq = measure_N_eq(D0, g, T0, n_patterns=20, steps=1000, trials=3)
        bar = "#" * int(neq)
        print(f"    gamma={g:.2f}  N_eq={neq:.1f}  {bar}")

    # Vary tau
    print("\n  N_eq vs tau (delta=0.19, gamma=0.05):")
    for t in [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0]:
        neq = measure_N_eq(D0, G0, t, n_patterns=20, steps=1000, trials=3)
        bar = "#" * int(neq)
        print(f"    tau={t:.2f}  N_eq={neq:.1f}  {bar}")

    # ---- Part 2: Composite parameter test ----
    # Hold P constant while varying (d,g,t) — does N_eq stay constant?
    print(f"\n{'='*70}")
    print("Part 2: Hold composite P constant, vary (d,g,t)")
    print("If N_eq = f(P), then N_eq should be CONSTANT across rows")
    print(f"{'='*70}")

    for form_name in ['P1', 'P2', 'P3', 'P4', 'P5', 'P6']:
        print(f"\n  --- {form_name} = {form_name} ---")

        # Pick a reference P from the GEME defaults
        P_ref = composite(D0, G0, T0, form_name)

        # Generate (d,g,t) triples with approximately the same P
        # Vary gamma and tau, adjust delta to keep P constant
        test_points = []
        for g in [0.03, 0.05, 0.07, 0.10]:
            for t in [0.4, 0.6, 0.8]:
                if form_name == 'P1':
                    d = P_ref * g
                elif form_name == 'P2':
                    d = P_ref * g * t
                elif form_name == 'P3':
                    d = D0  # delta-independent
                elif form_name == 'P4':
                    d = P_ref * g / t
                elif form_name == 'P5':
                    d = P_ref * g / math.exp(-t)
                elif form_name == 'P6':
                    d = D0  # delta-independent
                else:
                    d = D0

                # Clamp delta to reasonable range
                if 0.03 <= d <= 0.60:
                    test_points.append((d, g, t))

        if not test_points:
            print("    (no valid points in range)")
            continue

        neq_values = []
        P_values = []
        for d, g, t in test_points:
            neq = measure_N_eq(d, g, t, n_patterns=20, steps=1000, trials=2)
            P_actual = composite(d, g, t, form_name)
            neq_values.append(neq)
            P_values.append(P_actual)
            print(f"    d={d:.3f} g={g:.2f} t={t:.1f}  P={P_actual:.2f}  N_eq={neq:.1f}")

        # Check constancy: CV of N_eq across all points with same P
        avg_neq = sum(neq_values) / len(neq_values)
        std_neq = (sum((n - avg_neq)**2 for n in neq_values) / len(neq_values)) ** 0.5
        cv = std_neq / max(avg_neq, 0.1)
        verdict = "CONSTANT (P predicts N_eq)" if cv < 0.15 else "VARIABLE (P does NOT predict N_eq)"
        print(f"    N_eq range: [{min(neq_values):.1f}, {max(neq_values):.1f}]  CV={cv:.3f}  -> {verdict}")

    # ---- Part 3: The 6±2 attractor basin ----
    print(f"\n{'='*70}")
    print("Part 3: The 6+-2 attractor basin")
    print("For what range of (delta, gamma, tau) does N_eq fall in 4-8?")
    print(f"{'='*70}")

    d_vals = [0.05, 0.10, 0.15, 0.19, 0.25, 0.30, 0.40]
    g_vals = [0.01, 0.03, 0.05, 0.07, 0.10, 0.15, 0.20]
    t_vals = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]

    print(f"\n  N_eq at tau=0.60 (fixed), varying (delta, gamma):")
    print(f"  {'d\\g':>6}", end="")
    for g in g_vals:
        print(f"{g:8.2f}", end="")
    print(f"\n  {'-'*60}")
    for d in d_vals:
        print(f"  {d:6.2f}", end="")
        for g in g_vals:
            neq = measure_N_eq(d, g, T0, n_patterns=20, steps=1000, trials=2)
            in_range = " *" if 4 <= neq <= 8 else ""
            print(f"{neq:7.1f}{in_range}", end="")
        print()

    print(f"\n  Cells marked * have N_eq in [4, 8] (the 6+-2 basin)")
    print(f"  GEME defaults: delta={D0}, gamma={G0}, tau={T0}")
    print(f"  Composite P1 = delta/gamma = {D0/G0:.1f}")
    print(f"  Composite P2 = delta/(gamma*tau) = {D0/(G0*T0):.1f}")
    print(f"  Composite P6 = tau/gamma = {T0/G0:.1f}")
