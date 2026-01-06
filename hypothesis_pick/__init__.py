"""
hypothesis-pick: An add-on to Hypothesis for comparing multiple boolean predicates.

This module provides tools to:
1. Find "interesting" inputs where predicates disagree.
2. Build a generator for such disagreement inputs.
3. Infer implication relationships between predicates (p_i ⇒ p_j).
4. Find equivalence classes and stronger/weaker relations.
"""

from hypothesis_pick.core import (
    find_disagreements,
    disagreement_generator,
    infer_implications,
    find_equivalence_classes,
    find_stronger_weaker,
    PredicateResult,
    ImplicationResult,
)

__all__ = [
    "find_disagreements",
    "disagreement_generator",
    "infer_implications",
    "find_equivalence_classes",
    "find_stronger_weaker",
    "PredicateResult",
    "ImplicationResult",
]

__version__ = "0.1.0"
