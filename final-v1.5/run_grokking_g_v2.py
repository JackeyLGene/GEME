"""
Grokking + G句子 vs Self-Refine + 低数据区
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import math, random, json, os, time

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
PRIME = 97
N_VOCAB = PRIME + 4  # digits + '+ = [SELF] [CHECK]
N_DIGITS = 3
BS = 512
N_EPOCHS = 8000
TRAIN_RATIO = 0.20  # 20% data → grokking区
OUT = "g:/GEME/docs/robustness_results"
os.makedirs(OUT, exist_ok=True)

class MiniTransformer(nn.Module):
    def __init__(self, d_model=128, n_heads=4, d_ff=512, n_layers=3, max_len=15):
        super().__init__()
        self.embed = nn.Embedding(N_VOCAB, d_model)
        self.pos = nn.Embedding(max_len, d_model)
        layer = nn.TransformerEncoderLayer(d_model, n_heads, d_ff, dropout=0,
                                           activation='relu', batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, n_layers)
        self.out = nn.Linear(d_model, PRIME)
    def forward(self, x):
        B, S = x.shape
        h = self.embed(x) + self.pos(torch.arange(S, device=x.device).unsqueeze(0))
        return self.out(self.encoder(h)[:, -1])

def make_data(variant):
    rs = random.Random(42)
    inputs, labels = [], []
    G_TOK = PRIME + 1
    SELF_TOK = PRIME + 2
    CHECK_TOK = PRIME + 3
    EQ = PRIME  # '=' token
    for a in range(PRIME):
        for b in range(PRIME):
            c = (a + b) % PRIME
            if variant == 'standard':
                seq = [a, EQ, b, EQ]
            elif variant == 'G':
                seq = [G_TOK, G_TOK, a, EQ, b, EQ]
            elif variant == 'self_refine':
                seq = [a, EQ, b, EQ, SELF_TOK, CHECK_TOK]
            inputs.append(seq); labels.append(c)
    return torch.tensor(inputs), torch.tensor(labels)

def run(label, variant):
    data_in, data_lb = make_data(variant)
    N = len(data_in)
    perm = torch.randperm(N, generator=torch.Generator().manual_seed(42))
    split = int(N * TRAIN_RATIO)
    train_idx = perm[:split]; test_idx = perm[split:]
    
    model = MiniTransformer().to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1.2)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=N_EPOCHS)
    
    history = []; grok_step = None
    for epoch in range(N_EPOCHS):
        model.train()
        perm_train = train_idx[torch.randperm(len(train_idx))]
        for i in range(0, len(perm_train), BS):
            x = data_in[perm_train[i:i+BS]].to(DEVICE)
            y = data_lb[perm_train[i:i+BS]].to(DEVICE)
            opt.zero_grad()
            loss = F.cross_entropy(model(x), y)
            loss.backward(); opt.step()
        sched.step()
        
        if epoch % 25 == 0:
            model.eval()
            with torch.no_grad():
                tx = data_in[train_idx[:500]].to(DEVICE)
                ta = (model(tx).argmax(-1) == data_lb[train_idx[:500]].to(DEVICE)).float().mean().item()
                te_x = data_in[test_idx[:500]].to(DEVICE)
                tea = (model(te_x).argmax(-1) == data_lb[test_idx[:500]].to(DEVICE)).float().mean().item()
                history.append((epoch, ta, tea))
            if tea > 0.9 and grok_step is None:
                grok_step = epoch
        if epoch % 1000 == 0 and epoch > 0:
            ta_val = history[-1][1]; tea_val = history[-1][2] if history else 0
            print(f"  {label} ep={epoch:4d}  train={ta_val:.3f}  test={tea_val:.3f}")
    
    # 找到关键指标：标准条件的遗忘低谷
    min_test = min(h[2] for h in history)
    min_test_epoch = min((h[0] for h in history if h[2] == min_test), default=0)
    return {
        'grok_step': grok_step if grok_step else N_EPOCHS,
        'min_test': min_test,
        'min_test_epoch': min_test_epoch,
        'end_test': history[-1][2] if history else 0,
    }

print("="*55)
print("Grokking v2 — G vs Self-Refine vs 基线")
print(f"数据比例: {TRAIN_RATIO:.0%}")
print("="*55)

results = {}
for label, variant in [('standard','standard'), ('G','G'), ('self_refine','self_refine')]:
    t0 = time.time()
    r = run(label, variant)
    dt = time.time() - t0
    results[label] = r
    print(f"  {label:12s} grok={r['grok_step']:4d}ep  min_test={r['min_test']:.3f}(ep{r['min_test_epoch']:4d})  end={r['end_test']:.3f}  ({dt:.0f}s)")

print(f"\n核心指标——遗忘低谷期的test准确率（越低=遗忘越彻底）：")
for label in ['standard','G','self_refine']:
    r = results[label]
    print(f"  {label:12s}  test低谷={r['min_test']:.3f}  (ep{r['min_test_epoch']})  grok步数={r['grok_step']}")
    if label == 'G':
        print(f"  {'→':>12s} 标准低谷 - G低谷 = {results['standard']['min_test'] - r['min_test']:.3f}")
    elif label == 'self_refine':
        print(f"  {'→':>12s} 标准低谷 - SelfRefine低谷 = {results['standard']['min_test'] - r['min_test']:.3f}")

with open(os.path.join(OUT, 'grokking_v2_results.json'), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n保存至 {OUT}/grokking_v2_results.json")
