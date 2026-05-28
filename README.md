# ICC — Internet Calling Code Library

A robust, commercial-grade Python library and REST API providing deterministic 3-digit Internet Communications Codes (ICC) for global internet communication, along with comprehensive ISN (Internet Subscriber Number) support.

**Author**: Mobyap  
**Contact**: mobyap.com@gmail.com  
**License**: MIT (Free for commercial use)

---

## Features

- **Country Codes**: 882 deterministic 3-digit codes (100–999) assigned to sovereign nations based on land area (Russia = `100`, Canada = `200`, etc.).
- **Special Codes**: 18 reserved codes (e.g., `111` for Educational Institutions, `333` for Emergency Services) for global, non-national services.
- **App Codes**: 9 channels (`010`–`090`) exclusively reserved for the Mobyap blockchain VOIP application.
- **ISN Format**: Full routing and validation for 15-digit Internet Subscriber Numbers (`ICC-RRRR-SSSS-SSSS`).
- **REST API**: Built-in FastAPI endpoints for lookups, validation, code classification, and code generation.
- **VOIP Integration**: Utilities for SIP URI generation, E.164 mapping, and custom dial strings.
- **Blockchain Ready**: SHA-256 hashing, Merkle tree leaves, and ABI encoding for smart contract integration.

## Installation

This package requires Python 3.9+.

```bash
pip install -e .
```

To run the REST API:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
API Docs available at: `http://localhost:8000/docs`

## Quick Start (Python)

### 1. Lookup Country Information
```python
import icc

country = icc.get_country_by_icc(700)
print(country["name"])  # "India"

code = icc.get_icc_by_country("United States")
print(code)  # 400
```

### 2. Parse and Validate ISN
```python
from icc.isn import parse_isn, validate_isn

# Validate
result = validate_isn("100-1234-5678-0321")
print(result.is_valid)  # True
print(result.country)   # "Russia"

# Parse
components = parse_isn("100-1234-5678-0321")
print(components.icc_code)          # 100
print(components.region_code)       # "1234"
print(components.subscriber_number) # "56780321"
```

### 3. Code Classification
```python
import icc

print(icc.classify_code(111))  # "special"
print(icc.classify_code(10))   # "app"
print(icc.classify_code(100))  # "country"

# Check purpose
info = icc.get_code_info(111)
print(info["purpose"])  # "Educational Institutions"
```

### 4. VOIP & Blockchain Integration
```python
from icc import voip, blockchain

# Generate a SIP URI
sip_uri = voip.generate_sip_uri("100-1234-5678-0321", domain="mobyap.com")
print(sip_uri)  # "sip:100123456780321@mobyap.com"

# Generate a verification token for smart contracts
token = blockchain.generate_verification_token("100-1234-5678-0321", "0xAbCdE12345...")
```

## Documentation

For full details, please refer to the documentation:
- [ISN Specification](docs/ISN_SPECIFICATION.md) — Detailed format and rules for Internet Subscriber Numbers.
- [API Reference](docs/API_REFERENCE.md) — REST API endpoints and payload schemas.
- [Testing Guide](docs/TESTING.md) — Instructions for running and extending the test suite.
- [Code Tables](table.md) — Complete lists of all country codes, special codes, and app codes.
