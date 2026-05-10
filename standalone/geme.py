# GEME engine - broker.
# Re-exports everything from the canonical final-v1.5 implementation.
import sys, os
_d = os.path.dirname(os.path.abspath(__file__))
_p = os.path.join(_d, '..', 'final-v1.5')
os.chdir(_p)  # so relative imports in geme.py work
exec(open(os.path.join(_p, 'geme.py'), encoding='utf-8').read())
