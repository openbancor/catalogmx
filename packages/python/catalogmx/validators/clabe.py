#!/usr/bin/env python3
"""
CLABE (Clave Bancaria Estandarizada) Validator

CLABE is the standardized 18-digit bank account number used in Mexico for
interbank electronic transfers (SPEI).

Structure:
    - 3 digits: Bank code
    - 3 digits: Branch/Plaza code
    - 11 digits: Account number
    - 1 digit: Check digit (modulo 10 algorithm)

Example: 002010077777777771
    002: Banamex
    010: Branch code
    07777777777: Account number
    1: Check digit
"""


class CLABEException(Exception):
    pass


class CLABELengthError(CLABEException):
    pass


class CLABEStructureError(CLABEException):
    pass


class CLABECheckDigitError(CLABEException):
    pass


class CLABEValidator:
    """
    Validates CLABE (Clave Bancaria Estandarizada) bank account numbers
    """

    LENGTH = 18

    # Weights for check digit calculation (positions 0-16)
    WEIGHTS = [3, 7, 1] * 6  # Pattern repeats: 3,7,1,3,7,1,...

    def __init__(self, clabe: str | None) -> None:
        """
        :param clabe: The CLABE number to validate
        """
        self.clabe = ""
        if bool(clabe) and isinstance(clabe, str):
            self.clabe = clabe.strip()

    def validate(self) -> bool:
        """
        Validates the CLABE structure and check digit
        :return: True if valid, raises exception if invalid
        """
        value = self.clabe

        # Check length
        if len(value) != self.LENGTH:
            raise CLABELengthError(f"CLABE length must be {self.LENGTH} digits, got {len(value)}")

        # Check if all characters are digits
        if not value.isdigit():
            raise CLABEStructureError("CLABE must contain only digits")

        # Validate check digit
        if not self.verify_check_digit(value):
            raise CLABECheckDigitError("Invalid CLABE check digit")

        return True

    def is_valid(self) -> bool:
        """
        Checks if CLABE is valid without raising exceptions
        :return: True if valid, False otherwise
        """
        try:
            return self.validate()
        except CLABEException:
            return False

    @classmethod
    def calculate_check_digit(cls, clabe_17: str) -> str:
        """
        Calculates the check digit for a 17-digit CLABE

        Algorithm:
        1. Multiply each digit by its weight (3,7,1 pattern)
        2. Take modulo 10 of each result
        3. Sum all results
        4. Take modulo 10 of the sum
        5. Subtract from 10
        6. Take modulo 10 of the result

        :param clabe_17: First 17 digits of CLABE
        :return: Check digit (0-9)
        """
        if len(clabe_17) != 17:
            raise CLABELengthError("Need exactly 17 digits to calculate check digit")

        if not clabe_17.isdigit():
            raise CLABEStructureError("CLABE must contain only digits")

        # Calculate weighted sum
        weighted_sum = 0
        for i, digit in enumerate(clabe_17):
            product = int(digit) * cls.WEIGHTS[i]
            weighted_sum += product % 10

        # Calculate check digit
        check_digit = (10 - (weighted_sum % 10)) % 10

        return str(check_digit)

    @classmethod
    def verify_check_digit(cls, clabe: str) -> bool:
        """
        Verifies the check digit of an 18-digit CLABE

        :param clabe: Complete 18-digit CLABE
        :return: True if check digit is valid, False otherwise
        """
        if len(clabe) != cls.LENGTH:
            return False

        calculated = cls.calculate_check_digit(clabe[:17])
        return calculated == clabe[17]

    def get_bank_code(self) -> str | None:
        """
        Extracts the bank code (first 3 digits)
        :return: Bank code as string
        """
        if len(self.clabe) >= 3:
            return self.clabe[:3]
        return None

    def get_branch_code(self) -> str | None:
        """
        Extracts the branch/plaza code (digits 4-6)
        :return: Branch code as string
        """
        if len(self.clabe) >= 6:
            return self.clabe[3:6]
        return None

    def get_account_number(self) -> str | None:
        """
        Extracts the account number (digits 7-17)
        :return: Account number as string
        """
        if len(self.clabe) >= 17:
            return self.clabe[6:17]
        return None

    def get_check_digit(self) -> str | None:
        """
        Extracts the check digit (digit 18)
        :return: Check digit as string
        """
        if len(self.clabe) == self.LENGTH:
            return self.clabe[17]
        return None

    def get_parts(self) -> dict[str, str | None] | None:
        """
        Returns all CLABE parts as a dictionary
        :return: Dictionary with bank_code, branch_code, account_number, check_digit
        """
        if not self.is_valid():
            return None

        return {
            "bank_code": self.get_bank_code(),
            "branch_code": self.get_branch_code(),
            "account_number": self.get_account_number(),
            "check_digit": self.get_check_digit(),
            "clabe": self.clabe,
        }


def validate_clabe(clabe: str | None) -> bool:
    """
    Helper function to validate a CLABE

    :param clabe: CLABE number as string
    :return: True if valid, False otherwise
    """
    validator = CLABEValidator(clabe)
    return validator.is_valid()


def generate_clabe(bank_code: str | int, branch_code: str | int, account_number: str | int) -> str:
    """
    Generates a complete CLABE with check digit

    :param bank_code: 3-digit bank code
    :param branch_code: 3-digit branch code
    :param account_number: 11-digit account number
    :return: Complete 18-digit CLABE
    """
    # Ensure all parts are strings and properly formatted
    bank_code = str(bank_code).zfill(3)
    branch_code = str(branch_code).zfill(3)
    account_number = str(account_number).zfill(11)

    if len(bank_code) != 3:
        raise CLABEStructureError("Bank code must be 3 digits")
    if len(branch_code) != 3:
        raise CLABEStructureError("Branch code must be 3 digits")
    if len(account_number) != 11:
        raise CLABEStructureError("Account number must be 11 digits")

    clabe_17 = bank_code + branch_code + account_number
    check_digit = CLABEValidator.calculate_check_digit(clabe_17)

    return clabe_17 + check_digit


def get_clabe_info(clabe: str | None) -> dict[str, str | None] | None:
    """
    Helper function to get information from a CLABE

    :param clabe: CLABE number as string
    :return: Dictionary with CLABE parts or None if invalid
    """
    validator = CLABEValidator(clabe)
    return validator.get_parts()
