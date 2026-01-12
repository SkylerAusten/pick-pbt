
# pick-pbt

Small playground repo for generating and analyzing property-based tests (PBT) with Hypothesis, driven primarily from notebooks.

## Repository layout

Top-level components (excluding anything ignored by `.gitignore`):

- `pick_pbt.ipynb`: Main notebook that builds LLM prompts, calls the LLM, and records run outputs.
- `pick_pbt_testing.ipynb`: Scratch/testing notebook.
- `requirements.txt`: Python dependencies.

### Problem directories

Each folder like `roman_numerals/`, `alien_numerals/`, `tim_card_game/`, `toposort/`, `dpll/`, etc. represents a *problem* the tool can target.

The standard contents for each problem directory are:

- `description.md` — an explanation of the problem/function.
- `labeled_spec.xml` — the spec provided to an LLM call, broken down into XML tags.
- `freeform_spec.md` — a freeform open-response text spec.
- `implementation.py` — an implementation of the actual problem function(s) in Python.
- `example_unit_tests.py` — example unit tests of the implementation (written by the repo author, not the tool).
- `example_property_tests.py` — example property-based tests of the implementation (written by the repo author, not the tool).

Notes:

- Not every problem directory contain every file yet while the repo evolves.

### Supporting modules

- `hypothesis_pick/`: Helper utilities for analyzing and comparing candidate properties.

### Output

- `logs/`: Per-run JSON logs produced by the notebook pipeline. Filenames are `problem_timestamp.json`.
- 
## Quick start

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Open `pick_pbt.ipynb` and configure settings in cell 2.
4. Run cells top-to-bottom.