"""
Bank Catalog from Banxico

This module provides access to the official catalog of Mexican banks
participating in the SPEI (Sistema de Pagos Electrónicos Interbancarios).
"""

import json
from pathlib import Path

from catalogmx.utils.text import normalize_text


class BankCatalog:
    """
    Catalog of Mexican banks
    """

    _data: list[dict] | None = None
    _bank_by_code: dict[str, dict] | None = None
    _bank_by_name: dict[str, dict] | None = None
    _bank_by_name_normalized: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Load bank data from JSON file"""
        if cls._data is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/banxico/banks.py
            # Target: catalogmx/packages/shared-data/banxico/banks.json
            current_file = Path(__file__)
            shared_data_path = (
                current_file.parent.parent.parent.parent.parent
                / "shared-data"
                / "banxico"
                / "banks.json"
            )

            with open(shared_data_path, encoding="utf-8") as f:
                cls._data = json.load(f)

            # Create lookup dictionaries
            cls._bank_by_code = {bank["code"]: bank for bank in cls._data}
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
    def get_spei_banks(cls) -> list[dict]:
        """
        Get all banks that participate in SPEI

        :return: List of SPEI participant banks
        """
        cls._load_data()
        return [bank for bank in cls._data if bank.get("spei", False)]

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


def get_spei_banks() -> list[dict]:
    """Get list of all SPEI participant banks"""
    return BankCatalog.get_spei_banks()


# Export commonly used functions
__all__ = [
    "BankCatalog",
    "get_banks_dict",
    "get_spei_banks",
]
