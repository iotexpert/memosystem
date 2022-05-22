import re

# This code came from https://codereview.stackexchange.com/questions/182733/base-26-letters-and-base-10-using-recursion

A_UPPERCASE = ord('A')
ALPHABET_SIZE = 26


def _decompose(number):
    """Generate digits from `number` in base alphabet, least significants
    bits first.

    Since A is 1 rather than 0 in base alphabet, we are dealing with
    `number - 1` at each iteration to be able to extract the proper digits.
    """

    while number:
        number, remainder = divmod(number - 1, ALPHABET_SIZE)
        yield remainder


def b10_to_rev(number):
    """Convert a decimal number to its base alphabet representation"""

    return ''.join(
            chr(A_UPPERCASE + part)
            for part in _decompose(number)
    )[::-1]


def rev_to_b10(letters):
    """Convert an alphabet number to its decimal representation"""

    return sum(
            (ord(letter) - A_UPPERCASE + 1) * ALPHABET_SIZE**i
            for i, letter in enumerate(reversed(letters.upper()))
    )

def valid_rev(rev):
    if not isinstance(rev,str):
        return False
    
    return bool(re.match('^[a-zA-Z]+$',rev))
    
    