"""
ICC — Internet Calling Code Library
Blockchain integration helpers.

Provides utilities for integrating ICC codes with blockchain systems
including hashing, verification tokens, smart contract ABI, and encoding.
All cryptographic operations use Python's built-in hashlib (no external deps).
"""

import hashlib
import json
import struct
import time
from typing import Dict, Optional

from icc.data import _BY_ICC
from icc.exceptions import InvalidICCCode


def _get_country(icc_code: int) -> Dict:
    """Internal helper to get country by ICC code."""
    country = _BY_ICC.get(int(icc_code))
    if country is None:
        raise InvalidICCCode(icc_code)
    return country


def generate_country_hash(icc_code: int) -> str:
    """
    Generate a deterministic SHA-256 hash for a country's ICC record.

    The hash is computed over the canonical JSON representation of:
    - ICC code, country name, ISO codes, land area

    Args:
        icc_code: The 3-digit ICC code.

    Returns:
        Hex-encoded SHA-256 hash string.
    """
    country = _get_country(icc_code)
    payload = json.dumps({
        "icc_code": country["icc_code"],
        "name": country["name"],
        "iso_alpha2": country["iso_alpha2"],
        "iso_alpha3": country["iso_alpha3"],
        "iso_numeric": country["iso_numeric"],
        "land_area_km2": country["land_area_km2"],
    }, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generate_verification_token(
    icc_code: int,
    timestamp: Optional[str] = None,
    secret: str = "icc-default-secret",
) -> str:
    """
    Generate an HMAC-based verification token for an ICC code.

    Useful for verifying ICC code authenticity in distributed systems.

    Args:
        icc_code: The 3-digit ICC code.
        timestamp: ISO 8601 timestamp (defaults to current UTC time).
        secret: Shared secret for HMAC computation.

    Returns:
        Hex-encoded HMAC-SHA256 token.
    """
    import hmac

    country = _get_country(icc_code)
    if timestamp is None:
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    message = f"{icc_code}:{country['name']}:{country['iso_alpha2']}:{timestamp}"
    token = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return token


def verify_icc_hash(icc_code: int, hash_value: str) -> bool:
    """
    Verify that a hash matches the expected hash for an ICC code.

    Args:
        icc_code: The 3-digit ICC code.
        hash_value: The hash to verify.

    Returns:
        True if the hash matches, False otherwise.
    """
    try:
        expected = generate_country_hash(icc_code)
        return expected == hash_value.strip().lower()
    except InvalidICCCode:
        return False


def encode_for_chain(icc_code: int) -> bytes:
    """
    ABI-encode ICC data for smart contract interaction.

    Encodes the ICC code, ISO numeric code, and land area as
    uint256 values suitable for EVM-compatible chains.

    Args:
        icc_code: The 3-digit ICC code.

    Returns:
        ABI-encoded bytes (96 bytes: 3 x uint256).
    """
    country = _get_country(icc_code)
    # Encode as 3 x uint256 (32 bytes each)
    icc_encoded = icc_code.to_bytes(32, byteorder="big")
    iso_encoded = int(country["iso_numeric"]).to_bytes(32, byteorder="big")
    area_encoded = country["land_area_km2"].to_bytes(32, byteorder="big")
    return icc_encoded + iso_encoded + area_encoded


def get_smart_contract_abi() -> Dict:
    """
    Get the Solidity ABI for an ICC Registry smart contract.

    This ABI defines the interface for an on-chain ICC code registry
    that can be deployed on EVM-compatible blockchains (Ethereum, Polygon, etc.).

    Returns:
        Dict containing the contract ABI and deployment metadata.
    """
    return {
        "contractName": "ICCRegistry",
        "version": "1.0.0",
        "license": "MIT",
        "abi": [
            {
                "name": "registerCountry",
                "type": "function",
                "stateMutability": "nonpayable",
                "inputs": [
                    {"name": "iccCode", "type": "uint256"},
                    {"name": "isoNumeric", "type": "uint256"},
                    {"name": "landAreaKm2", "type": "uint256"},
                    {"name": "name", "type": "string"},
                    {"name": "isoAlpha2", "type": "string"},
                ],
                "outputs": [{"name": "success", "type": "bool"}],
            },
            {
                "name": "getCountry",
                "type": "function",
                "stateMutability": "view",
                "inputs": [{"name": "iccCode", "type": "uint256"}],
                "outputs": [
                    {"name": "isoNumeric", "type": "uint256"},
                    {"name": "landAreaKm2", "type": "uint256"},
                    {"name": "name", "type": "string"},
                    {"name": "isoAlpha2", "type": "string"},
                ],
            },
            {
                "name": "verifyHash",
                "type": "function",
                "stateMutability": "view",
                "inputs": [
                    {"name": "iccCode", "type": "uint256"},
                    {"name": "expectedHash", "type": "bytes32"},
                ],
                "outputs": [{"name": "valid", "type": "bool"}],
            },
            {
                "name": "getCodeCount",
                "type": "function",
                "stateMutability": "view",
                "inputs": [],
                "outputs": [{"name": "count", "type": "uint256"}],
            },
            {
                "name": "CountryRegistered",
                "type": "event",
                "inputs": [
                    {"name": "iccCode", "type": "uint256", "indexed": True},
                    {"name": "name", "type": "string", "indexed": False},
                    {"name": "registeredBy", "type": "address", "indexed": True},
                ],
            },
        ],
    }


def generate_merkle_leaf(icc_code: int) -> str:
    """
    Generate a Merkle tree leaf hash for an ICC record.

    Useful for building Merkle proofs of ICC code assignments.

    Args:
        icc_code: The 3-digit ICC code.

    Returns:
        Hex-encoded leaf hash.
    """
    country = _get_country(icc_code)
    data = encode_for_chain(icc_code)
    name_bytes = country["name"].encode("utf-8")
    leaf_data = data + len(name_bytes).to_bytes(32, byteorder="big") + name_bytes
    return hashlib.sha256(leaf_data).hexdigest()
