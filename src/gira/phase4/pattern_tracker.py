"""
M1: PatternTracker - L3 signal recorder and strategy reconstructor.

Records every formula classified as L3 during system operation.
Reconstructs strategies from proof history on demand --
no static strategy storage, only history-based reconstruction.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from gira.phase3.language import Formula, Term, forall, exists, eq, fn


@dataclass
class L3Record:
    """Record of a single L3 signal."""
    frame: int
    formula: Formula
    formula_str: str
    structural_signature: str
    system_L_at_time: int
    harm_value: float


@dataclass
class ProofAttempt:
    """Record of a single proof attempt."""
    frame: int
    formula_str: str
    signature: str
    rule_name: str
    succeeded: bool
    system_L_at_time: int


def compute_signature(formula: Formula) -> str:
    """Compute structural signature by traversing formula tree.
    
    Examples:
      AxAy(x*y = y*x)  ->  "forall_forall_equation_mul"
      Ax(x+0=x)        ->  "forall_equation_add"
      0+0=0            ->  "equation_add"
    """
    parts = []
    _traverse(formula, parts)
    return "_".join(parts) if parts else "empty"


def _traverse(node: Formula, parts: List[str]) -> None:
    """Recursively traverse Formula collecting structural labels."""
    kind = node.kind
    if kind in ("forall", "exists"):
        parts.append(kind)
        if node.left:
            _traverse(node.left, parts)
    elif kind == "negation":
        parts.append("neg")
        if node.left:
            _traverse(node.left, parts)
    elif kind == "equation":
        parts.append("equation")
        # Encode LHS-RHS structural relationship, not just function types
        _traverse_equation(node, parts)
    elif kind == "conjunction":
        parts.append("conj")
        if node.left: _traverse(node.left, parts)
        if node.right: _traverse(node.right, parts)
    elif kind == "disjunction":
        parts.append("disj")
        if node.left: _traverse(node.left, parts)
        if node.right: _traverse(node.right, parts)
    elif kind == "implication":
        parts.append("impl")
        if node.left: _traverse(node.left, parts)
        if node.right: _traverse(node.right, parts)


def _traverse_equation(node: Formula, parts: List[str]) -> None:
    """Encode the structural relationship between LHS and RHS of equation.
    
    Distinguishes:
      x*y = y*x  →  "mul_swap"  (commutative pattern)
      x*y = 0    →  "mul_const" (zero law)
      x+y = y+x  →  "add_swap"
    """
    lhs = node.left
    rhs = node.right
    if lhs is None or rhs is None:
        return
    
    if lhs.kind == "function" and rhs.kind == "function":
        # Both sides are function applications
        if lhs.symbol == rhs.symbol:
            # Same function on both sides - check operand relationship
            l_args = [_term_string(a) for a in lhs.args]
            r_args = [_term_string(b) for b in rhs.args]
            op_name = _op_name(lhs.symbol)
            if set(l_args) == set(r_args) and l_args != r_args:
                parts.append(f"{op_name}_swap")  # commutative
            elif l_args == r_args:
                parts.append(f"{op_name}_same")  # tautology
            else:
                parts.append(op_name)
        else:
            parts.append(f"{_op_name(lhs.symbol)}_{_op_name(rhs.symbol)}")
    elif lhs.kind == "function":
        # LHS function, RHS constant/variable
        parts.append(f"{_op_name(lhs.symbol)}_const")
    elif rhs.kind == "function":
        parts.append(f"{_op_name(rhs.symbol)}_const")
    else:
        parts.append("var_eq")


def _op_name(symbol: str) -> str:
    """Map function symbol to short signature name."""
    if symbol == '\u00d7':
        return "mul"
    elif symbol == '+':
        return "add"
    elif symbol == 's':
        return "succ"
    return "fn"


def _term_string(term: Term, _depth=0) -> str:
    """Stable string representation with recursion guard."""
    if term is None or _depth > 5:
        return "?"
    if term.kind in ("variable", "constant", "numeral"):
        return f"{term.kind[0]}:{term.symbol}"
    if term.kind == "function":
        args = "_".join(_term_string(a, _depth+1) for a in term.args)
        return f"f:{term.symbol}({args})"
    return str(term)


class PatternTracker:
    """Records L3 signals and proof attempts for strategy reconstruction.
    
    Strategy is not stored statically -- it is reconstructed from history
    by querying: "given this signature, what methods succeeded before?"
    """

    def __init__(self):
        self.history: List[L3Record] = []
        self.proof_history: List[ProofAttempt] = []

    def record(self, formula: Formula, frame: int,
               system_L: int = 0) -> str:
        """Record an L3 signal. Returns the structural signature."""
        formula_str = str(formula)
        sig = compute_signature(formula)
        record = L3Record(
            frame=frame,
            formula=formula,
            formula_str=formula_str,
            structural_signature=sig,
            system_L_at_time=system_L,
            harm_value=1.0,
        )
        self.history.append(record)
        return sig

    def get_pattern_summary(self) -> Dict[str, int]:
        """Aggregate pattern frequencies by signature."""
        summary: Dict[str, int] = {}
        for rec in self.history:
            sig = rec.structural_signature
            summary[sig] = summary.get(sig, 0) + 1
        return summary

    def get_history_since_transition(self, from_level: int = 0
                                     ) -> List[L3Record]:
        """Get L3 records since a given system level."""
        return [r for r in self.history
                if r.system_L_at_time >= from_level]

    def get_records_by_signature(self, signature: str) -> List[L3Record]:
        """Filter history by signature."""
        return [r for r in self.history
                if r.structural_signature == signature]

    def clear(self) -> None:
        """Clear all history."""
        self.history.clear()
        self.proof_history.clear()

    def record_proof(self, formula: Formula, rule_name: str,
                     succeeded: bool = True, frame: int = 0) -> None:
        """Record a proof attempt."""
        sig = compute_signature(formula)
        attempt = ProofAttempt(
            frame=frame,
            formula_str=str(formula),
            signature=sig,
            rule_name=rule_name,
            succeeded=succeeded,
            system_L_at_time=0,
        )
        self.proof_history.append(attempt)

    def reconstruct_strategy(self, signature: str) -> dict:
        """Reconstruct strategy from proof history (no static storage).
        
        Returns:
            {"strategy": "induction" | "naive" | None,
             "confidence": float, "related_attempts": int}
        """
        related = [a for a in self.proof_history
                   if a.signature == signature
                   or signature in a.signature
                   or a.signature in signature]

        if not related:
            return {"strategy": None, "confidence": 0.0, "related_attempts": 0}

        successes = sum(1 for a in related if a.succeeded)
        rate = successes / len(related)

        induction_attempts = [a for a in related
                              if "induction" in a.rule_name.lower()]
        if induction_attempts:
            induction_rate = sum(1 for a in induction_attempts
                                 if a.succeeded) / len(induction_attempts)
            if induction_rate > 0.5:
                return {
                    "strategy": "induction",
                    "confidence": induction_rate,
                    "related_attempts": len(related),
                }

        return {
            "strategy": "naive" if rate > 0.3 else None,
            "confidence": rate,
            "related_attempts": len(related),
        }

    def get_strategy_summary(self) -> str:
        """Return summary of all reconstructable strategies."""
        if not self.proof_history:
            return "  Strategy history: empty (no proof attempts)"
        from collections import Counter
        sig_counts = Counter(a.signature for a in self.proof_history)
        lines = [f"  Strategy history: {len(self.proof_history)} attempts, "
                 f"{len(sig_counts)} patterns"]
        for sig, count in sig_counts.most_common(5):
            strategy = self.reconstruct_strategy(sig)
            if strategy["strategy"]:
                lines.append(
                    f"    [{strategy['strategy']}] {sig}: "
                    f"{strategy['confidence']:.0%} confidence "
                    f"({strategy['related_attempts']} attempts)"
                )
        return "\n".join(lines)
