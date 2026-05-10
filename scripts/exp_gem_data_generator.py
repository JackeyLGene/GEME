"""
GEM 6.1 — Controlled DataGenerator for Q-Sandbox.

S-level category alignment:
  S0: 碎片/无关字符     "1+2" (不完整算式), "a" (非算术信号)
  S1: 符号运算(可判定)  "1+2=3", "1+2=4" (真/假都在语法内)
  S2: 恒等/公式变形     "1+2=2+1", "0+5=5" (结构等价)
  S3: 推论(需推理链)    ∀x∀y(x+y=y+x) (系统当前无法证明)
  S4: 悖论(自指)       哥德尔命题
"""

import sys, io, random
sys.path.insert(0, r'G:\GEME\src')

from gira.phase3.language import eq, fn, constant, Formula


class DataGenerator:
    """Controlled generation of Q arithmetic training data by S-level.
    
    S0: fragments / non-formulas
    S1: ground arithmetic (true or false, decidable)
    S2: identity / structural equivalence
    S3: universal formulas (not decidable without induction)
    S4: Godel propositions (not produced here — reserved)
    """
    
    def __init__(self, seed=42):
        random.seed(seed)
        self.generated = []
    
    def numeral(self, n):
        t = constant("0")
        for _ in range(n):
            t = fn("s", t)
        return t
    
    def gen_S0_fragment(self):
        """S0: incomplete expressions — no equation."""
        a, b = random.randint(0, 9), random.randint(0, 9)
        op = random.choice(["+", "\u00d7"])
        term = fn(op, self.numeral(a), self.numeral(b))
        self.generated.append((eq(term, term), f"{a}{op}{b}", "S0"))
    
    def gen_S0_char(self, ch="a"):
        """S0: non-arithmetic character."""
        from gira.phase3.language import constant as Const
        self.generated.append((eq(Const(ch), Const(ch)), f"'{ch}'", "S0"))
    
    def gen_S1_true(self, a, b, op):
        """S1: ground arithmetic true: a op b = result."""
        val = a + b if op == "+" else a * b
        f = eq(fn(op, self.numeral(a), self.numeral(b)), self.numeral(val))
        self.generated.append((f, f"{a}{op}{b}={val}", "S1"))
    
    def gen_S1_false(self, a, b, op):
        """S1: ground arithmetic false: a op b = wrong_result."""
        correct = a + b if op == "+" else a * b
        wrong = correct + max(1, random.randint(1, 5))
        f = eq(fn(op, self.numeral(a), self.numeral(b)), self.numeral(wrong))
        self.generated.append((f, f"{a}{op}{b}={wrong}", "S1"))
    
    def gen_S2_identity(self, a):
        """S2: identity: a+0=a"""
        f = eq(fn("+", self.numeral(a), constant("0")), self.numeral(a))
        self.generated.append((f, f"{a}+0={a}", "S2"))
    
    def gen_S2_swap(self, a, b, op):
        """S2: structural equivalence: a op b = b op a"""
        f = eq(fn(op, self.numeral(a), self.numeral(b)),
               fn(op, self.numeral(b), self.numeral(a)))
        self.generated.append((f, f"{a}{op}{b}={b}{op}{a}", "S2"))
    
    def gen_S2_reflexive(self, a, b, op):
        """S2: reflexive: a op b = a op b"""
        f = eq(fn(op, self.numeral(a), self.numeral(b)),
               fn(op, self.numeral(a), self.numeral(b)))
        self.generated.append((f, f"{a}{op}{b}={a}{op}{b}", "S2"))
    
    def gen_S3_universal(self):
        """S3: universal formula — NOT included in training, only for evaluation."""
        pass  # Handled by test targets
    
    def batch(self, config):
        """Generate a batch of training data from config dict.
        
        config = {
            "S0":  count,
            "S1":  (count, (min_num, max_num), [ops]),
            "S2":  (count, (min_num, max_num), [ops]),
        }
        """
        self.generated = []
        
        for cat, params in config.items():
            count = params[0]
            
            if cat == "S0":
                for _ in range(count):
                    if random.random() < 0.5:
                        self.gen_S0_fragment()
                    else:
                        self.gen_S0_char(random.choice("abcxyz"))
            
            elif cat == "S1":
                rng, ops = params[1], params[2]
                for _ in range(count):
                    a = random.randint(rng[0], rng[1])
                    b = random.randint(rng[0], rng[1])
                    op = random.choice(ops)
                    if random.random() < 0.7:
                        self.gen_S1_true(a, b, op)
                    else:
                        self.gen_S1_false(a, b, op)
            
            elif cat == "S2":
                rng, ops = params[1], params[2]
                for _ in range(count):
                    t = random.random()
                    a = random.randint(rng[0], rng[1])
                    b = random.randint(rng[0], rng[1])
                    op = random.choice(ops)
                    if t < 0.4:
                        self.gen_S2_swap(a, b, op)
                    elif t < 0.7:
                        self.gen_S2_identity(a)
                    else:
                        self.gen_S2_reflexive(a, b, op)
        
        random.shuffle(self.generated)
        return self.generated


def demo():
    from collections import Counter
    
    gen = DataGenerator(seed=42)
    config = {
        "S0": (10,),
        "S1": (30, (0, 10), ["+", "\u00d7"]),
        "S2": (30, (1, 8), ["+", "\u00d7"]),
    }
    data = gen.batch(config)
    
    cats = Counter(c for _, _, c in data)
    print(f"Dataset: {len(data)} statements")
    for cat in ["S0", "S1", "S2"]:
        cnt = cats.get(cat, 0)
        print(f"  {cat}: {cnt} ({cnt*100//len(data)}%)")


if __name__ == "__main__":
    demo()

