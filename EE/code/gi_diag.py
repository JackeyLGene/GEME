import sys; sys.path.insert(0,'.')
from geruon import Geruon
from geme import eq, fn, const, structural_signature, symbol_vector
import random as _rnd

r = _rnd.Random(42)
g = Geruon(vec_dim=27, memory_cap=24, cooccur_window=80)
g.memory.quantum_mode = True
g.memory._qrand = _rnd.Random(99)
syms = ['0','1','s','x','y','z','swap']
for step in range(300):
    a,b = r.choice(syms), r.choice(syms)
    f = eq(fn('swap', const(a), const(b)), fn('swap', const(b), const(a)))
    g.process_vec(list(symbol_vector(f)), structural_signature(f))
    if step % 50 == 0:
        m = g.metrics()
        print(f"  step{step}: tau={g.tau:.4f} phase={g.phase.value} pred={m['pred_total']} acc={m['pred_accuracy']}")

print(f"final: tau={g.tau:.4f} phase={g.phase.value}")
print(f"phase_transitions: {len(g.memory._phase_transitions)}")
print(f"phase_steps: {g.memory._phase_steps}")
print(f"pred_total: {g.metrics()['pred_total']}")
