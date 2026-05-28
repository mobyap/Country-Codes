"""
ICC — Internet Calling Code Library
Code categories and purpose definitions.

Author: Mobyap (mobyap.com@gmail.com)
License: MIT

This module defines the purpose and categorization of all ICC code types:
  - Special Codes: Reserved for global services (education, emergency, military, etc.)
  - App Codes: Reserved for Mobyap blockchain VOIP application
  - Country Codes: Assigned to sovereign nations based on land area

Rules:
  1. A country code or special code CANNOT start with 0
  2. An app code ALWAYS starts with 0 AND ends with 0
"""

from typing import Dict, List, Optional
from icc.sequence import (
    RESERVED_TRIPLE_CODES,
    RESERVED_PALINDROME_CODES,
    ALL_RESERVED_CODES,
    APP_CODES,
    APP_CODES_FORMATTED,
)


# ── Special Code Purposes ───────────────────────────────────────────────────

SPECIAL_CODE_PURPOSES: Dict[int, str] = {
    # Triple-digit codes (primary allocations)
    111: "Educational Institutions",
    222: "Scientific Communities",
    333: "Emergency Services",
    444: "Government & Federal Institutions",
    555: "Law Enforcement Agencies",
    666: "Military",
    777: "Marketing Institutions",
    888: "Journalism & Media",
    999: "Reserved — Future Use",
    # Palindrome codes (alternate allocations)
    101: "Educational Institutions (Alternate)",
    202: "Scientific Communities (Alternate)",
    303: "Emergency Services (Alternate)",
    404: "Government & Federal Institutions (Alternate)",
    505: "Law Enforcement Agencies (Alternate)",
    606: "Military (Alternate)",
    707: "Marketing Institutions (Alternate)",
    808: "Journalism & Media (Alternate)",
    909: "Reserved — Future Use (Alternate)",
}
"""
Mapping of reserved special codes to their designated global purposes.

These codes are used for institutional and service communications across all
countries — they are NOT assigned to any specific nation.

Primary allocations (triple-digit):
    111 — Educational Institutions
    222 — Scientific Communities
    333 — Emergency Services
    444 — Government & Federal Institutions
    555 — Law Enforcement Agencies
    666 — Military
    777 — Marketing Institutions
    888 — Journalism & Media
    999 — Reserved for future use

Alternate allocations (palindrome):
    101–909 — Same categories as above, alternate routing
"""


# ── App Code Purposes ────────────────────────────────────────────────────────

APP_CODE_PURPOSES: Dict[int, str] = {
    10: "Mobyap Blockchain VOIP — Internal Channel 1",
    20: "Mobyap Blockchain VOIP — Internal Channel 2",
    30: "Mobyap Blockchain VOIP — Internal Channel 3",
    40: "Mobyap Blockchain VOIP — Internal Channel 4",
    50: "Mobyap Blockchain VOIP — Internal Channel 5",
    60: "Mobyap Blockchain VOIP — Internal Channel 6",
    70: "Mobyap Blockchain VOIP — Internal Channel 7",
    80: "Mobyap Blockchain VOIP — Internal Channel 8",
    90: "Mobyap Blockchain VOIP — Internal Channel 9",
}
"""
Mapping of Mobyap app codes to their designated purposes.

These codes are reserved exclusively for the Mobyap blockchain-based VOIP
application for internal and external communications.

Displayed as 3-digit zero-padded: 010, 020, ..., 090.
Rule: App codes ALWAYS start with 0 and end with 0.
"""


# ── Code Rules ───────────────────────────────────────────────────────────────

CODE_RULES: Dict[str, str] = {
    "country_code_range": "100–999 (3-digit, never starts with 0)",
    "country_code_exclusions": "18 reserved special codes are excluded",
    "special_code_rule": "Cannot start with 0; triple-digit or palindrome pattern",
    "app_code_rule": "Always starts with 0 AND ends with 0 (010–090)",
    "total_country_codes": "882 (900 minus 18 reserved)",
    "total_special_codes": "18 (9 triple-digit + 9 palindrome)",
    "total_app_codes": "9 (Mobyap channels)",
}


# ── Lookup Functions ─────────────────────────────────────────────────────────

def get_special_code_purpose(code: int) -> Optional[str]:
    """
    Get the designated purpose for a reserved special code.

    Args:
        code: A reserved special code (e.g., 111, 333, 404).

    Returns:
        Purpose string, or None if the code is not a special code.
    """
    return SPECIAL_CODE_PURPOSES.get(code)


def get_app_code_purpose(code: int) -> Optional[str]:
    """
    Get the designated purpose for a Mobyap app code.

    Args:
        code: An app code as integer (e.g., 10 for 010).

    Returns:
        Purpose string, or None if the code is not an app code.
    """
    return APP_CODE_PURPOSES.get(code)


def get_all_special_codes() -> List[Dict]:
    """
    Get all reserved special codes with their purposes.

    Returns:
        List of dicts, each with 'code', 'formatted', 'purpose', and 'category'.
    """
    result = []
    for code in sorted(ALL_RESERVED_CODES):
        category = "triple" if code in set(RESERVED_TRIPLE_CODES) else "palindrome"
        result.append({
            "code": code,
            "formatted": str(code),
            "purpose": SPECIAL_CODE_PURPOSES[code],
            "category": category,
        })
    return result


def get_all_app_codes() -> List[Dict]:
    """
    Get all Mobyap app codes with their purposes.

    Returns:
        List of dicts, each with 'code', 'formatted', and 'purpose'.
    """
    result = []
    for code in APP_CODES:
        result.append({
            "code": code,
            "formatted": f"{code:03d}",
            "purpose": APP_CODE_PURPOSES[code],
        })
    return result


def get_code_rules() -> Dict[str, str]:
    """
    Get the complete set of ICC code assignment rules.

    Returns:
        Dict of rule names to descriptions.
    """
    return dict(CODE_RULES)
