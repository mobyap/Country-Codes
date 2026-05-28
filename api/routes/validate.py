"""
ICC API — Validation routes.
"""

from fastapi import APIRouter, HTTPException

from api.models import (
    ValidationResponse,
    BulkValidationRequest,
    BulkValidationResponse,
)
from icc.core import validate_icc, is_valid_icc_code, get_country_by_icc
from icc.exceptions import InvalidICCCode

router = APIRouter(prefix="/validate", tags=["Validation"])


@router.get(
    "/{icc_code}",
    response_model=ValidationResponse,
    summary="Validate an ICC code",
)
def validate(icc_code: int):
    """
    Validate whether an ICC code is valid and assigned to a country.

    Returns validity status and the assigned country name if applicable.
    """
    is_assigned = validate_icc(icc_code)
    is_valid = is_valid_icc_code(icc_code)
    country_name = None
    if is_assigned:
        try:
            country_name = get_country_by_icc(icc_code)["name"]
        except InvalidICCCode:
            pass
    return ValidationResponse(
        code=icc_code,
        is_valid=is_valid,
        is_assigned=is_assigned,
        country=country_name,
    )


@router.post(
    "/bulk",
    response_model=BulkValidationResponse,
    summary="Bulk validate ICC codes",
)
def bulk_validate(request: BulkValidationRequest):
    """
    Validate multiple ICC codes in a single request.

    Accepts a list of ICC codes and returns validation results for each.
    """
    if len(request.codes) > 200:
        raise HTTPException(status_code=400, detail="Maximum 200 codes per request")

    results = []
    for code in request.codes:
        is_assigned = validate_icc(code)
        is_valid = is_valid_icc_code(code)
        country_name = None
        if is_assigned:
            try:
                country_name = get_country_by_icc(code)["name"]
            except InvalidICCCode:
                pass
        results.append(ValidationResponse(
            code=code,
            is_valid=is_valid,
            is_assigned=is_assigned,
            country=country_name,
        ))
    return BulkValidationResponse(results=results)
