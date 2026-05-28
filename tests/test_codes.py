"""Tests for ICC code classification and categories."""

import pytest
from icc.codes import (
    get_special_code_purpose,
    get_app_code_purpose,
    get_all_special_codes,
    get_all_app_codes,
    get_code_rules,
)
from icc.sequence import ALL_RESERVED_CODES, APP_CODES


class TestCodePurposes:
    def test_special_code_purposes(self):
        assert get_special_code_purpose(111) == "Educational Institutions"
        assert get_special_code_purpose(999) == "Reserved — Future Use"
        assert get_special_code_purpose(101) == "Educational Institutions (Alternate)"
        assert get_special_code_purpose(100) is None

    def test_app_code_purposes(self):
        assert "Internal Channel 1" in get_app_code_purpose(10)
        assert "Internal Channel 9" in get_app_code_purpose(90)
        assert get_app_code_purpose(100) is None


class TestGetAllCodes:
    def test_get_all_special_codes(self):
        codes = get_all_special_codes()
        assert len(codes) == 18
        assert codes[0]["code"] == 101
        
        # Verify all reserved codes are present
        code_ints = [c["code"] for c in codes]
        for c in ALL_RESERVED_CODES:
            assert c in code_ints

    def test_get_all_app_codes(self):
        codes = get_all_app_codes()
        assert len(codes) == 9
        assert codes[0]["code"] == 10
        assert codes[0]["formatted"] == "010"
        
        code_ints = [c["code"] for c in codes]
        for c in APP_CODES:
            assert c in code_ints


class TestCodeRules:
    def test_get_code_rules(self):
        rules = get_code_rules()
        assert "country_code_range" in rules
        assert "18 reserved special codes" in rules["country_code_exclusions"]
        assert rules["total_country_codes"].startswith("882")
