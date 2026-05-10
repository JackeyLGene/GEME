# GEME API Quick Reference

## Current API (low-level — requires internal knowledge)

```python
from geme import GEME, _VEC_DIM
import math

g = GEME(memory_cap=32)
g.memory.preserve_sig = True
g.memory.quantum_mode = True
# ... many more internal configs ...

# Input: raw vectors
for i in range(500):
    v = [0.0]*27
    v[0] = math.cos(i*0.01)
    v[1] = math.sin(i*0.01)
    g.process_vec(v, 'input')

# Output: raw metrics
m = g.metrics()
print(m['L4_frame_count'], m['pred_accuracy'])
```

## Desired API (high-level)

```python
from geme import GEME
g = GEME()

# Simple text input
g.input("cat on mat")          # auto-encode text
g.input([0.1, 0.5, ...])       # vecs still work
g.input_file("data.txt")       # bulk from file

# Simple output
g.predict()                    # "下一个是: mat"
g.predict_next()               # same
g.anomaly_score()              # 0.0 (normal) 或 0.7 (异常)
g.state()                      # 可读的摘要
```

You can help implement this. See geme.py → need:
1. `GEME.text_to_vec()` — auto-encode any string to 27-dim
2. `GEME.input(text_or_vec)` — unified input
3. `GEME.state_summary()` — human-readable output
4. `GEME.anomaly_score()` — single number: is input surprising?
5. `GEME.save/load()` — persist trained models
