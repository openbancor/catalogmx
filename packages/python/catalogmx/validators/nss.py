#!/usr/bin/env python3
"""
NSS (Número de Seguridad Social) Validator

NSS is the 11-digit social security number issued by IMSS (Instituto Mexicano del Seguro Social).

Structure:
    - 2 digits: Subdelegation code
    - 2 digits: Year of registration (last 2 digits)
    - 2 digits: Registration serial number
    - 5 digits: Sequential number
    - 1 digit: Check digit (modified Luhn algorithm)

Example: 12345678903
    12: Subdelegation
    34: Year (2034 or 1934)
    56: Serial
    78903: Sequential and check digit

Note: The check digit uses a modified Luhn algorithm specific to NSS.
"""


class NSSException(Exception):
    pass


class NSSLengthError(NSSException):
    pass


class NSSStructureError(NSSException):
    pass


class NSSCheckDigitError(NSSException):
    pass


class NSSValidator:
    """
    Validates NSS (Número de Seguridad Social) from IMSS
    """

    LENGTH = 11

    def __init__(self, nss: str | None) -> None:
        """
        :param nss: The NSS number to validate
        """
        self.nss = ""
        if bool(nss) and isinstance(nss, str):
            self.nss = nss.strip()

    def validate(self) -> bool:
        """
        Validates the NSS structure and check digit
        :return: True if valid, raises exception if invalid
        """
        value = self.nss

        # Check length
        if len(value) != self.LENGTH:
            raise NSSLengthError(f"NSS length must be {self.LENGTH} digits, got {len(value)}")

        # Check if all characters are digits
        if not value.isdigit():
            raise NSSStructureError("NSS must contain only digits")

        # Validate check digit
        if not self.verify_check_digit(value):
            raise NSSCheckDigitError("Invalid NSS check digit")

        return True

    def is_valid(self) -> bool:
        """
        Checks if NSS is valid without raising exceptions
        :return: True if valid, False otherwise
        """
        try:
            return self.validate()
        except NSSException:
            return False

    @classmethod
    def calculate_check_digit(cls, nss_10: str) -> str:
        """
        Calculates the check digit for a 10-digit NSS using modified Luhn algorithm

        Algorithm (modified Luhn):
        1. Starting from the right, multiply alternating digits by 2 and 1
        2. If the product is > 9, sum its digits
        3. Sum all results
        4. The check digit is (10 - (sum % 10)) % 10

        :param nss_10: First 10 digits of NSS
        :return: Check digit (0-9)
        """
        if len(nss_10) != 10:
            raise NSSLengthError("Need exactly 10 digits to calculate check digit")

        if not nss_10.isdigit():
            raise NSSStructureError("NSS must contain only digits")

        # Process digits from right to left
        total = 0
        for i, digit in enumerate(reversed(nss_10)):
            n = int(digit)

            # Alternate between multiplying by 2 and 1 (starting with 2 for rightmost)
            if i % 2 == 0:
                n = n * 2
                # If result is > 9, sum its digits (e.g., 12 -> 1+2 = 3)
                if n > 9:
                    n = n // 10 + n % 10

            total += n

        # Calculate check digit
        check_digit = (10 - (total % 10)) % 10

        return str(check_digit)

    @classmethod
    def verify_check_digit(cls, nss: str) -> bool:
        """
        Verifies the check digit of an 11-digit NSS

        :param nss: Complete 11-digit NSS
        :return: True if check digit is valid, False otherwise
        """
        if len(nss) != cls.LENGTH:
            return False

        calculated = cls.calculate_check_digit(nss[:10])
        return calculated == nss[10]

    def get_subdelegation(self) -> str | None:
        """
        Extracts the subdelegation code (first 2 digits)
        :return: Subdelegation code as string
        """
        if len(self.nss) >= 2:
            return self.nss[:2]
        return None

    def get_year(self) -> str | None:
        """
        Extracts the registration year (digits 3-4, last 2 digits of year)
        Note: This is ambiguous - could be 19XX or 20XX
        :return: Year suffix as string
        """
        if len(self.nss) >= 4:
            return self.nss[2:4]
        return None

    def get_serial(self) -> str | None:
        """
        Extracts the registration serial (digits 5-6)
        :return: Serial number as string
        """
        if len(self.nss) >= 6:
            return self.nss[4:6]
        return None

    def get_sequential(self) -> str | None:
        """
        Extracts the sequential number (digits 7-10)
        :return: Sequential number as string
        """
        if len(self.nss) >= 10:
            return self.nss[6:10]
        return None

    def get_check_digit(self) -> str | None:
        """
        Extracts the check digit (digit 11)
        :return: Check digit as string
        """
        if len(self.nss) == self.LENGTH:
            return self.nss[10]
        return None

    def get_parts(self) -> dict[str, str] | None:
        """
        Returns all NSS parts as a dictionary
        :return: Dictionary with subdelegation, year, serial, sequential, check_digit
        """
        if not self.is_valid():
            return None

        return {
            "subdelegation": self.get_subdelegation(),
            "year": self.get_year(),
            "serial": self.get_serial(),
            "sequential": self.get_sequential(),
            "check_digit": self.get_check_digit(),
            "nss": self.nss,
        }


def validate_nss(nss: str | None) -> bool:
    """
    Helper function to validate an NSS

    :param nss: NSS number as string
    :return: True if valid, False otherwise
    """
    validator = NSSValidator(nss)
    return validator.is_valid()


def generate_nss(
    subdelegation: str | int, year: str | int, serial: str | int, sequential: str | int
) -> str:
    """
    Generates a complete NSS with check digit

    :param subdelegation: 2-digit subdelegation code
    :param year: 2-digit year (last 2 digits)
    :param serial: 2-digit serial number
    :param sequential: 4-digit sequential number
    :return: Complete 11-digit NSS
    """
    # Ensure all parts are strings and properly formatted
    subdelegation = str(subdelegation).zfill(2)
    year = str(year).zfill(2)
    serial = str(serial).zfill(2)
    sequential = str(sequential).zfill(4)

    if len(subdelegation) != 2:
        raise NSSStructureError("Subdelegation must be 2 digits")
    if len(year) != 2:
        raise NSSStructureError("Year must be 2 digits")
    if len(serial) != 2:
        raise NSSStructureError("Serial must be 2 digits")
    if len(sequential) != 4:
        raise NSSStructureError("Sequential must be 4 digits")

    nss_10 = subdelegation + year + serial + sequential
    check_digit = NSSValidator.calculate_check_digit(nss_10)

    return nss_10 + check_digit


def get_nss_info(nss: str | None) -> dict[str, str] | None:
    """
    Helper function to get information from an NSS

    :param nss: NSS number as string
    :return: Dictionary with NSS parts or None if invalid
    """
    validator = NSSValidator(nss)
    return validator.get_parts()
