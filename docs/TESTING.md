# ICC Library Testing Guide

This document outlines the testing strategy, tools, and instructions for running the test suite for the ICC (Internet Calling Code) library.

## 1. Test Framework

The ICC library uses `pytest` as its primary testing framework. All tests are located in the `tests/` directory.

### Requirements
- `pytest`
- `httpx` (for testing the FastAPI endpoints)

## 2. Running Tests

To run the entire test suite, execute the following from the project root:

```bash
python -m pytest tests/ -v
```

To run a specific test file:
```bash
python -m pytest tests/test_isn.py -v
```

To run a specific test class or function:
```bash
python -m pytest tests/test_isn.py::TestParseISN -v
```

## 3. Test Structure

The test suite is divided into logical modules mirroring the library's architecture:

### `test_sequence.py`
- **Goal**: Verify the deterministic numbering sequence generator.
- **Key Checks**:
  - Exactly 882 country codes and 18 reserved codes.
  - Phase 1 (codes ending in 0) followed by Phase 2 (codes not ending in 0).
  - Proper exclusion of palindromes and triple digits.

### `test_codes.py`
- **Goal**: Verify code classification and specialized code lists.
- **Key Checks**:
  - Correct purposes for Special codes (e.g., `111` = Educational).
  - Correct purposes for App codes (`010`–`090`).

### `test_isn.py`
- **Goal**: Verify the parsing, validation, and generation of the 15-digit ISN.
- **Key Checks**:
  - String formatting (`ICC-RRRR-SSSS-SSSS`).
  - Strict length validation (exactly 15 digits).
  - Rejecting unassigned or structurally invalid codes.

### `test_core.py`
- **Goal**: Verify the core data lookup and statistics functions.
- **Key Checks**:
  - Lookup by ICC, ISO, Name.
  - Country list integrity (sorted by land area).

### `test_api.py`
- **Goal**: Verify all FastAPI REST endpoints.
- **Key Checks**:
  - Valid HTTP status codes.
  - Correct JSON payload structures.
  - Integration with VOIP and Blockchain modules.

### `test_voip.py` & `test_blockchain.py`
- **Goal**: Verify protocol-specific integration logic.
- **Key Checks**:
  - Proper SIP URI generation.
  - Correct SHA-256 and Merkle hashing.

## 4. Adding New Tests

When adding new features or fixing bugs:
1. Identify the corresponding `test_*.py` file.
2. Add a method prefixed with `test_` within the appropriate test class.
3. Ensure assertions test both expected successes ("happy path") and expected failures (e.g., using `pytest.raises` for exceptions).
