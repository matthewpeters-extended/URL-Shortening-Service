ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)


def encode(number: int) -> str:
    """Base62-encodes a non-negative integer. Used to turn a Url row's
    primary key directly into its short code, so there is no separate
    random code to generate, store, or collision-check."""
    if number < 0:
        raise ValueError("cannot encode a negative number")
    if number == 0:
        return ALPHABET[0]

    digits = []
    while number > 0:
        number, remainder = divmod(number, BASE)
        digits.append(ALPHABET[remainder])
    return "".join(reversed(digits))


def decode(code: str) -> int:
    """Inverse of encode(). Raises ValueError on any character outside the
    base62 alphabet, which callers should treat as "no such short code"
    rather than a server error."""
    number = 0
    for char in code:
        index = ALPHABET.index(char)  # raises ValueError for a bad character
        number = number * BASE + index
    return number
