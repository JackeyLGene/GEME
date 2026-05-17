"""
Crab Canon → single Geruon → GI period-doubling.

BGM crab canon: fugue subject forward + backward, blended.
Simple test: feed the stream, measure phase transition periods,
compute period ratios. If Feigenbaum holds, ratio → delta=4.669.
"""
import sys, os, math, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'BGM', 'code'))

from geruon import Geruon, Phase
from data.bwv847_fugue import SCORE, chord_hz_vec as hz

# Build crab canon: full subject forward + reversed, blended
subject = SCORE
fwd = []
for notes, beats, _ in subject:
    v = hz(notes)
    for _ in range(beats):
        fwd.append(list(v))

bwd = list(reversed(fwd))
n = min(len(fwd), len(bwd))
blended = []
for i in range(n):
    b = [(fwd[i][j] + bwd[i][j])/2.0 for j in range(len(fwd[i]))]
    blended.append(b)

CYCLES = 15
stream = blended * CYCLES
print(f"Crab Canon: {len(blended)} steps/cycle x {CYCLES} cycles = {len(stream)} total")
print(f"Single Geruon, cap=24")
print("=" * 55)

g = Geruon(vec_dim=27, memory_cap=24, cooccur_window=100)
g.memory.quantum_mode = True

tau_traj = []
phase_traj = []
induction_points = []
last_ind = 0

for step, vec in enumerate(stream):
    g.process_vec(vec, f'crab_{step % len(blended)}')
    tau_traj.append(g.tau)
    phase_traj.append(g.phase.value)
    if g._last_induction != last_ind:
        last_ind = g._last_induction
        induction_points.append(step)

print(f"Induction cycles: {len(induction_points)}")
print(f"Final: tau={g.tau:.4f} phase={g.phase.value}")

# τ oscillation analysis: find peaks and troughs
# A τ "breath" = one cycle of τ rising then falling
tau_peaks = []
tau_troughs = []
for i in range(2, len(tau_traj)-2):
    # Local maximum
    if (tau_traj[i] > tau_traj[i-1] and tau_traj[i] > tau_traj[i-2] and
        tau_traj[i] >= tau_traj[i+1] and tau_traj[i] >= tau_traj[i+2]):
        tau_peaks.append(i)
    # Local minimum
    if (tau_traj[i] < tau_traj[i-1] and tau_traj[i] < tau_traj[i-2] and
        tau_traj[i] <= tau_traj[i+1] and tau_traj[i] <= tau_traj[i+2]):
        tau_troughs.append(i)

print(f"τ peaks: {len(tau_peaks)}  troughs: {len(tau_troughs)}")

# Measure peak-to-peak intervals (τ oscillation periods)
if len(tau_peaks) >= 4:
    peak_intervals = [tau_peaks[i+1]-tau_peaks[i] for i in range(len(tau_peaks)-1)]
    m = len(peak_intervals)
    Tp = [statistics.mean(peak_intervals[:m//3]) if m//3>0 else 0,
          statistics.mean(peak_intervals[m//3:2*m//3]) if m//3>0 else 0,
          statistics.mean(peak_intervals[2*m//3:]) if m//3>0 else 0]

    print(f"\nτ oscillation periods (peak-to-peak):")
    for i, (label, t) in enumerate([("early",Tp[0]),("mid",Tp[1]),("late",Tp[2])]):
        print(f"  T_{label}: {t:.1f}")

    delta = 4.669
    for i in range(len(Tp)-1):
        if Tp[i] > 0 and Tp[i+1] > 0:
            gi = Tp[i+1]/Tp[i]
            err = (gi-delta)/delta*100
            print(f"  GI_{i+1} = {gi:.3f}  (err: {err:+.1f}%)")

# Also: induction period ratio
if len(induction_points) >= 4:
    ind_int = [induction_points[i+1]-induction_points[i] for i in range(len(induction_points)-1)]
    m = len(ind_int)
    Ti = [statistics.mean(ind_int[:m//3]) if m//3>0 else 0,
          statistics.mean(ind_int[m//3:2*m//3]) if m//3>0 else 0,
          statistics.mean(ind_int[2*m//3:]) if m//3>0 else 0]
    print(f"\nInduction periods:")
    for i, (label, t) in enumerate([("early",Ti[0]),("mid",Ti[1]),("late",Ti[2])]):
        print(f"  T_{label}: {t:.1f}")
    for i in range(len(Ti)-1):
        if Ti[i] > 0 and Ti[i+1] > 0:
            gi = Ti[i+1]/Ti[i]
            err = (gi-4.669)/4.669*100
            print(f"  GI_ind_{i+1} = {gi:.3f}  (err: {err:+.1f}%)")
