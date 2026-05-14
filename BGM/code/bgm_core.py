"""
BGM Core: Multi-GEME audio perception experiment.

3 GEME units (A, B, C) hear same Hz-encoded Bach prelude.
1 G0 GEME receives their L6 outputs, feeds environment vector back.
No modifications to GEME core. L6 = only output. Environment = only feedback.
"""
import sys, math, time, statistics
sys.path.insert(0, '.')
from geme import GEME
import random as _qr2

# --- Frequency encoding ---
FREQ_MIN, FREQ_MAX, BINS = 65, 1050, 27

def freq_to_vec(freq):
    idx = int((freq - FREQ_MIN) / (FREQ_MAX - FREQ_MIN) * (BINS - 1))
    return [1.0 if i == max(0, min(BINS-1, idx)) else 0.0 for i in range(BINS)]

NOTE_FREQS = {
    'C2':65.41,'C#2':69.30,'D2':73.42,'D#2':77.78,'E2':82.41,'F2':87.31,
    'F#2':92.50,'G2':98.00,'G#2':103.83,'A2':110.00,'A#2':116.54,'B2':123.47,
    'C3':130.81,'C#3':138.59,'D3':146.83,'D#3':155.56,'E3':164.81,'F3':174.61,
    'F#3':185.00,'G3':196.00,'G#3':207.65,'A3':220.00,'A#3':233.08,'B3':246.94,
    'C4':261.63,'C#4':277.18,'D4':293.66,'D#4':311.13,'E4':329.63,'F4':349.23,
    'F#4':369.99,'G4':392.00,'G#4':415.30,'A4':440.00,'A#4':466.16,'B4':493.88,
    'C5':523.25,'C#5':554.37,'D5':587.33,'D#5':622.25,'E5':659.25,'F5':698.46,
    'F#5':739.99,'G5':783.99,'G#5':830.61,'A5':880.00,'A#5':932.33,'B5':987.77,
}

def chord_vec(notes):
    """Encode simultaneous notes as summed Hz-bin vector."""
    v = [0.0]*BINS
    for n in notes:
        f = NOTE_FREQS.get(n, 440)
        idx = max(0, min(BINS-1, int((f-FREQ_MIN)/(FREQ_MAX-FREQ_MIN)*(BINS-1))))
        v[idx] += 1.0
    s = sum(v); return [x/s for x in v] if s > 0 else v

def l6_to_vec(l6_val):
    """Encode L6 scalar (0-1) as 27-dim vector."""
    v = [0.0]*BINS
    idx = int(l6_val * (BINS-1))
    v[max(0, min(BINS-1, idx))] = 1.0
    return v

# --- BWV 846 Full Prelude (35 measures, ~140 time steps) ---
BWV846 = [
    (['C4','E4','G4'],4),(['C4','E4','G4'],4),
    (['C4','E4','A4'],4),(['C4','E4','A4'],4),
    (['C4','F4','A4'],4),(['C4','F4','A4'],4),
    (['B3','D4','F4','G4'],4),(['B3','D4','F4','G4'],4),
    (['C4','E4','G4','C5'],4),(['C4','E4','G4','C5'],4),
    (['C4','E4','A4','C5'],4),(['C4','E4','A4','C5'],4),
    (['C4','F4','A4','C5'],4),(['C4','F4','A4','C5'],4),
    (['B3','D4','F4','G4','B4'],4),(['B3','D4','F4','G4','B4'],4),
    (['C4','E4','G4','C5'],4),(['C4','E4','G4','C5'],4),
    (['D4','F#4','A4','C5'],4),(['D4','F#4','A4','C5'],4),
    (['G3','B3','D4','G4'],4),(['G3','B3','D4','G4'],4),
    (['C4','E4','G4','C5'],4),(['C4','E4','G4','C5'],4),
    (['F3','A3','C4','F4'],4),(['F3','A3','C4','F4'],4),
    (['B3','D4','F4','G4'],4),(['B3','D4','F4','G4'],4),
    (['C4','E4','G4','C5'],4),(['C4','E4','G4','C5'],4),
    (['A3','C4','E4','A4'],4),(['A3','C4','E4','A4'],4),
    (['D4','F#4','A4','C5'],4),(['D4','F#4','A4','C5'],4),
    (['G3','B3','D4','G4'],4),(['G3','B3','D4','G4'],4),
    (['C4','E4','G4','C5'],4),(['C4','E4','G4','C5'],4),
    (['F3','A3','C4','F4'],4),(['F3','A3','C4','F4'],4),
    (['F#3','A3','C4','D4','F4'],4),(['F#3','A3','C4','D4','F4'],4),
    (['G3','B3','D4','G4'],4),(['G3','B3','D4','G4'],4),
    (['C4','E4','G4','C5'],4),(['C4','E4','G4','C5'],4),
    (['C4','E4','G4'],6),
]

# --- GEMENet: manages multiple GEMEs + G0 ---
class GEMENet:
    def __init__(self, n_units=3, mem_cap=16, seed_base=0):
        self.units = []
        for i in range(n_units):
            g = GEME(memory_cap=mem_cap)
            g.memory.preserve_sig=True; g.memory.quantum_mode=True
            g.memory._merge_dists=[0.3]*30; g._induction_threshold=3.0
            g.memory.cooccur_thresh=0.08
            g.memory._qrand=_qr2.Random(seed_base + i * 777)
            self.units.append(g)
        # G0: standard GEME receiving L6 from all units
        self.g0 = GEME(memory_cap=mem_cap)
        self.g0.memory.preserve_sig=True; self.g0.memory.quantum_mode=True
        self.g0.memory._merge_dists=[0.3]*30; self.g0._induction_threshold=3.0
        self.g0.memory.cooccur_thresh=0.08
        self.g0.memory._qrand=_qr2.Random(seed_base + 9999)
        self.step = 0
        self.g0_feedback = None  # G0's self-observation vector
    
    def step_all(self, ext_vec):
        """One time step: all units process ext_vec + G0 feedback, then G0 processes their L6."""
        # Phase 1: Each unit processes external input + G0 feedback
        for unit in self.units:
            if self.g0_feedback:
                # Blend: 70% external, 30% G0 feedback
                blended = [0.7*ext_vec[i] + 0.3*self.g0_feedback[i] for i in range(len(ext_vec))]
                unit.process_vec(blended, 'bwv846')
            else:
                unit.process_vec(ext_vec, 'bwv846')
            unit.memory.self_observe()
        
        # Phase 2: Collect L6 from all units
        l6_vals = [unit.anomaly_score() for unit in self.units]
        
        # Phase 3: G0 processes L6 values as input
        g0_vec = l6_to_vec(sum(l6_vals)/len(l6_vals))
        self.g0.process_vec(g0_vec, 'g0_in')
        self.g0.memory.self_observe()
        
        # Phase 4: G0's self-observation becomes feedback vector
        self.g0_feedback = self.g0.metrics().get('g0_state', None)
        if not self.g0_feedback:
            # Compute G0's self-observation as weighted centroid
            frames = self.g0.memory.frames
            if frames:
                total_w = sum(f.weight for f in frames)
                if total_w > 0:
                    dim = len(frames[0].vec)
                    self.g0_feedback = tuple(
                        sum(f.vec[i] * f.weight for f in frames) / total_w
                        for i in range(dim))
                else:
                    self.g0_feedback = tuple(0.0 for _ in range(27))
            else:
                self.g0_feedback = tuple(0.0 for _ in range(27))
        
        self.step += 1
    
    def metrics(self):
        """Return combined metrics for all units + G0."""
        result = {}
        for i, unit in enumerate(self.units):
            m = unit.metrics()
            result[f'unit_{i}'] = {
                'acc': m.get('pred_accuracy', 0),
                'L4': m.get('L4_frame_count', 0),
                'MI': m.get('I(phi;X)', 0),
                'doubt': m.get('doubt_mode', False),
                'l6': unit.anomaly_score(),
            }
        m_g0 = self.g0.metrics()
        result['g0'] = {
            'frames': m_g0.get('frame_count', 0),
            'L4': m_g0.get('L4_frame_count', 0),
            'MI': m_g0.get('I(phi;X)', 0),
        }
        return result

if __name__ == '__main__':
    t0 = time.time()
    
    # Create network: 3 units + G0
    net = GEMENet(n_units=3, mem_cap=16)
    
    # Run full prelude 4 times
    for _ in range(4):
        for notes, beats in BWV846:
            for _ in range(beats):
                net.step_all(chord_vec(notes))
    
    m = net.metrics()
    
    print('='*55)
    print('BGM Core — 3 GEMEs + G0 on BWV 846')
    print('='*55)
    for k, v in m.items():
        if k.startswith('unit_'):
            idx = k.split('_')[1]
            print(f'  GEME_{idx}: Acc={v["acc"]:.3f}, L4={v["L4"]}, '
                  f'MI={v["MI"]:.4f}, L6={v["l6"]:.2f}')
        elif k == 'g0':
            print(f'  G0:     Frames={v["frames"]}, L4={v["L4"]}, MI={v["MI"]:.4f}')
    
    print(f'\nTime: {(time.time()-t0):.1f}s')
