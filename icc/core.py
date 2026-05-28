"""
ICC — Internet Calling Code Library
Core lookup, validation, and utility functions.

Author: Mobyap (mobyap.com@gmail.com)
License: MIT
"""

from typing import Dict, List, Optional, Union

from icc.data import (
    COUNTRIES, TOTAL_COUNTRIES,
    _BY_ICC, _BY_ISO2, _BY_ISO3, _BY_NAME, _BY_OFFICIAL,
)
from icc.exceptions import InvalidICCCode, CountryNotFound, InvalidInputError
from icc.sequence import (
    VALID_COUNTRY_CODES,
    VALID_ICC_CODES,
    ALL_RESERVED_CODES,
    APP_CODES,
    classify_code,
    is_reserved_code,
    is_app_code,
)
from icc.codes import (
    SPECIAL_CODE_PURPOSES,
    APP_CODE_PURPOSES,
    get_all_special_codes,
    get_all_app_codes,
    get_code_rules,
)


def get_country_by_icc(code: Union[int, str]) -> Dict:
    """
    Look up a country by its ICC code.

    Args:
        code: ICC code as integer (e.g., 100) or string (e.g., "100").

    Returns:
        Country dict with all fields.

    Raises:
        InvalidICCCode: If the code is not assigned.
    """
    code = int(code)
    country = _BY_ICC.get(code)
    if country is None:
        raise InvalidICCCode(code)
    return dict(country)


def get_country_by_name(name: str) -> Dict:
    """
    Look up a country by its common or official name (case-insensitive).

    Args:
        name: Country name (e.g., "India", "Republic of India").

    Returns:
        Country dict.

    Raises:
        CountryNotFound: If no match is found.
    """
    if not name:
        raise InvalidInputError(name, "non-empty country name")
    key = name.strip().lower()
    country = _BY_NAME.get(key) or _BY_OFFICIAL.get(key)
    if country is None:
        raise CountryNotFound(name)
    return dict(country)


def get_country_by_iso(iso_code: str) -> Dict:
    """
    Look up a country by ISO 3166-1 alpha-2 or alpha-3 code.

    Args:
        iso_code: ISO code (e.g., "IN", "IND", "us", "usa").

    Returns:
        Country dict.

    Raises:
        CountryNotFound: If no match is found.
    """
    if not iso_code:
        raise InvalidInputError(iso_code, "ISO alpha-2 or alpha-3 code")
    code = iso_code.strip().upper()
    country = _BY_ISO2.get(code) or _BY_ISO3.get(code)
    if country is None:
        raise CountryNotFound(iso_code)
    return dict(country)


def get_icc_by_country(name: str) -> int:
    """
    Get the ICC code for a country by name.

    Args:
        name: Country name.

    Returns:
        The 3-digit ICC code.
    """
    return get_country_by_name(name)["icc_code"]


def validate_icc(code: Union[int, str]) -> bool:
    """
    Check if an ICC code is valid and assigned to a country.

    Args:
        code: ICC code to validate.

    Returns:
        True if valid and assigned, False otherwise.
    """
    try:
        code = int(code)
    except (ValueError, TypeError):
        return False
    return code in _BY_ICC


def is_valid_icc_code(code: Union[int, str]) -> bool:
    """
    Check if an ICC code is a valid 3-digit code in the sequence
    (may or may not be assigned to a country).

    This includes both country-assignable codes and reserved special codes
    (all codes in the 100–999 range that are part of the ICC system).

    Args:
        code: ICC code to check.

    Returns:
        True if the code exists in the ICC system (country or reserved).
    """
    try:
        code = int(code)
    except (ValueError, TypeError):
        return False
    return code in VALID_ICC_CODES


def get_code_info(code: Union[int, str]) -> Dict:
    """
    Get comprehensive information about any ICC code.

    Works for country codes, reserved special codes, and app codes.

    Args:
        code: An ICC code (integer or string).

    Returns:
        Dict with:
          - code: The numeric code
          - code_type: "country", "special", "app", or "invalid"
          - is_assigned: Whether assigned to a country
          - country: Country name (if assigned, else None)
          - purpose: Purpose description (for special/app codes, else None)
    """
    try:
        code = int(code)
    except (ValueError, TypeError):
        return {
            "code": code,
            "code_type": "invalid",
            "is_assigned": False,
            "country": None,
            "purpose": None,
        }

    code_type = classify_code(code)
    country_name = None
    purpose = None

    if code_type == "country":
        country = _BY_ICC.get(code)
        if country:
            country_name = country["name"]

    elif code_type == "special":
        purpose = SPECIAL_CODE_PURPOSES.get(code, "Reserved")

    elif code_type == "app":
        purpose = APP_CODE_PURPOSES.get(code, "Mobyap Blockchain VOIP")

    return {
        "code": code,
        "code_type": code_type,
        "is_assigned": country_name is not None,
        "country": country_name,
        "purpose": purpose,
    }


def list_all_countries() -> List[Dict]:
    """
    List all countries with their ICC codes, sorted by rank (land area).

    Returns:
        List of country dicts.
    """
    return [dict(c) for c in COUNTRIES]


def search_countries(query: str) -> List[Dict]:
    """
    Search countries by partial name or ICC code.

    Args:
        query: Search string (partial name or code).

    Returns:
        List of matching country dicts.
    """
    if not query:
        return []
    query_lower = query.strip().lower()
    results = []
    for country in COUNTRIES:
        if (
            query_lower in country["name"].lower()
            or query_lower in country["official_name"].lower()
            or query_lower in country["iso_alpha2"].lower()
            or query_lower in country["iso_alpha3"].lower()
            or query_lower == str(country["icc_code"])
        ):
            results.append(dict(country))
    return results


def get_countries_by_continent(continent: str) -> List[Dict]:
    """
    Get all countries in a given continent.

    Args:
        continent: Continent name (e.g., "Asia", "Europe", "Africa").

    Returns:
        List of country dicts in that continent.
    """
    if not continent:
        return []
    continent_lower = continent.strip().lower()
    return [
        dict(c) for c in COUNTRIES
        if continent_lower in c["continent"].lower()
    ]


def get_continents() -> List[str]:
    """
    Get a list of all continents represented in the data.

    Returns:
        Sorted list of unique continent names.
    """
    return sorted(set(c["continent"] for c in COUNTRIES))


def get_statistics() -> Dict:
    """
    Get summary statistics about the ICC code system.

    Returns:
        Dict with total countries, codes, reserved/app code counts, etc.
    """
    continent_counts = {}
    for c in COUNTRIES:
        cont = c["continent"]
        continent_counts[cont] = continent_counts.get(cont, 0) + 1

    total_area = sum(c["land_area_km2"] for c in COUNTRIES)
    return {
        "total_countries": TOTAL_COUNTRIES,
        "total_country_codes_available": len(VALID_COUNTRY_CODES),
        "total_icc_codes_available": len(VALID_ICC_CODES),
        "codes_assigned": TOTAL_COUNTRIES,
        "codes_unassigned": len(VALID_COUNTRY_CODES) - TOTAL_COUNTRIES,
        "reserved_special_codes": len(ALL_RESERVED_CODES),
        "app_codes": len(APP_CODES),
        "total_land_area_km2": total_area,
        "continents": continent_counts,
        "largest_country": COUNTRIES[0]["name"],
        "smallest_country": COUNTRIES[-1]["name"],
    }


def get_special_codes() -> List[Dict]:
    """
    Get all reserved special codes with their designated purposes.

    Returns:
        List of dicts with code, purpose, and category.
    """
    return get_all_special_codes()


def get_app_codes_list() -> List[Dict]:
    """
    Get all Mobyap app codes with their purposes.

    Returns:
        List of dicts with code, formatted code, and purpose.
    """
    return get_all_app_codes()
