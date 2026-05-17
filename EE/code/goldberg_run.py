"""
Goldberg Variations → Geruon — direct structural vector encoding.

Each variation produces a unique vector sequence with rich labels
encoding: variation number, canon interval, voice count, and position
within the variation. Multiple passes with micro-timing variation.
"""
import sys, os, math, statistics, random as _rnd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase

VEC_DIM = 27
SEEDS = 10

def goldberg_stream(passes=5, noise=0.03):
    """Generate Goldberg variation stream with structural labels."""
    r = _rnd.Random(42)
    canon_interval = {3:1,6:2,9:3,12:4,15:5,18:6,21:7,24:8,27:9}

    stream = []
    for p in range(passes):
        # Opening Aria — 8 bars × 4 events
        for bar in range(8):
            for ev in range(4):
                v = [0.0]*VEC_DIM
                v[0] = 1.0  # is_aria
                v[1] = 0.0  # variation 0
                v[2] = bar/8.0
                v[3] = ev/4.0
                v[7] = 0.4; v[8] = 0.3; v[9] = 0.3
                v[20] = 1.0  # opening frame
                v = _noise(v, r, noise)
                stream.append((v, f'A_bar{bar}_ev{ev}'))

        # 30 variations
        for var in range(1, 31):
            ci = canon_interval.get(var, 0)
            n_bars = 16 if var <= 15 else 32
            n_events = 4 if var <= 10 else (6 if var <= 25 else 8)
            voices = 2 if var <= 10 else (3 if var <= 20 else 4)

            for bar in range(n_bars):
                for ev in range(n_events):
                    v = [0.0]*VEC_DIM
                    # Structural encoding
                    v[0] = var/30.0           # variation position
                    v[1] = 1.0 if ci > 0 else 0.0  # is_canon
                    v[2] = ci/9.0 if ci > 0 else 0.0  # canon interval
                    v[3] = bar/n_bars          # bar position
                    v[4] = ev/n_events         # event position
                    v[5] = voices/4.0          # voice density
                    v[6] = p/passes            # pass number

                    # Rhythmic density (increases with variation)
                    density = 0.2 + var*0.025 + ev/n_events*0.1
                    v[7] = min(1.0, density)
                    v[8] = 0.3 + ci*0.07       # canon tension
                    v[9] = 0.2

                    # Structural markers
                    v[10] = 1.0 if var%3==0 else 0.0   # every-3rd
                    v[11] = 1.0 if var%10==0 else 0.0  # every-10th
                    v[12] = 1.0 if var==30 else 0.0    # final variation
                    v[13] = 1.0 if ci==9 else 0.0      # final canon

                    # Position markers (which third of the work)
                    if var <= 10: v[14] = 1.0
                    elif var <= 20: v[15] = 1.0
                    else: v[16] = 1.0

                    # Harmonic tension (rises toward cadence points)
                    if ev >= n_events-2:
                        v[17] = 0.7  # approaching cadence
                    v[18] = 0.3 + bar/n_bars*0.4  # rising tension within variation

                    # Rhythmic articulation
                    v[19] = 0.5 + (ev%2)*0.3  # strong/weak beat
                    v[20] = 1.0 if bar==0 and ev==0 else 0.0  # variation start

                    v = _noise(v, r, noise)
                    label = f'v{var}_ci{ci}_b{bar}_e{ev}'
                    stream.append((v, label))

        # Closing Aria
        for bar in range(8):
            for ev in range(4):
                v = [0.0]*VEC_DIM
                v[0] = 1.0; v[1] = 0.0; v[2] = bar/8.0; v[3] = ev/4.0
                v[7] = 0.4; v[8] = 0.3; v[9] = 0.3
                v[20] = -1.0  # closing frame
                v = _noise(v, r, noise)
                stream.append((v, f'AriaClose_bar{bar}_ev{ev}'))

    return stream


def _noise(v, r, scale):
    return tuple(max(0.0, min(1.0, x + r.gauss(0, scale))) for x in v)


# ── Run ──
if __name__ == '__main__':
    passes = 8
    stream = goldberg_stream(passes=passes, noise=0.02)
    total = len(stream)
    unique_labels = len(set(l for _,l in stream))
    print(f"Goldberg Stream: {total} steps, {unique_labels} unique labels ({passes} passes)")
    print("=" * 55)

    all_gis = []
    for seed in range(SEEDS):
        g = Geruon(vec_dim=VEC_DIM, memory_cap=24, cooccur_window=100)
        g.memory.quantum_mode = True
        g.memory._qrand = _rnd.Random(seed + 1000)

        phase_traj = []
        for vec, label in stream:
            g.process_vec(list(vec), label)
            phase_traj.append(g.phase.value)

        trans = []
        for i in range(1, len(phase_traj)):
            if phase_traj[i] != phase_traj[i-1]:
                trans.append((i, phase_traj[i-1], phase_traj[i]))

        n = len(trans)
        if n < 6:
            print(f"  s{seed}: {n} trans — skip")
            continue

        t_steps = [t[0] for t in trans]
        ints = [t_steps[i+1]-t_steps[i] for i in range(len(t_steps)-1)]
        m = len(ints)
        T = [statistics.mean(ints[:m//3]) if m//3>0 else 0,
             statistics.mean(ints[m//3:2*m//3]) if m//3>0 else 0,
             statistics.mean(ints[2*m//3:]) if m//3>0 else 0]
        gi1 = T[1]/T[0] if T[0]>0 else 0
        gi2 = T[2]/T[1] if T[1]>0 else 0

        ph_c = {}
        for ph in phase_traj: ph_c[ph] = ph_c.get(ph,0)+1
        dom = max(ph_c, key=ph_c.get)

        print(f"  s{seed}: {n} trans tau={g.tau:.3f} {dom} "
              f"T={[round(t,0) for t in T]} GI=[{gi1:.2f},{gi2:.2f}] "
              f"phases={dict(sorted(ph_c.items()))}")
        all_gis.append((gi1, gi2))

    if all_gis:
        gi1s = [g[0] for g in all_gis if g[0] > 0]
        gi2s = [g[1] for g in all_gis if g[1] > 0]
        delta = 4.669
        print(f"\n{'='*55}")
        if gi1s:
            print(f"GI_1: mean={statistics.mean(gi1s):.3f} "
                  f"median={statistics.median(gi1s):.3f} "
                  f"range=[{min(gi1s):.3f},{max(gi1s):.3f}] "
                  f"err={(statistics.mean(gi1s)-delta)/delta*100:+.1f}%")
        if gi2s:
            print(f"GI_2: mean={statistics.mean(gi2s):.3f} "
                  f"median={statistics.median(gi2s):.3f} "
                  f"range=[{min(gi2s):.3f},{max(gi2s):.3f}] "
                  f"err={(statistics.mean(gi2s)-delta)/delta*100:+.1f}%")
        print(f"Feigenbaum delta = {delta}")
