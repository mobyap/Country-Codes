"""
ICC API — Blockchain integration routes.
"""

import time

from fastapi import APIRouter, HTTPException, Query

from api.models import (
    HashResponse,
    VerifyHashRequest,
    VerifyHashResponse,
    TokenResponse,
    AbiResponse,
    EncodeResponse,
    MerkleLeafResponse,
)
from icc.blockchain import (
    generate_country_hash,
    generate_verification_token,
    verify_icc_hash,
    encode_for_chain,
    get_smart_contract_abi,
    generate_merkle_leaf,
)
from icc.data import _BY_ICC
from icc.exceptions import InvalidICCCode

router = APIRouter(prefix="/blockchain", tags=["Blockchain"])


def _get_country_name(icc_code: int) -> str:
    country = _BY_ICC.get(icc_code)
    if country is None:
        raise InvalidICCCode(icc_code)
    return country["name"]


@router.get(
    "/hash/{icc_code}",
    response_model=HashResponse,
    summary="Get country hash",
)
def country_hash(icc_code: int):
    """Generate a deterministic SHA-256 hash for a country's ICC record."""
    try:
        h = generate_country_hash(icc_code)
        return HashResponse(
            icc_code=icc_code,
            country=_get_country_name(icc_code),
            hash=h,
        )
    except InvalidICCCode:
        raise HTTPException(status_code=404, detail=f"Invalid ICC code: {icc_code}")


@router.post(
    "/verify",
    response_model=VerifyHashResponse,
    summary="Verify a hash",
)
def verify_hash(request: VerifyHashRequest):
    """Verify that a hash matches the expected hash for an ICC code."""
    valid = verify_icc_hash(request.icc_code, request.hash)
    return VerifyHashResponse(icc_code=request.icc_code, valid=valid)


@router.get(
    "/token/{icc_code}",
    response_model=TokenResponse,
    summary="Generate verification token",
)
def verification_token(
    icc_code: int,
    secret: str = Query(default="icc-default-secret", description="HMAC secret"),
):
    """Generate an HMAC-based verification token for an ICC code."""
    try:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        token = generate_verification_token(icc_code, ts, secret)
        return TokenResponse(
            icc_code=icc_code,
            country=_get_country_name(icc_code),
            token=token,
            timestamp=ts,
        )
    except InvalidICCCode:
        raise HTTPException(status_code=404, detail=f"Invalid ICC code: {icc_code}")


@router.get(
    "/abi",
    response_model=AbiResponse,
    summary="Get smart contract ABI",
)
def smart_contract_abi():
    """Get the Solidity ABI for the ICC Registry smart contract."""
    return get_smart_contract_abi()


@router.get(
    "/encode/{icc_code}",
    response_model=EncodeResponse,
    summary="ABI-encode ICC data",
)
def encode_data(icc_code: int):
    """ABI-encode ICC data for smart contract interaction."""
    try:
        data = encode_for_chain(icc_code)
        return EncodeResponse(
            icc_code=icc_code,
            country=_get_country_name(icc_code),
            encoded_hex=data.hex(),
            byte_length=len(data),
        )
    except InvalidICCCode:
        raise HTTPException(status_code=404, detail=f"Invalid ICC code: {icc_code}")


@router.get(
    "/merkle-leaf/{icc_code}",
    response_model=MerkleLeafResponse,
    summary="Get Merkle leaf hash",
)
def merkle_leaf(icc_code: int):
    """Generate a Merkle tree leaf hash for an ICC record."""
    try:
        leaf = generate_merkle_leaf(icc_code)
        return MerkleLeafResponse(
            icc_code=icc_code,
            country=_get_country_name(icc_code),
            leaf_hash=leaf,
        )
    except InvalidICCCode:
        raise HTTPException(status_code=404, detail=f"Invalid ICC code: {icc_code}")
