"""Tests for ICC numbering sequence generator."""

import pytest
from icc.sequence import (
    generate_icc_sequence,
    get_code_at_position,
    get_position_of_code,
    classify_code,
    is_reserved_code,
    is_app_code,
    ICC_SEQUENCE,
    ALL_RESERVED_CODES,
    APP_CODES,
    VALID_COUNTRY_CODES,
    VALID_ICC_CODES,
)


class TestGenerateSequence:
    """Tests for the sequence generation logic."""

    def test_sequence_length(self):
        """Sequence must produce exactly 882 country codes."""
        seq = generate_icc_sequence(include_reserved=False)
        assert len(seq) == 882

    def test_full_sequence_length(self):
        """Full sequence must produce exactly 900 codes."""
        seq = generate_icc_sequence(include_reserved=True)
        assert len(seq) == 900

    def test_no_duplicates(self):
        """All codes in the sequence must be unique."""
        assert len(set(ICC_SEQUENCE)) == 882

    def test_all_codes_are_3_digit(self):
        """All codes must be between 100 and 999."""
        for code in ICC_SEQUENCE:
            assert 100 <= code <= 999, f"Code {code} is out of range"

    def test_first_nine_codes(self):
        """First 9 codes must be 100, 200, ..., 900."""
        expected = [100, 200, 300, 400, 500, 600, 700, 800, 900]
        assert ICC_SEQUENCE[:9] == expected

    def test_next_nine_codes(self):
        """Codes 10–18 must be 110, 120, ..., 190."""
        expected = [110, 120, 130, 140, 150, 160, 170, 180, 190]
        assert ICC_SEQUENCE[9:18] == expected

    def test_user_specified_sequence(self):
        """Match the exact user-specified sequence start."""
        expected = [
            100, 200, 300, 400, 500, 600, 700, 800, 900,
            110, 120, 130, 140, 150, 160, 170, 180, 190,
            210, 220,
        ]
        assert ICC_SEQUENCE[:20] == expected

    def test_no_reserved_codes(self):
        """Ensure no reserved codes are in the country sequence."""
        for code in ALL_RESERVED_CODES:
            assert code not in ICC_SEQUENCE


class TestGetCodeAtPosition:
    """Tests for rank → code mapping."""

    def test_rank_1(self):
        assert get_code_at_position(1) == 100

    def test_rank_9(self):
        assert get_code_at_position(9) == 900

    def test_rank_10(self):
        assert get_code_at_position(10) == 110

    def test_rank_out_of_range(self):
        with pytest.raises(ValueError):
            get_code_at_position(0)
        with pytest.raises(ValueError):
            get_code_at_position(883)


class TestGetPositionOfCode:
    """Tests for code → rank mapping."""

    def test_code_100(self):
        assert get_position_of_code(100) == 1

    def test_code_900(self):
        assert get_position_of_code(900) == 9

    def test_code_110(self):
        assert get_position_of_code(110) == 10

    def test_reserved_code(self):
        with pytest.raises(ValueError, match="reserved special code"):
            get_position_of_code(111)

    def test_invalid_code(self):
        with pytest.raises(ValueError):
            get_position_of_code(50)


class TestValidCodes:
    """Tests for the validity sets."""

    def test_contains_all_sequence_codes(self):
        for code in ICC_SEQUENCE:
            assert code in VALID_COUNTRY_CODES
            assert code in VALID_ICC_CODES

    def test_reserved_in_valid_icc(self):
        for code in ALL_RESERVED_CODES:
            assert code in VALID_ICC_CODES
            assert code not in VALID_COUNTRY_CODES

    def test_size(self):
        assert len(VALID_COUNTRY_CODES) == 882
        assert len(VALID_ICC_CODES) == 900


class TestClassifications:
    """Tests for code classification functions."""

    def test_classify_country(self):
        assert classify_code(100) == "country"
        assert classify_code(700) == "country"

    def test_classify_special(self):
        assert classify_code(111) == "special"
        assert classify_code(101) == "special"
        assert classify_code(999) == "special"

    def test_classify_app(self):
        assert classify_code(10) == "app"
        assert classify_code(90) == "app"

    def test_classify_invalid(self):
        assert classify_code(99) == "invalid"
        assert classify_code(1000) == "invalid"
        assert classify_code(0) == "invalid"

    def test_is_reserved_code(self):
        assert is_reserved_code(111) is True
        assert is_reserved_code(100) is False

    def test_is_app_code(self):
        assert is_app_code(10) is True
        assert is_app_code(100) is False
