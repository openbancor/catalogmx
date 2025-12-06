"""
Integration tests for SQLite-based catalogs

Tests the actual functionality of catalogs using the SQLite backend.
"""

import pytest

from catalogmx.catalogs.banxico.udis_sqlite import (
    UDICatalog,
    get_udi_actual,
    pesos_a_udis,
    udis_a_pesos,
)
from catalogmx.catalogs.banxico.tipo_cambio_usd_sqlite import (
    TipoCambioUSDCatalog,
    get_tipo_cambio_actual,
    usd_a_mxn,
    mxn_a_usd,
)
from catalogmx.catalogs.banxico.salarios_minimos_sqlite import (
    SalariosMinimosCatalog,
    get_salario_minimo_actual,
    salario_mensual,
    salario_anual,
)


class TestUDICatalogSQLite:
    """Test UDI catalog with SQLite backend"""

    def test_get_actual(self):
        """Test getting most recent UDI"""
        udi = UDICatalog.get_actual()

        assert udi is not None
        assert "fecha" in udi
        assert "valor" in udi
        assert udi["valor"] > 0

    def test_get_por_fecha_valid(self):
        """Test getting UDI for a specific date"""
        # Use a date we know exists
        udi = UDICatalog.get_por_fecha("2025-11-30")

        # May or may not exist depending on data
        if udi:
            assert "fecha" in udi
            assert "valor" in udi
            assert udi["valor"] > 0

    def test_get_por_fecha_invalid(self):
        """Test getting UDI for invalid date"""
        udi = UDICatalog.get_por_fecha("1990-01-01")
        # UDI started in 1995, so this should be None or fallback to monthly
        assert udi is None or udi["tipo"] == "promedio_mensual"

    def test_get_por_mes(self):
        """Test getting monthly average UDI"""
        udi = UDICatalog.get_por_mes(2025, 11)

        if udi:
            assert udi["año"] == 2025
            assert udi["mes"] == 11
            assert udi["tipo"] == "promedio_mensual"

    def test_get_promedio_anual(self):
        """Test getting annual average UDI"""
        udi = UDICatalog.get_promedio_anual(2024)

        if udi:
            assert udi["año"] == 2024
            assert udi["tipo"] == "promedio_anual"

    def test_get_por_anio(self):
        """Test getting all UDIs for a year"""
        udis = UDICatalog.get_por_anio(2025)

        assert isinstance(udis, list)
        if udis:
            assert all(udi["año"] == 2025 for udi in udis)
            # Should have daily records
            assert any(udi["tipo"] in ("diario", "oficial_banxico") for udi in udis)

    def test_pesos_a_udis(self):
        """Test converting pesos to UDIs"""
        # Get a valid date
        udi = UDICatalog.get_actual()
        if udi:
            fecha = udi["fecha"]
            udis = UDICatalog.pesos_a_udis(100000, fecha)

            assert udis is not None
            assert udis > 0
            # 100,000 pesos should be roughly 11,000-12,000 UDIs (depending on date)
            assert 10000 < udis < 15000

    def test_udis_a_pesos(self):
        """Test converting UDIs to pesos"""
        udi = UDICatalog.get_actual()
        if udi:
            fecha = udi["fecha"]
            pesos = UDICatalog.udis_a_pesos(10000, fecha)

            assert pesos is not None
            assert pesos > 0
            # 10,000 UDIs should be roughly 85,000-87,000 pesos
            assert 80000 < pesos < 90000

    def test_calcular_variacion(self):
        """Test calculating variation between dates"""
        # Use recent dates
        variacion = UDICatalog.calcular_variacion("2025-01-01", "2025-11-30")

        if variacion is not None:
            assert isinstance(variacion, float)
            # UDI typically grows slowly (inflation)
            assert -5 < variacion < 10  # Reasonable range for yearly variation

    def test_convenience_function_get_udi_actual(self):
        """Test convenience function"""
        udi = get_udi_actual()

        assert udi is not None
        assert "valor" in udi

    def test_convenience_function_pesos_a_udis(self):
        """Test convenience function"""
        udi = get_udi_actual()
        if udi:
            udis = pesos_a_udis(100000, udi["fecha"])
            assert udis is not None
            assert udis > 0


class TestTipoCambioUSDCatalogSQLite:
    """Test Tipo de Cambio USD/MXN catalog with SQLite backend"""

    def test_get_actual(self):
        """Test getting most recent exchange rate"""
        tc = TipoCambioUSDCatalog.get_actual()

        assert tc is not None
        assert "fecha" in tc
        assert "tipo_cambio" in tc
        assert tc["tipo_cambio"] > 0
        assert tc["fuente"] == "FIX"

    def test_get_valor_actual(self):
        """Test getting current exchange rate value"""
        valor = TipoCambioUSDCatalog.get_valor_actual()

        assert valor is not None
        assert valor > 0
        # USD/MXN typically between 15-25
        assert 10 < valor < 30

    def test_get_por_fecha_valid(self):
        """Test getting exchange rate for specific date"""
        tc = TipoCambioUSDCatalog.get_por_fecha("2025-11-25")

        if tc:
            assert "fecha" in tc
            assert "tipo_cambio" in tc
            assert tc["tipo_cambio"] > 0

    def test_get_por_anio(self):
        """Test getting all exchange rates for a year"""
        tcs = TipoCambioUSDCatalog.get_por_anio(2025)

        assert isinstance(tcs, list)
        if tcs:
            assert all(tc["año"] == 2025 for tc in tcs)
            assert all(tc["fuente"] == "FIX" for tc in tcs)

    def test_usd_a_mxn(self):
        """Test converting USD to MXN"""
        tc = TipoCambioUSDCatalog.get_actual()
        if tc:
            mxn = TipoCambioUSDCatalog.usd_a_mxn(1000, tc["fecha"])

            assert mxn is not None
            assert mxn > 0
            # 1000 USD should be roughly 15,000-25,000 MXN
            assert 10000 < mxn < 30000

    def test_mxn_a_usd(self):
        """Test converting MXN to USD"""
        tc = TipoCambioUSDCatalog.get_actual()
        if tc:
            usd = TipoCambioUSDCatalog.mxn_a_usd(20000, tc["fecha"])

            assert usd is not None
            assert usd > 0
            # 20,000 MXN should be roughly 800-1,300 USD
            assert 600 < usd < 1500

    def test_calcular_variacion(self):
        """Test calculating variation"""
        variacion = TipoCambioUSDCatalog.calcular_variacion("2025-01-01", "2025-11-25")

        if variacion is not None:
            assert isinstance(variacion, float)
            # Exchange rate can vary significantly
            assert -20 < variacion < 20

    def test_get_promedio_anual(self):
        """Test calculating annual average"""
        promedio = TipoCambioUSDCatalog.get_promedio_anual(2024)

        if promedio:
            assert promedio > 0
            assert 10 < promedio < 30

    def test_convenience_functions(self):
        """Test convenience functions"""
        tc = get_tipo_cambio_actual()
        assert tc is not None

        if tc:
            mxn = usd_a_mxn(100, tc["fecha"])
            assert mxn is not None

            usd = mxn_a_usd(2000, tc["fecha"])
            assert usd is not None


class TestSalariosMinimosCatalogSQLite:
    """Test Salarios Mínimos catalog with SQLite backend"""

    def test_get_actual_general(self):
        """Test getting current minimum wage for general zone"""
        salario = SalariosMinimosCatalog.get_actual("general")

        # Minimum wage data may not be in the database yet
        if salario:
            assert "salario_diario" in salario
            assert "zona" in salario
            assert salario["zona"] == "general"
            assert salario["salario_diario"] > 0

    def test_get_actual_frontera(self):
        """Test getting current minimum wage for northern border"""
        salario = SalariosMinimosCatalog.get_actual("frontera_norte")

        if salario:
            assert "salario_diario" in salario
            assert salario["zona"] == "frontera_norte"
            assert salario["salario_diario"] > 0

    def test_get_valor_actual(self):
        """Test getting current minimum wage value"""
        valor = SalariosMinimosCatalog.get_valor_actual("general")

        if valor:
            assert valor > 0
            # Minimum wage typically between 200-300 pesos/day
            assert 100 < valor < 400

    def test_salario_mensual(self):
        """Test calculating monthly minimum wage"""
        mensual = SalariosMinimosCatalog.salario_mensual("general")

        if mensual:
            assert mensual > 0
            # Monthly should be daily * 30.4
            assert 3000 < mensual < 12000

    def test_salario_anual(self):
        """Test calculating annual minimum wage"""
        anual = SalariosMinimosCatalog.salario_anual("general")

        if anual:
            assert anual > 0
            # Annual should be daily * 365
            assert 36000 < anual < 150000

    def test_get_por_fecha(self):
        """Test getting minimum wage for specific date"""
        # Use a recent date
        salario = SalariosMinimosCatalog.get_por_fecha("2025-01-01", "general")

        if salario:
            assert "salario_diario" in salario
            assert salario["salario_diario"] > 0

    def test_get_por_anio(self):
        """Test getting all minimum wages for a year"""
        salarios = SalariosMinimosCatalog.get_por_anio(2024)

        # May or may not have data
        if salarios:
            assert isinstance(salarios, list)
            assert all(s["año"] == 2024 for s in salarios)

    def test_calcular_variacion(self):
        """Test calculating variation"""
        # Minimum wage changes are typically annual
        variacion = SalariosMinimosCatalog.calcular_variacion(
            "2024-01-01", "2025-01-01", "general"
        )

        if variacion is not None:
            assert isinstance(variacion, float)
            # Minimum wage typically increases 5-15% annually
            assert 0 <= variacion <= 30

    def test_convenience_functions(self):
        """Test convenience functions"""
        salario = get_salario_minimo_actual("general")

        if salario:
            mensual = salario_mensual("general")
            assert mensual is not None

            anual = salario_anual("general")
            assert anual is not None


class TestCatalogConsistency:
    """Test consistency between catalogs"""

    def test_all_catalogs_use_same_database(self):
        """Verify all catalogs use the same database file"""
        udi_path = UDICatalog._get_db_path()
        tc_path = TipoCambioUSDCatalog._get_db_path()
        sm_path = SalariosMinimosCatalog._get_db_path()

        assert udi_path == tc_path == sm_path

    def test_database_version_consistency(self):
        """Verify database version is consistent"""
        import sqlite3

        db_path = UDICatalog._get_db_path()
        db = sqlite3.connect(db_path)

        cursor = db.execute("SELECT value FROM _metadata WHERE key = 'version'")
        version = cursor.fetchone()[0]

        assert version is not None
        assert isinstance(version, str)
        # Version should be a date (YYYY-MM-DD)
        assert len(version) == 10
        assert version.count("-") == 2

        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
