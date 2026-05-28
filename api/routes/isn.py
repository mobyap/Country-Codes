"""
ICC API — ISN (Internet Subscriber Number) routes.

Author: Mobyap (mobyap.com@gmail.com)
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

from icc.isn import (
    parse_isn,
    validate_isn,
    format_isn,
    generate_isn,
    get_country_from_isn,
)
from icc.exceptions import InvalidISNError

router = APIRouter(prefix="/isn", tags=["ISN"])


# ── Request/Response Models ──────────────────────────────────────────────────

class ISNValidateRequest(BaseModel):
    """Request to validate an ISN."""
    isn: str = Field(..., description="ISN string to validate (e.g., '100-1234-5678-0321')")


class ISNValidateResponse(BaseModel):
    """ISN validation result."""
    isn: str
    is_valid: bool
    icc_code: Optional[int] = None
    code_type: Optional[str] = None
    country: Optional[str] = None
    region_code: Optional[str] = None
    subscriber_number: Optional[str] = None
    error: Optional[str] = None


class ISNParseResponse(BaseModel):
    """Parsed ISN components."""
    icc_code: int
    region_code: str
    subscriber_number: str
    full_number: str
    raw_digits: str
    code_type: str


class ISNGenerateResponse(BaseModel):
    """Generated ISN."""
    isn: str
    icc_code: int
    country: Optional[str] = None
    code_type: str
    region_code: str
    subscriber_number: str


class ISNFormatRequest(BaseModel):
    """Request to format ISN from components."""
    icc_code: int = Field(..., description="3-digit ICC code")
    region_code: str = Field(..., description="4-digit region/purpose code")
    subscriber: str = Field(..., description="8-digit subscriber number")


class ISNFormatResponse(BaseModel):
    """Formatted ISN result."""
    isn: str
    icc_code: int
    region_code: str
    subscriber_number: str


class ISNCountryResponse(BaseModel):
    """Country info from ISN."""
    isn: str
    icc_code: int
    country: str
    iso_alpha2: str
    iso_alpha3: str
    continent: str


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post(
    "/validate",
    response_model=ISNValidateResponse,
    summary="Validate an ISN",
)
def isn_validate(request: ISNValidateRequest):
    """
    Validate an Internet Subscriber Number (ISN).

    Checks format (ICC-RRRR-SSSS-SSSS), ICC code validity,
    and returns detailed validation information.
    """
    result = validate_isn(request.isn)
    return ISNValidateResponse(
        isn=request.isn,
        is_valid=result.is_valid,
        icc_code=result.icc_code,
        code_type=result.code_type,
        country=result.country,
        region_code=result.region_code,
        subscriber_number=result.subscriber_number,
        error=result.error,
    )


@router.post(
    "/parse",
    response_model=ISNParseResponse,
    summary="Parse ISN into components",
)
def isn_parse(request: ISNValidateRequest):
    """
    Parse an ISN string into its constituent components.

    Returns ICC code, region code, subscriber number, and code type.
    """
    try:
        components = parse_isn(request.isn)
        return ISNParseResponse(
            icc_code=components.icc_code,
            region_code=components.region_code,
            subscriber_number=components.subscriber_number,
            full_number=components.full_number,
            raw_digits=components.raw_digits,
            code_type=components.code_type,
        )
    except InvalidISNError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/generate/{icc_code}",
    response_model=ISNGenerateResponse,
    summary="Generate an ISN",
)
def isn_generate(
    icc_code: int,
    region: str = Query(default="0001", description="4-digit region/purpose code"),
    subscriber: Optional[int] = Query(default=None, description="Subscriber ID (0–99999999)"),
):
    """
    Generate an Internet Subscriber Number for a given ICC code.

    If subscriber is not provided, a random subscriber ID is generated.
    """
    try:
        isn_string = generate_isn(icc_code, region, subscriber)
        components = parse_isn(isn_string)

        country_name = None
        if components.code_type == "country":
            try:
                from icc.data import _BY_ICC
                country = _BY_ICC.get(icc_code)
                if country:
                    country_name = country["name"]
            except ImportError:
                pass

        return ISNGenerateResponse(
            isn=isn_string,
            icc_code=icc_code,
            country=country_name,
            code_type=components.code_type,
            region_code=components.region_code,
            subscriber_number=components.subscriber_number,
        )
    except InvalidISNError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/format",
    response_model=ISNFormatResponse,
    summary="Format ISN from components",
)
def isn_format(request: ISNFormatRequest):
    """
    Format an ISN from its individual components.

    Takes ICC code, region code, and subscriber number and returns
    the properly formatted ISN string.
    """
    try:
        isn_string = format_isn(
            request.icc_code, request.region_code, request.subscriber
        )
        return ISNFormatResponse(
            isn=isn_string,
            icc_code=request.icc_code,
            region_code=request.region_code,
            subscriber_number=request.subscriber,
        )
    except InvalidISNError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/country",
    response_model=ISNCountryResponse,
    summary="Get country from ISN",
)
def isn_country(request: ISNValidateRequest):
    """
    Extract country information from an ISN.

    Only works for ISNs that use a country ICC code (not special or app codes).
    """
    try:
        country = get_country_from_isn(request.isn)
        components = parse_isn(request.isn)
        return ISNCountryResponse(
            isn=request.isn,
            icc_code=components.icc_code,
            country=country["name"],
            iso_alpha2=country["iso_alpha2"],
            iso_alpha3=country["iso_alpha3"],
            continent=country["continent"],
        )
    except InvalidISNError as e:
        raise HTTPException(status_code=400, detail=str(e))
