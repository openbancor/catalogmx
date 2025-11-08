"""
Mexican States Catalog from INEGI

This module provides access to the official catalog of Mexican states
(entidades federativas) with their CURP codes, INEGI codes, and abbreviations.
"""
import json
from pathlib import Path


class StateCatalog:
    """
    Catalog of Mexican states
    """

    _data: list[dict] | None = None
    _state_by_code: dict[str, dict] | None = None
    _state_by_name: dict[str, dict] | None = None
    _state_by_inegi: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Load state data from JSON file"""
        if cls._data is None:
            # Get path to shared data
            current_file = Path(__file__)
            shared_data_path = current_file.parent.parent.parent.parent.parent.parent / 'shared-data' / 'inegi' / 'states.json'

            with open(shared_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['states']

            # Create lookup dictionaries
            cls._state_by_code = {state['code']: state for state in cls._data}
            cls._state_by_name = {state['name'].upper(): state for state in cls._data}
            cls._state_by_inegi = {state['clave_inegi']: state for state in cls._data}

            # Add aliases to name lookup
            for state in cls._data:
                if 'aliases' in state:
                    for alias in state['aliases']:
                        cls._state_by_name[alias.upper()] = state

    @classmethod
    def get_all_states(cls) -> list[dict]:
        """
        Get all states in the catalog

        :return: List of state dictionaries
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_state_by_code(cls, code: str) -> dict | None:
        """
        Get state information by CURP code

        :param code: 2-letter CURP state code (e.g., 'AS' for Aguascalientes)
        :return: State dictionary or None if not found
        """
        cls._load_data()
        return cls._state_by_code.get(code.upper())

    @classmethod
    def get_state_by_name(cls, name: str) -> dict | None:
        """
        Get state information by name

        :param name: State name (case insensitive)
        :return: State dictionary or None if not found
        """
        cls._load_data()
        return cls._state_by_name.get(name.upper())

    @classmethod
    def get_state_by_inegi_code(cls, code: str) -> dict | None:
        """
        Get state information by INEGI code

        :param code: 2-digit INEGI code (e.g., '01' for Aguascalientes)
        :return: State dictionary or None if not found
        """
        cls._load_data()
        code = str(code).zfill(2)
        return cls._state_by_inegi.get(code)

    @classmethod
    def validate_state_code(cls, code: str) -> bool:
        """
        Validate if a state CURP code exists

        :param code: 2-letter CURP state code
        :return: True if exists, False otherwise
        """
        return cls.get_state_by_code(code) is not None

    @classmethod
    def get_state_codes(cls) -> dict[str, str]:
        """
        Get dictionary of state names to CURP codes

        :return: Dictionary mapping state names to codes
        """
        cls._load_data()
        return {state['name']: state['code'] for state in cls._data}

    @classmethod
    def get_inegi_codes(cls) -> dict[str, str]:
        """
        Get dictionary of state names to INEGI codes

        :return: Dictionary mapping state names to INEGI codes
        """
        cls._load_data()
        return {state['name']: state['clave_inegi'] for state in cls._data}


# Convenience functions
def get_states_dict() -> dict[str, dict]:
    """Get dictionary of all states indexed by CURP code"""
    StateCatalog._load_data()
    return StateCatalog._state_by_code.copy()


def get_state_names() -> list[str]:
    """Get list of all state names"""
    return [state['name'] for state in StateCatalog.get_all_states()]


# Export commonly used functions
__all__ = [
    'StateCatalog',
    'get_states_dict',
    'get_state_names',
]
