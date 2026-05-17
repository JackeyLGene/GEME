"""
Lock-to-lock period measurement — Feigenbaum cascade.

With forced release from LOCKED (30-step timeout), the system becomes
a relaxation oscillator. The intervals between successive LOCKED entries
form a sequence whose period ratios should converge to delta=4.669.
"""
import sys, os, math, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'BGM', 'code'))

from geruon import Geruon, Phase
from data.bwv847_fugue import SCORE, chord_hz_vec as hz

# Crab canon
subject = SCORE
fwd = []
for notes, beats, _ in subject:
    v = hz(notes); [fwd.append(list(v)) for _ in range(beats)]
bwd = list(reversed(fwd))
n = min(len(fwd), len(bwd))
base = [[(fwd[i][j]+bwd[i][j])/2.0 for j in range(len(fwd[i]))] for i in range(n)]

CYCLES = 50
stream = base * CYCLES
print(f"Crab Canon: {len(base)} steps x {CYCLES} cycles = {len(stream)} total")
print("Single Geruon, cap=24, forced release at 30 steps locked")
print("=" * 60)

g = Geruon(vec_dim=27, memory_cap=24, cooccur_window=100)
g.memory.quantum_mode = True

# Track lock entries and phase transitions
lock_entries = []
phase_traj = []
for step, vec in enumerate(stream):
    prev_ph = g.phase.value
    g.process_vec(list(vec), f'crab_{step % len(base)}')
    ph = g.phase.value
    phase_traj.append(ph)
    if ph == 'locked' and prev_ph != 'locked':
        lock_entries.append(step)

print(f"Lock entries: {len(lock_entries)}")
print(f"Final: tau={g.tau:.4f} phase={g.phase.value}")

if len(lock_entries) < 6:
    print("Not enough lock entries for period analysis")
    exit()

# Lock-to-lock periods
lock_periods = [lock_entries[i+1]-lock_entries[i] for i in range(len(lock_entries)-1)]
print(f"Lock periods (first 20): {[int(x) for x in lock_periods[:20]]}")

# Period-doubling: compare successive periods
# Feigenbaum: T_{n+1}/T_n → δ as n → ∞
period_ratios = []
for i in range(len(lock_periods)-1):
    if lock_periods[i] > 0:
        period_ratios.append(lock_periods[i+1]/lock_periods[i])

if period_ratios:
    # Split into early and late
    h = len(period_ratios)//2
    early_ratios = period_ratios[:h]
    late_ratios = period_ratios[h:]

    print(f"\nPeriod ratios ({len(period_ratios)} total):")
    print(f"  Early (n={len(early_ratios)}): mean={statistics.mean(early_ratios):.3f} "
          f"range=[{min(early_ratios):.3f},{max(early_ratios):.3f}]")
    if late_ratios:
        print(f"  Late  (n={len(late_ratios)}): mean={statistics.mean(late_ratios):.3f} "
              f"range=[{min(late_ratios):.3f},{max(late_ratios):.3f}]")

    # Overall average
    mean_ratio = statistics.mean(period_ratios)
    delta = 4.669
    print(f"\n  Overall mean ratio: {mean_ratio:.3f}")
    print(f"  Feigenbaum delta:   {delta}")
    print(f"  Error: {(mean_ratio-delta)/delta*100:+.1f}%")

    # Also: cumulative period ratios (T_n / T_1) should grow geometrically
    base_period = lock_periods[0]
    cum_ratios = [lp/base_period for lp in lock_periods]
    print(f"\nCumulative period growth (T_n / T_0):")
    for i in range(0, min(len(cum_ratios), 20), 4):
        print(f"  n={i}: {cum_ratios[i]:.2f}")
    if len(cum_ratios) > 20:
        print(f"  ...")
        print(f"  n={len(cum_ratios)-1}: {cum_ratios[-1]:.2f}")
