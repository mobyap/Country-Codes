"""
ICC API — Code classification and category routes.

Author: Mobyap (mobyap.com@gmail.com)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

from icc.sequence import classify_code, is_reserved_code, is_app_code
from icc.codes import (
    get_all_special_codes,
    get_all_app_codes,
    get_code_rules,
    get_special_code_purpose,
    get_app_code_purpose,
)

router = APIRouter(prefix="/codes", tags=["Code Categories"])


# ── Response Models ──────────────────────────────────────────────────────────

class SpecialCodeItem(BaseModel):
    """A single special code entry."""
    code: int
    formatted: str
    purpose: str
    category: str


class SpecialCodesResponse(BaseModel):
    """All reserved special codes."""
    total: int
    codes: List[SpecialCodeItem]


class AppCodeItem(BaseModel):
    """A single app code entry."""
    code: int
    formatted: str
    purpose: str


class AppCodesResponse(BaseModel):
    """All Mobyap app codes."""
    total: int
    codes: List[AppCodeItem]


class CodeClassifyResponse(BaseModel):
    """Code classification result."""
    code: int
    code_type: str = Field(..., description="One of: country, special, app, invalid")
    is_reserved: bool
    is_app: bool
    purpose: Optional[str] = None


class CodeRulesResponse(BaseModel):
    """ICC code assignment rules."""
    rules: Dict[str, str]


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get(
    "/special",
    response_model=SpecialCodesResponse,
    summary="List special codes",
)
def list_special_codes():
    """
    List all reserved special codes with their designated global purposes.

    Special codes are used for institutional and service communications
    across all countries (education, emergency, military, etc.).
    """
    codes = get_all_special_codes()
    return SpecialCodesResponse(total=len(codes), codes=codes)


@router.get(
    "/app",
    response_model=AppCodesResponse,
    summary="List Mobyap app codes",
)
def list_app_codes():
    """
    List all Mobyap blockchain VOIP application codes.

    App codes are reserved exclusively for the Mobyap blockchain-based
    VOIP application. They always start with 0 and end with 0.
    """
    codes = get_all_app_codes()
    return AppCodesResponse(total=len(codes), codes=codes)


@router.get(
    "/classify/{code}",
    response_model=CodeClassifyResponse,
    summary="Classify a code",
)
def classify(code: int):
    """
    Classify a code into its category: country, special, app, or invalid.

    Also returns whether the code is reserved and its purpose (if applicable).
    """
    code_type = classify_code(code)
    purpose = None

    if code_type == "special":
        purpose = get_special_code_purpose(code)
    elif code_type == "app":
        purpose = get_app_code_purpose(code)

    return CodeClassifyResponse(
        code=code,
        code_type=code_type,
        is_reserved=is_reserved_code(code),
        is_app=is_app_code(code),
        purpose=purpose,
    )


@router.get(
    "/rules",
    response_model=CodeRulesResponse,
    summary="Get code rules",
)
def code_rules():
    """
    Get the complete set of ICC code assignment rules.

    Documents the rules for country codes, special codes, and app codes.
    """
    return CodeRulesResponse(rules=get_code_rules())
