"""Tests for ICC VOIP integration helpers."""

import pytest
from icc.voip import (
    generate_sip_uri,
    get_e164_mapping,
    generate_dial_string,
    get_sip_header,
    icc_to_e164_prefix,
    generate_voip_config,
)
from icc.exceptions import InvalidICCCode


class TestGenerateSipUri:
    def test_basic(self):
        uri = generate_sip_uri(700, "alice")
        assert uri == "sip:alice@icc-700.icc.net"

    def test_custom_domain(self):
        uri = generate_sip_uri(700, "alice", domain="example.com")
        assert uri == "sip:alice@icc-700.example.com"

    def test_invalid_code(self):
        with pytest.raises(InvalidICCCode):
            generate_sip_uri(999, "alice")


class TestGetE164Mapping:
    def test_india(self):
        m = get_e164_mapping(700)
        assert m["country"] == "India"
        assert m["e164_code"] == "+91"
        assert m["iso_alpha2"] == "IN"

    def test_usa(self):
        m = get_e164_mapping(300)
        assert m["country"] == "United States"
        assert m["e164_code"] == "+1"


class TestGenerateDialString:
    def test_basic(self):
        ds = generate_dial_string(700, "9876543210")
        assert "SIP" in ds
        assert "+91" in ds
        assert "icc-700" in ds

    def test_strips_leading_zero(self):
        ds = generate_dial_string(700, "09876543210")
        assert "+919876543210" in ds


class TestGetSipHeader:
    def test_basic(self):
        headers = get_sip_header(700)
        assert headers["X-ICC-Code"] == "700"
        assert headers["X-ICC-Country"] == "India"
        assert headers["X-ICC-ISO"] == "IN"
        assert "P-Asserted-Identity" in headers

    def test_with_call_id(self):
        headers = get_sip_header(700, call_id="abc-123")
        assert headers["Call-ID"] == "abc-123"


class TestIccToE164Prefix:
    def test_india(self):
        assert icc_to_e164_prefix(700) == "+91"

    def test_russia(self):
        assert icc_to_e164_prefix(100) == "+7"


class TestGenerateVoipConfig:
    def test_basic(self):
        config = generate_voip_config(700, "bob")
        assert config["sip_uri"] == "sip:bob@icc-700.icc.net"
        assert config["e164_prefix"] == "+91"
        assert config["country"] == "India"
        assert "G.711" in config["codecs"]
        assert "OPUS" in config["codecs"]
        assert isinstance(config["sip_headers"], dict)
