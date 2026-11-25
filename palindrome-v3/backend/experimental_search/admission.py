import re
ALLOWED_RENDERING = re.compile(r"[A-Za-z][A-Za-z\s'\-.,;:!?]*")
def normalize_letters(text: str) -> str:
    """Return the ASCII letter tape, rejecting unsupported alphabetic input."""
    if any(character.isalpha() and not character.isascii() for character in text):
        raise ValueError("unsupported non-ASCII alphabetic character")
    return "".join(re.findall(r"[a-z]", text.casefold()))
