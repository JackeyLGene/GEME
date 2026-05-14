"""
Cat on the Mat — Input Granularity Test
Tests how GEME responds to the SAME content at different temporal granularities.

Three conditions:
  A. Full clause: "cat on the mat" as ONE input
  B. Word: "cat" "on" "the" "mat" as FOUR sequential inputs
  C. Character: "c" "a" "t" " " "o" "n" ... as 13 sequential inputs
"""
import sys, math, time, statistics
sys.path.insert(0, '../../final-v1.5')
from geme import GEME

def char_vec(ch):
    v=[0.0]*27; v[ord(ch)%27]=1.0; return v
def word_vec(w):
    v=[0.0]*27
    for ch in w: v[ord(ch)%27]+=1.0
    s=sum(v); return [x/s for x in v] if s>0 else v

def run_condition(condition, name):
    """Run GEME on one condition, return metrics."""
    g = GEME(memory_cap=16)
    g.memory.preserve_sig = True; g.memory.quantum_mode = True
    g.memory._merge_dists = [0.3]*30; g._induction_threshold = 3.0
    g.memory.cooccur_thresh = 0.08
    import random as _qr2; g.memory._qrand = _qr2.Random(42)
    
    # Repeat the phrase N times so conditions have comparable total exposure
    N = 20 if condition == 'char' else (100 if condition == 'clause' else 50)
    
    for cycle in range(N):
        if condition == 'clause':
            vec = word_vec("cat on the mat")
            g.process_vec(vec, 'cat_on_mat')
            g.memory.self_observe()
        elif condition == 'word':
            for w in ['cat','on','the','mat']:
                g.process_vec(word_vec(w), w)
                g.memory.self_observe()
        else:  # char
            for ch in "cat on the mat":
                g.process_vec(char_vec(ch), ch)
                g.memory.self_observe()
    
    m = g.metrics()
    return {
        'condition': name,
        'cycles': N,
        'inputs': m['input_count'],
        'frames': m['frame_count'],
        'L4': m['L4_frame_count'],
        'preds': m['pred_total'],
        'acc': m['pred_accuracy'],
        'MI': m.get('I(phi;X)', 0),
        'layers': dict(sorted(m.get('layers',{}).items())),
    }

if __name__ == '__main__':
    print('=' * 55)
    print('Cat on the Mat — Input Granularity Test')
    print('=' * 55)
    print(f'{"Condition":>12} {"Inputs":>6} {"Frames":>6} {"L4":>4} {"Preds":>6} {"Acc":>8} {"MI":>8} {"Layers":>20}')
    print('-' * 75)
    
    for cond, name in [('clause', 'Full clause'), ('word', 'Word-by-word'), ('char', 'Character')]:
        r = run_condition(cond, name)
        print(f'{r["condition"]:>12} {r["inputs"]:>6} {r["frames"]:>6} {r["L4"]:>4} '
              f'{r["preds"]:>6} {r["acc"]:>8.3f} {r["MI"]:>8.4f} {str(r["layers"]):>20s}')
    
    print('=' * 55)
    print('Expected: clause and word converge to similar L4; char may not.')
