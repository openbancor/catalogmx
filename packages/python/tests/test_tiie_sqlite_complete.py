"""
Complete tests for TIIECatalog (SQLite backend) to achieve 100% coverage
"""

import pytest
from unittest.mock import patch, MagicMock
from catalogmx.catalogs.banxico import TIIE28Catalog as TIIECatalog
from catalogmx.catalogs.banxico.tiie_sqlite import (
    get_tiie_actual,
    get_tiie_por_fecha,
    get_tiie_valor_actual,
)


class TestTIIECatalogComplete:
    """Complete tests for TIIECatalog"""

    def test_get_data(self):
        """Test getting all TIIE data"""
        data = TIIECatalog.get_data(plazo=28)
        assert isinstance(data, list)
        assert len(data) > 100
        if data:
            record = data[0]
            assert "fecha" in record
            assert "plazo" in record
            assert "tasa" in record

    def test_get_data_different_plazos(self):
        """Test getting data for different terms"""
        for plazo in [28, 91, 182]:
            data = TIIECatalog.get_data(plazo=plazo)
            assert isinstance(data, list)
            if data:
                assert all(r["plazo"] == plazo for r in data)

    def test_get_por_fecha_found(self):
        """Test getting TIIE by date when found"""
        data = TIIECatalog.get_data(plazo=28)
        if data:
            fecha = data[0]["fecha"]
            record = TIIECatalog.get_por_fecha(fecha, plazo=28)
            assert record is not None
            assert isinstance(record, dict)
            assert record["fecha"] == fecha
            assert record["plazo"] == 28
            assert "tasa" in record

    def test_get_por_fecha_not_found(self):
        """Test getting TIIE by date when not found"""
        record = TIIECatalog.get_por_fecha("1900-01-01", plazo=28)
        assert record is None

    def test_get_actual_found(self):
        """Test getting most recent TIIE record"""
        record = TIIECatalog.get_actual(plazo=28)
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

            result = TIIECatalog.get_actual(plazo=28)
            assert result is None

    def test_get_valor_actual(self):
        """Test getting current TIIE rate value"""
        valor = TIIECatalog.get_valor_actual(plazo=28)
        assert valor is not None
        assert isinstance(valor, (int, float))
        assert valor > 0

    def test_get_por_anio_found(self):
        """Test getting TIIE data for a specific year"""
        data = TIIECatalog.get_data(plazo=28)
        if data:
            anio = data[0]["año"]
            records = TIIECatalog.get_por_anio(anio, plazo=28)
            assert isinstance(records, list)
            assert len(records) > 0
            for record in records:
                assert record["año"] == anio
                assert record["plazo"] == 28

    def test_get_por_anio_not_found(self):
        """Test getting TIIE data for a year with no data"""
        records = TIIECatalog.get_por_anio(1900, plazo=28)
        assert isinstance(records, list)
        assert len(records) == 0

    def test_calcular_variacion_found(self):
        """Test calculating variation between two dates"""
        data = TIIECatalog.get_data(plazo=28)
        if len(data) >= 2:
            fecha_inicio = data[0]["fecha"]
            fecha_fin = data[1]["fecha"]

            result = TIIECatalog.calcular_variacion(fecha_inicio, fecha_fin, plazo=28)
            assert result is not None
            assert isinstance(result, (int, float))

    def test_calcular_variacion_invalid_dates(self):
        """Test calculating variation with invalid dates"""
        result = TIIECatalog.calcular_variacion("1900-01-01", "1900-02-01", plazo=28)
        assert result is None

    def test_calcular_variacion_none_tasas(self):
        """Test calculating variation when records exist but tasas are None"""
        with patch.object(TIIECatalog, "get_por_fecha") as mock_get:
            mock_get.side_effect = [
                {"fecha": "2024-01-01", "tasa": None, "plazo": 28},
                {"fecha": "2024-02-01", "tasa": 10.0, "plazo": 28},
            ]

            result = TIIECatalog.calcular_variacion("2024-01-01", "2024-02-01", plazo=28)
            assert result is None

    def test_get_promedio_anual_found(self):
        """Test calculating average annual TIIE rate"""
        data = TIIECatalog.get_data(plazo=28)
        if data:
            anio = data[0]["año"]
            promedio = TIIECatalog.get_promedio_anual(anio, plazo=28)
            if promedio is not None:
                assert isinstance(promedio, (int, float))
                assert promedio >= 0

    def test_get_promedio_anual_not_found(self):
        """Test calculating average for year with no data"""
        promedio = TIIECatalog.get_promedio_anual(1900, plazo=28)
        assert promedio is None

    def test_get_tasa_actual(self):
        """Test getting current TIIE rate (alias method)"""
        rate = TIIECatalog.get_tasa_actual(plazo=28)
        assert rate is not None
        assert isinstance(rate, (int, float))
        assert rate == TIIECatalog.get_valor_actual(plazo=28)

    def test_calcular_interes_both_records(self):
        """Test calculating interest when both dates have records"""
        data = TIIECatalog.get_data(plazo=28)
        if len(data) >= 2:
            fecha_inicio = data[0]["fecha"]
            fecha_fin = data[1]["fecha"]

            result = TIIECatalog.calcular_interes(10000, fecha_inicio, fecha_fin, plazo=28)
            if result is not None:
                assert isinstance(result, float)
                assert result >= 0

    def test_calcular_interes_no_records(self):
        """Test calculating interest when no records found"""
        result = TIIECatalog.calcular_interes(10000, "1900-01-01", "1900-02-01", plazo=28)
        assert result is None

    def test_calcular_interes_only_inicio(self):
        """Test calculating interest with only start date record"""
        with patch.object(TIIECatalog, "get_por_fecha") as mock_get:
            mock_get.side_effect = [{"fecha": "2024-01-01", "tasa": 10.0, "plazo": 28}, None]

            result = TIIECatalog.calcular_interes(10000, "2024-01-01", "2024-02-01", plazo=28)
            assert result is not None
            assert isinstance(result, float)

    def test_calcular_interes_only_fin(self):
        """Test calculating interest with only end date record"""
        with patch.object(TIIECatalog, "get_por_fecha") as mock_get:
            mock_get.side_effect = [None, {"fecha": "2024-02-01", "tasa": 10.0, "plazo": 28}]

            result = TIIECatalog.calcular_interes(10000, "2024-01-01", "2024-02-01", plazo=28)
            assert result is not None
            assert isinstance(result, float)

    def test_calcular_interes_only_fin_none_tasa(self):
        """Test calculating interest with only end date record but tasa is None"""
        with patch.object(TIIECatalog, "get_por_fecha") as mock_get:
            mock_get.side_effect = [None, {"fecha": "2024-02-01", "tasa": None, "plazo": 28}]

            result = TIIECatalog.calcular_interes(10000, "2024-01-01", "2024-02-01", plazo=28)
            assert result is None

    def test_calcular_interes_none_tasa(self):
        """Test calculating interest when tasa is None"""
        with patch.object(TIIECatalog, "get_por_fecha") as mock_get:
            mock_get.side_effect = [{"fecha": "2024-01-01", "tasa": None, "plazo": 28}, None]

            result = TIIECatalog.calcular_interes(10000, "2024-01-01", "2024-02-01", plazo=28)
            assert result is None

    def test_calcular_interes_zero_days(self):
        """Test calculating interest when same date"""
        data = TIIECatalog.get_data(plazo=28)
        if data:
            fecha = data[0]["fecha"]
            result = TIIECatalog.calcular_interes(10000, fecha, fecha, plazo=28)
            if result is not None:
                assert result == 0.0  # Zero interest if zero days


class TestConvenienceFunctions:
    """Test convenience functions at module level"""

    def test_get_tiie_actual(self):
        """Test get_tiie_actual convenience function"""
        record = get_tiie_actual(plazo=28)
        assert record is not None
        assert isinstance(record, dict)
        assert "fecha" in record

    def test_get_tiie_por_fecha(self):
        """Test get_tiie_por_fecha convenience function"""
        data = TIIECatalog.get_data(plazo=28)
        if data:
            fecha = data[0]["fecha"]
            record = get_tiie_por_fecha(fecha, plazo=28)
            assert record is not None
            assert isinstance(record, dict)

    def test_get_tiie_valor_actual(self):
        """Test get_tiie_valor_actual convenience function"""
        valor = get_tiie_valor_actual(plazo=28)
        assert valor is not None
        assert isinstance(valor, (int, float))
        assert valor > 0
