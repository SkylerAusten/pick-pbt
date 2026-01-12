"""hypothesis-pick

An add-on to Hypothesis for comparing multiple boolean predicates.

Note:
    This package's core utilities require the third-party `hypothesis` dependency.
    Some submodules (e.g., `hypothesis_pick.toposort`) are usable without it.
"""

from __future__ import annotations

from typing import Any

__version__ = "0.1.0"


_CORE_EXPORTS = {
    "find_disagreements",
    "disagreement_generator",
    "infer_implications",
    "find_equivalence_classes",
    "find_stronger_weaker",
    "PredicateResult",
    "ImplicationResult",
}


def __getattr__(name: str) -> Any:
    if name not in _CORE_EXPORTS:
        raise AttributeError(name)

    try:
        from hypothesis_pick.core import (  # type: ignore
            find_disagreements,
            disagreement_generator,
            infer_implications,
            find_equivalence_classes,
            find_stronger_weaker,
            PredicateResult,
            ImplicationResult,
        )
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "hypothesis_pick core features require the 'hypothesis' package. "
            "Install dependencies from requirements.txt to use these exports."
        ) from exc

    globals().update(
        {
            "find_disagreements": find_disagreements,
            "disagreement_generator": disagreement_generator,
            "infer_implications": infer_implications,
            "find_equivalence_classes": find_equivalence_classes,
            "find_stronger_weaker": find_stronger_weaker,
            "PredicateResult": PredicateResult,
            "ImplicationResult": ImplicationResult,
        }
    )
    return globals()[name]


__all__ = ["__version__", *_CORE_EXPORTS]
