import math


def to_vesicular(number, precision=6):
    """
    Converts a real-world number (Base-10) into Alien Vesicular Notation (Base-6).

    Args:
        number (float/int): The number to convert (e.g., 7.5, 49).
        precision (int): Max depth for fractional bubbles to prevent infinite loops.

    Returns:
        str: The vesicular representation (e.g., "(•) • C(•••)").
    """
    if number == 0:
        return "()"  # The Null Void (Empty Vesicle)

    # 1. Split into Integer and Fractional parts
    frac_part, int_part = math.modf(abs(number))
    int_part = int(int_part)

    # Symbols
    SPORE = "•"
    VESICLE_OPEN = "("
    VESICLE_CLOSE = ")"
    SIEVE_OPEN = "C("
    SIEVE_CLOSE = ")"

    terms = []

    # --- PART A: The Integer Shells (Positive Powers) ---
    # We convert the integer part to Base-6, tracking the power (depth).
    power = 0
    while int_part > 0:
        digit = int_part % 6
        int_part //= 6

        if digit > 0:
            # Create the spores for this place value
            spores = SPORE * digit  # e.g., •••

            # Wrap them in the correct number of Vesicles for the power
            # Power 0 = Loose spores
            # Power 1 = (spores)
            # Power 2 = ((spores))
            term = (VESICLE_OPEN * power) + spores + (VESICLE_CLOSE * power)

            # We insert at the beginning so the largest bubbles come first (convention)
            terms.insert(0, term)

        power += 1

    # --- PART B: The Fractional Sieves (Negative Powers) ---
    # We multiply by 6 repeatedly to find the fit for each depth.
    depth = 1
    while (
        frac_part > 1e-9 and depth <= precision
    ):  # 1e-9 handles floating point float drift
        frac_part *= 6
        digit = int(frac_part)

        if digit > 0:
            spores = SPORE * digit

            # Wrap in Sieves recursively
            # Depth 1 (1/6) = C(...)
            # Depth 2 (1/36) = C(C(...))
            term = (SIEVE_OPEN * depth) + spores + (SIEVE_CLOSE * depth)
            terms.append(term)

        frac_part -= digit
        depth += 1

    # --- PART C: Assembly ---
    result = " ".join(terms)

    # Handle Negative Numbers (The Anti-Spore)
    if number < 0:
        return f"ANTI-MATTER[{result}]"  # Or simple logic: replace • with Anti-Spore symbol

    return result


def from_vesicular(alien_str):
    """
    Parses a Vesicular Notation string (Base-6 topological) back to a Base-10 number.

    Logic:
    - We start at the "Universe" level (Multiplier = 1).
    - Entering a Vesicle '(' multiplies the current environment by 6.
    - Entering a Sieve 'C(' divides the current environment by 6.
    - Finding a Spore '•' adds the current environment's multiplier to the total.
    """

    # 1. Pre-processing:
    # We treat 'C(' as a single unique token. Let's replace it with '{' for easy parsing.
    # This distinguishes Sieves '{' from Vesicles '('.
    clean_str = alien_str.replace("C(", "{")

    current_multiplier = 1.0
    # The stack remembers the multiplier of the previous layer so we can 'pop' back to it.
    stack = [1.0]

    total_value = 0.0

    i = 0
    while i < len(clean_str):
        char = clean_str[i]

        if char == "(":
            # Enter Vesicle: Increase depth (Multiply by 6)
            current_multiplier *= 6
            stack.append(current_multiplier)

        elif char == "{":  # This represents the original "C("
            # Enter Sieve: Decrease depth (Divide by 6)
            current_multiplier /= 6
            stack.append(current_multiplier)

        elif char == ")":
            # Exit Container: Pop the stack to return to previous layer's math
            if len(stack) > 1:
                stack.pop()
                current_multiplier = stack[-1]
            else:
                # Value error: More closing parens than opening ones
                # For robustness, we just ignore extra closing tags.
                pass

        elif char == "•":
            # Found a Spore: Add its current worth to the total
            total_value += current_multiplier

        # Ignore spaces and other junk characters
        i += 1

    # Floating point arithmetic can leave tiny artifacts (e.g. 7.00000000001).
    # We round slightly to clean up, but return float to support fractions.
    return round(total_value, 8)


# --- Verification Test ---
test_cases = [
    "(•) • C(•••)",  # 7.5 (Logic: 6 + 1 + 3/6)
    "((•)) (••) •",  # 49  (Logic: 36 + 12 + 1)
    "C((•))",  # 1.0 (Logic: Cancellation! 1/6 * 6 * 1)
    "C(•) C(•)",  # 0.333... (Logic: 1/6 + 1/6 = 2/6)
    "((•) •)",  # 42 (Logic: 6 * (6 + 1)) -> Complex nesting test
]

print(f"{'VESICULAR STRING':<20} | {'DECODED VALUE':<10}")
print("-" * 45)

for alien in test_cases:
    decoded = from_vesicular(alien)
    # Print as int if it's a whole number, else float
    display_val = int(decoded) if decoded.is_integer() else decoded
    print(f"{alien:<20} | {display_val}")

# --- Testing the System ---
examples = [
    4,  # Simple spores
    6,  # 1 Vesicle
    7.5,  # Mixed
    49,  # Deep nesting
    0.1666666,  # 1/6 approx
    3.14159,  # Pi (approx)
]

print(f"{'BASE-10':<10} | {'VESICULAR NOTATION':<40}")
print("-" * 60)

for val in examples:
    alien_num = to_vesicular(val)
    print(f"{val:<10} | {alien_num}")

# ==========================================
# EXPANDED TEST SUITE
# ==========================================


def run_test_suite():
    print(
        f"{'TEST CATEGORY':<20} | {'INPUT':<15} | {'VESICULAR OUTPUT':<30} | {'DECODED':<10} | {'STATUS'}"
    )
    print("-" * 100)

    # Dictionary of tests: { Description: [List of Numbers] }
    tests = {
        "Base Integers": [1, 2, 3, 4, 5],
        "Base-6 Boundaries": [6, 36, 216],
        "Complex Integers": [7, 13, 49, 100],
        "Simple Fractions": [0.16666667, 0.5, 0.83333333],  # 1/6, 3/6, 5/6
        "Deep Fractions": [0.02777778, 0.00462963],  # 1/36, 1/216
        "Mixed Numbers": [1.5, 7.16666667, 36.5],
        "Edge Cases": [0, -6],
    }

    passes = 0
    total = 0

    for category, values in tests.items():
        for val in values:
            # 1. Convert to Alien
            alien = to_vesicular(val)

            # 2. Convert back (Round trip)
            back = from_vesicular(alien)

            # 3. Validation (allow tiny float tolerance)
            is_valid = abs(val - back) < 0.0001
            status = "PASS" if is_valid else "FAIL"
            if is_valid:
                passes += 1
            total += 1

            # Formatting for display
            display_val = str(val) if isinstance(val, int) else f"{val:.4f}"
            display_back = f"{back:.4f}"

            print(
                f"{category:<20} | {display_val:<15} | {alien:<30} | {display_back:<10} | {status}"
            )

    print("-" * 100)
    print(f"Standard Tests Completed: {passes}/{total} Passed.\n")


# ==========================================
# TOPOLOGY & LOGIC TESTS
# ==========================================
# These test specific structural rules (cancellation, nesting) that simple conversion doesn't cover.


def run_topology_tests():
    print("RUNNING TOPOLOGY & LOGIC CHECKS...")

    manual_cases = [
        # (Alien String, Expected Value, Description)
        ("((•))", 36, "Deep Nesting (6^2)"),
        ("C(C(•))", 1 / 36, "Deep Sieve (6^-2)"),
        ("C((•))", 1, "Cancellation (1/6 * 6 * 1)"),
        ("(• • •)", 18, "Grouping (3 * 6)"),
        ("((•) •)", 42, "Mixed Nesting (6 * (6 + 1))"),
        ("C(• • • • • •)", 1, "Overflow Sieve (6 * 1/6)"),
        ("()", 0, "The Null Void"),
    ]

    for alien, expected, desc in manual_cases:
        result = from_vesicular(alien)
        # Check proximity for floats
        passed = abs(result - expected) < 0.0001
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {desc:<25}: '{alien}' -> {result} (Expected {expected})")


if __name__ == "__main__":
    run_test_suite()
    run_topology_tests()
