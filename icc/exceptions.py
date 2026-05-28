"""
ICC — Internet Calling Code Library
Custom exceptions for the ICC library.

Author: Mobyap (mobyap.com@gmail.com)
License: MIT
"""


class ICCError(Exception):
    """Base exception for all ICC library errors."""
    pass


class InvalidICCCode(ICCError):
    """Raised when an ICC code is invalid or not assigned to any country."""

    def __init__(self, code, message=None):
        self.code = code
        self.message = message or f"Invalid or unassigned ICC code: {code}"
        super().__init__(self.message)


class CountryNotFound(ICCError):
    """Raised when a country cannot be found by the given identifier."""

    def __init__(self, identifier, message=None):
        self.identifier = identifier
        self.message = message or f"Country not found: {identifier}"
        super().__init__(self.message)


class InvalidInputError(ICCError):
    """Raised when input format is invalid."""

    def __init__(self, input_value, expected_format=None, message=None):
        self.input_value = input_value
        self.expected_format = expected_format
        self.message = message or (
            f"Invalid input: {input_value}"
            + (f" (expected: {expected_format})" if expected_format else "")
        )
        super().__init__(self.message)


class InvalidISNError(ICCError):
    """
    Raised when an Internet Subscriber Number (ISN) is invalid.

    The ISN format is: ICC-RRRR-SSSS-SSSS
    where ICC is a 3-digit code, RRRR is a 4-digit region/purpose code,
    and SSSS-SSSS is an 8-digit subscriber number.
    """

    def __init__(self, isn_value, reason=None, message=None):
        self.isn_value = isn_value
        self.reason = reason
        self.message = message or (
            f"Invalid ISN: {isn_value}"
            + (f" ({reason})" if reason else "")
        )
        super().__init__(self.message)


class ReservedCodeError(ICCError):
    """
    Raised when attempting to use a reserved special code as a country code.

    Reserved codes (111, 222, ..., 999, 101, 202, ..., 909) are designated
    for global services and cannot be assigned to countries.
    """

    def __init__(self, code, purpose=None, message=None):
        self.code = code
        self.purpose = purpose
        self.message = message or (
            f"Code {code} is reserved"
            + (f" for: {purpose}" if purpose else "")
            + " — cannot be assigned to a country"
        )
        super().__init__(self.message)
