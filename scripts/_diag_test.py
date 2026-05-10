# -*- coding: utf-8 -*-
import sys, math
sys.set_int_max_str_digits(10000)
sys.path.insert(0, r'G:\GEME\src')

from gira.phase3.language import eq, fn, var, constant, Term, forall
from gira.phase3.godel import sub

x = var("x")
F = eq(x, constant("1"))
gn_F = F.gn()

F_self = sub(F, "x", "#%d" % gn_F)
gn_F_self = F_self.gn()

dev = abs(gn_F_self - gn_F)
degree = math.log(dev + 1) / math.log(gn_F_self + 1) if gn_F_self > 0 else 0

print("=== Diag 1: x=1 ===")
print("F:          %s" % F)
print("GN(F)       has %d digits" % (len(str(gn_F))))
print("F_self:     %s" % F_self)
print("GN(F_self): has %d digits" % (len(str(gn_F_self))))
print("|GN'-GN|:   %d digits" % len(str(dev)))
print("self-ref:   %.6f" % degree)
print()

# Test 2: universal formula
F2 = forall("x", forall("y", eq(fn("+", x, y), fn("+", y, x))))
gn_F2 = F2.gn()
F2_self = sub(F2, "x", "#%d" % gn_F2)
gn_F2_self = F2_self.gn()

dev2 = abs(gn_F2_self - gn_F2)
degree2 = math.log(dev2 + 1) / math.log(gn_F2_self + 1) if gn_F2_self > 0 else 0

print("=== Diag 2: forall commutativity ===")
print("F2:         %s" % F2)
print("GN(F2)      has %d digits" % (len(str(gn_F2))))
print("F2_self:    %s" % F2_self)
print("GN(F_self): has %d digits" % (len(str(gn_F2_self))))
print("|GN'-GN|:   %d" % len(str(dev2)))
print("self-ref:   %.6f" % degree2)
