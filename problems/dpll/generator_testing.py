
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import hypothesis.strategies as st
from hypothesis import given, settings

try:
	# When running from repo root.
	from problems.dpll.implementation import Literal, dpll, evaluate_cnf, make_cnf
except ImportError:  # pragma: no cover
	# When running with cwd set to this directory.
	from implementation import Literal, dpll, evaluate_cnf, make_cnf  # type: ignore


def _fmt_cnf(cnf) -> str:
	return "[" + ", ".join("{" + ", ".join(sorted(str(l) for l in clause)) + "}" for clause in cnf) + "]"


@dataclass(frozen=True)
class SatInstance:
	cnf: tuple[frozenset[Literal], ...]
	witness: Dict[int, bool]


@st.composite
def satisfiable_cnf(draw) -> SatInstance:
	"""Generate a CNF that is guaranteed SAT by construction.

	We first generate a random witness assignment, then generate each clause so
	that at least one literal is True under the witness.
	"""
	n_vars = draw(st.integers(min_value=1, max_value=8))
	vars_ = list(range(n_vars))

	# Witness assignment (include var 0 frequently).
	witness = {v: draw(st.booleans()) for v in vars_}

	n_clauses = draw(st.integers(min_value=1, max_value=12))
	clauses: List[List[Literal]] = []

	for _ in range(n_clauses):
		k = draw(st.integers(min_value=1, max_value=min(4, len(vars_))))
		chosen_vars = draw(
			st.lists(st.sampled_from(vars_), min_size=k, max_size=k, unique=True)
		)

		# Build literals, then force at least one literal to be True under witness.
		lits: List[Literal] = []
		for v in chosen_vars:
			neg = draw(st.booleans())
			lits.append(Literal(v, neg))

		force_idx = draw(st.integers(min_value=0, max_value=len(lits) - 1))
		v = lits[force_idx].var
		# Choose polarity so that the selected literal is True.
		lits[force_idx] = Literal(v, negated=not witness[v])

		clauses.append(lits)

	cnf = make_cnf(clauses)
	return SatInstance(cnf=cnf, witness=witness)


@st.composite
def unsatisfiable_cnf(draw):
	"""Generate a CNF that is guaranteed UNSAT by construction.

	Core unsat kernel: (x) AND (¬x).
	Optionally add extra clauses (which cannot restore satisfiability).
	"""
	n_vars = draw(st.integers(min_value=1, max_value=8))
	vars_ = list(range(n_vars))

	v = draw(st.sampled_from(vars_))
	clauses: List[List[Literal]] = [[Literal(v, False)], [Literal(v, True)]]

	# Add some extra random clauses.
	extra = draw(st.integers(min_value=0, max_value=8))
	for _ in range(extra):
		k = draw(st.integers(min_value=1, max_value=min(4, len(vars_))))
		chosen_vars = draw(
			st.lists(st.sampled_from(vars_), min_size=k, max_size=k, unique=True)
		)
		lits = [Literal(var, draw(st.booleans())) for var in chosen_vars]
		clauses.append(lits)

	return make_cnf(clauses)


# -----------------------------
# Two PBT functions
# -----------------------------


@given(satisfiable_cnf())
@settings(max_examples=50, deadline=None, print_blob=True)
def pbt_inputs_that_pass(inst: SatInstance) -> None:
	"""Generate SAT inputs; DPLL should return a satisfying model."""
	print("\nSAT CNF:", _fmt_cnf(inst.cnf))
	print("Witness (constructor):", inst.witness)

	model = dpll(inst.cnf)
	print("DPLL model:", model)

	assert model is not None
	assert evaluate_cnf(inst.cnf, model)


@given(unsatisfiable_cnf())
@settings(max_examples=50, deadline=None, print_blob=True)
def pbt_inputs_that_fail(cnf) -> None:
	"""Generate UNSAT inputs; DPLL should return None."""
	print("\nUNSAT CNF:", _fmt_cnf(cnf))

	model = dpll(cnf)
	print("DPLL model:", model)

	assert model is None


if __name__ == "__main__":
	# Running this file directly will execute both property tests.
	# Note: these print a lot by design.
	print("Running SAT generator PBT (expected to PASS)...")
	pbt_inputs_that_pass()
	print("\nRunning UNSAT generator PBT (expected to FAIL satisfiable, i.e. return None)...")
	pbt_inputs_that_fail()
