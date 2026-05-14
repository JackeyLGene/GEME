"""Author signature from UNSELECTED merge candidates — the multiverse."""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from geme import GEME
import random as _qr2

GREEK = 'αβγδεζηθικλμνξοπρστυφχψω'
def text_vec(t):
    v=[0.0]*27
    for ch in t.lower():
        if ch in GREEK: v[GREEK.index(ch)]+=1.0
    s=sum(v); return [x/s for x in v] if s>0 else v

def chunks(text, n=5):
    words=text.replace('\n',' ').split()
    return [' '.join(words[i:i+n]) for i in range(0,len(words),n) if words[i:i+n]]

PLATO = """κατεβην χθες εις τον πειραια μετα γλαυκωνος του αριστωνος
προσευξομενος τε τη θεω και αμα την εορτην βουλομενος θεασασθαι
τινι τροπω ποιησουσιν ατε νυν πρωτον αγοντες καλην μεν ουν μοι
η και η των πολιτων πομπη εδοξεν ειναι ου μεντοι ηττον εφαινετο
πρεπειν ην οι θρακες επεμπον επειδη δε προσευξαμεν τε και εθεασαμεθα
απιμεν προς το αστυ κατιδων ουν πορρωθεν ημας πολεμαρχος ο κεφαλου"""

ARISTOTLE = """παντες ανθρωποι του ειδεναι ορεγονται φυσει σημειον δ
η των αισθησεων αγαπησις και γαρ χωρις της χρειας αγαπωνται δι αυτας
και μαλιστα των αλλων η δια των ομματων ου γαρ μονον ινα πραττωμεν
αλλα και μηδεν μελλοντες πραττειν την οψιν ελοιμεθα αν αντι παντων
των αλλων αιτιον δε τουτο οτι μαλιστα ποιει γνωριζειν ημας αυτη"""

def count_branches(geme):
    """Count unselected candidates that were 'close' (within 2x the winner's distance)."""
    mv = getattr(geme.memory, '_multiverse', [])
    if not mv:
        return 0, 0, 0.0
    
    total_branches = len(mv)
    # Branch diversity: how many different frame structures exist?
    unique_fids = set()
    for _, _, lbl in mv:
        unique_fids.add(lbl)
    
    return total_branches, len(unique_fids), len(unique_fids) / max(total_branches, 1)

def run(name, text):
    g = GEME(memory_cap=16)
    g.memory.preserve_sig=True; g.memory.quantum_mode=True
    g.memory._merge_dists=[0.3]*30; g._induction_threshold=3.0
    g.memory.cooccur_thresh=0.08
    g.memory._qrand=_qr2.Random(42)
    
    cls = chunks(text)
    for cl in cls:
        g.process_vec(text_vec(cl), cl[:8])
        g.memory.self_observe()
    
    m = g.metrics()
    branches, unique_b, ratio = count_branches(g)
    
    return {
        'name': name,
        'clauses': len(cls),
        'frames': m['frame_count'],
        'L4': m['L4_frame_count'],
        'branches': branches,
        'branch_diversity': unique_b,
        'branch_ratio': ratio,
        'MI': m.get('I(phi;X)', 0),
    }

print('='*55)
print('Author Signature from UNSELECTED Merge Candidates')
print('='*55)

for name, text in [('Plato_Republic', PLATO), ('Aristotle_Metaphysics', ARISTOTLE)]:
    r = run(name, text)
    print(f'\n{r["name"]}')
    print(f'  Clauses: {r["clauses"]}')
    print(f'  Total branches (unselected): {r["branches"]}')
    print(f'  Branch diversity:             {r["branch_diversity"]}')
    print(f'  Branch/Merge ratio:           {r["branch_ratio"]:.3f}')
    print(f'  GEME MI:                      {r["MI"]:.4f}')
    print(f'  L4 frames:                    {r["L4"]}')
