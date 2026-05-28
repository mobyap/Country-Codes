"""Integration tests for the ICC REST API."""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestSystemEndpoints:
    def test_root(self):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "ICC — Internet Calling Code API"
        assert "version" in data

    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "healthy"
        assert data["countries_loaded"] == 195


class TestLookupRoutes:
    def test_list_countries(self):
        r = client.get("/api/v1/countries?limit=10")
        assert r.status_code == 200
        data = r.json()
        assert data["total"] == 195
        assert len(data["countries"]) == 10

    def test_get_by_icc(self):
        r = client.get("/api/v1/countries/700")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "India"
        assert data["icc_code"] == 700

    def test_get_by_icc_not_found(self):
        r = client.get("/api/v1/countries/999")
        assert r.status_code == 404

    def test_search(self):
        r = client.get("/api/v1/countries/search?q=Ind")
        assert r.status_code == 200
        names = [c["name"] for c in r.json()["countries"]]
        assert "India" in names

    def test_by_iso(self):
        r = client.get("/api/v1/countries/iso/US")
        assert r.status_code == 200
        assert r.json()["name"] == "United States"

    def test_by_continent(self):
        r = client.get("/api/v1/countries/continent/Africa")
        assert r.status_code == 200
        assert r.json()["total"] > 40

    def test_stats(self):
        r = client.get("/api/v1/countries/stats")
        assert r.status_code == 200
        assert r.json()["total_countries"] == 195


class TestValidationRoutes:
    def test_validate_valid(self):
        r = client.get("/api/v1/validate/100")
        assert r.status_code == 200
        data = r.json()
        assert data["is_valid"] is True
        assert data["is_assigned"] is True
        assert data["country"] == "Russia"

    def test_validate_unassigned(self):
        r = client.get("/api/v1/validate/999")
        assert r.status_code == 200
        data = r.json()
        assert data["is_valid"] is True  # Valid sequence code
        assert data["is_assigned"] is False  # Not assigned to a country

    def test_bulk_validate(self):
        r = client.post("/api/v1/validate/bulk", json={"codes": [100, 700, 999]})
        assert r.status_code == 200
        results = r.json()["results"]
        assert len(results) == 3


class TestVoipRoutes:
    def test_sip_uri(self):
        r = client.get("/api/v1/voip/sip-uri/700?user=alice")
        assert r.status_code == 200
        assert "sip:alice@icc-700" in r.json()["sip_uri"]

    def test_e164(self):
        r = client.get("/api/v1/voip/e164/700")
        assert r.status_code == 200
        assert r.json()["e164_code"] == "+91"

    def test_dial_string(self):
        r = client.get("/api/v1/voip/dial-string/700?number=9876543210")
        assert r.status_code == 200
        assert "+91" in r.json()["dial_string"]

    def test_sip_headers(self):
        r = client.get("/api/v1/voip/sip-headers/700")
        assert r.status_code == 200
        headers = r.json()["headers"]
        assert headers["X-ICC-Code"] == "700"

    def test_voip_config(self):
        r = client.get("/api/v1/voip/config/700?user=bob")
        assert r.status_code == 200
        data = r.json()
        assert data["country"] == "India"
        assert "OPUS" in data["codecs"]


class TestBlockchainRoutes:
    def test_hash(self):
        r = client.get("/api/v1/blockchain/hash/700")
        assert r.status_code == 200
        assert len(r.json()["hash"]) == 64

    def test_verify_valid(self):
        h = client.get("/api/v1/blockchain/hash/700").json()["hash"]
        r = client.post("/api/v1/blockchain/verify", json={"icc_code": 700, "hash": h})
        assert r.status_code == 200
        assert r.json()["valid"] is True

    def test_verify_invalid(self):
        r = client.post("/api/v1/blockchain/verify", json={"icc_code": 700, "hash": "0" * 64})
        assert r.status_code == 200
        assert r.json()["valid"] is False

    def test_token(self):
        r = client.get("/api/v1/blockchain/token/700")
        assert r.status_code == 200
        assert len(r.json()["token"]) == 64

    def test_abi(self):
        r = client.get("/api/v1/blockchain/abi")
        assert r.status_code == 200
        assert r.json()["contractName"] == "ICCRegistry"

    def test_encode(self):
        r = client.get("/api/v1/blockchain/encode/700")
        assert r.status_code == 200
        assert r.json()["byte_length"] == 96

    def test_merkle_leaf(self):
        r = client.get("/api/v1/blockchain/merkle-leaf/700")
        assert r.status_code == 200
        assert len(r.json()["leaf_hash"]) == 64


class TestISNRoutes:
    def test_validate_isn(self):
        r = client.post("/api/v1/isn/validate", json={"isn": "100-1234-5678-0321"})
        assert r.status_code == 200
        data = r.json()
        assert data["is_valid"] is True
        assert data["icc_code"] == 100
        assert data["country"] == "Russia"

    def test_parse_isn(self):
        r = client.post("/api/v1/isn/parse", json={"isn": "100123456780321"})
        assert r.status_code == 200
        data = r.json()
        assert data["icc_code"] == 100
        assert data["region_code"] == "1234"
        assert data["subscriber_number"] == "56780321"

    def test_generate_isn(self):
        r = client.get("/api/v1/isn/generate/700?region=0001&subscriber=12345")
        assert r.status_code == 200
        assert r.json()["isn"] == "700-0001-0001-2345"

    def test_format_isn(self):
        r = client.post("/api/v1/isn/format", json={
            "icc_code": 100,
            "region_code": "1234",
            "subscriber": "56780321"
        })
        assert r.status_code == 200
        assert r.json()["isn"] == "100-1234-5678-0321"

    def test_isn_country(self):
        r = client.post("/api/v1/isn/country", json={"isn": "700-1234-5678-0321"})
        assert r.status_code == 200
        assert r.json()["country"] == "India"


class TestCodesRoutes:
    def test_special_codes(self):
        r = client.get("/api/v1/codes/special")
        assert r.status_code == 200
        assert r.json()["total"] == 18

    def test_app_codes(self):
        r = client.get("/api/v1/codes/app")
        assert r.status_code == 200
        assert r.json()["total"] == 9

    def test_classify(self):
        r = client.get("/api/v1/codes/classify/111")
        assert r.status_code == 200
        data = r.json()
        assert data["code_type"] == "special"
        assert data["is_reserved"] is True
        assert "Educational" in data["purpose"]

    def test_rules(self):
        r = client.get("/api/v1/codes/rules")
        assert r.status_code == 200
        assert "country_code_range" in r.json()["rules"]
