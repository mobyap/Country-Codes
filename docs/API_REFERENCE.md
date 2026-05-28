# ICC REST API Reference

The ICC API is a FastAPI-based REST service providing access to the Internet Calling Code dataset, ISN validation, code classification, and integration endpoints for VOIP and Blockchain.

**Base URL**: `/api/v1`

---

## 1. System Endpoints

### `GET /`
Returns basic system information.

### `GET /health`
Returns system health, version, and loaded data statistics.

---

## 2. ISN (Internet Subscriber Number)

Endpoints prefixed with `/isn`.

### `POST /isn/validate`
Validates an ISN string.
**Payload:** `{"isn": "100-1234-5678-0321"}`
**Response:** Validation status, extracted ICC code, country, etc.

### `POST /isn/parse`
Parses an ISN into components.
**Payload:** `{"isn": "100123456780321"}`
**Response:** `{"icc_code": 100, "region_code": "1234", "subscriber_number": "56780321", ...}`

### `GET /isn/generate/{icc_code}`
Generates a random or specific ISN for an ICC code.
**Query Params:** `?region=0001&subscriber=12345`
**Response:** `{"isn": "100-0001-0000-2345", ...}`

### `POST /isn/format`
Formats components into an ISN string.
**Payload:** `{"icc_code": 100, "region_code": "1234", "subscriber": "56780321"}`
**Response:** `{"isn": "100-1234-5678-0321", ...}`

### `POST /isn/country`
Gets country information from an ISN.
**Payload:** `{"isn": "100-1234-5678-0321"}`
**Response:** `{"country": "Russia", "iso_alpha2": "RU", ...}`

---

## 3. Code Categories

Endpoints prefixed with `/codes`.

### `GET /codes/special`
Lists all 18 reserved special codes (e.g., 111, 222) and their purposes.

### `GET /codes/app`
Lists all 9 Mobyap app codes (010–090).

### `GET /codes/classify/{code}`
Classifies any 3-digit code.
**Response:** `{"code_type": "special", "is_reserved": true, "purpose": "Educational Institutions", ...}`

### `GET /codes/rules`
Returns the rules for code allocation.

---

## 4. Country Lookup

Endpoints prefixed with `/lookup`.

### `GET /lookup/all`
Returns all assigned country codes.

### `GET /lookup/icc/{code}`
Looks up a country by its ICC code.

### `GET /lookup/name/{name}`
Looks up a country by its name.

### `GET /lookup/iso/{iso_code}`
Looks up a country by its ISO alpha-2 or alpha-3 code.

### `GET /lookup/continent/{continent}`
Returns all countries in a given continent.

### `GET /lookup/search?q={query}`
Searches countries by partial name or code.

### `GET /lookup/stats`
Returns system statistics.

---

## 5. Validation

Endpoints prefixed with `/validate`.

### `GET /validate/icc/{code}`
Checks if an ICC code is assigned to a country.

---

## 6. VOIP Integration

Endpoints prefixed with `/voip`.

### `GET /voip/sip-uri`
Generates a SIP URI for an ISN.
**Query Params:** `?isn=100-1234-5678-0321&domain=mobyap.com`

### `GET /voip/dial-string`
Generates a raw dial string.
**Query Params:** `?isn=100-1234-5678-0321`

### `GET /voip/e164/{icc_code}`
Returns the E.164 (traditional phone code) mapping for an ICC code.

### `GET /voip/config`
Generates full VOIP configuration blocks.
**Query Params:** `?isn=100...&domain=mobyap.com`

---

## 7. Blockchain Integration

Endpoints prefixed with `/blockchain`.

### `GET /blockchain/hash`
Generates a SHA-256 hash of an ISN.
**Query Params:** `?isn=100...`

### `GET /blockchain/token`
Generates a verification token.
**Query Params:** `?isn=100...&address=0x...`

### `GET /blockchain/abi/registry`
Returns the standard smart contract ABI.

### `GET /blockchain/merkle-leaf/{icc_code}`
Generates a Merkle tree leaf for an ICC code.
