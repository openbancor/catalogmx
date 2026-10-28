"""
Bank Catalog from Banxico

This module provides access to the official catalog of Mexican banks
participating in the SPEI (Sistema de Pagos Electrónicos Interbancarios).
"""

import json

from catalogmx.utils.shared_data import get_shared_data_path
from catalogmx.utils.text import normalize_text


class BankCatalog:
    """
    Catalog of Mexican banks
    """

    _data: list[dict] | None = None
    _bank_by_code: dict[str, dict] | None = None
    _bank_by_spei_code: dict[str, dict] | None = None
    _bank_by_name: dict[str, dict] | None = None
    _bank_by_name_normalized: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Load bank data from JSON file"""
        if cls._data is None:
            shared_data_path = get_shared_data_path("banxico", "banks.json")

            with open(shared_data_path, encoding="utf-8") as f:
                cls._data = json.load(f)

            # Create lookup dictionaries
            cls._bank_by_code = {bank["code"]: bank for bank in cls._data}
            cls._bank_by_spei_code = {
                bank["spei_code"]: bank for bank in cls._data if bank.get("spei_code")
            }
            cls._bank_by_name = {bank["name"].upper(): bank for bank in cls._data}
            # Accent-insensitive lookup
            cls._bank_by_name_normalized = {
                normalize_text(bank["name"]): bank for bank in cls._data
            }

    @classmethod
    def get_all_banks(cls) -> list[dict]:
        """
        Get all banks in the catalog

        :return: List of bank dictionaries
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_bank_by_code(cls, code: str) -> dict | None:
        """
        Get bank information by code

        :param code: 3-digit bank code (e.g., '002' for Banamex)
        :return: Bank dictionary or None if not found
        """
        cls._load_data()
        code = str(code).zfill(3)
        return cls._bank_by_code.get(code)

    @classmethod
    def get_bank_by_clabe_code(cls, code: str) -> dict | None:
        """
        Get bank information by its 3-digit CLABE bank code.

        Alias of :meth:`get_bank_by_code`. Historical (disaffiliated) banks are
        returned too, with ``status == "historical"``, so old CLABEs resolve.
        """
        return cls.get_bank_by_code(code)

    @classmethod
    def get_bank_by_spei_code(cls, spei_code: str) -> dict | None:
        """
        Get bank information by the Banxico SPEI participant code.

        :param spei_code: 5-digit participant key (e.g. '40012' for BBVA MEXICO;
            Banxico itself is the official 4-digit '2001')
        :return: Bank dictionary or None if not an active SPEI participant
        """
        cls._load_data()
        return cls._bank_by_spei_code.get(str(spei_code))

    @classmethod
    def validate_spei_code(cls, spei_code: str, code: str | None = None) -> bool:
        """
        Validate an SPEI participant code and, optionally, its 3-digit code.

        :param spei_code: 5-digit SPEI participant code
        :param code: optional 3-digit CLABE bank code; must equal ``spei_code[-3:]``
            and the catalog record
        :return: True if the code is an active participant and consistent
        """
        bank = cls.get_bank_by_spei_code(spei_code)
        if bank is None:
            return False
        if code is None:
            return True
        code = str(code).zfill(3)
        return bank["code"] == code and str(spei_code)[-3:] == code

    @classmethod
    def get_bank_by_name(cls, name: str) -> dict | None:
        """
        Get bank information by name (accent-insensitive)

        :param name: Bank name (case and accent insensitive, e.g., 'BANAMEX' or 'Banamex')
        :return: Bank dictionary or None if not found

        Examples:
            >>> # Both searches work the same
            >>> bank = BankCatalog.get_bank_by_name("Banamex")
            >>> bank = BankCatalog.get_bank_by_name("Banámex")  # same result
        """
        cls._load_data()
        return cls._bank_by_name_normalized.get(normalize_text(name))

    @classmethod
    def is_spei_participant(cls, code: str) -> bool:
        """
        Check if a bank participates in SPEI

        :param code: 3-digit bank code
        :return: True if bank participates in SPEI, False otherwise
        """
        bank = cls.get_bank_by_code(code)
        return bank.get("spei", False) if bank else False

    @classmethod
    def get_spei_banks(cls, include_historical: bool = False) -> list[dict]:
        """
        Get the banks that participate in SPEI today

        :param include_historical: also return banks marked ``status == "historical"``
            (disaffiliated from SPEI), which are excluded by default
        :return: List of SPEI participant banks
        """
        cls._load_data()
        return [
            bank
            for bank in cls._data
            if (bank.get("status") != "historical" and bank.get("spei", False))
            or (include_historical and bank.get("status") == "historical")
        ]

    @classmethod
    def validate_bank_code(cls, code: str) -> bool:
        """
        Validate if a bank code exists

        :param code: 3-digit bank code
        :return: True if exists, False otherwise
        """
        return cls.get_bank_by_code(code) is not None


# Convenience dictionaries for direct access
def get_banks_dict() -> dict[str, dict]:
    """Get dictionary of all banks indexed by code"""
    BankCatalog._load_data()
    return BankCatalog._bank_by_code.copy()


def get_spei_banks(include_historical: bool = False) -> list[dict]:
    """Get list of SPEI participant banks (active only by default)"""
    return BankCatalog.get_spei_banks(include_historical=include_historical)


# Export commonly used functions
__all__ = [
    "BankCatalog",
    "get_banks_dict",
    "get_spei_banks",
]
