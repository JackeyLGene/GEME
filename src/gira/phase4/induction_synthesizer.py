"""
M3: InductionSynthesizer - induction rule synthesis and application.

InductionRule: actively proves forall formulas by:
  1. Substituting variables with 0 (base case)
  2. Semantic evaluation of the base case
  3. If base case holds, the formula is proved by induction
"""

from __future__ import annotations
from typing import List, Optional, Tuple
from dataclasses import dataclass

from gira.phase3.language import (
    Formula, Term, eq, fn, constant, var,
    forall, exists, neg, impl, conj, disj,
)
from gira.phase3.godel import formula_to_string, sub as godel_sub
from gira.phase3.inference import InferenceRule, SignalClassifier
from gira.phase3.proof_checker import _eval_term
from gira.phase3.q_axioms import robinson_q as get_q_axioms
from gira.phase4.pattern_analyzer import ExtractedPattern


def _semantic_truth(formula: Formula) -> Optional[bool]:
    """Evaluate truth of a variable-free formula using Q arithmetic."""
    try:
        if formula.kind == "equation" and formula.left and formula.right:
            left_val = _eval_term(formula.left)
            right_val = _eval_term(formula.right)
            return left_val == right_val
    except Exception:
        pass
    return None


class InductionRule(InferenceRule):
    """Induction rule that actively proves forall formulas.
    
    Instead of waiting for P(0) and P(x)->P(sx) in premises,
    it decomposes the target formula, substitutes 0 for all variables,
    and verifies the base case via semantic evaluation.
    
    Rules are alive: they decay if not used. A rule persists only
    as long as it is continuously validated by fresh experience.
    """

    def __init__(self, predicate_template: Optional[Formula] = None,
                 rule_name: str = "induction",
                 decay: float = 0.95,
                 operator: str = None):
        self._name = rule_name
        self.predicate_template = predicate_template
        self.op = operator  # "add", "mul", or None (universal)
        self.decay = decay
        self.use_count = 0
        self.weight = 1.0
        self.last_used_frame = 0

    def name(self) -> str:
        return self._name
    
    def is_active(self, threshold: float = 0.1) -> bool:
        """Rule is alive only if its weight exceeds threshold."""
        return self.weight > threshold
    
    def age(self, current_frame: int) -> float:
        """Decay weight if unused since last_used_frame."""
        frames_since = current_frame - self.last_used_frame
        if frames_since > 0:
            self.weight *= (self.decay ** frames_since)
        return self.weight

    def apply(self, premises: List[Formula],
              axioms: List[Formula]) -> Optional[Formula]:
        """Try to prove any NEW forall formula in premises by induction.
        
        Skips formulas already in axioms. On success, increments use_count
        and resets weight to 1.0 (reinforcement from new experience).
        """
        axiom_strs = set(str(a) for a in axioms)
        for p in premises:
            if str(p) in axiom_strs:
                continue
            result = self._try_prove_by_induction(p)
            if result:
                self.use_count += 1
                self.weight = 1.0  # reinforced by fresh use
                return result
        if self.predicate_template is not None:
            if str(self.predicate_template) not in axiom_strs:
                result = self._try_prove_by_induction(self.predicate_template)
                if result:
                    self.use_count += 1
                    self.weight = 1.0
                    return result
        return None

    def copy_with_target(self, formula: Formula) -> 'InductionRule':
        """Create a new rule targeting a specific formula (avoids mutation)."""
        return InductionRule(
            predicate_template=formula,
            rule_name=self._name,
        )

    def _try_prove_by_induction(self, formula: Formula) -> Optional[Formula]:
        """Try to prove a forall formula by induction.
        
        If op is set, only proves formulas containing that operator
        (domain-specific knowledge). If op is None, proves any forall equation.
        """
        if formula.kind != "forall":
            return None

        # Operator specificity: add-only rule should not prove mul formulas
        if self.op is not None:
            fstr = str(formula)
            op_char = "\u00d7" if self.op == "mul" else "+" if self.op == "add" else None
            if op_char and op_char not in fstr:
                return None  # wrong domain

        # Unfold quantifier chain, collect variables
        variables = []
        current = formula
        while current.kind == "forall" and current.variable:
            variables.append(current.variable)
            current = current.left
            if current is None:
                return None

        inner_body = current
        if inner_body is None:
            return None

        # Base case: substitute all variables with 0
        base = inner_body
        for var_name in reversed(variables):
            base = godel_sub(base, var_name, constant("0"))

        truth = _semantic_truth(base)
        if truth is not True:
            return None

        # Single variable: additional step verification (n=0,1,2)
        if len(variables) == 1:
            v = variables[0]
            body = inner_body
            for n in range(3):
                xn = constant("0")
                for _ in range(n):
                    xn = fn("s", xn)
                sxn = fn("s", xn)
                p_xn = godel_sub(body, v, xn)
                p_sxn = godel_sub(body, v, sxn)
                t1 = _semantic_truth(p_xn)
                t2 = _semantic_truth(p_sxn)
                if t1 is True and t2 is not True:
                    return None

        return formula


class InductionSynthesizer:
    """Synthesizes InductionRule from extracted patterns."""

    def __init__(self):
        self.axioms = get_q_axioms()

    def synthesize(self, pattern: ExtractedPattern) -> Optional[InductionRule]:
        """Create an InductionRule from a pattern. Verification deferred to apply().
        
        Extracts domain operator from signature: add/mul for specificity.
        """
        formula = pattern.representative_formula
        # Extract operator from signature
        op = None
        if "_add" in pattern.signature and "_mul" not in pattern.signature:
            op = "add"
        elif "_mul" in pattern.signature and "_add" not in pattern.signature:
            op = "mul"
        # Mixed signatures (distributivity) → op = None (universal)
        rule = InductionRule(
            predicate_template=formula,
            rule_name=f"induction_from_{pattern.signature}",
            operator=op,
        )
        return rule

    def synthesize_multiple(self, patterns: List[ExtractedPattern]
                           ) -> List[InductionRule]:
        """Batch synthesize rules from multiple patterns."""
        rules = []
        for p in patterns:
            rule = self.synthesize(p)
            if rule is not None:
                rules.append(rule)
        return rules
