"""Author signature via G0 doubt trajectory — Plato vs Aristotle."""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))
from bgm_core import GEMENet

GREEK_LETTERS = 'αβγδεζηθικλμνξοπρστυφχψω'
def text_to_vec(text):
    v=[0.0]*27
    for ch in text.lower():
        if ch in GREEK_LETTERS: v[GREEK_LETTERS.index(ch)]+=1.0
    s=sum(v); return [x/s for x in v] if s>0 else v

# Texts (from earlier experiments)
PLATO_REP = """κατεβην χθες εις τον πειραια μετα γλαυκωνος του αριστωνος
προσευξομενος τε τη θεω και αμα την εορτην βουλομενος θεασασθαι
τινι τροπω ποιησουσιν ατε νυν πρωτον αγοντες καλην μεν ουν μοι
η και η των πολιτων πομπη εδοξεν ειναι ου μεντοι ηττον εφαινετο
πρεπειν ην οι θρακες επεμπον επειδη δε προσευξαμεν τε και εθεασαμεθα
απιμεν προς το αστυ κατιδων ουν πορρωθεν ημας πολεμαρχος ο κεφαλου
εκελευσε δραμοντα τον παιδα περιμειναι ε κελευσαι και μου οπισθεν
ο παις λαβομενος του ιματιου εφη κελευει υμας πολεμαρχος περιμειναι"""

ARISTOTLE_META = """παντες ανθρωποι του ειδεναι ορεγονται φυσει σημειον δ
η των αισθησεων αγαπησις και γαρ χωρις της χρειας αγαπωνται δι αυτας
και μαλιστα των αλλων η δια των ομματων ου γαρ μονον ινα πραττωμεν
αλλα και μηδεν μελλοντες πραττειν την οψιν ελοιμεθα αν αντι παντων
των αλλων αιτιον δε τουτο οτι μαλιστα ποιει γνωριζειν ημας αυτη
και πολλας δηλοι διαφορας εχθυρον γαρ ουσιας και νοητον οραν εστιν
ορατον γαρ το χρωμα εστιν και τουτο λεγεται ορατον τι δ εστι το χρωμα"""

PLATO_REP_P2 = """τον δε λογον τουτον ζητουν τι εστιν δικαιοσυνη και αδικια
και εν τινι πολιτεια και κατα ποιους τροπους η μετιουσα πολις αν
ειη αριστη και τον ανδρα ο δει τον βελτιστον αποδεξασθαι αλλα μεντοι
σκοπει ει σοι τα αυτα δοκει α μοι δοκει ο μεν γαρ δικαιος πειραται
πανταχου πλεον εκεινου ελαττον εχειν ο δε αδικος και πλειστον"""

ARISTOTLE_ETHICS = """πασα τεχνη και πασα μεθοδος ομοιως δε πραξις τε και
προαιρεσις αγαθου τινος εφιεσθαι δοκει διο καλως απεφηναντο ταγαθον
ου παντ εφιεται διαφορα δε τις φαινεται των τελων τα μεν γαρ εισιν
ενεργειαι τα δε παρ αυτας εργα τινα ων δ εισιν εργα παρα τας ενεργειας
ενταυθα δη το τελος φαινεται αγαθον ειναι και κρειττον ισως δε το
την κοινον βελτιον ειναι και τελειοτερον"""

def chunks(text, n=5):
    words=text.replace('\n',' ').split()
    return [' '.join(words[i:i+n]) for i in range(0,len(words),n) if words[i:i+n]]

def run_author(name, text, passes=1):
    net = GEMENet(n_units=3, g0_enabled=True, g0_weight=0.3,
                  g0_interval=1, seed_base=42)
    cls = chunks(text)
    for _ in range(passes):
        for cl in cls:
            net.step(text_to_vec(cl))
    m = net.metrics()
    
    g0 = net.g0
    g0_m = g0.metrics()
    mi_vals = [u['MI'] for u in m['units']]
    
    return {
        'name': name,
        'clauses': len(cls),
        'g0_l4': g0_m.get('L4_frame_count', 0),
        'g0_mi': g0_m.get('I(phi;X)', 0),
        'g0_doubt': g0_m.get('doubt_mode', False),
        'mi_spread': max(mi_vals)-min(mi_vals),
        'g0_layers': g0_m.get('layers', {}),
    }

print('='*55)
print('Author Signature via G0 Doubt Trajectory')
print('='*55)

tests = [
    ('Plato_Republic_I', PLATO_REP),
    ('Aristotle_Metaphysics_I', ARISTOTLE_META),
    ('Plato_Republic_I(p2)', PLATO_REP_P2),
    ('Aristotle_Ethics_I', ARISTOTLE_ETHICS),
]

results = []
for name, text in tests:
    r = run_author(name, text)
    results.append(r)
    print(f'\n{r["name"]}')
    print(f'  Clauses: {r["clauses"]}')
    print(f'  G0 L4:   {r["g0_l4"]}')
    print(f'  G0 MI:   {r["g0_mi"]}')
    print(f'  G0 doubt:{r["g0_doubt"]}')
    print(f'  MI spread:{r["mi_spread"]}')
    print(f'  Layers:  {r["g0_layers"]}')

print(f'\n{"="*55}')
print('Same-author vs cross-author comparison:')
plato = [r for r in results if 'Plato' in r['name']]
arist = [r for r in results if 'Aristotle' in r['name']]
print(f'Plato avg G0 L4: {sum(r["g0_l4"] for r in plato)/len(plato):.1f}')
print(f'Aristotle avg G0 L4: {sum(r["g0_l4"] for r in arist)/len(arist):.1f}')
print(f'Plato avg MI spread: {sum(r["mi_spread"] for r in plato)/len(plato):.4f}')
print(f'Aristotle avg MI spread: {sum(r["mi_spread"] for r in arist)/len(arist):.4f}')
