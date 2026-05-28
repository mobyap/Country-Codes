"""
ICC API — VOIP integration routes.
"""

from fastapi import APIRouter, HTTPException, Query

from api.models import (
    SipUriResponse,
    E164MappingResponse,
    DialStringResponse,
    SipHeaderResponse,
    VoipConfigResponse,
)
from icc.voip import (
    generate_sip_uri,
    get_e164_mapping,
    generate_dial_string,
    get_sip_header,
    icc_to_e164_prefix,
    generate_voip_config,
)
from icc.exceptions import InvalidICCCode

router = APIRouter(prefix="/voip", tags=["VOIP"])


@router.get(
    "/sip-uri/{icc_code}",
    response_model=SipUriResponse,
    summary="Generate SIP URI",
)
def sip_uri(
    icc_code: int,
    user: str = Query(default="caller", description="SIP user identifier"),
    domain: str = Query(default="icc.net", description="Base domain"),
):
    """Generate a SIP URI for a given ICC code and user."""
    try:
        uri = generate_sip_uri(icc_code, user, domain)
        mapping = get_e164_mapping(icc_code)
        return SipUriResponse(
            icc_code=icc_code,
            country=mapping["country"],
            sip_uri=uri,
        )
    except InvalidICCCode:
        raise HTTPException(status_code=404, detail=f"Invalid ICC code: {icc_code}")


@router.get(
    "/e164/{icc_code}",
    response_model=E164MappingResponse,
    summary="Get E.164 mapping",
)
def e164_mapping(icc_code: int):
    """Get the E.164 phone code mapping for an ICC code."""
    try:
        return get_e164_mapping(icc_code)
    except InvalidICCCode:
        raise HTTPException(status_code=404, detail=f"Invalid ICC code: {icc_code}")


@router.get(
    "/dial-string/{icc_code}",
    response_model=DialStringResponse,
    summary="Generate dial string",
)
def dial_string(
    icc_code: int,
    number: str = Query(..., description="Phone number to dial (local format)"),
    protocol: str = Query(default="SIP", description="Protocol (SIP, IAX2, etc.)"),
):
    """Generate a VOIP dial string for routing calls via ICC."""
    try:
        ds = generate_dial_string(icc_code, number, protocol)
        mapping = get_e164_mapping(icc_code)
        return DialStringResponse(
            icc_code=icc_code,
            country=mapping["country"],
            dial_string=ds,
        )
    except InvalidICCCode:
        raise HTTPException(status_code=404, detail=f"Invalid ICC code: {icc_code}")


@router.get(
    "/sip-headers/{icc_code}",
    response_model=SipHeaderResponse,
    summary="Get SIP headers",
)
def sip_headers(
    icc_code: int,
    call_id: str = Query(default=None, description="Optional SIP Call-ID"),
):
    """Generate SIP header fields enriched with ICC metadata."""
    try:
        headers = get_sip_header(icc_code, call_id)
        mapping = get_e164_mapping(icc_code)
        return SipHeaderResponse(
            icc_code=icc_code,
            country=mapping["country"],
            headers=headers,
        )
    except InvalidICCCode:
        raise HTTPException(status_code=404, detail=f"Invalid ICC code: {icc_code}")


@router.get(
    "/config/{icc_code}",
    response_model=VoipConfigResponse,
    summary="Get full VOIP config",
)
def voip_config(
    icc_code: int,
    user: str = Query(default="caller", description="SIP user identifier"),
    domain: str = Query(default="icc.net", description="Base domain"),
):
    """Generate a complete VOIP configuration block for a given ICC destination."""
    try:
        return generate_voip_config(icc_code, user, domain)
    except InvalidICCCode:
        raise HTTPException(status_code=404, detail=f"Invalid ICC code: {icc_code}")
