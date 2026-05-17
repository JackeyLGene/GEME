"""
Goldberg → single Geruon → measure GI as period-doubling within one run.

The Feigenbaum hypothesis: GI is not a multi-layer ratio but the
period-doubling constant of self-referential dynamics. We measure it
by comparing phase cycle periods at different stages of processing.
"""
import sys, os, math, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase
from goldberg import make_stream

VEC_DIM = 27
STEPS_PER_PASS = 96  # 32 variations × 3 micro-events

stream = make_stream(passes=80)
total = len(stream)
print(f"Goldberg stream: {total} steps ({total//STEPS_PER_PASS} passes)")

g = Geruon(vec_dim=VEC_DIM, memory_cap=24, cooccur_window=120)
g.memory.quantum_mode = True

# Track phase at every step
phase_traj = []
tau_traj = []
for step, vec in enumerate(stream):
    sig = f'v{step % STEPS_PER_PASS}'
    g.process_vec(list(vec), sig)
    phase_traj.append(g.phase.value)
    tau_traj.append(g.tau)
    if step % 1000 == 0:
        print(f"  step {step}: tau={g.tau:.4f} phase={g.phase.value}")

# Compute phase transition intervals
transitions = []
for i in range(1, len(phase_traj)):
    if phase_traj[i] != phase_traj[i-1]:
        transitions.append((i, phase_traj[i-1], phase_traj[i]))

print(f"\nTotal transitions: {len(transitions)}")
print(f"Final tau: {g.tau:.4f}  phase: {g.phase.value}")

if len(transitions) < 10:
    print("Not enough transitions for GI measurement")
    exit()

# Split into thirds: early, middle, late
n = len(transitions)
t_early = transitions[:n//3]
t_mid   = transitions[n//3:2*n//3]
t_late  = transitions[2*n//3:]

def period(trans):
    if len(trans) < 3:
        return None
    steps = [t[0] for t in trans]
    ints = [steps[i+1]-steps[i] for i in range(len(steps)-1)]
    return statistics.mean(ints)

T0 = period(t_early)  # early learning period
T1 = period(t_mid)    # middle
T2 = period(t_late)   # late consolidation

print(f"\nPeriod-doubling measurement:")
print(f"  T_early  (learn):     {T0:.1f}" if T0 else "  T_early: N/A")
print(f"  T_mid    (transient):  {T1:.1f}" if T1 else "  T_mid: N/A")
print(f"  T_late   (consolidate):{T2:.1f}" if T2 else "  T_late: N/A")

# GI as period ratio
delta = 4.669
print(f"\nGI vs Feigenbaum delta={delta}:")
for label, Ta, Tb in [("mid/early", T0, T1), ("late/mid", T1, T2)]:
    if Ta and Tb and Ta > 0:
        gi = Tb/Ta
        err = (gi-delta)/delta*100
        print(f"  GI({label}) = {Tb:.1f}/{Ta:.1f} = {gi:.3f}  (err: {err:+.1f}%)")
