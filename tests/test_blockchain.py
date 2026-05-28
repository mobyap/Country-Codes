"""Tests for ICC blockchain integration helpers."""

import pytest
from icc.blockchain import (
    generate_country_hash,
    generate_verification_token,
    verify_icc_hash,
    encode_for_chain,
    get_smart_contract_abi,
    generate_merkle_leaf,
)
from icc.exceptions import InvalidICCCode


class TestGenerateCountryHash:
    def test_deterministic(self):
        h1 = generate_country_hash(700)
        h2 = generate_country_hash(700)
        assert h1 == h2

    def test_different_countries(self):
        h1 = generate_country_hash(100)
        h2 = generate_country_hash(700)
        assert h1 != h2

    def test_is_hex_sha256(self):
        h = generate_country_hash(100)
        assert len(h) == 64  # SHA-256 hex length
        assert all(c in "0123456789abcdef" for c in h)

    def test_invalid_code(self):
        with pytest.raises(InvalidICCCode):
            generate_country_hash(999)


class TestVerifyIccHash:
    def test_valid_hash(self):
        h = generate_country_hash(700)
        assert verify_icc_hash(700, h) is True

    def test_invalid_hash(self):
        assert verify_icc_hash(700, "0" * 64) is False

    def test_invalid_code(self):
        assert verify_icc_hash(999, "0" * 64) is False


class TestGenerateVerificationToken:
    def test_basic(self):
        token = generate_verification_token(700, timestamp="2024-01-01T00:00:00Z")
        assert len(token) == 64

    def test_deterministic_with_same_inputs(self):
        t1 = generate_verification_token(700, "2024-01-01T00:00:00Z", "secret")
        t2 = generate_verification_token(700, "2024-01-01T00:00:00Z", "secret")
        assert t1 == t2

    def test_different_secrets(self):
        t1 = generate_verification_token(700, "2024-01-01T00:00:00Z", "secret1")
        t2 = generate_verification_token(700, "2024-01-01T00:00:00Z", "secret2")
        assert t1 != t2


class TestEncodeForChain:
    def test_output_length(self):
        data = encode_for_chain(700)
        assert len(data) == 96  # 3 x uint256 (32 bytes each)

    def test_is_bytes(self):
        data = encode_for_chain(700)
        assert isinstance(data, bytes)

    def test_icc_code_embedded(self):
        data = encode_for_chain(700)
        # First 32 bytes should encode 700
        icc_value = int.from_bytes(data[:32], byteorder="big")
        assert icc_value == 700


class TestGetSmartContractAbi:
    def test_structure(self):
        abi = get_smart_contract_abi()
        assert abi["contractName"] == "ICCRegistry"
        assert abi["license"] == "MIT"
        assert isinstance(abi["abi"], list)
        assert len(abi["abi"]) > 0

    def test_has_register_function(self):
        abi = get_smart_contract_abi()
        names = [item["name"] for item in abi["abi"]]
        assert "registerCountry" in names
        assert "getCountry" in names
        assert "verifyHash" in names


class TestGenerateMerkleLeaf:
    def test_deterministic(self):
        l1 = generate_merkle_leaf(700)
        l2 = generate_merkle_leaf(700)
        assert l1 == l2

    def test_different_countries(self):
        l1 = generate_merkle_leaf(100)
        l2 = generate_merkle_leaf(700)
        assert l1 != l2

    def test_is_hex_sha256(self):
        leaf = generate_merkle_leaf(100)
        assert len(leaf) == 64
