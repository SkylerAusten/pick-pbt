"""Unit tests for Roman numeral conversion functions."""

import pytest
from implementation import to_numerals, from_numerals


class TestToNumerals:
    """Test cases for integer to Roman numeral conversion."""
    
    def test_basic_symbols(self):
        """Test conversion of basic symbol values."""
        assert to_numerals(1) == "I"
        assert to_numerals(5) == "V"
        assert to_numerals(10) == "X"
        assert to_numerals(50) == "L"
        assert to_numerals(100) == "C"
        assert to_numerals(500) == "D"
        assert to_numerals(1000) == "M"
    
    def test_subtractive_notation(self):
        """Test conversion using subtractive notation."""
        assert to_numerals(4) == "IV"
        assert to_numerals(9) == "IX"
        assert to_numerals(40) == "XL"
        assert to_numerals(90) == "XC"
        assert to_numerals(400) == "CD"
        assert to_numerals(900) == "CM"
    
    def test_additive_combinations(self):
        """Test conversion of additive combinations."""
        assert to_numerals(2) == "II"
        assert to_numerals(3) == "III"
        assert to_numerals(6) == "VI"
        assert to_numerals(7) == "VII"
        assert to_numerals(8) == "VIII"
        assert to_numerals(11) == "XI"
        assert to_numerals(12) == "XII"
        assert to_numerals(13) == "XIII"
    
    def test_complex_numbers(self):
        """Test conversion of complex numbers."""
        assert to_numerals(1994) == "MCMXCIV"
        assert to_numerals(2023) == "MMXXIII"
        assert to_numerals(444) == "CDXLIV"
        assert to_numerals(888) == "DCCCLXXXVIII"
        assert to_numerals(1984) == "MCMLXXXIV"
        assert to_numerals(3999) == "MMMCMXCIX"
    
    def test_boundary_values(self):
        """Test conversion at boundary values."""
        assert to_numerals(1) == "I"
        assert to_numerals(3999) == "MMMCMXCIX"
    
    def test_out_of_range_error(self):
        """Test that out-of-range values raise ValueError."""
        with pytest.raises(ValueError):
            to_numerals(0)
        with pytest.raises(ValueError):
            to_numerals(-1)
        with pytest.raises(ValueError):
            to_numerals(4000)
        with pytest.raises(ValueError):
            to_numerals(10000)
    
    def test_type_error(self):
        """Test that non-integer inputs raise TypeError."""
        with pytest.raises(TypeError):
            to_numerals("42")
        with pytest.raises(TypeError):
            to_numerals(3.14)
        with pytest.raises(TypeError):
            to_numerals(None)


class TestFromNumerals:
    """Test cases for Roman numeral to integer conversion."""
    
    def test_basic_symbols(self):
        """Test conversion of basic symbols."""
        assert from_numerals("I") == 1
        assert from_numerals("V") == 5
        assert from_numerals("X") == 10
        assert from_numerals("L") == 50
        assert from_numerals("C") == 100
        assert from_numerals("D") == 500
        assert from_numerals("M") == 1000
    
    def test_subtractive_notation(self):
        """Test conversion of subtractive notation."""
        assert from_numerals("IV") == 4
        assert from_numerals("IX") == 9
        assert from_numerals("XL") == 40
        assert from_numerals("XC") == 90
        assert from_numerals("CD") == 400
        assert from_numerals("CM") == 900
    
    def test_additive_combinations(self):
        """Test conversion of additive combinations."""
        assert from_numerals("II") == 2
        assert from_numerals("III") == 3
        assert from_numerals("VI") == 6
        assert from_numerals("VII") == 7
        assert from_numerals("VIII") == 8
        assert from_numerals("XI") == 11
        assert from_numerals("XII") == 12
        assert from_numerals("XIII") == 13
    
    def test_complex_numbers(self):
        """Test conversion of complex Roman numerals."""
        assert from_numerals("MCMXCIV") == 1994
        assert from_numerals("MMXXIII") == 2023
        assert from_numerals("CDXLIV") == 444
        assert from_numerals("DCCCLXXXVIII") == 888
        assert from_numerals("MCMLXXXIV") == 1984
        assert from_numerals("MMMCMXCIX") == 3999
    
    def test_invalid_characters(self):
        """Test that invalid characters raise ValueError."""
        with pytest.raises(ValueError):
            from_numerals("ABC")
        with pytest.raises(ValueError):
            from_numerals("IXZ")
        with pytest.raises(ValueError):
            from_numerals("123")
    
    def test_empty_string_error(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            from_numerals("")
    
    def test_type_error(self):
        """Test that non-string inputs raise TypeError."""
        with pytest.raises(TypeError):
            from_numerals(42)
        with pytest.raises(TypeError):
            from_numerals(None)
        with pytest.raises(TypeError):
            from_numerals(["I", "V"])


class TestRoundTrip:
    """Test round-trip conversion properties."""
    
    def test_round_trip_all_valid_range(self):
        """Test that to_numerals(from_numerals(x)) == x for sample values."""
        test_values = [1, 4, 5, 9, 10, 40, 50, 90, 100, 400, 500, 900, 1000,
                       1994, 2023, 3999]
        for n in test_values:
            roman = to_numerals(n)
            assert from_numerals(roman) == n
    
    def test_round_trip_canonical_form(self):
        """Test that canonical Roman numerals convert correctly."""
        test_cases = [
            ("I", 1),
            ("IV", 4),
            ("IX", 9),
            ("XLIV", 44),
            ("XCIX", 99),
            ("CDXC", 490),
            ("MCMXCIV", 1994),
            ("MMMCMXCIX", 3999),
        ]
        for roman, expected in test_cases:
            assert from_numerals(roman) == expected
            assert to_numerals(expected) == roman


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
