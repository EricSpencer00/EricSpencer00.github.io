from typing import Optional
def consume(letters: str, overhang: str) -> Optional[tuple[str, bool]]:
    """Match a word's letters against the current overhang.

    Returns (new_overhang, flipped) where flipped means the remainder is now
    owed by the opposite side, or None if the letters don't line up.
    """
    if overhang.startswith(letters):
        return overhang[len(letters):], False
    if letters.startswith(overhang):
        return letters[len(overhang):], True
    return None
