"""Property-based tests for Roman numeral conversion functions using Hypothesis."""

import pytest
from hypothesis import given, assume, strategies as st
from implementation import to_numerals, from_numerals


# Custom strategies
valid_integers = st.integers(min_value=1, max_value=3999)
invalid_low_integers = st.integers(max_value=0)
invalid_high_integers = st.integers(min_value=4000)
roman_characters = st.sampled_from(['I', 'V', 'X', 'L', 'C', 'D', 'M'])
invalid_characters = st.characters(blacklist_categories=('Cs',)).filter(
    lambda c: c not in 'IVXLCDM'
)


class TestToNumeralsProperties:
    """Property-based tests for to_numerals function."""
    
    @given(valid_integers)
    def test_output_is_string(self, n):
        """Property: Output is always a non-empty string."""
        result = to_numerals(n)
        assert isinstance(result, str)
        assert len(result) > 0
    
    @given(valid_integers)
    def test_output_only_valid_characters(self, n):
        """Property: Output contains only valid Roman numeral characters."""
        result = to_numerals(n)
        valid_chars = set('IVXLCDM')
        assert all(c in valid_chars for c in result)
    
    @given(valid_integers)
    def test_deterministic(self, n):
        """Property: Same input always produces same output."""
        result1 = to_numerals(n)
        result2 = to_numerals(n)
        assert result1 == result2
    
    @given(valid_integers)
    def test_round_trip_with_from_numerals(self, n):
        """Property: from_numerals(to_numerals(n)) == n for all valid n."""
        roman = to_numerals(n)
        assert from_numerals(roman) == n
    
    @given(valid_integers, valid_integers)
    def test_monotonic_length_for_larger_values(self, n1, n2):
        """Property: Larger numbers generally don't produce shorter strings."""
        assume(n1 < n2)
        assume(n2 - n1 >= 1000)  # Significant difference
        len1 = len(to_numerals(n1))
        len2 = len(to_numerals(n2))
        assert len2 >= len1, f"Length decreased from {len1} to {len2} for {n1} -> {n2}"
    
    @given(st.integers(min_value=1, max_value=3998))
    def test_successor_property(self, n):
        """Property: to_numerals(n+1) differs from to_numerals(n)."""
        roman_n = to_numerals(n)
        roman_n_plus_1 = to_numerals(n + 1)
        assert roman_n != roman_n_plus_1
    
    @given(valid_integers)
    def test_no_more_than_three_consecutive_same_additive_symbols(self, n):
        """Property: Canonical form has at most 3 consecutive I, X, C, or M."""
        result = to_numerals(n)
        # Check for runs of more than 3 of the same additive symbol
        for symbol in ['I', 'X', 'C', 'M']:
            assert symbol * 4 not in result
    
    @given(valid_integers)
    def test_subtractive_pairs_valid(self, n):
        """Property: Only valid subtractive pairs appear (IV, IX, XL, XC, CD, CM)."""
        result = to_numerals(n)
        # Check no invalid subtractive combinations
        invalid_pairs = ['IL', 'IC', 'ID', 'IM', 'XD', 'XM', 'VX', 'VL', 'VC', 'VD', 'VM',
                        'LC', 'LD', 'LM', 'DM']
        for pair in invalid_pairs:
            assert pair not in result
    
    @given(invalid_low_integers)
    def test_rejects_values_below_range(self, n):
        """Property: Values < 1 raise ValueError."""
        with pytest.raises(ValueError):
            to_numerals(n)
    
    @given(invalid_high_integers)
    def test_rejects_values_above_range(self, n):
        """Property: Values > 3999 raise ValueError."""
        with pytest.raises(ValueError):
            to_numerals(n)
    
    @given(st.one_of(st.floats(), st.text(), st.none(), st.lists(st.integers())))
    def test_rejects_non_integer_types(self, value):
        """Property: Non-integer inputs raise TypeError."""
        assume(not isinstance(value, bool))  # bool is subclass of int
        with pytest.raises(TypeError):
            to_numerals(value)
    
    @given(st.integers(min_value=1, max_value=999))
    def test_length_bounded_for_small_values(self, n):
        """Property: Numbers up to 999 produce strings of reasonable length."""
        result = to_numerals(n)
        assert len(result) <= 15  # Max would be 888 = DCCCLXXXVIII (13 chars)


class TestFromNumeralsProperties:
    """Property-based tests for from_numerals function."""
    
    @given(valid_integers)
    def test_output_is_integer(self, n):
        """Property: Output is always a positive integer."""
        roman = to_numerals(n)  # Generate valid Roman numeral
        result = from_numerals(roman)
        assert isinstance(result, int)
        assert result > 0
    
    @given(valid_integers)
    def test_deterministic(self, n):
        """Property: Same input always produces same output."""
        roman = to_numerals(n)
        result1 = from_numerals(roman)
        result2 = from_numerals(roman)
        assert result1 == result2
    
    @given(valid_integers)
    def test_round_trip_with_to_numerals(self, n):
        """Property: to_numerals(from_numerals(to_numerals(n))) == to_numerals(n)."""
        roman = to_numerals(n)
        reconstructed = to_numerals(from_numerals(roman))
        assert reconstructed == roman
    
    @given(valid_integers)
    def test_output_in_valid_range(self, n):
        """Property: Output is always in range [1, 3999]."""
        roman = to_numerals(n)
        result = from_numerals(roman)
        assert 1 <= result <= 3999
    
    @given(valid_integers)
    def test_case_sensitive(self, n):
        """Property: Roman numerals should be uppercase (lowercase fails or differs)."""
        roman = to_numerals(n)
        if roman.lower() != roman:  # If there are actual letters
            # We expect lowercase to fail with ValueError (invalid characters)
            with pytest.raises(ValueError):
                from_numerals(roman.lower())
    
    @given(st.text(alphabet=invalid_characters, min_size=1))
    def test_rejects_invalid_characters(self, text):
        """Property: Strings with invalid characters raise ValueError."""
        with pytest.raises(ValueError):
            from_numerals(text)
    
    @given(st.text(alphabet='IVXLCDM', min_size=1))
    def test_accepts_only_valid_character_strings(self, text):
        """Property: Any string of valid chars is accepted (produces some int)."""
        result = from_numerals(text)
        assert isinstance(result, int)
        assert result > 0
    
    def test_rejects_empty_string(self):
        """Property: Empty string raises ValueError."""
        with pytest.raises(ValueError):
            from_numerals("")
    
    @given(st.one_of(st.integers(), st.floats(), st.none(), st.lists(st.text())))
    def test_rejects_non_string_types(self, value):
        """Property: Non-string inputs raise TypeError."""
        with pytest.raises(TypeError):
            from_numerals(value)
    
    @given(st.text(alphabet='IVXLCDM', min_size=1, max_size=3))
    def test_short_strings_bounded_output(self, roman):
        """Property: Short Roman numerals produce reasonably bounded values."""
        result = from_numerals(roman)
        # MMM = 3000 is max for 3 characters
        assert result <= 3000


class TestRelationalProperties:
    """Property-based tests for relationships between the functions."""
    
    @given(valid_integers, valid_integers)
    def test_order_preservation(self, n1, n2):
        """Property: If n1 < n2, then from_numerals(to_numerals(n1)) < from_numerals(to_numerals(n2))."""
        assume(n1 != n2)
        result1 = from_numerals(to_numerals(n1))
        result2 = from_numerals(to_numerals(n2))
        
        if n1 < n2:
            assert result1 < result2
        else:
            assert result1 > result2
    
    @given(valid_integers)
    def test_idempotent_string_conversion(self, n):
        """Property: to_numerals is idempotent through from_numerals."""
        roman1 = to_numerals(n)
        roman2 = to_numerals(from_numerals(roman1))
        assert roman1 == roman2
    
    @given(st.integers(min_value=1, max_value=3998))
    def test_addition_property_for_small_increments(self, n):
        """Property: from_numerals(to_numerals(n)) + 1 == from_numerals(to_numerals(n+1))."""
        value_n = from_numerals(to_numerals(n))
        value_n_plus_1 = from_numerals(to_numerals(n + 1))
        assert value_n + 1 == value_n_plus_1


class TestMetamorphicProperties:
    """Metamorphic property-based tests."""
    
    @given(valid_integers)
    def test_concatenation_reflects_addition_for_some_cases(self, n):
        """Property: For certain values, concatenating Roman numerals is like addition."""
        # This is true for additive cases, e.g., to_numerals(2) = "II"
        assume(1 <= n <= 3)  # Simple cases where concatenation works
        roman_n = to_numerals(n)
        roman_2n = to_numerals(2 * n)
        
        # For small values, doubling might involve concatenation patterns
        if n == 1:
            assert from_numerals(roman_n + roman_n) == 2, f"Failed for n={n}"
        elif n == 2:
            assert from_numerals(roman_n + roman_n) == 4, f"Failed for n={n}"
        elif n == 3:
            assert from_numerals(roman_n + roman_n) == 6, f"Failed for n={n}"
    
    @given(valid_integers)
    def test_string_length_grows_with_magnitude(self, n):
        """Property: Generally, larger numbers have longer or equal string representations."""
        assume(n >= 1000)  # Focus on larger numbers
        
        # Divide by 2 and compare lengths
        half_n = n // 2
        if half_n >= 1:
            len_n = len(to_numerals(n))
            len_half = len(to_numerals(half_n))
            # Length should not decrease dramatically
            assert len_n >= len_half - 1, f"Length decreased too much from {len_half} to {len_n} for {half_n} -> {n}"


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
