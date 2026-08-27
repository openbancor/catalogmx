"""Shared loader for SAT Nómina 1.2 compatibility views."""

from __future__ import annotations

import json
from typing import Any, ClassVar

from catalogmx.utils.shared_data import get_shared_data_path


class NominaJsonCatalog:
    """Lazy code lookup backed by a Nómina 1.2 compatibility JSON view."""

    filename: ClassVar[str]
    _data: ClassVar[list[dict[str, Any]] | None] = None
    _by_code: ClassVar[dict[str, dict[str, Any]] | None] = None

    @classmethod
    def _normalize(cls, item: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(item)
        code = normalized.get("code", normalized.get("clave", normalized.get("id")))
        if code is None:
            raise ValueError(f"{cls.filename}: catalog row has no code")
        code = str(code)
        normalized["code"] = code
        normalized.setdefault("clave", code)

        description = normalized.get(
            "description", normalized.get("descripcion", normalized.get("texto"))
        )
        if description is not None:
            normalized["description"] = str(description)
            normalized.setdefault("descripcion", str(description))

        name = normalized.get("name", normalized.get("nombre"))
        if name is not None:
            normalized["name"] = str(name)
            normalized.setdefault("nombre", str(name))

        legal_name = normalized.get("razon_social", normalized.get("full_name"))
        if legal_name is not None:
            normalized["razon_social"] = str(legal_name)
            normalized.setdefault("full_name", str(legal_name))
        return normalized

    @classmethod
    def _load(cls) -> list[dict[str, Any]]:
        if cls._data is None:
            path = get_shared_data_path("sat", "nomina_1.2", cls.filename)
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, list):
                raise ValueError(f"{cls.filename}: expected a JSON array")
            cls._data = [cls._normalize(item) for item in payload]
            cls._by_code = {item["code"]: item for item in cls._data}
        return cls._data

    @classmethod
    def reload(cls) -> None:
        cls._data = None
        cls._by_code = None

    @classmethod
    def get_all(cls) -> list[dict[str, Any]]:
        return cls._load()

    @classmethod
    def get_by_code(cls, code: str) -> dict[str, Any] | None:
        cls._load()
        assert cls._by_code is not None
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        return cls.get_by_code(code) is not None

    @classmethod
    def search(cls, text: str) -> list[dict[str, Any]]:
        query = text.casefold()
        return [
            item
            for item in cls._load()
            if query
            in str(
                item.get("description")
                or item.get("name")
                or item.get("full_name")
                or ""
            ).casefold()
        ]
