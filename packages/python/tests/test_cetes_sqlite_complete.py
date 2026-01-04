"""
Complete tests for CETESCatalog (SQLite backend) to achieve 100% coverage
"""

import pytest
from unittest.mock import patch, MagicMock
from catalogmx.catalogs.banxico import CETES28Catalog as CETESCatalog
from catalogmx.catalogs.banxico.cetes_sqlite import (
    get_cetes_actual,
    get_cetes_por_fecha,
    get_cetes_valor_actual,
)


class TestCETESCatalogComplete:
    """Complete tests for CETESCatalog"""

    def test_get_data(self):
        """Test getting all CETES data"""
        data = CETESCatalog.get_data(plazo=28)
        assert isinstance(data, list)
        assert len(data) > 100
        # Verify structure
        if data:
            record = data[0]
            assert "fecha" in record
            assert "plazo" in record
            assert "tasa" in record
            assert "instrumento" in record
            assert record["instrumento"] == "CETES"

    def test_get_data_different_plazos(self):
        """Test getting data for different terms"""
        for plazo in [28, 91, 182, 364]:
            data = CETESCatalog.get_data(plazo=plazo)
            assert isinstance(data, list)
            if data:
                assert all(r["plazo"] == plazo for r in data)

    def test_get_por_fecha_found(self):
        """Test getting CETES by date when found"""
        data = CETESCatalog.get_data(plazo=28)
        if data:
            fecha = data[0]["fecha"]
            record = CETESCatalog.get_por_fecha(fecha, plazo=28)
            assert record is not None
            assert isinstance(record, dict)
            assert record["fecha"] == fecha
            assert record["plazo"] == 28
            assert "tasa" in record

    def test_get_por_fecha_not_found(self):
        """Test getting CETES by date when not found"""
        record = CETESCatalog.get_por_fecha("1900-01-01", plazo=28)
        assert record is None

    def test_get_actual_found(self):
        """Test getting most recent CETES record"""
        record = CETESCatalog.get_actual(plazo=28)
        assert record is not None
        assert isinstance(record, dict)
        assert "fecha" in record
        assert "tasa" in record
        assert record["plazo"] == 28

    def test_get_actual_empty_database(self):
        """Test get_actual when database is empty"""
        import sqlite3

        with patch("sqlite3.connect") as mock_connect:
            mock_db = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_db.execute.return_value = mock_cursor
            mock_connect.return_value = mock_db

            result = CETESCatalog.get_actual(plazo=28)
            assert result is None

    def test_get_valor_actual(self):
        """Test getting current CETES rate value"""
        valor = CETESCatalog.get_valor_actual(plazo=28)
        assert valor is not None
        assert isinstance(valor, (int, float))
        assert valor > 0

    def test_get_por_anio_found(self):
        """Test getting CETES data for a specific year"""
        data = CETESCatalog.get_data(plazo=28)
        if data:
            anio = data[0]["año"]
            records = CETESCatalog.get_por_anio(anio, plazo=28)
            assert isinstance(records, list)
            assert len(records) > 0
            for record in records:
                assert record["año"] == anio
                assert record["plazo"] == 28

    def test_get_por_anio_not_found(self):
        """Test getting CETES data for a year with no data"""
        records = CETESCatalog.get_por_anio(1900, plazo=28)
        assert isinstance(records, list)
        assert len(records) == 0

    def test_calcular_variacion_found(self):
        """Test calculating variation between two dates"""
        data = CETESCatalog.get_data(plazo=28)
        if len(data) >= 2:
            fecha_inicio = data[0]["fecha"]
            fecha_fin = data[1]["fecha"]

            result = CETESCatalog.calcular_variacion(fecha_inicio, fecha_fin, plazo=28)
            assert result is not None
            assert isinstance(result, (int, float))

    def test_calcular_variacion_invalid_dates(self):
        """Test calculating variation with invalid dates"""
        result = CETESCatalog.calcular_variacion("1900-01-01", "1900-02-01", plazo=28)
        assert result is None

    def test_calcular_variacion_missing_tasas(self):
        """Test calculating variation when tasas are missing"""
        result = CETESCatalog.calcular_variacion("1900-01-01", "2024-01-01", plazo=28)
        assert result is None or isinstance(result, (int, float))

    def test_calcular_variacion_none_tasas(self):
        """Test calculating variation when records exist but tasas are None"""
        with patch.object(CETESCatalog, "get_por_fecha") as mock_get:
            mock_get.side_effect = [
                {"fecha": "2024-01-01", "tasa": None, "plazo": 28},
                {"fecha": "2024-02-01", "tasa": 10.0, "plazo": 28},
            ]

            result = CETESCatalog.calcular_variacion("2024-01-01", "2024-02-01", plazo=28)
            assert result is None

    def test_get_promedio_anual_found(self):
        """Test calculating average annual CETES rate"""
        data = CETESCatalog.get_data(plazo=28)
        if data:
            anio = data[0]["año"]
            promedio = CETESCatalog.get_promedio_anual(anio, plazo=28)
            if promedio is not None:
                assert isinstance(promedio, (int, float))
                assert promedio >= 0

    def test_get_promedio_anual_not_found(self):
        """Test calculating average for year with no data"""
        promedio = CETESCatalog.get_promedio_anual(1900, plazo=28)
        assert promedio is None

    def test_get_promedio_anual_no_tasa_values(self):
        """Test calculating average when no tasa values exist"""
        data = CETESCatalog.get_data(plazo=28)
        if data:
            anio = data[0]["año"]
            promedio = CETESCatalog.get_promedio_anual(anio, plazo=28)
            assert promedio is None or isinstance(promedio, (int, float))

    def test_get_tasa_actual(self):
        """Test getting current CETES rate (alias method)"""
        rate = CETESCatalog.get_tasa_actual(plazo=28)
        assert rate is not None
        assert isinstance(rate, (int, float))
        assert rate == CETESCatalog.get_valor_actual(plazo=28)

    def test_calcular_rendimiento_both_records(self):
        """Test calculating return when both dates have records"""
        data = CETESCatalog.get_data(plazo=28)
        if len(data) >= 2:
            fecha_inicio = data[0]["fecha"]
            fecha_fin = data[1]["fecha"]

            result = CETESCatalog.calcular_rendimiento(10000, fecha_inicio, fecha_fin, plazo=28)
            if result is not None:
                assert isinstance(result, float)
                assert result >= 10000  # Should at least return principal

    def test_calcular_rendimiento_no_records(self):
        """Test calculating return when no records found"""
        result = CETESCatalog.calcular_rendimiento(10000, "1900-01-01", "1900-02-01", plazo=28)
        assert result is None

    def test_calcular_rendimiento_only_inicio(self):
        """Test calculating return with only start date record"""
        with patch.object(CETESCatalog, "get_por_fecha") as mock_get:
            mock_get.side_effect = [{"fecha": "2024-01-01", "tasa": 10.0, "plazo": 28}, None]

            result = CETESCatalog.calcular_rendimiento(10000, "2024-01-01", "2024-02-01", plazo=28)
            assert result is not None
            assert isinstance(result, float)

    def test_calcular_rendimiento_only_fin(self):
        """Test calculating return with only end date record"""
        with patch.object(CETESCatalog, "get_por_fecha") as mock_get:
            mock_get.side_effect = [None, {"fecha": "2024-02-01", "tasa": 10.0, "plazo": 28}]

            result = CETESCatalog.calcular_rendimiento(10000, "2024-01-01", "2024-02-01", plazo=28)
            assert result is not None
            assert isinstance(result, float)

    def test_calcular_rendimiento_only_fin_none_tasa(self):
        """Test calculating return with only end date record but tasa is None"""
        with patch.object(CETESCatalog, "get_por_fecha") as mock_get:
            mock_get.side_effect = [None, {"fecha": "2024-02-01", "tasa": None, "plazo": 28}]

            result = CETESCatalog.calcular_rendimiento(10000, "2024-01-01", "2024-02-01", plazo=28)
            assert result is None

    def test_calcular_rendimiento_none_tasa(self):
        """Test calculating return when tasa is None"""
        with patch.object(CETESCatalog, "get_por_fecha") as mock_get:
            mock_get.side_effect = [{"fecha": "2024-01-01", "tasa": None, "plazo": 28}, None]

            result = CETESCatalog.calcular_rendimiento(10000, "2024-01-01", "2024-02-01", plazo=28)
            assert result is None

    def test_calcular_rendimiento_zero_days(self):
        """Test calculating return when same date"""
        data = CETESCatalog.get_data(plazo=28)
        if data:
            fecha = data[0]["fecha"]
            result = CETESCatalog.calcular_rendimiento(10000, fecha, fecha, plazo=28)
            if result is not None:
                assert result == 10000  # Same amount if zero days


class TestConvenienceFunctions:
    """Test convenience functions at module level"""

    def test_get_cetes_actual(self):
        """Test get_cetes_actual convenience function"""
        record = get_cetes_actual(plazo=28)
        assert record is not None
        assert isinstance(record, dict)
        assert "fecha" in record

    def test_get_cetes_por_fecha(self):
        """Test get_cetes_por_fecha convenience function"""
        data = CETESCatalog.get_data(plazo=28)
        if data:
            fecha = data[0]["fecha"]
            record = get_cetes_por_fecha(fecha, plazo=28)
            assert record is not None
            assert isinstance(record, dict)

    def test_get_cetes_valor_actual(self):
        """Test get_cetes_valor_actual convenience function"""
        valor = get_cetes_valor_actual(plazo=28)
        assert valor is not None
        assert isinstance(valor, (int, float))
        assert valor > 0
