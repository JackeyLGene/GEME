"""
GI_n → δ 递归深度实验

假说：GI 是 Feigenbaum δ ≈ 4.669 在自指系统中的投影。
预测：GI₁ ≈ 4.0, GI₂ > GI₁, GI_n → δ as n → ∞.
"""
import sys, os, math, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase
from geme import eq, fn, const, structural_signature, symbol_vector
import random as _rnd

DEPTH = 3
STEPS = 4000
VEC_DIM = 27
MEM_CAP = 20

class RecursiveStack:
    def __init__(self, depth, vec_dim, mem_cap, seed=42):
        self.depth = depth
        self.layers = []
        self.phase_logs = [[] for _ in range(depth)]
        self.transitions = [[] for _ in range(depth)]

        for i in range(depth):
            g = Geruon(vec_dim=vec_dim, memory_cap=mem_cap, cooccur_window=80)
            g.memory.quantum_mode = True
            g.memory._qrand = _rnd.Random(seed + i * 777)
            self.layers.append(g)

    def step(self, ext_vec, ext_sig=''):
        vec = ext_vec
        for i, g in enumerate(self.layers):
            if i == 0:
                sig = ext_sig
            else:
                # Encode the phase of the previous layer into the sig
                prev_phase = self.layers[i-1].phase.value
                sig = f'L{i}_ph_{prev_phase}'
            g.process_vec(list(vec), sig)
            ph = g.phase.value
            self.phase_logs[i].append(ph)
            if len(self.phase_logs[i]) >= 2:
                prev = self.phase_logs[i][-2]
                if prev != ph:
                    self.transitions[i].append(
                        (len(self.phase_logs[i]) - 1, prev, ph))
            vec = g.phase_output()

    def run(self, steps, seed=42):
        r = _rnd.Random(seed)
        symbols = ['0','1','s','+','x','y','z','swap','pair','comm','succ']
        for s in range(steps):
            a, b, c = r.choice(symbols), r.choice(symbols), r.choice(symbols)
            if s % 3 == 0:
                f = eq(fn(a, const(b)), const(c))
            elif s % 3 == 1:
                f = eq(fn('swap', const(a), const(b)),
                       fn('swap', const(b), const(a)))
            else:
                f = eq(fn(a, fn(b, const(c))), fn(b, fn(a, const(c))))
            self.step(list(symbol_vector(f)), structural_signature(f))


def measure(transitions):
    """Average inter-transition interval."""
    if len(transitions) < 5:
        return None
    steps = [t[0] for t in transitions]
    intervals = [steps[i+1] - steps[i] for i in range(len(steps)-1)]
    return statistics.mean(intervals)


if __name__ == '__main__':
    print(f"GI_n -> delta  Depth={DEPTH} Steps={STEPS} dim={VEC_DIM} cap={MEM_CAP}")
    print("=" * 60)

    stack = RecursiveStack(DEPTH, VEC_DIM, MEM_CAP)
    stack.run(STEPS)

    periods = []
    for i in range(DEPTH):
        g = stack.layers[i]
        n_trans = len(stack.transitions[i])
        T = measure(stack.transitions[i])
        periods.append(T)

        ph_counts = {}
        for ph in stack.phase_logs[i]:
            ph_counts[ph] = ph_counts.get(ph, 0) + 1
        dom_phase = max(ph_counts, key=ph_counts.get) if ph_counts else '?'

        t_str = f"{T:.1f}" if T else "N/A"
        print(f"L{i}: tau={g.tau:.4f} {dom_phase} "
              f"trans={n_trans} T={t_str}  phases={dict(sorted(ph_counts.items()))}")

    print("-" * 60)
    print("GI MEASUREMENTS vs Feigenbaum delta=4.669")
    for i in range(DEPTH - 1):
        if periods[i] and periods[i+1] and periods[i] > 0:
            gi = periods[i+1] / periods[i]
            err_pct = (gi - 4.669) / 4.669 * 100
            print(f"  GI_{i+1} = T_{i+1}/T_{i} = {gi:.3f}  "
                  f"(delta={4.669:.1f}, err={err_pct:+.1f}%)")
        else:
            print(f"  GI_{i+1} = N/A")

    if periods[0] and periods[0] > 0:
        print(f"\n  BGM baseline: GI_1 = T_g0/T_unit = 4.0")
        print(f"  This run:    GI_1 = {periods[1]/periods[0]:.3f}" if periods[1] else "  GI_1 = N/A")
