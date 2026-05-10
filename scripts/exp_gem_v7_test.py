"""V7 test."""
import sys, random
sys.path.insert(0, r'G:\GEME\src')
from gira.phase6.geme_v7 import GEME
from gira.phase3.language import eq, fn, var, constant, forall, Term
from gira.phase3.q_axioms import robinson_q

NUM = lambda n: constant("0") if n==0 else fn("s", NUM(n-1))
x,y = var("x"),var("y")
T_ADD = forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))
S4 = eq(Term("function","sub",[Term("numeral",value=T_ADD.gn()),Term("numeral",value=17),Term("numeral",value=T_ADD.gn())]),
        Term("function","sub",[Term("numeral",value=T_ADD.gn()),Term("numeral",value=17),Term("numeral",value=T_ADD.gn())]))

data = [(eq(fn("+",NUM(random.randint(1,8)),NUM(random.randint(1,8))),NUM(0)),"S0") for _ in range(10)]
for _ in range(3): a,b=random.randint(1,5),random.randint(1,5); data.append((eq(fn("+",NUM(a),NUM(b)),fn("+",NUM(b),NUM(a))),"S2"))
data.append((S4,"S4"))
random.seed(42); random.shuffle(data)

for label, s4d in [("S4 derive ON",True),("S4 derive OFF",False)]:
    bits=[]
    for rep in range(15):
        e=GEME(robinson_q(),mem_cap=8,merge_thresh=0.15,max_weight=100,s4_derive=s4d)
        for r in range(8):
            for f,c in data: e.process(f)
        bits.append(1 if e.evaluate(T_ADD)==2 else 0)
    print(f"  {label:<20} {sum(bits)/15*100:.0f}% ({sum(bits)}/15)")

print("  V7 features: selective decay, dynamic sigs, no weight explosion")
