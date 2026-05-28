"""
ICC — Internet Calling Code Library
VOIP integration helpers.

Provides utilities for integrating ICC codes with VOIP systems including
SIP URI generation, E.164 mapping, dial string formatting, and SIP headers.
"""

from typing import Dict, Optional

from icc.data import _BY_ICC
from icc.exceptions import InvalidICCCode


def _get_country(icc_code: int) -> Dict:
    """Internal helper to get country by ICC code."""
    country = _BY_ICC.get(int(icc_code))
    if country is None:
        raise InvalidICCCode(icc_code)
    return country


def generate_sip_uri(icc_code: int, user: str, domain: str = "icc.net") -> str:
    """
    Generate a SIP URI using ICC code as the routing domain.

    Args:
        icc_code: The 3-digit ICC code.
        user: The SIP user identifier.
        domain: Base domain (default: "icc.net").

    Returns:
        SIP URI string, e.g., "sip:user@icc-700.icc.net"

    Raises:
        InvalidICCCode: If the ICC code is not valid.
    """
    country = _get_country(icc_code)
    return f"sip:{user}@icc-{icc_code}.{domain}"


def get_e164_mapping(icc_code: int) -> Dict:
    """
    Get the E.164 phone code mapping for an ICC code.

    Args:
        icc_code: The 3-digit ICC code.

    Returns:
        Dict with ICC code, country name, E.164 phone code, and ISO codes.
    """
    country = _get_country(icc_code)
    return {
        "icc_code": icc_code,
        "country": country["name"],
        "e164_code": country["phone_code"],
        "iso_alpha2": country["iso_alpha2"],
        "iso_alpha3": country["iso_alpha3"],
    }


def generate_dial_string(
    icc_code: int,
    number: str,
    protocol: str = "SIP",
    gateway: str = "gw.icc.net",
) -> str:
    """
    Generate a VOIP dial string for routing calls via ICC.

    Args:
        icc_code: The destination ICC code.
        number: The phone number to dial (local format).
        protocol: Protocol identifier (default: "SIP").
        gateway: Gateway hostname.

    Returns:
        Formatted dial string for VOIP systems.
    """
    country = _get_country(icc_code)
    e164 = country["phone_code"]
    # Strip leading zeros from number
    clean_number = number.lstrip("0")
    return f"{protocol}/{gateway}/{e164}{clean_number}@icc-{icc_code}"


def get_sip_header(icc_code: int, call_id: Optional[str] = None) -> Dict:
    """
    Generate SIP header fields enriched with ICC metadata.

    These headers can be added to SIP INVITE messages for ICC-aware routing.

    Args:
        icc_code: The 3-digit ICC code.
        call_id: Optional SIP Call-ID.

    Returns:
        Dict of SIP header field names and values.
    """
    country = _get_country(icc_code)
    headers = {
        "X-ICC-Code": str(icc_code),
        "X-ICC-Country": country["name"],
        "X-ICC-ISO": country["iso_alpha2"],
        "X-ICC-Region": country["continent"],
        "X-ICC-E164": country["phone_code"],
        "P-Asserted-Identity": f"sip:icc-{icc_code}@icc.net",
    }
    if call_id:
        headers["Call-ID"] = call_id
    return headers


def icc_to_e164_prefix(icc_code: int) -> str:
    """
    Get the E.164 calling prefix for an ICC code.

    Args:
        icc_code: The 3-digit ICC code.

    Returns:
        E.164 prefix string (e.g., "+91" for India).
    """
    country = _get_country(icc_code)
    return country["phone_code"]


def generate_voip_config(icc_code: int, user: str, domain: str = "icc.net") -> Dict:
    """
    Generate a complete VOIP configuration block for a given ICC destination.

    Useful for auto-configuring softphones and VOIP gateways.

    Args:
        icc_code: The 3-digit ICC code.
        user: SIP user identifier.
        domain: Base domain.

    Returns:
        Dict with SIP URI, dial prefix, headers, and routing info.
    """
    country = _get_country(icc_code)
    return {
        "sip_uri": f"sip:{user}@icc-{icc_code}.{domain}",
        "registrar": f"sip:registrar.icc-{icc_code}.{domain}",
        "proxy": f"sip:proxy.icc-{icc_code}.{domain}",
        "e164_prefix": country["phone_code"],
        "country": country["name"],
        "iso_alpha2": country["iso_alpha2"],
        "icc_code": icc_code,
        "transport": "UDP",
        "codecs": ["G.711", "G.729", "OPUS"],
        "sip_headers": get_sip_header(icc_code),
    }
