"""Tests for ISN (Internet Subscriber Number) module."""

import pytest
from icc.isn import (
    parse_isn,
    validate_isn,
    is_valid_isn,
    format_isn,
    generate_isn,
    get_country_from_isn,
)
from icc.exceptions import InvalidISNError


class TestParseISN:
    def test_parse_formatted(self):
        res = parse_isn("100-1234-5678-0321")
        assert res.icc_code == 100
        assert res.region_code == "1234"
        assert res.subscriber_number == "56780321"
        assert res.full_number == "100-1234-5678-0321"
        assert res.raw_digits == "100123456780321"
        assert res.code_type == "country"

    def test_parse_raw_digits(self):
        res = parse_isn("100123456780321")
        assert res.icc_code == 100
        assert res.region_code == "1234"
        assert res.subscriber_number == "56780321"

    def test_parse_spaces(self):
        res = parse_isn("100 1234 5678 0321")
        assert res.full_number == "100-1234-5678-0321"

    def test_parse_special_code(self):
        res = parse_isn("111-1234-5678-0321")
        assert res.icc_code == 111
        assert res.code_type == "special"

    def test_parse_app_code(self):
        res = parse_isn("010-1234-5678-0321")
        assert res.icc_code == 10
        assert res.code_type == "app"

    def test_invalid_length(self):
        with pytest.raises(InvalidISNError):
            parse_isn("100-123-5678-0321")  # region too short

        with pytest.raises(InvalidISNError):
            parse_isn("10012345678032")  # 14 digits


class TestValidateISN:
    def test_valid_country_isn(self):
        res = validate_isn("100-1234-5678-0321")
        assert res.is_valid is True
        assert res.icc_code == 100
        assert res.code_type == "country"
        assert res.country == "Russia"

    def test_valid_special_isn(self):
        res = validate_isn("111-1234-5678-0321")
        assert res.is_valid is True
        assert res.icc_code == 111
        assert res.code_type == "special"
        assert res.country is None

    def test_invalid_icc(self):
        res = validate_isn("000-1234-5678-0321")
        assert res.is_valid is False
        assert res.icc_code == 0
        assert "not a valid code" in res.error

    def test_is_valid_isn_helper(self):
        assert is_valid_isn("100-1234-5678-0321") is True
        assert is_valid_isn("000-1234-5678-0321") is False


class TestFormatGenerateISN:
    def test_format_isn(self):
        assert format_isn(100, "1234", "56780321") == "100-1234-5678-0321"
        assert format_isn(10, "0001", "00000001") == "010-0001-0000-0001"

    def test_format_invalid(self):
        with pytest.raises(InvalidISNError):
            format_isn(100, "12345", "56780321")  # region 5 digits
        with pytest.raises(InvalidISNError):
            format_isn(100, "1234", "567803219")  # sub 9 digits

    def test_generate_isn(self):
        isn = generate_isn(100, "1234", 12345)
        assert isn == "100-1234-0001-2345"
        
        # random subscriber
        isn2 = generate_isn(100)
        assert is_valid_isn(isn2)

    def test_generate_invalid_icc(self):
        with pytest.raises(InvalidISNError):
            generate_isn(99)


class TestGetCountryFromISN:
    def test_valid_country(self):
        c = get_country_from_isn("100-1234-5678-0321")
        assert c["name"] == "Russia"

    def test_special_code(self):
        with pytest.raises(InvalidISNError, match="not a country code"):
            get_country_from_isn("111-1234-5678-0321")

    def test_unassigned_country(self):
        # Find an unassigned country code
        with pytest.raises(InvalidISNError, match="not assigned to any country"):
            get_country_from_isn("998-1234-5678-0321")
