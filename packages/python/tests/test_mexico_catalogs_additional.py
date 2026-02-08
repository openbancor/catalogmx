"""Additional coverage for Mexico salary and UMA catalogs."""

from catalogmx.catalogs.mexico.salarios_minimos import (
    SalariosMinimos,
    calcular_mensual,
    get_salario_actual,
    get_salario_por_anio,
)
from catalogmx.catalogs.mexico.uma import (
    UMACatalog,
    calcular_monto,
    calcular_umas,
    get_uma_actual,
    get_uma_por_anio,
)


def test_salarios_convenience_and_incremento_paths(monkeypatch):
    sample = [
        {
            "año": 2024,
            "resto_pais": 248.93,
            "zona_frontera_norte": 374.89,
            "incremento_porcentual": 20.0,
        }
    ]
    monkeypatch.setattr(SalariosMinimos, "_data", sample.copy())

    assert SalariosMinimos.get_data() == sample
    assert get_salario_actual()["año"] == 2024
    assert get_salario_por_anio(2024)["año"] == 2024
    assert SalariosMinimos.get_incremento(2024) == 20.0
    assert SalariosMinimos.get_incremento(1900) is None
    assert calcular_mensual(100.0, 31) == 3100.0


def test_salarios_get_actual_none_when_empty(monkeypatch):
    monkeypatch.setattr(SalariosMinimos, "_data", [])
    assert SalariosMinimos.get_actual() is None


def test_uma_fallback_derives_values_from_salario(monkeypatch):
    monkeypatch.setattr(UMACatalog, "_data", [])
    monkeypatch.setattr(
        SalariosMinimos,
        "get_por_anio",
        lambda anio: {
            "año": anio,
            "resto_pais": 100.0,
            "vigencia_inicio": f"{anio}-01-01",
            "moneda": "MXN",
        },
    )

    result = UMACatalog.get_por_anio(2015)
    assert result is not None
    assert result["valor_diario"] == 100.0
    assert result["valor_mensual"] == 3040.0
    assert result["valor_anual"] == 36500.0
    assert "Equivalencia de UMA" in result["notas"]


def test_uma_fallback_returns_none_for_missing_salary_values(monkeypatch):
    monkeypatch.setattr(UMACatalog, "_data", [])
    monkeypatch.setattr(SalariosMinimos, "get_por_anio", lambda anio: None)
    assert UMACatalog.get_por_anio(2014) is None

    monkeypatch.setattr(SalariosMinimos, "get_por_anio", lambda anio: {"año": anio})
    assert UMACatalog.get_por_anio(2014) is None


def test_uma_convenience_and_error_paths(monkeypatch):
    monkeypatch.setattr(
        UMACatalog,
        "_data",
        [
            {
                "año": 2024,
                "valor_diario": 108.57,
                "valor_mensual": 3300.53,
                "valor_anual": 39606.36,
                "incremento_porcentual": 4.66,
            }
        ],
    )

    assert get_uma_actual()["año"] == 2024
    assert get_uma_por_anio(2024)["año"] == 2024
    assert UMACatalog.get_valor(2024, "invalido") is None
    assert UMACatalog.get_valor(1900, "diario") is None
    assert UMACatalog.calcular_umas(1000.0, 1900) is None
    assert UMACatalog.calcular_monto(10.0, 1900) is None
    assert calcular_umas(1000.0, 2024, "diario") is not None
    assert calcular_monto(10.0, 2024, "mensual") is not None
