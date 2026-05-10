"""
DG via SUB — Godel's prime-factorization substitution.

Sub(x, v, y): pure arithmetic on integers.
  x = product of primes^(exponents)
  Find position where exponent = v
  Replace with exponents from y's factorization
  Return the new integer.

DG(m) = 1 / (1 + distance(m, Sub(m, v_code, m)))
  m close to Sub(m, v_code, m) → DG ≈ 1 (self-referential)
  m far from Sub(m, v_code, m)  → DG ≈ 0
"""
import sys, math
sys.path.insert(0, r'G:\GEME\src')

from gira.phase3.language import eq, fn, var, constant, Term, forall


# Variable code (Godel's original: 17 = "x")
V_CODE = 17


def prime_factors(n, limit=100):
    """Decompose n into prime factors."""
    result = {}
    remaining = n
    p = 2
    while p <= limit and remaining > 1:
        count = 0
        while remaining % p == 0:
            remaining //= p
            count += 1
        if count > 0:
            result[p] = count
        p += 1
    return result


def sub_arithmetic(gn_value, var_code, sub_gn_value):
    """Godel's Sub(x, v, y) — pure integer operation.
    
    Sub(x, v, y):
      Decompose x into prime factors.
      Find the first position where exponent == v.
      Replace that position and subsequent ones with
      exponents from y's prime factorization.
    """
    x_factors = prime_factors(gn_value)
    y_factors = prime_factors(sub_gn_value)
    
    # Sort primes to get ordered list of exponents
    primes = sorted(x_factors.keys())
    exponents = [x_factors[p] for p in primes]
    
    # Find first exponent equal to var_code
    pos = -1
    for i, exp in enumerate(exponents):
        if exp == var_code:
            pos = i
            break
    
    if pos == -1:
        # Variable not found — Sub is the identity
        return gn_value
    
    # Get y's exponents (ordered)
    y_primes = sorted(y_factors.keys())
    y_exponents = [y_factors[p] for p in y_primes]
    
    # Replace at position
    new_exponents = exponents[:pos] + y_exponents + exponents[pos + 1:]
    
    # Rebuild from exponents
    result = 1
    y_primes_for_new = primes[:pos] + [primes[pos + i] if pos + i < len(primes) else primes[-1] + i for i in range(len(y_exponents))] + primes[len(new_exponents):]
    
    # Simpler: 2^i * 3^j * 5^k * ...
    new_prime = 2
    for exp in new_exponents:
        result *= (new_prime ** exp)
        new_prime += 1
    
    return result


def dg(formula):
    """DG(F) = 1 / (1 + |Sub(g, 17, g) - g| / g)."""
    g = formula.gn()
    sub_result = sub_arithmetic(g, V_CODE, g)
    
    # Distance: normalized difference
    if g == 0:
        return 0.0, g, sub_result
    
    diff = abs(sub_result - g)
    ratio = diff / max(g, sub_result)
    
    # DG = 1 at fixed point (Sub(g,g) = g), approaches 0 when far
    dg_value = 1.0 / (1.0 + ratio)
    
    return dg_value, g, sub_result, ratio


def estimate_gn_formula(string_repr):
    """Quick GN estimate via string-as-formula proxy."""
    from gira.phase3.language import Formula
    # use character ordinates encoding
    val = 1
    for ch in string_repr:
        val *= (2 ** ord(ch))
    return val


if __name__ == "__main__":
    x, y = var("x"), var("y")
    z0, z1 = constant("0"), constant("1")
    
    # Build Godel formula: sub(#g, #g) = sub(#g, #g)
    sub_gg_term = Term("function", "sub", [x, x])
    F_of_x = eq(sub_gg_term, sub_gg_term)
    g_godel = F_of_x.gn()
    
    # Self-referential instance
    g_num = Term("numeral", value=g_godel)
    sub_g_g = Term("function", "sub", [g_num, g_num])
    F_godel = eq(sub_g_g, sub_g_g)
    
    formulas = [
        ("1=1",      eq(z1, z1),        True),
        ("x=1",      eq(x, z1),          True),
        ("x+y=y+x",  eq(fn("+", x, y), fn("+", y, x)), True),
        ("sub(x,x)=sub(x,x)", F_of_x,    True),
        ("F(#g)",    F_godel,            True),
    ]
    
    print("=== DG = 1/(1+|Sub(g,17,g)-g|/g) ===")
    print("(var_code=17 for 'x')")
    print()
    for label, F, use_gn in formulas:
        if use_gn:
            dgv, g_val, sub_val, ratio = dg(F)
            print("  %-20s g=%d bits  Sub(g,g)=%d bits  ratio=%.4f  DG=%.4f"
                  % (label, g_val.bit_length(), sub_val.bit_length(), ratio, dgv))
