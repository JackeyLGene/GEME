"""
PA = Q + G  — Geruon replication of GEME Paper I §3.3.

Original finding: Q+G and PA produce identical prediction behavior,
while Q alone is weaker. This tests whether Geruon (with endogenous τ
and StructuralSig) preserves the functional equivalence.

Quick run — single seed, 100 cycles per condition.
"""
import sys, os
# Script is in code/ — ensure code/ is on path for geme import
_here = os.path.dirname(os.path.abspath(__file__))
if _here not in sys.path:
    sys.path.insert(0, _here)
from geruon import Geruon, Phase
from geme import eq, fn, const, structural_signature, symbol_vector, _VEC_DIM
import random as _rnd

VEC_DIM = _VEC_DIM  # 27 — match GEME paper for comparability


def vec_for_axiom_sig(sig):
    """Sparse vector from axiom signature string."""
    v = [0.0] * VEC_DIM
    h = hash(sig) & 0x7FFFFFFF
    for _ in range(2):
        v[h % VEC_DIM] = 1.0
        h = h // VEC_DIM
    return v


# ── Robinson Arithmetic axioms (Q1–Q7) ──
# Q1: ∀x ∀y (succ(x) = succ(y) → x = y)
# Q2: ∀x ¬(succ(x) = 0)
# Q3: ∀x (x + 0 = x)
# Q4: ∀x ∀y (x + succ(y) = succ(x + y))
# Q5: ∀x (x × 0 = 0)
# Q6: ∀x ∀y (x × succ(y) = (x × y) + x)
# Q7: ∀x ¬(x = 0) → ∃y (x = succ(y))

_AXIOMS = [
    eq(fn("succ", fn("succ", const("x"))), fn("=", const("x"), const("y"))),
    eq(fn("=", fn("succ", const("x")), const("0")), const("false")),
    eq(fn("+", const("x"), const("0")), const("x")),
    eq(fn("+", const("x"), fn("succ", const("y"))),
       fn("succ", fn("+", const("x"), const("y")))),
    eq(fn("×", const("x"), const("0")), const("0")),
    eq(fn("×", const("x"), fn("succ", const("y"))),
       fn("+", fn("×", const("x"), const("y")), const("x"))),
]


def feed_cycle(geruon, axioms, extra_g=False, induction=False):
    """Feed one cycle of axiom sequence. Returns step count."""
    for ax in axioms:
        sig = structural_signature(ax)
        vec = list(symbol_vector(ax))
        if extra_g:
            g_vec = [0.0] * VEC_DIM
            g_vec[2] = 1.0   # succ
            g_vec[7] = 1.0   # exists
            vec = [(vec[i] + g_vec[i]) / 2.0 for i in range(VEC_DIM)]
        geruon.process_vec(vec, sig)

    if induction:
        for n in range(3):
            base = eq(fn("swap", const(str(n)), const(str(n + 1))),
                      fn("swap", const(str(n + 1)), const(str(n))))
            geruon.process_sig(base)


def run_condition(label, extra_g=False, induction=False, seed=42, cycles=100):
    r = _rnd.Random(seed)
    g = Geruon(vec_dim=VEC_DIM, memory_cap=16, cooccur_window=60)
    g.memory.quantum_mode = True
    g.memory._qrand = _rnd.Random(seed + 1)

    for cyc in range(cycles):
        feed_cycle(g, _AXIOMS, extra_g=extra_g, induction=induction)

    m = g.metrics()
    return {
        'label': label,
        'pred_total': m['pred_total'],
        'pred_accuracy': m['pred_accuracy'],
        'L4_frame_count': m['L4_frame_count'],
        'I(phi;X)': m['I(phi;X)'],
        'tau': round(g.tau, 4),
        'phase': g.phase.value,
        'doubt_mode': m['doubt_mode'],
        'circular_refs': m['circular_refs'],
        'pengshu_count': m['pengshu_count'],
        'phase_steps': m['phase_steps'],
        'frames': m['frame_count'],
    }


if __name__ == '__main__':
    print("=" * 65)
    print("PA = Q + G  — Geruon replication")
    print("=" * 65)

    results = {}
    for cond in [
        ('Q-only',        False, False),
        ('Q + G',         True,  False),
        ('Q + PA (ind)',  False, True),
    ]:
        label, extra_g, induction = cond
        print(f"\n{label}...", end=' ', flush=True)
        r = run_condition(label, extra_g=extra_g, induction=induction, cycles=30)
        results[label] = r
        print(f"pred={r['pred_total']} acc={r['pred_accuracy']:.3f} "
              f"L4={r['L4_frame_count']} I={r['I(phi;X)']:.4f} "
              f"τ={r['tau']:.3f} {r['phase']} doubt={r['doubt_mode']}")

    print("\n" + "-" * 65)
    print(f"{'Condition':<16s} {'Pred':>6s} {'Acc':>7s} {'L4':>4s} {'I(Φ;X)':>8s} {'τ':>6s} {'Phase':>10s} {'Doubt':>6s}")
    print("-" * 65)
    for label in ['Q-only', 'Q + G', 'Q + PA (ind)']:
        r = results[label]
        print(f"{label:<16s} {r['pred_total']:>6d} {r['pred_accuracy']:>7.3f} "
              f"{r['L4_frame_count']:>4d} {r['I(phi;X)']:>8.4f} "
              f"{r['tau']:>6.3f} {r['phase']:>10s} {str(r['doubt_mode']):>6s}")

    # Key comparison
    qg = results['Q + G']
    pa = results['Q + PA (ind)']
    print(f"\n  Q+G vs PA — pred: {qg['pred_total']} vs {pa['pred_total']} "
          f"({'MATCH' if qg['pred_total'] == pa['pred_total'] else 'DIFF'})")
    print(f"  Q+G vs PA — acc:  {qg['pred_accuracy']:.3f} vs {pa['pred_accuracy']:.3f} "
          f"({'MATCH' if abs(qg['pred_accuracy'] - pa['pred_accuracy']) < 0.01 else 'DIFF'})")
    print(f"  Q+G vs PA — L4:   {qg['L4_frame_count']} vs {pa['L4_frame_count']} "
          f"({'MATCH' if qg['L4_frame_count'] == pa['L4_frame_count'] else 'DIFF'})")

    print(f"\n  Q-only pred: {results['Q-only']['pred_total']} "
          f"(weaker than Q+G by {qg['pred_total'] - results['Q-only']['pred_total']})")
