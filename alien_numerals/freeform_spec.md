# Specification: Vesicular Numeral System

## 1. Mathematical Definition

The Vesicular Numeral System is a **non-positional, topological, base-6 (heximal)** notation system. Unlike standard positional notation where value is derived from a digit's linear index (e.g., 10^0, 10^1, 10^2), value in this system is derived from **nesting depth**.

The system is **additive**, meaning the total value of a number is the sum of all individual unit symbols, modified by their enclosing delimiters.

### 1.1 Core Symbols

* **Unit (•):** Represents a base value of **1**.
* **Multiplier ( ... ):** A recursive container that multiplies the value of its contents by **6**.
* **Divisor C( ... ):** A recursive container that divides the value of its contents by **6**.

### 1.2 Evaluation Rules

The value **V** of a given string is calculated as:

> **V = Sum of (1 * 6^Di)**

Where:

* **n** is the total count of Unit symbols (•) in the string.
* **Di** is the **Net Depth** of the *i*-th Unit.
* Net Depth is calculated by incrementing for every enclosing Multiplier and decrementing for every enclosing Divisor.

**Topological Equivalence:**
Because the system is additive, the order of symbols does not affect the value, provided their nesting depth remains constant. For example, `(•) •` is mathematically equivalent to `• (•)`.

---

## 2. Function Specification: `to_vesicular`

### 2.1 Purpose

Converts a base-10 real number (integer or floating-point) into its canonical Vesicular string representation.

### 2.2 Inputs

* **number** (Float/Integer): The base-10 value to be converted.
* **precision** (Integer, Default=6): The maximum nesting depth for the fractional component to prevent infinite recursion on irrational numbers.

### 2.3 Logic Flow

1. **Zero Handling:** If the input is exactly `0`, return the null identifier `()`.
2. **Sign Handling:** If the input is negative, format the result within a negative indicator (e.g., `ANTI[...]`) and process the absolute value.
3. **Decomposition:** Separate the number into its integer part and fractional part.
4. **Integer Processing (Positive Powers):**
* Perform a standard base-6 conversion algorithm on the integer part.
* For each coefficient **c** at power **p** (where c > 0):
* Generate **c** Unit symbols.
* Enclose these Units in **p** layers of Multiplier brackets `( )`.


* Prefix these terms to the result string.


5. **Fractional Processing (Negative Powers):**
* Iteratively multiply the fractional remainder by 6.
* Extract the integer part of the result as the coefficient **c**.
* For each coefficient **c** at depth **d** (where c > 0):
* Generate **c** Unit symbols.
* Enclose these Units in **d** layers of Divisor brackets `C( )`.


* Append these terms to the result string.
* Terminate if the remainder is 0 or **precision** limit is reached.


6. **Output:** Return the concatenated string of all terms.

---

## 3. Function Specification: `from_vesicular`

### 3.1 Purpose

Parses a Vesicular string to reconstruct the base-10 real number value. This function must handle arbitrary nesting and topological cancellation.

### 3.2 Inputs

* **alien_str** (String): The Vesicular notation string to be parsed.

### 3.3 Logic Flow

The parsing utilizes a **Stack-Based State Machine** to track the current multiplicative context.

1. **Initialization:**
* `total_value` = 0.
* `stack` = `[1.0]` (The base multiplier of the "universe" is 1).
* `current_multiplier` = 1.0.


2. **Token Processing:** Iterate through the string character by character:
* **Open Multiplier (:**
* Push `current_multiplier` to stack.
* Update `current_multiplier` = `current_multiplier * 6`.


* **Open Divisor C(:**
* Push `current_multiplier` to stack.
* Update `current_multiplier` = `current_multiplier / 6`.


* **Close Container ):**
* Pop the last value from the stack.
* Restore `current_multiplier` to the popped value.


* **Unit •:**
* Add `current_multiplier` to `total_value`.




3. **Cancellation Handling:**
* The logic must inherently support topological cancellation. A sequence representing `Multiplier( Divisor( Unit ) )` results in a net multiplier of **1** (6 * 1/6), effectively cancelling the containers.


4. **Output:** Return `total_value`.

---

## 4. Edge Case & Constraint Handling

* **Float Precision:** Due to binary floating-point architecture, conversion of fractions (e.g., 1/6) may result in epsilon errors (0.999... vs 1.0). Implementations must utilize rounding or epsilon comparisons when determining integer coefficients.
* **Infinite Fractions:** Irrational numbers or repeating decimals in base-6 (like 1/5) must be truncated according to the **precision** argument in `to_vesicular`.
* **Malformed Strings:** The `from_vesicular` function should be robust against unbalanced parenthesis by ignoring excess closing tags, though strict validation is optional depending on implementation requirements.