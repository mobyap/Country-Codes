"""
ICC — Internet Calling Code Library
ISN (Internet Subscriber Number) module.

Author: Mobyap (mobyap.com@gmail.com)
License: MIT

ISN Format: ICC-RRRR-SSSS-SSSS (15 digits, displayed with hyphens)
  - ICC  (3 digits):  Internet Calling Code (country, special, or app code)
  - RRRR (4 digits):  Region and Purpose Code
  - SSSS-SSSS (8 digits): Subscriber Number

Example: 100-1234-5678-0321
  - ICC = 100 (Russia)
  - Region/Purpose = 1234
  - Subscriber = 56780321

Full number as digits: 100123456780321 (15 digits)
"""

import re
from dataclasses import dataclass
from typing import Optional

from icc.sequence import (
    classify_code,
    ALL_RESERVED_CODES,
    VALID_COUNTRY_CODES,
    APP_CODES,
)
from icc.exceptions import InvalidISNError


# ── ISN Pattern ──────────────────────────────────────────────────────────────

# Matches formatted ISN: "100-1234-5678-0321" or "100-1234-56780321"
_ISN_FORMATTED_PATTERN = re.compile(
    r"^(\d{3})-(\d{4})-(\d{4})-(\d{4})$"
)

# Matches raw digits: "100123456780321" (exactly 15 digits)
_ISN_RAW_PATTERN = re.compile(r"^\d{15}$")

# Matches flexible formats: with or without hyphens, spaces
_ISN_FLEXIBLE_PATTERN = re.compile(
    r"^(\d{3})[\s\-]?(\d{4})[\s\-]?(\d{4})[\s\-]?(\d{4})$"
)


# ── Data Classes ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ISNComponents:
    """
    Parsed components of an Internet Subscriber Number.

    Attributes:
        icc_code: 3-digit Internet Calling Code (integer).
        region_code: 4-digit region and purpose code (string, preserves leading zeros).
        subscriber_number: 8-digit subscriber number (string, preserves leading zeros).
        full_number: Formatted ISN string (e.g., "100-1234-5678-0321").
        raw_digits: All 15 digits without separators (e.g., "100123456780321").
        code_type: Classification of the ICC code ("country", "special", "app").
    """
    icc_code: int
    region_code: str
    subscriber_number: str
    full_number: str
    raw_digits: str
    code_type: str


@dataclass(frozen=True)
class ISNValidationResult:
    """
    Result of ISN validation.

    Attributes:
        is_valid: Whether the ISN passes all validation checks.
        icc_code: Extracted ICC code (if parseable), else None.
        code_type: Classification ("country", "special", "app"), or None.
        country: Country name if ICC is a country code, else None.
        region_code: Extracted region code (if parseable), else None.
        subscriber_number: Extracted subscriber number (if parseable), else None.
        error: Description of validation failure, or None if valid.
    """
    is_valid: bool
    icc_code: Optional[int] = None
    code_type: Optional[str] = None
    country: Optional[str] = None
    region_code: Optional[str] = None
    subscriber_number: Optional[str] = None
    error: Optional[str] = None


# ── Core Functions ───────────────────────────────────────────────────────────

def parse_isn(isn_string: str) -> ISNComponents:
    """
    Parse an ISN string into its components.

    Accepts multiple formats:
      - Formatted:  "100-1234-5678-0321"
      - Raw digits: "100123456780321"
      - Flexible:   "100 1234 5678 0321"

    Args:
        isn_string: The ISN string to parse.

    Returns:
        ISNComponents with all parsed fields.

    Raises:
        InvalidISNError: If the string cannot be parsed as a valid ISN.
    """
    if not isn_string or not isinstance(isn_string, str):
        raise InvalidISNError(isn_string, "ISN must be a non-empty string")

    cleaned = isn_string.strip()

    # Try formatted pattern first
    match = _ISN_FLEXIBLE_PATTERN.match(cleaned)
    if not match:
        # Try raw digits
        digits = re.sub(r"[\s\-]", "", cleaned)
        if _ISN_RAW_PATTERN.match(digits):
            icc_str = digits[:3]
            region = digits[3:7]
            sub_part1 = digits[7:11]
            sub_part2 = digits[11:15]
        else:
            raise InvalidISNError(
                isn_string,
                "Expected format: ICC-RRRR-SSSS-SSSS (15 digits)"
            )
    else:
        icc_str = match.group(1)
        region = match.group(2)
        sub_part1 = match.group(3)
        sub_part2 = match.group(4)

    icc_code = int(icc_str)
    subscriber = sub_part1 + sub_part2
    raw_digits = icc_str + region + subscriber
    formatted = f"{icc_str}-{region}-{sub_part1}-{sub_part2}"
    code_type = classify_code(icc_code)

    return ISNComponents(
        icc_code=icc_code,
        region_code=region,
        subscriber_number=subscriber,
        full_number=formatted,
        raw_digits=raw_digits,
        code_type=code_type,
    )


def validate_isn(isn_string: str) -> ISNValidationResult:
    """
    Validate an ISN string comprehensively.

    Checks:
      1. Format is correct (15 digits in ICC-RRRR-SSSS-SSSS pattern)
      2. ICC code is a valid code (country, special, or app)
      3. Region code is a valid 4-digit string
      4. Subscriber number is a valid 8-digit string

    Args:
        isn_string: The ISN string to validate.

    Returns:
        ISNValidationResult with detailed validation information.
    """
    try:
        components = parse_isn(isn_string)
    except (InvalidISNError, Exception) as e:
        return ISNValidationResult(
            is_valid=False,
            error=str(e),
        )

    icc_code = components.icc_code
    code_type = components.code_type

    # Check if ICC code is valid
    if code_type == "invalid":
        return ISNValidationResult(
            is_valid=False,
            icc_code=icc_code,
            code_type=None,
            error=f"ICC code {icc_code} is not a valid code",
        )

    # Look up country if it's a country code
    country_name = None
    if code_type == "country":
        try:
            from icc.data import _BY_ICC
            country = _BY_ICC.get(icc_code)
            if country:
                country_name = country["name"]
        except ImportError:
            pass

    return ISNValidationResult(
        is_valid=True,
        icc_code=icc_code,
        code_type=code_type,
        country=country_name,
        region_code=components.region_code,
        subscriber_number=components.subscriber_number,
    )


def is_valid_isn(isn_string: str) -> bool:
    """
    Quick check whether an ISN string is valid.

    Args:
        isn_string: The ISN string to check.

    Returns:
        True if valid, False otherwise.
    """
    return validate_isn(isn_string).is_valid


def format_isn(icc_code: int, region_code: str, subscriber: str) -> str:
    """
    Format ISN components into the standard display format.

    Args:
        icc_code: 3-digit ICC code (integer).
        region_code: 4-digit region/purpose code (string).
        subscriber: 8-digit subscriber number (string).

    Returns:
        Formatted ISN string: "ICC-RRRR-SSSS-SSSS"

    Raises:
        InvalidISNError: If any component is invalid.
    """
    # Validate ICC code
    icc_str = str(icc_code).zfill(3)
    if len(icc_str) != 3:
        raise InvalidISNError(
            f"{icc_code}", f"ICC code must be 3 digits, got {len(icc_str)}"
        )

    # Validate region code
    region_clean = str(region_code).zfill(4)
    if len(region_clean) != 4 or not region_clean.isdigit():
        raise InvalidISNError(
            f"{region_code}", f"Region code must be 4 digits"
        )

    # Validate subscriber
    sub_clean = str(subscriber).zfill(8)
    if len(sub_clean) != 8 or not sub_clean.isdigit():
        raise InvalidISNError(
            f"{subscriber}", f"Subscriber number must be 8 digits"
        )

    return f"{icc_str}-{region_clean}-{sub_clean[:4]}-{sub_clean[4:]}"


def generate_isn(
    icc_code: int,
    region_code: str = "0001",
    subscriber_id: Optional[int] = None,
) -> str:
    """
    Generate an ISN for a given ICC code.

    Args:
        icc_code: 3-digit ICC code (integer).
        region_code: 4-digit region/purpose code (default: "0001").
        subscriber_id: Subscriber ID as integer (0–99999999).
            If None, generates a random subscriber ID.

    Returns:
        Formatted ISN string.

    Raises:
        InvalidISNError: If any parameter is invalid.
    """
    import random

    # Validate ICC code type
    code_type = classify_code(icc_code)
    if code_type == "invalid":
        raise InvalidISNError(
            str(icc_code), f"ICC code {icc_code} is not a valid code"
        )

    # Generate or validate subscriber ID
    if subscriber_id is None:
        subscriber_id = random.randint(0, 99999999)
    elif not 0 <= subscriber_id <= 99999999:
        raise InvalidISNError(
            str(subscriber_id),
            "Subscriber ID must be between 0 and 99999999"
        )

    subscriber_str = f"{subscriber_id:08d}"
    return format_isn(icc_code, region_code, subscriber_str)


def get_country_from_isn(isn_string: str) -> dict:
    """
    Extract the country information from an ISN.

    Args:
        isn_string: The ISN string to look up.

    Returns:
        Country dict if the ISN uses a country ICC code.

    Raises:
        InvalidISNError: If the ISN is invalid or uses a non-country code.
    """
    components = parse_isn(isn_string)

    if components.code_type != "country":
        raise InvalidISNError(
            isn_string,
            f"ISN uses a {components.code_type} code ({components.icc_code}), "
            f"not a country code"
        )

    from icc.data import _BY_ICC
    country = _BY_ICC.get(components.icc_code)
    if country is None:
        raise InvalidISNError(
            isn_string,
            f"ICC code {components.icc_code} is not assigned to any country"
        )

    return dict(country)
