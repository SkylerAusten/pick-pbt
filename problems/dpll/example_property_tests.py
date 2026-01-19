
from __future__ import annotations

from itertools import product
from pathlib import Path
from typing import List

import hypothesis.strategies as st
from hypothesis import given, settings

try:
	# When running `pytest` from repo root.
	from problems.dpll.implementation import (
		Literal,
		dpll,
		evaluate_cnf,
		is_satisfiable,
		load_instances,
		make_cnf,
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
	)


HERE = Path(__file__).resolve().parent


def _vars_in_cnf(cnf) -> List[int]:
	vs: set[int] = set()
	for clause in cnf:
		for lit in clause:
			vs.add(lit.var)
	return sorted(vs)


def _bruteforce_sat(cnf) -> bool:
	# Any empty clause is an immediate contradiction.
	if any(len(clause) == 0 for clause in cnf):
		return False
	vars_ = _vars_in_cnf(cnf)
	if not vars_:
		# With no variables and no empty clause, the only satisfiable CNF is the empty CNF.
		return len(cnf) == 0
	if len(vars_) > 10:
		raise ValueError(f"Too many vars for brute force: {len(vars_)}")
	for values in product([False, True], repeat=len(vars_)):
		model = dict(zip(vars_, values))
		if evaluate_cnf(cnf, model):
			return True
	return False


@st.composite
def cnf_strategy(draw):
	"""Generate small random CNFs where brute-force is feasible."""
	n_vars = draw(st.integers(min_value=0, max_value=6))
	n_clauses = draw(st.integers(min_value=0, max_value=10))

	# Variable IDs include 0..n_vars-1 (so 0 is common).
	var_ids = list(range(n_vars))

	clauses = []
	for _ in range(n_clauses):
		# Allow empty clauses sometimes to exercise UNSAT quickly.
		k = draw(st.integers(min_value=0, max_value=4))
		lits = []
		for _ in range(k):
			if not var_ids:
				break
			v = draw(st.sampled_from(var_ids))
			neg = draw(st.booleans())
			lits.append(Literal(v, neg))
		clauses.append(lits)

	return make_cnf(clauses)


@given(cnf_strategy())
@settings(max_examples=200, deadline=None)
def test_dpll_matches_bruteforce_oracle_on_small_random_cnfs(cnf) -> None:
	expected = _bruteforce_sat(cnf)
	got = is_satisfiable(cnf)
	assert got == expected


@given(cnf_strategy())
@settings(max_examples=200, deadline=None)
def test_dpll_model_is_sound_if_returned(cnf) -> None:
	model = dpll(cnf)
	if model is not None:
		assert evaluate_cnf(cnf, model)


@given(cnf_strategy())
@settings(max_examples=200, deadline=None)
def test_satisfiability_invariant_under_clause_and_literal_reordering(cnf) -> None:
	# Reorder clauses
	clauses = list(cnf)
	clauses_reordered = tuple(reversed(clauses))

	# Reorder literals within each clause (frozenset loses order, but we can
	# rebuild clauses to ensure we're not relying on object identity).
	rebuilt = make_cnf([list(clause) for clause in clauses_reordered])

	assert is_satisfiable(cnf) == is_satisfiable(rebuilt)


@given(st.integers(min_value=1, max_value=5))
@settings(max_examples=20, deadline=None)
def test_loaded_small_instances_are_consistent_with_dpll(count: int) -> None:
	instances = load_instances(HERE / "small_instances.txt")
	assert len(instances) >= count

	for cnf in instances[:count]:
		model = dpll(cnf)
		if model is not None:
			assert evaluate_cnf(cnf, model)


@given(st.integers(min_value=1, max_value=2))
@settings(max_examples=5, deadline=None)
def test_loaded_big_instances_smoke(count: int) -> None:
	# Keep this very light: big instances may be slow.
	instances = load_instances(HERE / "big_instances.txt")
	assert len(instances) >= count

	for cnf in instances[:count]:
		model = dpll(cnf)
		if model is not None:
			assert evaluate_cnf(cnf, model)


if __name__ == "__main__":
	import sys
	import pytest

	raise SystemExit(pytest.main([str(Path(__file__).resolve())] + sys.argv[1:]))
