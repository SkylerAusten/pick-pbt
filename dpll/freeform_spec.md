Here is the revised specification using standard plain text. I have removed all mathematical symbols, LaTeX formatting, and special characters to ensure it is completely copy-paste friendly.

# DPLL Algorithm Specification

## 1. Introduction

The DPLL (Davis-Putnam-Logemann-Loveland) algorithm is a recursive search procedure used to determine if a logical formula is "Satisfiable." Satisfiable means there is a way to set variables to True or False so that the entire statement evaluates to True.

The algorithm works on formulas in "Conjunctive Normal Form" (CNF).

## 2. Definitions and Data Representation

To understand the functions below, the following terms are used:

* **Literal:** A variable (e.g., A) or its negation (e.g., NOT A).
* **Clause:** A collection of literals combined with OR logic. For the clause to be true, at least one literal inside it must be true.
* **Formula:** A collection of clauses combined with AND logic. For the formula to be true, every single clause must be true.
* **Empty Clause:** A clause that has no literals left in it. This represents a conflict (False).
* **Empty Formula:** A formula that has no clauses left in it. This represents success (True).
* **Model:** The current list of variables and their assigned values (True/False).

## 3. Main Algorithm Logic

The main function is recursive. It takes the current Formula and the current Model as input.

### Step 1: Base Case Checks

1. **Check for Success:** If the Formula is empty (contains no clauses), return **True**. The current Model is a valid solution.
2. **Check for Failure:** If the Formula contains an Empty Clause, return **False**. This path leads to a contradiction.

### Step 2: Simplification (Deterministic)

Before guessing, the algorithm applies logical rules to reduce the problem size.

1. **Unit Propagation:** Locate clauses that have only one literal. Since a clause must be true, this literal *must* be assigned a value to make it true. Apply this assignment and simplify the formula.
2. **Pure Literal Elimination:** Locate variables that appear with the same "polarity" (always positive or always negative) in every clause where they exist. Assign the value that makes them true and simplify the formula.

*Note: If simplifications result in an Empty Clause, return False immediately.*

### Step 3: Branching (Non-Deterministic)

If the formula is not solved and no simplifications are possible:

1. **Pick a Variable:** Select an unassigned variable (P) using a heuristic function.
2. **Branch 1:** Assume P is **True**. Simplify the formula and recursively call the main function.
* If this returns True, pass the result up (Success).


3. **Branch 2:** If Branch 1 failed, backtrack. Assume P is **False**. Simplify the formula and recursively call the main function.
4. **Result:** If both branches return False, the formula is Unsatisfiable.

---

## 4. Function Descriptions

The algorithm relies on the following specific subroutines.

### Function: Unit Propagate

**Goal:** Identify forced moves where a clause has only one option left.

**Process:**

1. Scan the formula for any clause containing exactly one literal.
2. If found, add that literal to the Model.
3. Call the **Simplify** function using this literal.
4. Repeat this process until no unit clauses remain.
5. Return the updated Formula and Model.

### Function: Pure Literal Elimination

**Goal:** Identify variables that can be assigned without risk of causing a conflict.

**Process:**

1. Scan the entire formula.
2. Identify "Pure" literals. A literal is pure if its negation does not appear anywhere in the remaining formula.
* *Example:* If "A" appears in three clauses, but "NOT A" appears in zero clauses, "A" is pure.


3. Assign these literals to True.
4. Call the **Simplify** function for each pure literal found.
5. Return the updated Formula and Model.

### Function: Simplify

**Goal:** Update the formula based on a new truth assignment.

**Input:** The Formula and a specific Literal (L) that has just been set to True.

**Process:**

1. **Remove Satisfied Clauses:** Look at every clause in the formula. If a clause contains L, remove the entire clause from the formula. (Because L is True, the clause is now True and effectively "done").
2. **Remove False Literals:** Look at the remaining clauses. If a clause contains the negation of L (NOT L), remove just that literal from the clause. (Because L is True, NOT L is False. A False literal contributes nothing to an OR clause).
3. **Conflict Check:** If removing "NOT L" from a clause results in that clause becoming empty, the function notes that a conflict has occurred.

### Function: Choose Literal

**Goal:** Decide which variable to guess next when branching is required.

**Process:**

1. Identify all variables that are not yet in the Model.
2. Select one based on a strategy:
* **Simple Strategy:** Pick the first variable available.
* **Frequency Strategy:** Pick the variable that appears most often in the remaining clauses.
* **Smallest Clause Strategy:** Pick a variable that appears in the shortest clauses (to encourage Unit Propagation in the next step).


3. Return the selected variable.