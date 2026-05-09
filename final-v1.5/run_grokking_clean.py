"""
Grokking clean run — Power et al. 框架
三条件：standard / +G / +Self-Refine
序列长度对齐（padding到6tokens），2层transformer
"""
import torch, torch.nn as nn, torch.nn.functional as F, random, json, os, time, math

DEVICE = "cuda"
PRIME = 97
PAD = PRIME      # = token  /  padding token
G_TOK = PRIME+1  # G sentence marker
SELF = PRIME+2   # self-refine marker
CHECK = PRIME+3  # check marker
N_VOCAB = PRIME + 4
SEQ_LEN = 6      # 统一长度
BS = 512
WD = 1.0         # weight decay
N_EPOCHS = 5000
TRAIN_RATIO = 0.30  # 30% → 有足够信号但不会太快grok
OUT = "g:/GEME/docs/robustness_results"
os.makedirs(OUT, exist_ok=True)

class Model(nn.Module):
    def __init__(self):
        super().__init__()
        self.tok = nn.Embedding(N_VOCAB, 128)
        self.pos = nn.Embedding(SEQ_LEN, 128)
        layer = nn.TransformerEncoderLayer(128, 4, 512, dropout=0, activation='relu', batch_first=True, norm_first=True)
        self.enc = nn.TransformerEncoder(layer, 2)
        self.out = nn.Linear(128, PRIME)
    def forward(self, x):
        h = self.tok(x) + self.pos(torch.arange(x.shape[1], device=x.device).unsqueeze(0))
        return self.out(self.enc(h)[:, -1])

def make_data(variant):
    rs = random.Random(42)
    inputs, labels = [], []
    for a in range(PRIME):
        for b in range(PRIME):
            c = (a + b) % PRIME
            if variant == 'standard':
                seq = [a, PAD, b, PAD, PAD, PAD]
            elif variant == 'G':
                seq = [G_TOK, G_TOK, a, PAD, b, PAD]
            elif variant == 'self_refine':
                seq = [a, PAD, b, PAD, SELF, CHECK]
            inputs.append(seq); labels.append(c)
    return torch.tensor(inputs), torch.tensor(labels)

def run(label, variant):
    data_in, data_lb = make_data(variant)
    N = len(data_in)
    perm = torch.randperm(N, generator=torch.Generator().manual_seed(42))
    split = int(N * TRAIN_RATIO)
    train_idx = perm[:split]
    test_idx = perm[split:]
    data_in, data_lb = data_in.to(DEVICE), data_lb.to(DEVICE)
    
    model = Model().to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=WD)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=N_EPOCHS)
    
    history = []; grok = None
    for ep in range(N_EPOCHS):
        model.train()
        perm_t = train_idx[torch.randperm(len(train_idx))]
        for i in range(0, len(perm_t), BS):
            idx = perm_t[i:i+BS]
            opt.zero_grad()
            loss = F.cross_entropy(model(data_in[idx]), data_lb[idx])
            loss.backward(); opt.step()
        sched.step()
        
        if ep % 50 == 0:
            model.eval()
            with torch.no_grad():
                ta = (model(data_in[train_idx]).argmax(-1) == data_lb[train_idx]).float().mean().item()
                tea = (model(data_in[test_idx]).argmax(-1) == data_lb[test_idx]).float().mean().item()
                history.append((ep, ta, tea))
                if tea > 0.9 and grok is None: grok = ep
        if ep % 2000 == 0 and ep > 0:
            print(f"  {label:12s} ep={ep:4d}  train={history[-1][1]:.3f}  test={history[-1][2]:.3f}")
    
    return {'grok': grok if grok else N_EPOCHS, 'end_test': history[-1][2], 'history': history,
            'min_test': min(h[2] for h in history)}

print("="*55)
print("Grokking Clean — Power框架，序列长度对齐")
print(f"数据={TRAIN_RATIO:.0%}  wd={WD}  seq_len={SEQ_LEN}")
print("="*55)

results = {}
for label, variant in [('Standard','standard'), ('+G','G'), ('+SelfRefine','self_refine')]:
    print(f"\n[{label}]")
    t0 = time.time()
    r = run(label, variant)
    dt = time.time() - t0
    results[label] = r
    # 找遗忘谷
    hist = r['history']
    valley = min(hist, key=lambda x: x[2])
    print(f"  → grok={r['grok']:4d}ep  遗忘谷=ep{valley[0]:4d} test={valley[2]:.3f}  end={r['end_test']:.3f}  ({dt:.0f}s)")

print(f"\n{'='*55}")
print(f"  对比表")
print(f"{'='*55}")
print(f"{'条件':>15}  {'grok步数':>8}  {'遗忘谷test':>10}  {'最终test':>8}")
print(f"{'-'*45}")
for label in ['Standard', '+G', '+SelfRefine']:
    r = results[label]
    h = r['history']
    valley = min(h, key=lambda x: x[2])
    print(f"{label:>15}  {r['grok']:>8d}  {valley[2]:>10.3f}(ep{valley[0]})  {r['end_test']:>8.3f}")

# 关键：G vs standard的遗忘谷对比
s_val = min(results['Standard']['history'], key=lambda x: x[2])[2]
g_val = min(results['+G']['history'], key=lambda x: x[2])[2]
print(f"\n  G - Standard 遗忘谷差 = {g_val - s_val:.3f}")

with open(os.path.join(OUT, 'grokking_clean.json'), 'w') as f:
    json.dump({k:{'grok':v['grok'],'end_test':v['end_test'],'min_test':v['min_test']} for k,v in results.items()}, f, indent=2)
print(f"\n保存至 {OUT}/grokking_clean.json")
