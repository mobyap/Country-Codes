"""Tests for ICC core lookup and utility functions."""

import pytest
from icc.core import (
    get_country_by_icc,
    get_country_by_name,
    get_country_by_iso,
    get_icc_by_country,
    validate_icc,
    is_valid_icc_code,
    list_all_countries,
    search_countries,
    get_countries_by_continent,
    get_continents,
    get_statistics,
    get_code_info,
    get_special_codes,
    get_app_codes_list,
)
from icc.exceptions import InvalidICCCode, CountryNotFound, InvalidInputError
from icc.data import COUNTRIES, TOTAL_COUNTRIES


class TestGetCountryByICC:
    def test_russia(self):
        c = get_country_by_icc(100)
        assert c["name"] == "Russia"
        assert c["icc_code"] == 100

    def test_india(self):
        c = get_country_by_icc(700)
        assert c["name"] == "India"
        assert c["iso_alpha2"] == "IN"

    def test_string_code(self):
        c = get_country_by_icc("100")
        assert c["name"] == "Russia"

    def test_invalid_code(self):
        with pytest.raises(InvalidICCCode):
            get_country_by_icc(999)  # Unassigned

    def test_returns_copy(self):
        c1 = get_country_by_icc(100)
        c2 = get_country_by_icc(100)
        assert c1 == c2
        assert c1 is not c2  # Must be a copy


class TestGetCountryByName:
    def test_common_name(self):
        c = get_country_by_name("India")
        assert c["icc_code"] == 700

    def test_case_insensitive(self):
        c = get_country_by_name("INDIA")
        assert c["icc_code"] == 700

    def test_official_name(self):
        c = get_country_by_name("Republic of India")
        assert c["icc_code"] == 700

    def test_not_found(self):
        with pytest.raises(CountryNotFound):
            get_country_by_name("Atlantis")

    def test_empty_string(self):
        with pytest.raises(InvalidInputError):
            get_country_by_name("")


class TestGetCountryByISO:
    def test_alpha2(self):
        c = get_country_by_iso("US")
        assert c["name"] == "United States"

    def test_alpha3(self):
        c = get_country_by_iso("USA")
        assert c["name"] == "United States"

    def test_case_insensitive(self):
        c = get_country_by_iso("in")
        assert c["name"] == "India"

    def test_not_found(self):
        with pytest.raises(CountryNotFound):
            get_country_by_iso("XX")


class TestGetICCByCountry:
    def test_basic(self):
        assert get_icc_by_country("Russia") == 100
        assert get_icc_by_country("India") == 700


class TestValidateICC:
    def test_valid_assigned(self):
        assert validate_icc(100) is True
        assert validate_icc(700) is True

    def test_invalid(self):
        assert validate_icc(999) is False
        assert validate_icc("abc") is False

    def test_is_valid_icc_code(self):
        assert is_valid_icc_code(100) is True
        assert is_valid_icc_code(999) is True  # Valid code, may not be assigned
        assert is_valid_icc_code(50) is False  # Not a 3-digit code


class TestListAllCountries:
    def test_returns_195(self):
        countries = list_all_countries()
        assert len(countries) == 195

    def test_sorted_by_rank(self):
        countries = list_all_countries()
        ranks = [c["rank"] for c in countries]
        assert ranks == list(range(1, 196))


class TestSearchCountries:
    def test_partial_name(self):
        results = search_countries("Ind")
        names = [r["name"] for r in results]
        assert "India" in names
        assert "Indonesia" in names

    def test_iso_code(self):
        results = search_countries("US")
        names = [r["name"] for r in results]
        assert "United States" in names

    def test_empty_query(self):
        assert search_countries("") == []


class TestGetCountriesByContinent:
    def test_africa(self):
        results = get_countries_by_continent("Africa")
        assert len(results) > 40
        assert all("Africa" in r["continent"] for r in results)

    def test_case_insensitive(self):
        results = get_countries_by_continent("asia")
        assert len(results) > 20


class TestGetContinents:
    def test_returns_list(self):
        continents = get_continents()
        assert "Africa" in continents
        assert "Asia" in continents
        assert "Europe" in continents


class TestGetStatistics:
    def test_stats(self):
        stats = get_statistics()
        assert stats["total_countries"] == 195
        assert stats["total_icc_codes_available"] == 900
        assert stats["codes_assigned"] == 195
        assert stats["largest_country"] == "Russia"
        assert stats["smallest_country"] == "Vatican City"


class TestDataIntegrity:
    def test_unique_icc_codes(self):
        codes = [c["icc_code"] for c in COUNTRIES]
        assert len(set(codes)) == TOTAL_COUNTRIES

    def test_unique_iso_alpha2(self):
        codes = [c["iso_alpha2"] for c in COUNTRIES]
        assert len(set(codes)) == TOTAL_COUNTRIES

    def test_unique_iso_alpha3(self):
        codes = [c["iso_alpha3"] for c in COUNTRIES]
        assert len(set(codes)) == TOTAL_COUNTRIES

    def test_all_have_required_fields(self):
        required = {"rank", "name", "official_name", "iso_alpha2", "iso_alpha3",
                     "iso_numeric", "land_area_km2", "icc_code", "continent", "phone_code"}
        for c in COUNTRIES:
            assert required.issubset(c.keys()), f"Missing fields in {c['name']}"

    def test_sorted_by_area(self):
        areas = [c["land_area_km2"] for c in COUNTRIES]
        assert areas == sorted(areas, reverse=True)


class TestGetCodeInfo:
    def test_country_assigned(self):
        info = get_code_info(100)
        assert info["code"] == 100
        assert info["code_type"] == "country"
        assert info["is_assigned"] is True
        assert info["country"] == "Russia"
        assert info["purpose"] is None

    def test_special_code(self):
        info = get_code_info(111)
        assert info["code_type"] == "special"
        assert info["is_assigned"] is False
        assert "Educational Institutions" in info["purpose"]

    def test_app_code(self):
        info = get_code_info(10)
        assert info["code_type"] == "app"
        assert info["is_assigned"] is False
        assert "Channel 1" in info["purpose"]

    def test_invalid_code(self):
        info = get_code_info(99)
        assert info["code_type"] == "invalid"
        assert info["is_assigned"] is False

    def test_string_code(self):
        info = get_code_info("100")
        assert info["code"] == 100


class TestGetCodeLists:
    def test_get_special_codes(self):
        codes = get_special_codes()
        assert len(codes) == 18
        assert "purpose" in codes[0]

    def test_get_app_codes_list(self):
        codes = get_app_codes_list()
        assert len(codes) == 9
        assert codes[0]["formatted"] == "010"
