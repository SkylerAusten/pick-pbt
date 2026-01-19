from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import Dict, Iterable, Mapping

import pytest

try:
    # When running `pytest` from repo root.
    from problems.dpll.implementation import (
        Literal,
        dpll,
        evaluate_cnf,
        is_satisfiable,
        load_instances,
        make_cnf,
        parse_literal,
    )
except ImportError:  # pragma: no cover
    # When running tests with cwd set to this directory.
    from implementation import (  # type: ignore
        Literal,
        dpll,
        evaluate_cnf,
        is_satisfiable,
        load_instances,
        make_cnf,
        parse_literal,
    )


HERE = Path(__file__).resolve().parent


def _vars_in_cnf(cnf) -> set[int]:
    vs: set[int] = set()
    for clause in cnf:
        for lit in clause:
            vs.add(lit.var)
    return vs


def _bruteforce_sat(cnf) -> bool:
    """Brute-force SAT oracle for small formulas."""
    vars_ = sorted(_vars_in_cnf(cnf))
    if not vars_:
        return True

    # Keep this only for truly small problems.
    if len(vars_) > 12:
        raise ValueError(f"Too many vars for brute force: {len(vars_)}")

    for values in product([False, True], repeat=len(vars_)):
        model = dict(zip(vars_, values))
        if evaluate_cnf(cnf, model):
            return True
    return False


def test_parse_literal_negative_zero_is_distinct() -> None:
    neg0 = parse_literal("-0")
    pos0 = parse_literal("0")

    assert neg0 == Literal(0, True)
    assert pos0 == Literal(0, False)
    assert neg0 != pos0
    assert str(neg0) == "-0"
    assert str(pos0) == "0"


def test_empty_formula_is_satisfiable() -> None:
    cnf = make_cnf([])
    model = dpll(cnf)
    assert model == {}
    assert is_satisfiable(cnf) is True


def test_formula_with_empty_clause_is_unsat() -> None:
    cnf = (frozenset(),)
    assert dpll(cnf) is None
    assert is_satisfiable(cnf) is False


def test_small_instances_match_bruteforce_oracle() -> None:
    instances_path = HERE / "small_instances.txt"
    instances = load_instances(instances_path)
    assert instances, "Expected at least one CNF instance in small_instances.txt"

    for idx, cnf in enumerate(instances, 1):
        expected = _bruteforce_sat(cnf)
        got_model = dpll(cnf)
        got_sat = got_model is not None

        assert got_sat == expected, f"Mismatch on instance #{idx}"
        if got_model is not None:
            assert evaluate_cnf(
                cnf, got_model
            ), f"Returned model invalid for instance #{idx}"


@pytest.mark.parametrize("count", [1, 2])
def test_big_instances_smoke_models_validate(count: int) -> None:
    """Smoke test on big instances: if we produce a model, it must satisfy the CNF.

    We intentionally do not assert SAT/UNSAT here because big instances are too
    large for a brute-force oracle.
    """
    instances_path = HERE / "big_instances.txt"
    instances = load_instances(instances_path)
    assert len(instances) >= count

    for idx, cnf in enumerate(instances[:count], 1):
        model = dpll(cnf)
        if model is not None:
            assert evaluate_cnf(
                cnf, model
            ), f"Returned model invalid for big instance #{idx}"


if __name__ == "__main__":
    import sys

    raise SystemExit(pytest.main([str(Path(__file__).resolve())] + sys.argv[1:]))
