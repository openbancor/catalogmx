#!/usr/bin/env python3
"""Generate synthetic daily UDI series from monthly averages.

This script reads ``packages/shared-data/banxico/udis.json`` and, whenever it
finds monthly average entries (``tipo == 'promedio_mensual'``), it generates
one record per calendar day using the same value. This is a stop-gap solution so
that both the Python and TypeScript catalogs can expose daily values while the
team integrates the official Banxico feed (which requires an API token).

The script is idempotent: if daily entries already exist for a month it leaves
it untouched. A small provenance flag (``fuente``) is attached to every
synthetic record so downstream consumers can distinguish them from official
values.
"""
from __future__ import annotations

import json
import calendar
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[2]
UDI_PATH = REPO_ROOT / "packages" / "shared-data" / "banxico" / "udis.json"


@dataclass
class UDIRecord:
    fecha: date
    valor: float
    moneda: str
    tipo: str
    año: int
    mes: int | None
    notas: str | None
    fuente: str | None

    @classmethod
    def from_json(cls, raw: Dict[str, Any]) -> "UDIRecord":
        year = int(raw.get("año") or raw.get("anio") or raw["fecha"].split("-")[0])
        month = raw.get("mes")
        if month is None and raw["tipo"] in {"promedio_mensual", "diario"}:
            month = int(raw["fecha"].split("-")[1])
        notas = raw.get("notas")
        fuente = raw.get("fuente")
        return cls(
            fecha=date.fromisoformat(raw["fecha"]),
            valor=float(raw["valor"]),
            moneda=raw.get("moneda", "MXN"),
            tipo=raw.get("tipo", "diario"),
            año=year,
            mes=int(month) if month is not None else None,
            notas=notas,
            fuente=fuente,
        )

    def to_json(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "fecha": self.fecha.isoformat(),
            "valor": round(self.valor, 6),
            "moneda": self.moneda,
            "tipo": self.tipo,
            "año": self.año,
        }
        if self.mes is not None:
            payload["mes"] = self.mes
        if self.notas:
            payload["notas"] = self.notas
        if self.fuente:
            payload["fuente"] = self.fuente
        return payload


def load_udi_records() -> List[UDIRecord]:
    data = json.loads(UDI_PATH.read_text(encoding="utf-8"))
    return [UDIRecord.from_json(item) for item in data]


def month_has_daily(records: List[UDIRecord], year: int, month: int) -> bool:
    for rec in records:
        if (
            rec.tipo == "diario"
            and rec.año == year
            and rec.mes == month
        ):
            return True
    return False


def generate_daily(records: List[UDIRecord]) -> List[UDIRecord]:
    enhanced = list(records)
    for rec in records:
        if rec.tipo != "promedio_mensual" or rec.mes is None:
            continue
        if month_has_daily(enhanced, rec.año, rec.mes):
            continue

        days_in_month = calendar.monthrange(rec.año, rec.mes)[1]
        for day in range(1, days_in_month + 1):
            synthetic = UDIRecord(
                fecha=date(rec.año, rec.mes, day),
                valor=rec.valor,
                moneda=rec.moneda,
                tipo="diario",
                año=rec.año,
                mes=rec.mes,
                notas="Valor diario estimado a partir del promedio mensual",
                fuente="promedio_mensual",
            )
            enhanced.append(synthetic)
    return enhanced


def sort_records(records: List[UDIRecord]) -> List[UDIRecord]:
    return sorted(records, key=lambda r: (r.fecha, r.tipo))


def main() -> None:
    records = load_udi_records()
    enhanced = generate_daily(records)
    enhanced = sort_records(enhanced)
    payload = [rec.to_json() for rec in enhanced]
    UDI_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Generated synthetic daily UDI entries. Total records: {len(payload)}")


if __name__ == "__main__":
    main()
