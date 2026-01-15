"""Roman numeral conversion functions.

This module provides conversion between positive integers (1-3999) 
and their canonical Roman numeral string representations.
"""

def to_numerals(N: int) -> str:
    """Convert an integer to its canonical Roman numeral representation.
    
    Args:
        N: Integer in the range [1, 3999]
        
    Returns:
        A canonical Roman numeral string representing N
        
    Raises:
        TypeError: If N is not an integer
        ValueError: If N is outside the range [1, 3999]
        
    Example:
        >>> to_numerals(4)
        'IV'
        >>> to_numerals(1994)
        'MCMXCIV'
    """
    if not isinstance(N, int):
        raise TypeError(f"Input must be an integer, got {type(N).__name__}")
    
    if N < 1 or N > 3999:
        raise ValueError(f"Input must be in range [1, 3999], got {N}")
    
    # Greedy decomposition in descending order
    value_map = [
        (1000, 'M'),
        (900, 'CM'),
        (500, 'D'),
        (400, 'CD'),
        (100, 'C'),
        (90, 'XC'),
        (50, 'L'),
        (40, 'XL'),
        (10, 'X'),
        (9, 'IX'),
        (5, 'V'),
        (4, 'IV'),
        (1, 'I'),
    ]
    
    result = []
    remaining = N
    
    for value, token in value_map:
        while remaining >= value:
            result.append(token)
            remaining -= value
    
    return ''.join(result)

def from_numerals(roman: str) -> int:
    """Convert a Roman numeral string to its integer value.
    
    Args:
        roman: A Roman numeral string
        
    Returns:
        The integer value represented by the Roman numeral
        
    Raises:
        TypeError: If roman is not a string
        ValueError: If roman contains invalid characters or is malformed
        
    Example:
        >>> from_numerals('IV')
        4
        >>> from_numerals('MCMXCIV')
        1994
    """
    if not isinstance(roman, str):
        raise TypeError(f"Input must be a string, got {type(roman).__name__}")
    
    if not roman:
        raise ValueError("Input cannot be an empty string")
    
    # Symbol values
    symbol_values = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000,
    }
    
    # Validate all characters are valid Roman numeral symbols
    for char in roman:
        if char not in symbol_values:
            raise ValueError(f"Invalid Roman numeral character: '{char}'")
    
    total = 0
    prev_value = 0
    
    # Process from right to left
    for char in reversed(roman):
        value = symbol_values[char]
        
        # If current value is less than previous, subtract (subtractive notation)
        if value < prev_value:
            total -= value
        else:
            total += value
        
        prev_value = value
    
    return total