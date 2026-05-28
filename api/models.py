"""
ICC API — Pydantic models for request/response schemas.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ── Response Models ──────────────────────────────────────────────────────────

class CountryResponse(BaseModel):
    """Full country record."""
    rank: int = Field(..., description="Rank by land area (1 = largest)")
    name: str = Field(..., description="Common country name")
    official_name: str = Field(..., description="Official country name")
    iso_alpha2: str = Field(..., description="ISO 3166-1 alpha-2 code")
    iso_alpha3: str = Field(..., description="ISO 3166-1 alpha-3 code")
    iso_numeric: str = Field(..., description="ISO 3166-1 numeric code")
    land_area_km2: int = Field(..., description="Total land area in km²")
    icc_code: int = Field(..., description="3-digit ICC code")
    continent: str = Field(..., description="Continent")
    phone_code: str = Field(..., description="E.164 calling code")


class CountryListResponse(BaseModel):
    """List of countries."""
    total: int
    countries: List[CountryResponse]


class ValidationResponse(BaseModel):
    """ICC code validation result."""
    code: int
    is_valid: bool
    is_assigned: bool
    country: Optional[str] = None


class BulkValidationRequest(BaseModel):
    """Request body for bulk validation."""
    codes: List[int] = Field(..., description="List of ICC codes to validate")


class BulkValidationResponse(BaseModel):
    """Response for bulk validation."""
    results: List[ValidationResponse]


class SipUriResponse(BaseModel):
    """SIP URI generation result."""
    icc_code: int
    country: str
    sip_uri: str


class E164MappingResponse(BaseModel):
    """E.164 mapping result."""
    icc_code: int
    country: str
    e164_code: str
    iso_alpha2: str
    iso_alpha3: str


class DialStringResponse(BaseModel):
    """Dial string result."""
    icc_code: int
    country: str
    dial_string: str


class SipHeaderResponse(BaseModel):
    """SIP header fields."""
    icc_code: int
    country: str
    headers: Dict[str, str]


class VoipConfigResponse(BaseModel):
    """Full VOIP configuration."""
    sip_uri: str
    registrar: str
    proxy: str
    e164_prefix: str
    country: str
    iso_alpha2: str
    icc_code: int
    transport: str
    codecs: List[str]
    sip_headers: Dict[str, str]


class HashResponse(BaseModel):
    """Country hash result."""
    icc_code: int
    country: str
    algorithm: str = "SHA-256"
    hash: str


class VerifyHashRequest(BaseModel):
    """Hash verification request."""
    icc_code: int
    hash: str


class VerifyHashResponse(BaseModel):
    """Hash verification result."""
    icc_code: int
    valid: bool


class TokenResponse(BaseModel):
    """Verification token result."""
    icc_code: int
    country: str
    token: str
    timestamp: str


class AbiResponse(BaseModel):
    """Smart contract ABI."""
    contractName: str
    version: str
    license: str
    abi: List[Dict]


class EncodeResponse(BaseModel):
    """ABI-encoded data."""
    icc_code: int
    country: str
    encoded_hex: str
    byte_length: int


class MerkleLeafResponse(BaseModel):
    """Merkle leaf hash."""
    icc_code: int
    country: str
    leaf_hash: str


class StatsResponse(BaseModel):
    """System statistics."""
    total_countries: int
    total_icc_codes_available: int
    codes_assigned: int
    codes_unassigned: int
    total_land_area_km2: int
    continents: Dict[str, int]
    largest_country: str
    smallest_country: str


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: str
    code: int
