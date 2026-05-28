"""
ICC — Internet Calling Code Library
Numbering sequence generator.

Author: Mobyap (mobyap.com@gmail.com)
License: MIT

Sequence pattern (country-assignable codes):
  Phase 1 — All codes ending in 0:
    100, 200, 300, 400, 500, 600, 700, 800, 900,
    110, 120, 130, 140, 150, 160, 170, 180, 190,
    210, 220, 230, ..., 990

  Phase 2 — All remaining codes (units 1–9), excluding reserved:
    For tens = 1..9:
      For hundreds = 1..9:
        For units = 1..9:
          Skip if code is reserved (111, 222, ..., 999, 101, 202, ..., 909)

Reserved Special Codes (not assignable to countries):
  Triple-digit:  111, 222, 333, 444, 555, 666, 777, 888, 999
  Palindromes:   101, 202, 303, 404, 505, 606, 707, 808, 909

App Codes (Mobyap blockchain VOIP — start and end with 0):
  010, 020, 030, 040, 050, 060, 070, 080, 090

Rules:
  - Country codes and special codes NEVER start with 0
  - App codes ALWAYS start with 0 AND end with 0
  - Country codes are 3-digit integers in range 100–999 (excluding reserved)

Total country-assignable codes: 882 (900 minus 18 reserved)
"""

from typing import List, Set


# ── Reserved Special Codes ───────────────────────────────────────────────────

RESERVED_TRIPLE_CODES: List[int] = [111, 222, 333, 444, 555, 666, 777, 888, 999]
"""Codes with all three digits identical — reserved for global services."""

RESERVED_PALINDROME_CODES: List[int] = [101, 202, 303, 404, 505, 606, 707, 808, 909]
"""Codes where first and last digit match with 0 in the middle — reserved."""

ALL_RESERVED_CODES: Set[int] = set(RESERVED_TRIPLE_CODES + RESERVED_PALINDROME_CODES)
"""All 18 reserved special codes (not assignable to countries)."""

# ── Mobyap App Codes ────────────────────────────────────────────────────────

APP_CODES: List[int] = [10, 20, 30, 40, 50, 60, 70, 80, 90]
"""
Mobyap blockchain VOIP application codes.

Stored as integers (10, 20, ..., 90) but displayed with leading zero
as 3-digit strings: 010, 020, ..., 090.

Rule: App codes always start with 0 and end with 0.
"""

APP_CODES_FORMATTED: List[str] = [f"{c:03d}" for c in APP_CODES]
"""App codes as zero-padded 3-digit strings: ['010', '020', ..., '090']."""


# ── Sequence Generation ─────────────────────────────────────────────────────

def generate_icc_sequence(*, include_reserved: bool = False) -> List[int]:
    """
    Generate the complete ICC numbering sequence for country assignment.

    The sequence follows the exact ordering specified by the ICC standard:

    **Phase 1** (90 codes) — All codes ending in 0:
      - hundreds=1..9, tens=0, units=0  → 100, 200, ..., 900
      - For each hundreds=1..9:
          tens=1..9, units=0            → 110..190, 210..290, ..., 910..990

    **Phase 2** (remaining codes) — Codes with non-zero units digit:
      - For each tens=1..9:
          For each hundreds=1..9:
              For each units=1..9:
                  Emit code if not reserved
      - Then tens=0, hundreds=1..9, units=1..9 (skip reserved palindromes)

    Args:
        include_reserved: If True, include reserved codes in the sequence.
            Default is False (reserved codes excluded for country assignment).

    Returns:
        List of unique 3-digit integers in ICC sequence order.
        Without reserved: 882 codes. With reserved: 900 codes.
    """
    codes: List[int] = []

    # ── Phase 1: All codes ending in 0 ──────────────────────────────────
    # First: hundreds varies 1–9, tens=0, units=0
    for h in range(1, 10):
        codes.append(h * 100)

    # Then: for each hundreds 1–9, tens varies 1–9, units=0
    for h in range(1, 10):
        for t in range(1, 10):
            codes.append(h * 100 + t * 10)

    # ── Phase 2: Non-zero units digit ───────────────────────────────────
    # For each tens digit 1–9:
    #   For each hundreds digit 1–9:
    #     For each units digit 1–9:
    #       Skip reserved codes unless include_reserved is True
    for t in range(1, 10):
        for h in range(1, 10):
            for u in range(1, 10):
                code = h * 100 + t * 10 + u
                if include_reserved or code not in ALL_RESERVED_CODES:
                    codes.append(code)

    # Phase 2b: tens=0, units=1–9 (codes like 102, 103, ..., 909)
    # These follow after all tens=1–9 blocks.
    # Includes palindrome positions (101, 202, ...) only when include_reserved.
    for h in range(1, 10):
        for u in range(1, 10):
            code = h * 100 + u
            if include_reserved or code not in ALL_RESERVED_CODES:
                codes.append(code)

    return codes


def get_code_at_position(rank: int) -> int:
    """
    Get the ICC code assigned to a given rank (1-indexed).

    Rank 1 = largest country by land area (Russia → 100).

    Args:
        rank: The rank position (1-based). Valid range: 1–882.

    Returns:
        The 3-digit ICC code at that position.

    Raises:
        ValueError: If rank is out of range.
    """
    max_rank = len(ICC_SEQUENCE)
    if not 1 <= rank <= max_rank:
        raise ValueError(f"Rank must be between 1 and {max_rank}, got {rank}")
    return ICC_SEQUENCE[rank - 1]


def get_position_of_code(code: int) -> int:
    """
    Get the rank position (1-indexed) for a given ICC code.

    Args:
        code: A 3-digit ICC code (100–999, excluding reserved).

    Returns:
        The rank position of the code in the country sequence.

    Raises:
        ValueError: If the code is not in the country-assignable sequence.
    """
    if not 100 <= code <= 999:
        raise ValueError(f"ICC code must be between 100 and 999, got {code}")
    try:
        return ICC_SEQUENCE.index(code) + 1
    except ValueError:
        if code in ALL_RESERVED_CODES:
            raise ValueError(
                f"Code {code} is a reserved special code and cannot be "
                f"assigned to a country"
            )
        raise ValueError(f"Code {code} not found in ICC sequence")


# ── Classification Helpers ───────────────────────────────────────────────────

def classify_code(code: int) -> str:
    """
    Classify a 3-digit code into its category.

    Args:
        code: An integer code to classify.

    Returns:
        One of: ``"country"``, ``"special"``, ``"app"``, or ``"invalid"``.
    """
    if code in _APP_CODES_SET:
        return "app"
    if code in ALL_RESERVED_CODES:
        return "special"
    if code in VALID_COUNTRY_CODES:
        return "country"
    return "invalid"


def is_reserved_code(code: int) -> bool:
    """Check if a code is a reserved special code (111, 222, ..., 909)."""
    return code in ALL_RESERVED_CODES


def is_app_code(code: int) -> bool:
    """Check if a code is a Mobyap app code (010–090)."""
    return code in _APP_CODES_SET


# ── Pre-computed Data ────────────────────────────────────────────────────────

# Country-assignable sequence (excludes reserved codes)
ICC_SEQUENCE: List[int] = generate_icc_sequence(include_reserved=False)

# Full sequence including reserved codes (for validation purposes)
ICC_FULL_SEQUENCE: List[int] = generate_icc_sequence(include_reserved=True)

# Sets for O(1) lookup
VALID_COUNTRY_CODES: Set[int] = set(ICC_SEQUENCE)
VALID_ICC_CODES: Set[int] = set(ICC_FULL_SEQUENCE)  # All 900 codes (100–999)

_APP_CODES_SET: Set[int] = set(APP_CODES)
