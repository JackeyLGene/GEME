"""Debug precipitation activation tracking."""
import sys; sys.path.insert(0, '.')
from geruon import Geruon
from geme import eq, fn, const, structural_signature
import random as _rnd

r = _rnd.Random(42)
g = Geruon(vec_dim=16, memory_cap=16, cooccur_window=60)
g.memory.quantum_mode = True
g.memory._qrand = _rnd.Random(99)

symbols = ['0','1','s','+','x','y','z','swap']
for step in range(200):
    a = r.choice(symbols)
    b = r.choice(symbols)
    c = r.choice(symbols)
    if step % 3 == 0:
        f = eq(fn(a, const(b)), const(c))
    else:
        f = eq(fn('swap', const(a), const(b)), fn('swap', const(b), const(a)))
    g.process_sig(f, structural_signature(f))

print(f"Frames: {len(g.memory.frames)}")
print(f"sig_to_gid size: {len(g.memory._sig_to_gid)}")
print(f"sig_index size: {len(g.memory._sig_index)}")
print(f"pred_path_gids (last): {g.memory._prediction_path_gids}")
print(f"pred_total: {g.metrics()['pred_total']}")

# Check key sigs
for f in g.memory.frames[:5]:
    sig = f.sig
    gid = g.memory._sig_to_gid.get(sig, 'NOT FOUND')
    print(f"  sig={sig[:40]}  gid={gid}  layer={f.layer}")

# Check window entries
print(f"Window size: {len(g.memory._window)}")
if g.memory._window:
    w_sig = g.memory._window[-1][0]
    w_gid = g.memory._sig_to_gid.get(w_sig, 'NOT FOUND')
    print(f"  Last window sig: {w_sig[:40]}  gid={w_gid}")
