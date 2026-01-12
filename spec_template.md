## 1. Domain & Context
*High-level background logic. Crucial for the AI to understand the "rules of the universe" so it doesn't generate nonsense test data.*

## 2. Data Types & Generators
*Definitions of custom data structures. This tells the tool how to write the data generation strategies.*

* **Type Name:** Description
  
`class CustomType ...`

## 3. Functions Under Test
*The specific API surface area to test.*

### Function: `[name]`
* **Signature:** `input_types -> output_type`
* **Pre-conditions:** (Input validation rules)
* **Post-conditions:** (What must be true about the output?)

## 4. Invariants & Properties
*The heart of PBT. These describe relationships that hold true across all valid inputs.*

* **Round-Trip:** `inverse(function(x)) == x`
* **Idempotence:** `function(function(x)) == function(x)`
* **Invariant:** (e.g., "Sorting a list should not change its length")
* **Metamorphic:** (e.g., "If I double the input, the output should double")
* **Oracle:** (e.g., "Must match result of Reference Implementation X")