#!/usr/bin/env python3
"""Enrich the minimum wage catalog with UMA-equivalent values.

The SAT and Banxico documentation frequently require UMA values even for
historical calculations. UMA started in 2017; for prior years we use the
applicable minimum wage as a proxy so downstream consumers can still perform
comparisons. The script adds three new fields to every record in
``salarios_minimos.json``:

* ``uma_equivalente_diario``
* ``uma_equivalente_mensual``
* ``uma_equivalente_anual``

Each entry also receives a ``fuente_uma_equivalente`` flag that states whether
it comes from the official UMA table or from the salary minimum proxy.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[2]
SALARIOS_PATH = REPO_ROOT / 'packages' / 'shared-data' / 'mexico' / 'salarios_minimos.json'
UMA_PATH = REPO_ROOT / 'packages' / 'shared-data' / 'mexico' / 'uma.json'

UMA_MONTHLY_FACTOR = 30.4
UMA_ANNUAL_FACTOR = 365


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def get_base_salary(record: Dict[str, Any]) -> float | None:
    for key in ('resto_pais', 'zona_general', 'zona_frontera_norte', 'zona_b', 'zona_a'):
        value = record.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def main() -> None:
    salarios = load_json(SALARIOS_PATH)
    uma_catalog = load_json(UMA_PATH)
    uma_por_anio = {entry['año']: entry for entry in uma_catalog}

    for record in salarios:
        year = record['año']
        fuente = 'salario_minimo'
        valor_diario = get_base_salary(record)

        uma_entry = uma_por_anio.get(year)
        if uma_entry:
            valor_diario = float(uma_entry['valor_diario'])
            valor_mensual = float(uma_entry['valor_mensual'])
            valor_anual = float(uma_entry['valor_anual'])
            fuente = 'uma_oficial'
        elif valor_diario is None:
            raise ValueError(f'No base salary available to approximate UMA for year {year}')
        else:
            valor_mensual = round(valor_diario * UMA_MONTHLY_FACTOR, 2)
            valor_anual = round(valor_diario * UMA_ANNUAL_FACTOR, 2)

        record['uma_equivalente_diario'] = round(valor_diario, 2)
        record['uma_equivalente_mensual'] = valor_mensual
        record['uma_equivalente_anual'] = valor_anual
        record['fuente_uma_equivalente'] = fuente

    save_json(SALARIOS_PATH, salarios)
    print(f'✅ UMA equivalents added to {len(salarios)} salary minimum records.')


if __name__ == '__main__':
    main()
