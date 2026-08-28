"""Temporary branch-local patcher for CFDI resolver consumer migration."""

from pathlib import Path

ROOT = Path("packages/python/catalogmx/catalogs/sat/cfdi_4")

REPLACEMENTS = {
    "exportacion.py": (
        "code_description_rows",
        '''    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = code_description_rows("cfdi_40_exportaciones")
            cls._by_code = {item["code"]: item for item in cls._data}

''',
    ),
    "forma_pago.py": (
        "code_description_rows",
        '''    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = code_description_rows("cfdi_40_formas_pago")
            cls._by_code = {item["code"]: item for item in cls._data}

''',
    ),
    "metodo_pago.py": (
        "code_description_rows",
        '''    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = code_description_rows("cfdi_40_metodos_pago")
            cls._by_code = {item["code"]: item for item in cls._data}

''',
    ),
    "objeto_imp.py": (
        "code_description_rows",
        '''    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = code_description_rows(
                "cfdi_40_objetos_impuestos", strip_terminal_period=True
            )
            cls._by_code = {item["code"]: item for item in cls._data}

''',
    ),
    "tipo_relacion.py": (
        "code_description_rows",
        '''    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = code_description_rows("cfdi_40_tipos_relaciones")
            cls._by_code = {item["code"]: item for item in cls._data}

''',
    ),
    "tipo_comprobante.py": (
        "code_description_rows",
        '''    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = code_description_rows("cfdi_40_tipos_comprobantes")
            cls._by_code = {item["code"]: item for item in cls._data}

''',
    ),
    "impuesto.py": (
        "impuesto_rows",
        '''    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = impuesto_rows()
            cls._by_code = {item["code"]: item for item in cls._data}

''',
    ),
    "regimen_fiscal.py": (
        "regimen_fiscal_rows",
        '''    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = regimen_fiscal_rows()
            cls._by_code = {item["code"]: item for item in cls._data}

''',
    ),
    "uso_cfdi.py": (
        "uso_cfdi_rows",
        '''    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = uso_cfdi_rows()
            cls._by_code = {item["code"]: item for item in cls._data}

''',
    ),
    "meses.py": (
        "value_rows",
        '''    @classmethod
    def _load_data(cls):
        if cls._data is None:
            rows = value_rows("cfdi_40_meses")
            cls._data = {item["valor"]: item for item in rows}
        return cls._data

''',
    ),
    "periodicidad.py": (
        "value_rows",
        '''    @classmethod
    def _load_data(cls):
        if cls._data is None:
            rows = value_rows("cfdi_40_periodicidades")
            cls._data = {item["valor"]: item for item in rows}
        return cls._data

''',
    ),
    "tipo_factor.py": (
        "value_rows",
        '''    @classmethod
    def _load_data(cls):
        if cls._data is None:
            rows = value_rows("cfdi_40_tipos_factores")
            cls._data = {item["valor"]: item for item in rows}
        return cls._data

''',
    ),
    "clave_unidad.py": (
        "clave_unidad_rows",
        '''    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is not None:
            return
        cls._data = clave_unidad_rows()
        cls._by_id = {item["id"]: item for item in cls._data}

''',
    ),
}


def replace_loader(text: str, replacement: str, filename: str) -> str:
    start_marker = "    @classmethod\n    def _load_data"
    start = text.find(start_marker)
    if start < 0:
        raise RuntimeError(f"no _load_data start in {filename}")
    next_decorator = text.find("    @classmethod\n", start + len(start_marker))
    if next_decorator < 0:
        raise RuntimeError(f"no following classmethod in {filename}")
    return text[:start] + replacement + text[next_decorator:]


def add_import(text: str, helper: str, filename: str) -> str:
    text = text.replace("import json\n", "")
    text = text.replace(
        "from catalogmx.utils.shared_data import get_shared_data_path\n", ""
    )
    import_line = (
        "from catalogmx.catalogs.sat.cfdi_4._resolver_views "
        f"import {helper}\n"
    )
    if import_line in text:
        return text
    future = "from __future__ import annotations\n"
    if future in text:
        return text.replace(future, future + "\n" + import_line, 1)
    class_index = text.find("\nclass ")
    if class_index < 0:
        raise RuntimeError(f"no class anchor in {filename}")
    return text[:class_index] + "\n" + import_line + text[class_index:]


for filename, (helper, replacement) in REPLACEMENTS.items():
    path = ROOT / filename
    text = path.read_text(encoding="utf-8")
    text = add_import(text, helper, filename)
    text = replace_loader(text, replacement, filename)
    path.write_text(text, encoding="utf-8")
