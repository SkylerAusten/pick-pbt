# Roman Numeral Conversion Specification

## 1. Overview

This document defines the formal specification for the representation of Roman numerals and specifies the logic for the transformation functions `to_numerals` (integer to Roman numeral string) and `from_numerals` (Roman numeral string to integer).

---

## 2. Definitions and Symbols

### 2.1 Basic Symbols

The Roman numeral system is based on seven distinct symbols, each assigned a fixed integer value.

| Symbol | Value |
| --- | --- |
| **I** | 1 |
| **V** | 5 |
| **X** | 10 |
| **L** | 50 |
| **C** | 100 |
| **D** | 500 |
| **M** | 1000 |

### 2.2 Formation Rules

A valid Roman numeral string is formed by combining the basic symbols according to the following rules:

1. **Additive Principle:** When a symbol appears after a symbol of equal or greater value, its value is added to the total.
* *Example:* VI = 5 + 1 = 6


2. **Subtractive Principle:** When a symbol appears before a symbol of greater value, its value is subtracted from the total. This is used to avoid four consecutive identical symbols (e.g., using IV instead of IIII).
* *Example:* IV = 5 - 1 = 4
* *Constraint:* Subtraction is restricted to specific pairs:
* I can be placed before V (4) and X (9).
* X can be placed before L (40) and C (90).
* C can be placed before D (400) and M (900).




3. **Repetition Limit:** The symbols V, L, and D are never repeated. The symbols I, X, C, and M may be repeated up to three times consecutively.
4. **Order of Magnitude:** Numerals are written from highest value (left) to lowest value (right), with the exception of subtractive pairs.

---

## 3. Function Specification: `to_numerals`

### 3.1 Description

Converts a positive integer into its standard Roman numeral string representation.

### 3.2 Inputs

* **Input N:** An integer value.

### 3.3 Pre-conditions

* N must be an integer such that 1 <= N <= 3999.
* (Note: The upper bound is traditionally 3999 because standard Roman numerals do not have a standard symbol for 5,000 or above without using special notation).

### 3.4 Logic and Behavior

The transformation follows a greedy algorithm approach:

1. **Iterate** through the mapping of decimal values to Roman symbols in descending order of value. The mapping includes both basic symbols and valid subtractive pairs:
* 1000 -> M
* 900 -> CM
* 500 -> D
* 400 -> CD
* 100 -> C
* 90 -> XC
* 50 -> L
* 40 -> XL
* 10 -> X
* 9 -> IX
* 5 -> V
* 4 -> IV
* 1 -> I


2. **Compare:** For the current map value (map_value), determine how many times it fits into the current remainder of N.
3. **Append:** Append the corresponding Roman symbol(s) to the output string.
4. **Decrement:** Subtract the value represented by the appended symbols from N.
5. **Repeat:** Continue until N equals zero.

### 3.5 Output

* Returns a string S containing the Roman numeral representation of N.

### 3.6 Error Handling

* If N < 1 or N > 3999, the function must raise a `RangeError` or equivalent exception indicating the input is outside the supported bounds of standard Roman numerals.

---

## 4. Function Specification: `from_numerals`

### 4.1 Description

Parses a string containing a Roman numeral and converts it into its integer equivalent.

### 4.2 Inputs

* **Input S:** A case-insensitive string representing a Roman numeral.

### 4.3 Pre-conditions

* S must be a non-empty string.
* S must contain only valid Roman numeral characters (I, V, X, L, C, D, M).

### 4.4 Logic and Behavior

The transformation evaluates the string from left to right:

1. **Normalization:** Convert the input string S to uppercase to ensure case-insensitivity.
2. **Accumulation:** Initialize a total integer value named `total` to 0.
3. **Iteration:** Traverse the string at index `i` from 0 to (length of S) - 1.
* Let `current_val` be the integer value of the symbol at S[i].
* Let `next_val` be the integer value of the symbol at S[i+1] (if i+1 is within bounds).


4. **Comparison:**
* **If** `current_val` < `next_val`: This indicates a subtractive pair. Subtract `current_val` from `total`.
* **Else** (`current_val` >= `next_val` or parsing the last character): This indicates an additive value. Add `current_val` to `total`.


5. **Completion:** Return `total`.

### 4.5 Output

* Returns an integer N representing the decimal value of the input string.

### 4.6 Validation and Error Handling

Ideally, the function should validate strict adherence to Roman numeral syntax rules.

* **Invalid Characters:** If S contains characters not in the symbol set, raise a `FormatError`.
* **Invalid Repetition:** If S contains more than three consecutive I, X, C, M or any repetition of V, L, D, raise a `ValidationError` (unless lenient parsing is specified).
* **Malformed Subtraction:** If a subtraction occurs that violates the pairs defined in Section 2.2 (e.g., IL for 49), raise a `ValidationError`.