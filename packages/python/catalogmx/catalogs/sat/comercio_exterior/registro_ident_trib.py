"""Foreign tax-identity validation for Comercio Exterior.

SAT publishes ``NumRegIdTrib`` format metadata by country in the shared CFDI
``c_Pais`` catalog.  Historical CatalogMX versions also exposed a small,
non-SAT list of generic identity-type aliases (``01``..``14``/``99``).  Those
aliases remain as code-owned compatibility labels, but regulatory validation is
country-scoped and resolver-backed.
"""

from __future__ import annotations

import re

from catalogmx.catalogs.sat.comercio_exterior._cfdi_views import (
    country_tax_identity_rows,
)

_LEGACY_TYPES = (
    ("01", "Número de identificación fiscal"),
    ("02", "Número de identificación tributaria"),
    ("03", "Número de identificación empresarial"),
    ("04", "Cédula de identificación"),
    ("05", "CURP"),
    ("06", "EIN (Employer Identification Number - USA)"),
    ("07", "ITIN (Individual Taxpayer Identification Number - USA)"),
    ("08", "NIF (Número de Identificación Fiscal - España)"),
    ("09", "RUC (Registro Único de Contribuyentes)"),
    ("10", "RUT (Rol Único Tributario - Chile)"),
    ("11", "CUIT (Clave Única de Identificación Tributaria - Argentina)"),
    ("12", "CNPJ (Cadastro Nacional da Pessoa Jurídica - Brasil)"),
    ("13", "CPF (Cadastro de Pessoas Físicas - Brasil)"),
    ("14", "Número de pasaporte"),
    ("99", "Otro"),
)


class RegistroIdentTribCatalog:
    """Compatibility facade plus country-scoped SAT tax-identity validation."""

    _data: list[dict] | None = None
    _tipo_by_code: dict[str, dict] | None = None
    _country_rules: list[dict] | None = None
    _country_rule_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Materialize historical aliases without a separate data lifecycle."""
        if cls._data is None:
            cls._data = [
                {"code": code, "descripcion": description, "source": "catalogmx-legacy"}
                for code, description in _LEGACY_TYPES
            ]
            cls._tipo_by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def _load_country_rules(cls) -> None:
        """Load SAT country rules from the shared resolver-backed CFDI dataset."""
        if cls._country_rules is None:
            cls._country_rules = country_tax_identity_rows()
            cls._country_rule_by_code = {item["country"]: item for item in cls._country_rules}

    @classmethod
    def get_tipo(cls, code: str) -> dict | None:
        """Return one historical CatalogMX identity-type alias."""
        cls._load_data()
        return cls._tipo_by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Return whether a historical compatibility alias exists."""
        return cls.get_tipo(code) is not None

    @classmethod
    def get_country_rule(cls, country_code: str) -> dict | None:
        """Return SAT tax-identity metadata for an ISO Alpha-3 country code."""
        cls._load_country_rules()
        return cls._country_rule_by_code.get(country_code.upper())

    @classmethod
    def validate_for_country(cls, country_code: str, num_reg_id_trib: str) -> dict:
        """Validate ``NumRegIdTrib`` using the SAT rule published for a country.

        Most SAT country rows do not publish a local regex, so CatalogMX cannot
        invent one and accepts the value locally. Mexico explicitly requests
        ``Lista del SAT`` validation; that remote/registry validation is likewise
        not reduced to the accompanying pattern.
        """
        rule = cls.get_country_rule(country_code)
        if not rule:
            return {"valid": False, "errors": ["País no válido para NumRegIdTrib"]}
        if not num_reg_id_trib:
            return {"valid": False, "errors": ["NumRegIdTrib no puede estar vacío"]}

        pattern = rule.get("format_pattern")
        validation_mode = rule.get("validation_mode")
        if pattern and validation_mode != "Lista del SAT":
            if re.fullmatch(pattern, num_reg_id_trib) is None:
                return {
                    "valid": False,
                    "errors": [f"Formato de NumRegIdTrib no válido para país {rule['country']}"],
                }

        return {"valid": True, "errors": []}

    @classmethod
    def validate_tax_id(cls, tipo_registro: str, num_reg_id_trib: str) -> dict:
        """Validate the historical compatibility alias API.

        The legacy alias list never contained format rules, so this method keeps
        its historical behavior: validate alias existence only. New regulatory
        code should use :meth:`validate_for_country`.
        """
        if len(tipo_registro) == 3 and cls.get_country_rule(tipo_registro):
            return cls.validate_for_country(tipo_registro, num_reg_id_trib)

        tipo = cls.get_tipo(tipo_registro)
        if not tipo:
            return {"valid": False, "errors": ["Tipo de registro no válido"]}
        return {"valid": True, "errors": []}

    @classmethod
    def get_all(cls) -> list[dict]:
        """Return historical non-SAT aliases for compatibility."""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_all_country_rules(cls) -> list[dict]:
        """Return all country-scoped SAT tax-identity metadata."""
        cls._load_country_rules()
        return cls._country_rules.copy()
