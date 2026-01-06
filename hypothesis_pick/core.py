"""
Core functionality for comparing boolean predicates using Hypothesis.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from itertools import combinations

from hypothesis import given, settings, Verbosity, Phase
from hypothesis import strategies as st


# Type aliases for clarity
Predicate = Callable[..., bool]


@dataclass
class PredicateResult:
    """Result of predicate evaluation on an input."""
    
    input_value: Any
    results: Dict[str, bool]
    
    def disagreement_pairs(self) -> List[Tuple[str, str]]:
        """Return pairs of predicates that disagree on this input."""
        pairs = []
        names = list(self.results.keys())
        for i, name1 in enumerate(names):
            for name2 in names[i + 1:]:
                if self.results[name1] != self.results[name2]:
                    pairs.append((name1, name2))
        return pairs
    
    def has_disagreement(self) -> bool:
        """Check if any predicates disagree on this input."""
        values = list(self.results.values())
        return len(set(values)) > 1


@dataclass
class ImplicationResult:
    """Result of implication inference between predicates."""
    
    # p_i => p_j: if p_i(x) is True, then p_j(x) is also True
    implications: Dict[str, Set[str]] = field(default_factory=dict)
    # Pairs where no implication holds in either direction
    independent: List[Tuple[str, str]] = field(default_factory=list)
    # Counterexamples: {(p_i, p_j): [inputs where p_i but not p_j]}
    counterexamples: Dict[Tuple[str, str], List[Any]] = field(default_factory=dict)
    
    def implies(self, p_i: str, p_j: str) -> bool:
        """Check if p_i => p_j."""
        return p_j in self.implications.get(p_i, set())
    
    def equivalent(self, p_i: str, p_j: str) -> bool:
        """Check if p_i <=> p_j (mutual implication)."""
        return self.implies(p_i, p_j) and self.implies(p_j, p_i)
    
    def stronger_than(self, p_i: str, p_j: str) -> bool:
        """Check if p_i is strictly stronger than p_j (p_i => p_j but not p_j => p_i)."""
        return self.implies(p_i, p_j) and not self.implies(p_j, p_i)
    
    def weaker_than(self, p_i: str, p_j: str) -> bool:
        """Check if p_i is strictly weaker than p_j (p_j => p_i but not p_i => p_j)."""
        return self.implies(p_j, p_i) and not self.implies(p_i, p_j)


def _get_predicate_name(pred: Predicate, index: int) -> str:
    """Get a name for a predicate, using __name__ if available."""
    if hasattr(pred, '__name__') and pred.__name__ != '<lambda>':
        return pred.__name__
    return f"predicate_{index}"


def _evaluate_predicates(
    predicates: Dict[str, Predicate],
    input_value: Any
) -> PredicateResult:
    """Evaluate all predicates on a given input."""
    results = {}
    for name, pred in predicates.items():
        try:
            results[name] = bool(pred(input_value))
        except Exception:
            # If a predicate raises an exception, treat as False
            results[name] = False
    return PredicateResult(input_value=input_value, results=results)


def find_disagreements(
    predicates: List[Predicate],
    strategy: st.SearchStrategy,
    max_examples: int = 1000,
    predicate_names: Optional[List[str]] = None,
) -> List[PredicateResult]:
    """
    Find inputs where predicates disagree.
    
    Args:
        predicates: List of boolean predicates with the same signature.
        strategy: Hypothesis strategy to generate inputs.
        max_examples: Maximum number of examples to test.
        predicate_names: Optional list of names for the predicates.
    
    Returns:
        List of PredicateResult objects for inputs where predicates disagree.
    """
    if len(predicates) < 2:
        raise ValueError("At least two predicates are required")
    
    # Build name mapping
    if predicate_names is not None:
        if len(predicate_names) != len(predicates):
            raise ValueError("predicate_names must match the number of predicates")
        pred_dict = dict(zip(predicate_names, predicates))
    else:
        pred_dict = {_get_predicate_name(p, i): p for i, p in enumerate(predicates)}
    
    disagreements: List[PredicateResult] = []
    
    @given(strategy)
    @settings(
        max_examples=max_examples,
        database=None,
        verbosity=Verbosity.quiet,
        phases=[Phase.generate],
    )
    def find_disagreement(x: Any) -> None:
        result = _evaluate_predicates(pred_dict, x)
        if result.has_disagreement():
            disagreements.append(result)
    
    find_disagreement()
    return disagreements


def disagreement_generator(
    predicates: List[Predicate],
    strategy: st.SearchStrategy,
    predicate_names: Optional[List[str]] = None,
) -> st.SearchStrategy:
    """
    Build a Hypothesis strategy that generates inputs where predicates disagree.
    
    This uses Hypothesis's filter mechanism to only generate values where
    at least two predicates give different results.
    
    Args:
        predicates: List of boolean predicates with the same signature.
        strategy: Base Hypothesis strategy to generate inputs.
        predicate_names: Optional list of names for the predicates.
    
    Returns:
        A Hypothesis strategy that only generates disagreement inputs.
    """
    if len(predicates) < 2:
        raise ValueError("At least two predicates are required")
    
    # Build name mapping
    if predicate_names is not None:
        if len(predicate_names) != len(predicates):
            raise ValueError("predicate_names must match the number of predicates")
        pred_dict = dict(zip(predicate_names, predicates))
    else:
        pred_dict = {_get_predicate_name(p, i): p for i, p in enumerate(predicates)}
    
    def is_disagreement(x: Any) -> bool:
        result = _evaluate_predicates(pred_dict, x)
        return result.has_disagreement()
    
    return strategy.filter(is_disagreement)


def infer_implications(
    predicates: List[Predicate],
    strategy: st.SearchStrategy,
    max_examples: int = 1000,
    predicate_names: Optional[List[str]] = None,
    collect_counterexamples: bool = True,
    max_counterexamples: int = 5,
) -> ImplicationResult:
    """
    Infer implication relationships between predicates.
    
    For each pair (p_i, p_j), checks if p_i => p_j holds (i.e., whenever
    p_i(x) is True, p_j(x) is also True).
    
    Note: This uses statistical sampling. If an implication holds for all
    sampled inputs, it's considered to hold, but this is not a formal proof.
    
    Args:
        predicates: List of boolean predicates with the same signature.
        strategy: Hypothesis strategy to generate inputs.
        max_examples: Maximum number of examples to test.
        predicate_names: Optional list of names for the predicates.
        collect_counterexamples: Whether to collect counterexamples for
            implications that don't hold.
        max_counterexamples: Maximum number of counterexamples to collect
            per implication.
    
    Returns:
        ImplicationResult with inferred implications and counterexamples.
    """
    if len(predicates) < 2:
        raise ValueError("At least two predicates are required")
    
    # Build name mapping
    if predicate_names is not None:
        if len(predicate_names) != len(predicates):
            raise ValueError("predicate_names must match the number of predicates")
        pred_dict = dict(zip(predicate_names, predicates))
    else:
        pred_dict = {_get_predicate_name(p, i): p for i, p in enumerate(predicates)}
    
    names = list(pred_dict.keys())
    
    # Initialize: assume all implications hold until we find a counterexample
    # potential_implications[p_i] = set of p_j where p_i => p_j might hold
    potential_implications: Dict[str, Set[str]] = {
        name: set(n for n in names if n != name) for name in names
    }
    
    counterexamples: Dict[Tuple[str, str], List[Any]] = {}
    
    @given(strategy)
    @settings(
        max_examples=max_examples,
        database=None,
        verbosity=Verbosity.quiet,
        phases=[Phase.generate],
    )
    def check_implications(x: Any) -> None:
        result = _evaluate_predicates(pred_dict, x)
        
        # For each predicate p_i that is True
        for p_i, val_i in result.results.items():
            if val_i:  # p_i(x) is True
                # Check if p_j is also True for all p_j in potential_implications[p_i]
                for p_j in list(potential_implications[p_i]):
                    if not result.results[p_j]:  # p_j(x) is False
                        # Counterexample found: p_i(x) but not p_j(x)
                        potential_implications[p_i].discard(p_j)
                        
                        if collect_counterexamples:
                            key = (p_i, p_j)
                            if key not in counterexamples:
                                counterexamples[key] = []
                            if len(counterexamples[key]) < max_counterexamples:
                                counterexamples[key].append(x)
    
    check_implications()
    
    # Build the result
    result = ImplicationResult(
        implications=potential_implications,
        counterexamples=counterexamples if collect_counterexamples else {},
    )
    
    # Find independent pairs (no implication in either direction)
    for i, name1 in enumerate(names):
        for name2 in names[i + 1:]:
            if not result.implies(name1, name2) and not result.implies(name2, name1):
                result.independent.append((name1, name2))
    
    return result


def find_equivalence_classes(
    predicates: List[Predicate],
    strategy: st.SearchStrategy,
    max_examples: int = 1000,
    predicate_names: Optional[List[str]] = None,
) -> List[Set[str]]:
    """
    Find equivalence classes of predicates.
    
    Predicates are considered equivalent if they produce the same result
    on all tested inputs.
    
    Args:
        predicates: List of boolean predicates with the same signature.
        strategy: Hypothesis strategy to generate inputs.
        max_examples: Maximum number of examples to test.
        predicate_names: Optional list of names for the predicates.
    
    Returns:
        List of sets, where each set contains names of equivalent predicates.
    """
    if len(predicates) < 2:
        raise ValueError("At least two predicates are required")
    
    impl_result = infer_implications(
        predicates,
        strategy,
        max_examples=max_examples,
        predicate_names=predicate_names,
        collect_counterexamples=False,
    )
    
    # Build name mapping for iteration
    if predicate_names is not None:
        names = predicate_names
    else:
        names = [_get_predicate_name(p, i) for i, p in enumerate(predicates)]
    
    # Use union-find to group equivalent predicates
    parent: Dict[str, str] = {name: name for name in names}
    
    def find(x: str) -> str:
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x: str, y: str) -> None:
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
    
    # Group predicates that are equivalent (mutual implication)
    for i, name1 in enumerate(names):
        for name2 in names[i + 1:]:
            if impl_result.equivalent(name1, name2):
                union(name1, name2)
    
    # Build equivalence classes
    classes: Dict[str, Set[str]] = {}
    for name in names:
        root = find(name)
        if root not in classes:
            classes[root] = set()
        classes[root].add(name)
    
    return list(classes.values())


def find_stronger_weaker(
    predicates: List[Predicate],
    strategy: st.SearchStrategy,
    max_examples: int = 1000,
    predicate_names: Optional[List[str]] = None,
) -> Dict[str, Dict[str, List[str]]]:
    """
    Find stronger and weaker relationships between predicates.
    
    A predicate p_i is stronger than p_j if p_i => p_j but not p_j => p_i.
    A predicate p_i is weaker than p_j if p_j => p_i but not p_i => p_j.
    
    Args:
        predicates: List of boolean predicates with the same signature.
        strategy: Hypothesis strategy to generate inputs.
        max_examples: Maximum number of examples to test.
        predicate_names: Optional list of names for the predicates.
    
    Returns:
        Dictionary mapping predicate names to their stronger and weaker
        relations: {pred_name: {"stronger_than": [...], "weaker_than": [...]}}.
    """
    if len(predicates) < 2:
        raise ValueError("At least two predicates are required")
    
    impl_result = infer_implications(
        predicates,
        strategy,
        max_examples=max_examples,
        predicate_names=predicate_names,
        collect_counterexamples=False,
    )
    
    # Build name mapping for iteration
    if predicate_names is not None:
        names = predicate_names
    else:
        names = [_get_predicate_name(p, i) for i, p in enumerate(predicates)]
    
    result: Dict[str, Dict[str, List[str]]] = {}
    
    for name in names:
        stronger_than = []
        weaker_than = []
        
        for other in names:
            if other == name:
                continue
            if impl_result.stronger_than(name, other):
                stronger_than.append(other)
            elif impl_result.weaker_than(name, other):
                weaker_than.append(other)
        
        result[name] = {
            "stronger_than": stronger_than,
            "weaker_than": weaker_than,
        }
    
    return result
