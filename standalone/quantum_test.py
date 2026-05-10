# Quantum merge test: v_in equally close to two prototypes
import sys, math
sys.path.insert(0,'g:/GEME/final-v1.5')
from geme import GEME, _VEC_DIM

# Two prototypes far apart (won't cross-merge)
v1=[0.0]*_VEC_DIM; v1[0]=1.0
v2=[0.0]*_VEC_DIM; v2[10]=1.0

# Input exactly between them (both distances equal)
v_in=[0.0]*_VEC_DIM; v_in[0]=0.5; v_in[10]=0.5

g=GEME(memory_cap=5); g.memory.quantum_mode=True; g.memory.preserve_sig=True
th=0.8
g.memory._merge_thresh_val=th; g.memory._merge_dists=[th]*50

# Check distances
da=math.sqrt(sum((v_in[i]-v1[i])**2 for i in range(_VEC_DIM)))
db=math.sqrt(sum((v_in[i]-v2[i])**2 for i in range(_VEC_DIM)))
print(f'da={da:.3f} db={db:.3f} thresh={th}')
print(f'Both within threshold? {da<=th and db<=th}')

g.process_vec(v1,'proto_a')
g.process_vec(v2,'proto_b')

for _ in range(1000):
    g.process_vec(v_in,'test')

counts={'a':0,'b':0}
for f in g.memory.frames:
    s=f.sig_full or f.sig
    if 'proto_a' in s: counts['a']=int(f.weight) - 1
    if 'proto_b' in s: counts['b']=int(f.weight) - 1

print(f'Merged into a: {counts["a"]}, b: {counts["b"]}')
print(f'Ratio a/b: {counts["a"]/max(counts["b"],1):.3f}')
print(f'Expected 50/50 (both distances equal)')
if 0.3 < counts['a']/max(counts['a']+counts['b'],1) < 0.7:
    print('YES: Quantum merge is probabilistic')
else:
    print('NO: Merge is still deterministic - quantum path not triggered')
