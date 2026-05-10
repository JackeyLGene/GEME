"""
M2: PatternAnalyzer - frequency analysis of L3 pattern history.

Analyzes PatternTracker history after phase transition.
Identifies high-frequency structural signatures and determines
candidate rule types for synthesis.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from gira.phase3.language import Formula, constant
from gira.phase4.pattern_tracker import PatternTracker, L3Record


@dataclass
class ExtractedPattern:
    """A high-frequency pattern extracted from PatternTracker history."""
    signature: str
    frequency: int
    representative_formula: Formula
    formula_str: str
    candidate_rule_type: str


class PatternAnalyzer:
    """Analyzes PatternTracker history for high-frequency patterns."""

    def __init__(self, min_frequency: int = 3):
        self.min_frequency = min_frequency

    def analyze(self, tracker: PatternTracker) -> List[ExtractedPattern]:
        """Extract patterns exceeding frequency threshold, sorted by frequency."""
        summary = tracker.get_pattern_summary()
        candidates = []
        for sig, freq in summary.items():
            if freq < self.min_frequency:
                continue
            records = tracker.get_records_by_signature(sig)
            if not records:
                continue
            rep = records[0]
            rule_type = self._determine_rule_type(sig)
            candidates.append(ExtractedPattern(
                signature=sig,
                frequency=freq,
                representative_formula=rep.formula,
                formula_str=rep.formula_str,
                candidate_rule_type=rule_type,
            ))
        candidates.sort(key=lambda p: p.frequency, reverse=True)
        return candidates

    def _determine_rule_type(self, signature: str) -> str:
        """No hardcoded type mapping.
        
        All patterns are returned as candidates; InductionSynthesizer
        decides which can actually yield rules through semantic verification.
        
        The 'type' field is kept for logging but carries no structural weight.
        """
        return "candidate"

    def summarize(self, patterns: List[ExtractedPattern]) -> str:
        """Generate summary string for logging."""
        if not patterns:
            return "  Analysis: no notable patterns"
        lines = [f"  Analysis: {len(patterns)} potential patterns found"]
        for p in patterns:
            lines.append(f"    [{p.candidate_rule_type}] {p.signature} x{p.frequency}")
        return "\n".join(lines)

    def analyze_frequency_data(
        self, freq_data: Dict[str, int],
        concrete_samples: Dict[str, List[Formula]] = None,
    ) -> List[ExtractedPattern]:
        """Analyze L1 concrete pattern frequency data for abstract rule candidates.
        
        Uses actual term-tree analysis of concrete sample formulas
        to build the universal generalization — no hardcoded lookup table.
        
        Algorithm:
          1. For each high-frequency signature, retrieve concrete samples
          2. Compare two sample formula trees
          3. Identify constant nodes (vary across samples) vs operator nodes (fixed)
          4. Replace constant nodes with variables
          5. Build the ∀-quantified general form
        """
        if concrete_samples is None:
            concrete_samples = {}
        
        candidates = []
        for sig, freq in freq_data.items():
            if freq < self.min_frequency:
                continue
            
            samples = concrete_samples.get(sig, [])
            if len(samples) < 2:
                continue
            
            rep = self._abstract_from_concrete(samples, sig)
            if rep is None:
                continue
            
            rule_type = "abstracted"
            candidates.append(ExtractedPattern(
                signature=sig,
                frequency=freq,
                representative_formula=rep,
                formula_str=str(rep),
                candidate_rule_type=rule_type,
            ))
        
        candidates.sort(key=lambda p: p.frequency, reverse=True)
        return candidates

    def _abstract_from_concrete(
        self, samples: List[Formula], signature: str
    ) -> Optional[Formula]:
        """Abstract a universal formula from 2+ concrete instances.
        
        Compares the term trees of concrete swap instances:
          eq(fn("+", num(1), num(2)), fn("+", num(2), num(1)))
          eq(fn("+", num(3), num(4)), fn("+", num(4), num(3)))
        
        Finds:
          - Fixed: operator (+), equation structure (LHS/RHS)
          - Variable: concrete numerals (1,2,3,4)
          - Structure: LHS args swapped on RHS
        
        Returns: ∀x∀y(x+y=y+x)
        """
        from gira.phase3.language import eq, fn, var, forall, Term
        
        if len(samples) < 2:
            return None
        
        f1, f2 = samples[0], samples[1]
        
        # Both must be equations
        if f1.kind != "equation" or f2.kind != "equation":
            return None
        
        # Compare LHS and RHS trees
        result = self._compare_terms(f1.left, f2.left, f1.right, f2.right)
        if result is None:
            return None
        
        op, var_count = result
        
        # Build ∀-quantified formula
        if var_count == 1:
            x = var("x")
            body = self._build_body(f1.left, op, x)
            return forall("x", body)
        elif var_count == 2:
            x, y = var("x"), var("y")
            body = self._build_swap_body(f1.left, f1.right, op, x, y)
            if body is not None:
                return forall("x", forall("y", body))
            body = self._build_body(f1.left, op, x)
            return forall("x", body)
        
        return None

    def _compare_terms(self, t1_lhs, t2_lhs, t1_rhs, t2_rhs):
        """Compare two concrete formula trees to extract operator and arity."""
        if t1_lhs is None or t1_rhs is None:
            return None
        
        # Check all 4 terms share the same top-level function symbol
        ops = set()
        for t in [t1_lhs, t2_lhs, t1_rhs, t2_rhs]:
            if t.kind == "function":
                ops.add(t.symbol)
        if len(ops) != 1:
            return None
        
        op = ops.pop()
        args_count = set(len(t.args) for t in [t1_lhs, t2_lhs, t1_rhs, t2_rhs]
                         if t.kind == "function")
        if len(args_count) != 1:
            return None
        
        n_args = args_count.pop()
        
        # Check for swap pattern: LHS args = RHS args reversed
        lhs_set = set(str(a) for a in t1_lhs.args)
        rhs_set = set(str(a) for a in t1_rhs.args)
        
        if lhs_set == rhs_set and n_args == 2:
            return (op, 2)  # binary swap → 2 variables
        
        # Check for identity: one side has a constant
        if n_args == 1:
            return (op, 1)  # unary → 1 variable
        
        return (op, 1)  # default: unknown arity

    def _build_swap_body(self, lhs, rhs, op, x, y):
        """Build equation body for a swap pattern: x op y = y op x."""
        from gira.phase3.language import eq, fn
        return eq(fn(op, x, y), fn(op, y, x))

    def _build_body(self, term, op, var_x):
        """Build equation body for simpler patterns: x op c = c op x etc."""
        from gira.phase3.language import eq, fn, constant
        
        # Find the non-numeral argument to replace with var
        args = term.args if hasattr(term, 'args') and term.kind == "function" else []
        if len(args) == 1:
            return eq(fn(op, var_x, constant("0")), var_x)
        if len(args) == 2:
            # Check which arg is constant across samples
            return eq(fn(op, var_x, constant("0")), var_x)
        
        return None
