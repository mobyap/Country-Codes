"""
ICC — Internet Calling Code Library
====================================

A Python library providing 3-digit Internet Communications Codes (ICC) for
every sovereign country in the world, with integration helpers for VOIP
and blockchain systems.

Author: Mobyap (mobyap.com@gmail.com)
License: MIT — Free for commercial use

Usage:
    >>> import icc
    >>> icc.get_country_by_icc(700)
    {'rank': 7, 'name': 'India', 'icc_code': 700, ...}

    >>> icc.get_icc_by_country("India")
    700

    >>> icc.validate_icc(100)
    True

ISN (Internet Subscriber Number) Format:
    ICC-RRRR-SSSS-SSSS (15 digits)
    Example: 100-1234-5678-0321

    >>> from icc.isn import parse_isn
    >>> result = parse_isn("100-1234-5678-0321")
    >>> result.icc_code
    100

Code Types:
    - Country codes: 100–999 (excluding reserved), assigned by land area
    - Special codes: 111, 222, ..., 999, 101, 202, ..., 909 (global services)
    - App codes: 010, 020, ..., 090 (Mobyap blockchain VOIP)
"""

__version__ = "2.0.0"
__author__ = "Mobyap"
__email__ = "mobyap.com@gmail.com"
__license__ = "MIT"

# Core functions
from icc.core import (
    get_country_by_icc,
    get_country_by_name,
    get_country_by_iso,
    get_icc_by_country,
    validate_icc,
    is_valid_icc_code,
    get_code_info,
    list_all_countries,
    search_countries,
    get_countries_by_continent,
    get_continents,
    get_statistics,
    get_special_codes,
    get_app_codes_list,
)

# Sequence
from icc.sequence import (
    generate_icc_sequence,
    get_code_at_position,
    get_position_of_code,
    classify_code,
    is_reserved_code,
    is_app_code,
    ICC_SEQUENCE,
    ALL_RESERVED_CODES,
    APP_CODES,
    APP_CODES_FORMATTED,
    VALID_COUNTRY_CODES,
    VALID_ICC_CODES,
)

# Code categories
from icc.codes import (
    SPECIAL_CODE_PURPOSES,
    APP_CODE_PURPOSES,
    CODE_RULES,
    get_special_code_purpose,
    get_app_code_purpose,
    get_all_special_codes,
    get_all_app_codes,
    get_code_rules,
)

# ISN (Internet Subscriber Number)
from icc.isn import (
    parse_isn,
    validate_isn,
    is_valid_isn,
    format_isn,
    generate_isn,
    get_country_from_isn,
    ISNComponents,
    ISNValidationResult,
)

# Data
from icc.data import COUNTRIES, TOTAL_COUNTRIES

# Exceptions
from icc.exceptions import (
    ICCError,
    InvalidICCCode,
    CountryNotFound,
    InvalidInputError,
    InvalidISNError,
    ReservedCodeError,
)

# VOIP helpers
from icc import voip
from icc import blockchain

__all__ = [
    # Core
    "get_country_by_icc",
    "get_country_by_name",
    "get_country_by_iso",
    "get_icc_by_country",
    "validate_icc",
    "is_valid_icc_code",
    "get_code_info",
    "list_all_countries",
    "search_countries",
    "get_countries_by_continent",
    "get_continents",
    "get_statistics",
    "get_special_codes",
    "get_app_codes_list",
    # Sequence
    "generate_icc_sequence",
    "get_code_at_position",
    "get_position_of_code",
    "classify_code",
    "is_reserved_code",
    "is_app_code",
    "ICC_SEQUENCE",
    "ALL_RESERVED_CODES",
    "APP_CODES",
    "APP_CODES_FORMATTED",
    "VALID_COUNTRY_CODES",
    "VALID_ICC_CODES",
    # Code categories
    "SPECIAL_CODE_PURPOSES",
    "APP_CODE_PURPOSES",
    "CODE_RULES",
    "get_special_code_purpose",
    "get_app_code_purpose",
    "get_all_special_codes",
    "get_all_app_codes",
    "get_code_rules",
    # ISN
    "parse_isn",
    "validate_isn",
    "is_valid_isn",
    "format_isn",
    "generate_isn",
    "get_country_from_isn",
    "ISNComponents",
    "ISNValidationResult",
    # Data
    "COUNTRIES",
    "TOTAL_COUNTRIES",
    # Exceptions
    "ICCError",
    "InvalidICCCode",
    "CountryNotFound",
    "InvalidInputError",
    "InvalidISNError",
    "ReservedCodeError",
    # Modules
    "voip",
    "blockchain",
]
