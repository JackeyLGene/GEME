"""Quick Geruon diagnostic — PA=Q+G minimal test."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ''))
from geruon import Geruon, Phase
from geme import eq, fn, const, structural_signature, symbol_vector, _VEC_DIM

VEC_DIM = 27

_AXIOMS = [
    eq(fn('succ', fn('succ', const('x'))), fn('=', const('x'), const('y'))),
    eq(fn('=', fn('succ', const('x')), const('0')), const('false')),
    eq(fn('+', const('x'), const('0')), const('x')),
    eq(fn('+', const('x'), fn('succ', const('y'))),
       fn('succ', fn('+', const('x'), const('y')))),
    eq(fn('x', const('x'), const('0')), const('0')),
    eq(fn('x', const('x'), fn('succ', const('y'))),
       fn('+', fn('x', const('x'), const('y')), const('x'))),
]

def run(label, extra_g=False, induction=False, cycles=100, seed=42):
    import random as _rnd
    r = _rnd.Random(seed)
    g = Geruon(vec_dim=VEC_DIM, memory_cap=16, cooccur_window=60)
    g.memory.quantum_mode = True
    g.memory._qrand = _rnd.Random(seed + 1)
    t0 = time.time()
    for cyc in range(cycles):
        for ax in _AXIOMS:
            sig = structural_signature(ax)
            vec = list(symbol_vector(ax))
            if extra_g:
                g_vec = [0.0] * VEC_DIM
                g_vec[2] = 1.0
                g_vec[7] = 1.0
                vec = [(vec[i] + g_vec[i]) / 2.0 for i in range(VEC_DIM)]
            g.process_vec(vec, sig)
        if induction:
            for n in range(3):
                base = eq(fn('swap', const(str(n)), const(str(n + 1))),
                          fn('swap', const(str(n + 1)), const(str(n))))
                g.process_sig(base)
    elapsed = time.time() - t0
    m = g.metrics()
    print(f"  {label}: {cycles}c in {elapsed:.1f}s | "
          f"pred={m['pred_total']} acc={m['pred_accuracy']:.3f} "
          f"L4={m['L4_frame_count']} I={m['I(phi;X)']:.4f} "
          f"tau={g.tau:.3f} {g.phase.value} doubt={m['doubt_mode']} "
          f"circ={m['circular_refs']} ps={m['pengshu_count']} "
          f"dep={m['precipitated']}/{m['precipitate_candidates']}")
    return m

if __name__ == '__main__':
    print("PA=Q+G Geruon (100 cycles)")
    t0 = time.time()
    q  = run('Q-only',        extra_g=False, induction=False)
    qg = run('Q + G',         extra_g=True,  induction=False)
    pa = run('Q + PA (ind)',  extra_g=False, induction=True)
    print(f"\nTotal: {time.time()-t0:.1f}s")
    print(f"Q vs Q+G: pred {q['pred_total']} vs {qg['pred_total']} (delta={qg['pred_total']-q['pred_total']})")
    match = qg['pred_total'] == pa['pred_total'] and abs(qg['pred_accuracy'] - pa['pred_accuracy']) < 0.01
    print(f"Q+G vs PA: {'MATCH' if match else 'DIFF'}")
