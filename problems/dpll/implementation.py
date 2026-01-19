from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import (
    Dict,
    FrozenSet,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

# -----------------------------
# Data types
# -----------------------------
Var = int


@dataclass(frozen=True, order=True)
class Literal:
    """A propositional literal.

    Note on variable 0:
      The instance files in this repo include literals like "-0".
      In Python, int("-0") == 0, so you cannot represent "-0" with
      a plain negative integer. This class preserves the sign.
    """

    var: Var
    negated: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.var, int):
            raise TypeError(f"var must be int, got {type(self.var).__name__}")
        if self.var < 0:
            raise ValueError("var must be >= 0")

    def negate(self) -> "Literal":
        return Literal(self.var, not self.negated)

    def __str__(self) -> str:
        return f"-{self.var}" if self.negated else str(self.var)


LiteralLike = Union[Literal, str, int]
Clause = FrozenSet[Literal]
CNF = Tuple[Clause, ...]
Model = Dict[Var, bool]


# -----------------------------
# Parsing / normalization
# -----------------------------
def parse_literal(x: LiteralLike) -> Literal:
    """Parse a literal from Literal / str token / int.

    Supported forms:
      - Literal(var, negated)
      - str: "3", "-3", "-0"
      - int: 3, -3  (NOTE: -0 cannot be represented as an int)
    """
    if isinstance(x, Literal):
        return x

    if isinstance(x, int):
        if x < 0:
            return Literal(-x, True)
        return Literal(x, False)

    if isinstance(x, str):
        s = x.strip()
        if not s:
            raise ValueError("Empty literal token")
        if s[0] == "-":
            v = s[1:]
            if not v.isdigit():
                raise ValueError(f"Invalid literal token: {x!r}")
            return Literal(int(v), True)
        if not s.isdigit():
            raise ValueError(f"Invalid literal token: {x!r}")
        return Literal(int(s), False)

    raise TypeError(f"Unsupported literal type: {type(x).__name__}")


def make_clause(lits: Iterable[LiteralLike]) -> Clause:
    clause = frozenset(parse_literal(l) for l in lits)
    return clause


def make_cnf(clauses: Iterable[Iterable[LiteralLike] | Clause]) -> CNF:
    normalized: List[Clause] = []
    for c in clauses:
        if isinstance(c, frozenset):
            normalized.append(c)
        else:
            normalized.append(make_clause(c))
    return tuple(normalized)


def parse_instances_text(text: str) -> List[CNF]:
    """Parse a DIMACS-ish instance file format used in this repo.

    - Each non-empty line is a clause.
    - Clauses are space-separated literal tokens like "2 -0 4".
    - Blank lines separate different SAT problems.
    """
    problems: List[List[Clause]] = []
    current: List[Clause] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                problems.append(current)
                current = []
            continue
        tokens = line.split()
        current.append(make_clause(tokens))

    if current:
        problems.append(current)

    return [make_cnf(p) for p in problems]


def load_instances(path: Union[str, Path]) -> List[CNF]:
    p = Path(path)
    return parse_instances_text(p.read_text(encoding="utf-8"))


# -----------------------------
# Core DPLL
# -----------------------------


def _apply_literal(formula: CNF, lit_true: Literal) -> Optional[CNF]:
    """Simplify CNF given that `lit_true` is assigned True.

    - Remove clauses satisfied by lit_true
    - Remove negation of lit_true from remaining clauses
    - If any clause becomes empty, return None (conflict)
    """
    lit_false = lit_true.negate()
    new_clauses: List[Clause] = []

    for clause in formula:
        if lit_true in clause:
            continue
        if lit_false in clause:
            reduced = frozenset(l for l in clause if l != lit_false)
            if len(reduced) == 0:
                return None
            new_clauses.append(reduced)
        else:
            new_clauses.append(clause)

    return tuple(new_clauses)


def _assign(model: Model, lit_true: Literal) -> bool:
    """Add the implied variable assignment to model.

    Returns False if this contradicts an existing assignment.
    """
    value = not lit_true.negated
    existing = model.get(lit_true.var)
    if existing is None:
        model[lit_true.var] = value
        return True
    return existing == value


def _find_unit_literal(formula: CNF) -> Optional[Literal]:
    for clause in formula:
        if len(clause) == 1:
            return next(iter(clause))
    return None


def _unit_propagate(formula: CNF, model: Model) -> Optional[CNF]:
    while True:
        unit = _find_unit_literal(formula)
        if unit is None:
            return formula
        if not _assign(model, unit):
            return None
        formula = _apply_literal(formula, unit)
        if formula is None:
            return None


def _pure_literals(formula: CNF, model: Model) -> List[Literal]:
    polarity: Dict[Var, set[bool]] = {}
    for clause in formula:
        for lit in clause:
            if lit.var in model:
                continue
            polarity.setdefault(lit.var, set()).add(lit.negated)

    pures: List[Literal] = []
    for var, negs in polarity.items():
        if len(negs) == 1:
            (negated,) = tuple(negs)
            pures.append(Literal(var, negated))
    return pures


def _eliminate_pure_literals(formula: CNF, model: Model) -> Optional[CNF]:
    while True:
        pures = _pure_literals(formula, model)
        if not pures:
            return formula
        for lit in pures:
            if not _assign(model, lit):
                return None
            formula = _apply_literal(formula, lit)
            if formula is None:
                return None


def _choose_branch_literal(formula: CNF, model: Model) -> Literal:
    """Pick a literal to branch on (deterministic heuristic).

    Strategy:
      - Pick a clause with the smallest size (encourages unit propagation).
      - From that clause, pick the smallest literal (stable ordering).
    """
    # Prefer clauses that still contain an unassigned variable.
    candidate_clauses: List[Clause] = []
    for clause in formula:
        if any(l.var not in model for l in clause):
            candidate_clauses.append(clause)
    if not candidate_clauses:
        # Should be rare; fall back to any literal.
        clause = min(formula, key=len)
        return min(clause)

    clause = min(candidate_clauses, key=len)
    # Only consider unassigned vars
    unassigned = [l for l in clause if l.var not in model]
    return min(unassigned)


def dpll(
    formula: Iterable[Iterable[LiteralLike] | Clause] | CNF,
    model: Optional[Mapping[Var, bool]] = None,
) -> Optional[Model]:
    """Solve SAT for a CNF formula using the DPLL algorithm.

    Args:
            formula:
                    A CNF formula.
                    Preferred representation is a tuple of frozensets of `Literal`.
                    Convenience forms are accepted: e.g. [["-0", "1"], ["0"]].
            model:
                    Optional partial assignment {var: bool} to start from.

    Returns:
            A satisfying assignment as a dict {var: bool}, or None if UNSAT.
    """
    cnf = formula if isinstance(formula, tuple) else make_cnf(formula)
    current_model: Model = dict(model) if model is not None else {}

    # Apply any provided partial model to simplify upfront.
    for var, value in list(current_model.items()):
        lit_true = Literal(var, negated=not value)
        cnf = _apply_literal(cnf, lit_true)
        if cnf is None:
            return None

    # Base cases
    if not cnf:
        return current_model
    if any(len(c) == 0 for c in cnf):
        return None

    # Deterministic simplifications (loop because they can enable each other).
    while True:
        before = cnf
        cnf = _unit_propagate(cnf, current_model)
        if cnf is None:
            return None
        cnf = _eliminate_pure_literals(cnf, current_model)
        if cnf is None:
            return None

        if not cnf:
            return current_model
        if cnf == before:
            break

    # Branching
    lit = _choose_branch_literal(cnf, current_model)

    # Try True branch first (i.e., set this literal to True), then backtrack.
    for branch_lit in (lit, lit.negate()):
        new_model: Model = dict(current_model)
        if not _assign(new_model, branch_lit):
            continue
        new_cnf = _apply_literal(cnf, branch_lit)
        if new_cnf is None:
            continue
        result = dpll(new_cnf, new_model)
        if result is not None:
            return result

    return None


def is_satisfiable(formula: Iterable[Iterable[LiteralLike] | Clause] | CNF) -> bool:
    """Return True iff the CNF formula is satisfiable."""
    return dpll(formula) is not None


def evaluate_cnf(
    formula: Iterable[Iterable[LiteralLike] | Clause] | CNF, model: Mapping[Var, bool]
) -> bool:
    """Evaluate a CNF formula under a (possibly partial) assignment.

    Unassigned variables are treated as "unknown"; a clause with all literals
    false/unknown is considered unsatisfied.
    """
    cnf = formula if isinstance(formula, tuple) else make_cnf(formula)
    for clause in cnf:
        clause_sat = False
        for lit in clause:
            if lit.var not in model:
                continue
            val = model[lit.var]
            lit_val = (not val) if lit.negated else val
            if lit_val:
                clause_sat = True
                break
        if not clause_sat:
            return False
    return True
