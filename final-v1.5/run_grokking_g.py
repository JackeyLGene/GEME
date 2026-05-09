"""
Grokking + G句子 — 补充材料S2的小小震撼
2层Transformer, a+b mod 97, 看G句子能否压缩grokking步数
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import math, random, json, os, time

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
PRIME = 97
N_VOCAB = PRIME + 3  # digits 0-96 + + = pad
N_DIGITS = 3  # a + b = c (3 tokens)
BS = 512
N_EPOCHS = 5000
OUT = "g:/GEME/docs/robustness_results"
os.makedirs(OUT, exist_ok=True)

class MiniTransformer(nn.Module):
    def __init__(self, d_model=128, n_heads=4, d_ff=512, n_layers=2, max_len=10):
        super().__init__()
        self.embed = nn.Embedding(N_VOCAB, d_model)
        self.pos = nn.Embedding(max_len, d_model)
        layer = nn.TransformerEncoderLayer(d_model, n_heads, d_ff, dropout=0,
                                           activation='relu', batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(layer, n_layers)
        self.out = nn.Linear(d_model, PRIME)
        
    def forward(self, x):
        # x: (B, seq_len)
        B, S = x.shape
        pos = self.pos(torch.arange(S, device=x.device).unsqueeze(0))
        h = self.embed(x) + pos
        h = self.encoder(h)
        # 取最后一个token的表示 -> 预测结果
        return self.out(h[:, -1])

def make_data(with_g=False):
    """生成模运算数据"""
    rs = random.Random(42)
    inputs, labels = [], []
    for a in range(PRIME):
        for b in range(PRIME):
            c = (a + b) % PRIME
            if with_g:
                # G句子：两个特殊token作为自指标记
                in_seq = [PRIME+1, PRIME+2, a, PRIME, b, PRIME]
            else:
                in_seq = [a, PRIME, b, PRIME]
            inputs.append(in_seq)
            labels.append(c)
    return torch.tensor(inputs), torch.tensor(labels)

def run_experiment(with_g, label):
    data_in, data_lb = make_data(with_g)
    N = len(data_in)
    perm = torch.randperm(N, generator=torch.Generator().manual_seed(42))
    split = N * 50 // 100  # 50% train, 50% test (standard grokking setup)
    train_idx = perm[:split]
    test_idx = perm[split:]
    
    model = MiniTransformer().to(DEVICE)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1.0)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=N_EPOCHS)
    
    train_accs, test_accs, grok_step = [], [], None
    
    for epoch in range(N_EPOCHS):
        model.train()
        perm_train = train_idx[torch.randperm(len(train_idx))]
        losses = 0
        for i in range(0, len(perm_train), BS):
            idx = perm_train[i:i+BS]
            x = data_in[idx].to(DEVICE)
            y = data_lb[idx].to(DEVICE)
            opt.zero_grad()
            logits = model(x)
            loss = F.cross_entropy(logits, y)
            loss.backward()
            opt.step()
            losses += loss.item()
        scheduler.step()
        
        if epoch % 10 == 0:
            model.eval()
            with torch.no_grad():
                tx = data_in[train_idx[:1000]].to(DEVICE)
                ty = data_lb[train_idx[:1000]].to(DEVICE)
                train_acc = (model(tx).argmax(-1) == ty).float().mean().item()
                
                te_x = data_in[test_idx[:1000]].to(DEVICE)
                te_y = data_lb[test_idx[:1000]].to(DEVICE)
                test_acc = (model(te_x).argmax(-1) == te_y).float().mean().item()
                
                if test_acc > 0.9 and grok_step is None:
                    grok_step = epoch
                
                if epoch % 200 == 0 or (grok_step is not None and epoch - grok_step < 100):
                    pass  # suppress per-epoch print
        
        if epoch % 500 == 0:
            with torch.no_grad():
                tx = data_in[train_idx[:1000]].to(DEVICE)
                ty = data_lb[train_idx[:1000]].to(DEVICE)
                ta = (model(tx).argmax(-1) == ty).float().mean().item()
                te_x = data_in[test_idx[:1000]].to(DEVICE)
                te_y = data_lb[test_idx[:1000]].to(DEVICE)
                tea = (model(te_x).argmax(-1) == te_y).float().mean().item()
            print(f"  {label} ep={epoch:4d}  train={ta:.3f}  test={tea:.3f}")
    
    return {'grok_step': grok_step if grok_step else N_EPOCHS, 'label': label}

print("="*55)
print("Grokking + G句子 — 小小震撼")
print("="*55)
print(f"Device: {DEVICE}")
print(f"Prime: {PRIME}, Training examples: 97*97*50% = {97*97*50//100}")
print()

# A: 标准训练
print("[A] 标准grokking...")
t0 = time.time()
r_a = run_experiment(False, "standard")
t_a = time.time() - t0
print(f"  Done in {t_a:.0f}s")

# B: 加G句子
print("[B] 加G句子...")
t0 = time.time()
r_b = run_experiment(True, "G-sentence")
t_b = time.time() - t0
print(f"  Done in {t_b:.0f}s")

results = {
    'standard_grok_step': r_a['grok_step'],
    'G_grok_step': r_b['grok_step'],
    'compression': round(r_a['grok_step'] / max(r_b['grok_step'], 1), 2),
}
print(f"\n结果:")
print(f"  标准grok: {r_a['grok_step']}步")
print(f"  +G句子:   {r_b['grok_step']}步")
print(f"  压缩比:   {results['compression']}x")

with open(os.path.join(OUT, 'grokking_results.json'), 'w') as f:
    json.dump(results, f, indent=2)
print(f"\n保存至 {OUT}/grokking_results.json")
