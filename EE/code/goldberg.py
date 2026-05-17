"""
Goldberg Variations (BWV 988) → Geruon GI_n → delta experiment.

Structure: Aria → 30 variations → Aria da capo.
Every 3rd variation is a canon (interval 1-9).
Each variation = 3 micro-events for rich co-occurrence.
50 passes = 4800 steps for Geruon prediction learning.
"""
import sys, os, math, statistics, random as _rnd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geruon import Geruon, Phase

VEC_DIM = 27
CANON_INTERVALS = {3:1,6:2,9:3,12:4,15:5,18:6,21:7,24:8,27:9}

def make_stream(passes=50):
    r = _rnd.Random(42)
    stream = []
    for p in range(passes):
        # Opening Aria (3 micro-events)
        for m in range(3):
            stream.append(_aria('open', p, m, r))
        # 30 variations (3 micro-events each)
        for v in range(1, 31):
            ci = CANON_INTERVALS.get(v, 0)
            base = _var(v, ci, p)
            for m in range(3):
                noisy = [max(0.0, min(1.0, x + r.gauss(0, 0.02))) for x in base]
                stream.append(tuple(noisy))
        # Closing Aria (3 micro-events)
        for m in range(3):
            stream.append(_aria('close', p, m, r))
    return stream

def _aria(which, pass_num, micro, r):
    v = [0.0]*VEC_DIM
    v[0] = 1.0                           # is_aria
    v[1] = 0.5 if which == 'open' else 0.0
    v[2] = 0.0 if which == 'open' else 0.5
    v[3] = 1.0                           # is_frame
    v[4] = 1.0 if which == 'open' else -1.0
    v[5] = pass_num/50.0
    v[7] = 0.5; v[8] = 0.3; v[9] = 0.2  # voice density
    v[26] = micro/3.0                    # micro-position
    return tuple(v)

def _var(var_num, canon_interval, pass_num):
    v = [0.0]*VEC_DIM
    v[0] = var_num/30.0                 # position
    if canon_interval > 0:
        v[3] = 1.0                       # is_canon
        v[4] = canon_interval/9.0        # interval
    v[5] = pass_num/50.0
    v[7] = 0.3 + canon_interval*0.07 if canon_interval>0 else 0.4
    v[8] = 0.2; v[9] = 0.1
    v[10] = (var_num&1)*1.0             # binary position bits
    v[11] = ((var_num>>1)&1)*1.0
    v[12] = ((var_num>>2)&1)*1.0
    if canon_interval > 0:
        v[13] = canon_interval/9.0
        v[14] = 1.0 if canon_interval > 4 else 0.0
        v[15] = 1.0 if canon_interval == 9 else 0.0
    v[16] = 1.0 if var_num%3==0 else 0.0  # every-3rd
    v[17] = 1.0 if var_num==30 else 0.0   # final
    if var_num<=10: v[18]=1.0
    elif var_num<=20: v[19]=1.0
    else: v[20]=1.0
    v[21] = 0.2 + var_num*0.025
    v[22] = 0.5
    if canon_interval > 0:
        v[24] = canon_interval/9.0
        v[25] = 1.0
    return tuple(v)


if __name__ == '__main__':
    print("=" * 55)
    print("Goldberg Variations → Geruon GI_n → delta")
    print("=" * 55)

    stream = make_stream(passes=50)
    print(f"Stream: {len(stream)} steps")

    g0 = Geruon(vec_dim=VEC_DIM, memory_cap=24, cooccur_window=80)
    g0.memory.quantum_mode = True
    g1 = Geruon(vec_dim=VEC_DIM, memory_cap=20, cooccur_window=80)
    g1.memory.quantum_mode = True
    g2 = Geruon(vec_dim=VEC_DIM, memory_cap=16, cooccur_window=80)
    g2.memory.quantum_mode = True

    layers = [g0, g1, g2]
    phase_logs = [[], [], []]
    transitions = [[], [], []]

    for step, vec in enumerate(stream):
        v = vec
        for i, g in enumerate(layers):
            if i == 0:
                sig = f'v{step%96}'
            else:
                sig = f'L{i}_ph_{layers[i-1].phase.value}'
            g.process_vec(list(v), sig)
            ph = g.phase.value
            phase_logs[i].append(ph)
            if len(phase_logs[i]) >= 2 and phase_logs[i][-2] != ph:
                transitions[i].append((step, phase_logs[i][-2], ph))
            # Pass full frame centroid (rich state) to next layer, not sparse phase
            frames = g.memory.frames
            if frames:
                tw = sum(f.weight for f in frames)
                v = tuple(sum(f.vec[j]*f.weight for f in frames)/max(tw,0.001)
                          for j in range(VEC_DIM))
            else:
                v = vec

    # Report
    Ts = []
    for i, g in enumerate(layers):
        n = len(transitions[i])
        ph_c = {}
        for ph in phase_logs[i]:
            ph_c[ph] = ph_c.get(ph,0)+1
        if n >= 5:
            tsteps = [t[0] for t in transitions[i]]
            ints = [tsteps[j+1]-tsteps[j] for j in range(len(tsteps)-1)]
            T = statistics.mean(ints)
        else:
            T = None
        Ts.append(T)
        ts = f"T={T:.1f}" if T else "T=N/A"
        print(f"L{i}: tau={g.tau:.4f} {g.phase.value} trans={n} {ts}  phases={dict(sorted(ph_c.items()))}")

    print("\n" + "-" * 40)
    print("GI vs Feigenbaum delta=4.669")
    for i in range(2):
        if Ts[i] and Ts[i+1] and Ts[i] > 0:
            gi = Ts[i+1]/Ts[i]
            err = (gi-4.669)/4.669*100
            arrow = "→δ" if gi > 4.0 else "?"
            print(f"  GI_{i+1} = {gi:.3f}  (delta err: {err:+.1f}%)  {arrow}")
        else:
            print(f"  GI_{i+1} = N/A")
