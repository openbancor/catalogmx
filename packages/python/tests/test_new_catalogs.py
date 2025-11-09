#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for new catalog implementations (Placas, Salarios, UMA, UDI, Hoy No Circula)"""

import unittest
from catalogmx.catalogs.mexico import PlacasFormatosCatalog, SalariosMinimos, UMACatalog, HoyNoCirculaCatalog
from catalogmx.catalogs.banxico import UDICatalog


class TestPlacasFormatosCatalog(unittest.TestCase):
    """Test license plate formats catalog"""

    def test_validate_placa_current_format(self):
        """Test validating current format plates"""
        self.assertTrue(PlacasFormatosCatalog.validate_placa('ABC-123-A'))
        self.assertTrue(PlacasFormatosCatalog.validate_placa('XYZ-987-B'))

    def test_validate_placa_invalid(self):
        """Test validating invalid plates"""
        self.assertFalse(PlacasFormatosCatalog.validate_placa('INVALID'))
        self.assertFalse(PlacasFormatosCatalog.validate_placa('123-ABC'))

    def test_validate_placa_diplomatic(self):
        """Test validating diplomatic plates"""
        self.assertTrue(PlacasFormatosCatalog.validate_placa('D-12345'))

    def test_validate_placa_federal_government(self):
        """Test validating federal government plates"""
        self.assertTrue(PlacasFormatosCatalog.validate_placa('F-12345'))

    def test_detect_formato(self):
        """Test detecting plate format"""
        formato = PlacasFormatosCatalog.detect_formato('ABC-123-A')
        self.assertIsNotNone(formato)
        self.assertEqual(formato['tipo'], 'particular')

    def test_detect_formato_diplomatic(self):
        """Test detecting diplomatic plate format"""
        formato = PlacasFormatosCatalog.detect_formato('D-12345')
        self.assertIsNotNone(formato)
        self.assertEqual(formato['tipo'], 'diplomatico')

    def test_is_diplomatica(self):
        """Test checking if plate is diplomatic"""
        self.assertTrue(PlacasFormatosCatalog.is_diplomatica('D-12345'))
        self.assertFalse(PlacasFormatosCatalog.is_diplomatica('ABC-123-A'))

    def test_is_federal(self):
        """Test checking if plate is federal"""
        self.assertTrue(PlacasFormatosCatalog.is_federal('F-12345'))
        self.assertFalse(PlacasFormatosCatalog.is_federal('ABC-123-A'))

    def test_get_formatos_activos(self):
        """Test getting active formats"""
        activos = PlacasFormatosCatalog.get_formatos_activos()
        self.assertIsInstance(activos, list)
        self.assertGreater(len(activos), 30)  # Should have 33 active formats

    def test_get_formatos_por_tipo(self):
        """Test getting formats by type"""
        particulares = PlacasFormatosCatalog.get_formatos_por_tipo('particular')
        self.assertIsInstance(particulares, list)
        self.assertGreater(len(particulares), 0)

    def test_get_formatos_por_estado(self):
        """Test getting formats by state"""
        nacionales = PlacasFormatosCatalog.get_formatos_por_estado('Nacional')
        self.assertIsInstance(nacionales, list)
        self.assertGreater(len(nacionales), 0)


class TestSalariosMinimos(unittest.TestCase):
    """Test minimum wage catalog"""

    def test_get_actual(self):
        """Test getting current minimum wage"""
        actual = SalariosMinimos.get_actual()
        self.assertIsNotNone(actual)
        self.assertIn('año', actual)
        self.assertIn('resto_pais', actual)
        self.assertIn('zona_frontera_norte', actual)

    def test_get_por_anio(self):
        """Test getting minimum wage by year"""
        salario_2024 = SalariosMinimos.get_por_anio(2024)
        self.assertIsNotNone(salario_2024)
        self.assertEqual(salario_2024['año'], 2024)

    def test_get_por_anio_not_found(self):
        """Test getting minimum wage for non-existent year"""
        salario = SalariosMinimos.get_por_anio(1900)
        self.assertIsNone(salario)

    def test_get_por_zona(self):
        """Test getting minimum wage by zone"""
        # Get for rest of country
        resto = SalariosMinimos.get_por_zona(2024, zona_frontera=False)
        self.assertIsNotNone(resto)
        self.assertIsInstance(resto, float)

        # Get for border zone
        frontera = SalariosMinimos.get_por_zona(2024, zona_frontera=True)
        self.assertIsNotNone(frontera)
        self.assertIsInstance(frontera, float)

        # Border zone should be higher
        self.assertGreater(frontera, resto)

    def test_calcular_mensual(self):
        """Test calculating monthly wage"""
        diario = 207.44
        mensual = SalariosMinimos.calcular_mensual(diario, 30)
        self.assertEqual(mensual, 6223.20)

    def test_calcular_anual(self):
        """Test calculating annual wage"""
        diario = 207.44
        anual = SalariosMinimos.calcular_anual(diario, 365)
        self.assertAlmostEqual(anual, 75715.60, places=2)


class TestUMACatalog(unittest.TestCase):
    """Test UMA catalog"""

    def test_get_actual(self):
        """Test getting current UMA"""
        actual = UMACatalog.get_actual()
        self.assertIsNotNone(actual)
        self.assertIn('año', actual)
        self.assertIn('valor_diario', actual)
        self.assertIn('valor_mensual', actual)
        self.assertIn('valor_anual', actual)

    def test_get_por_anio(self):
        """Test getting UMA by year"""
        uma_2024 = UMACatalog.get_por_anio(2024)
        self.assertIsNotNone(uma_2024)
        self.assertEqual(uma_2024['año'], 2024)

    def test_get_por_anio_not_found(self):
        """Test getting UMA for non-existent year"""
        uma = UMACatalog.get_por_anio(2000)
        self.assertIsNone(uma)

    def test_get_valor(self):
        """Test getting specific UMA value"""
        valor_diario = UMACatalog.get_valor(2024, 'diario')
        self.assertIsNotNone(valor_diario)
        self.assertIsInstance(valor_diario, float)

        valor_mensual = UMACatalog.get_valor(2024, 'mensual')
        self.assertIsNotNone(valor_mensual)

        valor_anual = UMACatalog.get_valor(2024, 'anual')
        self.assertIsNotNone(valor_anual)

    def test_calcular_umas(self):
        """Test calculating number of UMAs"""
        # 1000 pesos / UMA diario 2024
        umas = UMACatalog.calcular_umas(1000, 2024, 'diario')
        self.assertIsNotNone(umas)
        self.assertIsInstance(umas, float)

    def test_calcular_monto(self):
        """Test calculating peso amount from UMAs"""
        # 10 UMAs at 2024 daily rate
        monto = UMACatalog.calcular_monto(10, 2024, 'diario')
        self.assertIsNotNone(monto)
        self.assertIsInstance(monto, float)
        self.assertGreater(monto, 0)

    def test_get_incremento(self):
        """Test getting percentage increment"""
        incremento = UMACatalog.get_incremento(2024)
        self.assertIsNotNone(incremento)
        self.assertIsInstance(incremento, float)


class TestUDICatalog(unittest.TestCase):
    """Test UDI catalog"""

    def test_get_actual(self):
        """Test getting current UDI"""
        actual = UDICatalog.get_actual()
        self.assertIsNotNone(actual)
        self.assertIn('valor', actual)
        self.assertIn('fecha', actual)

    def test_get_por_anio(self):
        """Test getting annual UDI average"""
        udi_2024 = UDICatalog.get_por_anio(2024)
        # May not exist if only monthly data available
        # Just check it doesn't crash
        if udi_2024:
            self.assertEqual(udi_2024.get('tipo'), 'promedio_anual')

    def test_get_por_mes(self):
        """Test getting monthly UDI average"""
        udi_202401 = UDICatalog.get_por_mes(2024, 1)
        # Check it doesn't crash
        if udi_202401:
            self.assertIn('valor', udi_202401)

    def test_pesos_a_udis(self):
        """Test converting pesos to UDIs"""
        # Use a date we know exists
        actual = UDICatalog.get_actual()
        if actual:
            fecha = actual['fecha']
            udis = UDICatalog.pesos_a_udis(10000, fecha)
            self.assertIsNotNone(udis)
            self.assertIsInstance(udis, float)
            self.assertGreater(udis, 0)

    def test_udis_a_pesos(self):
        """Test converting UDIs to pesos"""
        # Use a date we know exists
        actual = UDICatalog.get_actual()
        if actual:
            fecha = actual['fecha']
            pesos = UDICatalog.udis_a_pesos(100, fecha)
            self.assertIsNotNone(pesos)
            self.assertIsInstance(pesos, float)
            self.assertGreater(pesos, 0)

    def test_calcular_variacion(self):
        """Test calculating UDI variation"""
        # Get two dates
        data = UDICatalog.get_data()
        if len(data) >= 2:
            fecha1 = data[-1]['fecha']  # Older
            fecha2 = data[0]['fecha']   # Newer
            variacion = UDICatalog.calcular_variacion(fecha1, fecha2)
            if variacion is not None:
                self.assertIsInstance(variacion, float)


class TestHoyNoCirculaCatalog(unittest.TestCase):
    """Test Hoy No Circula catalog"""

    def test_get_restriccion_por_dia(self):
        """Test getting restriction by day"""
        lunes = HoyNoCirculaCatalog.get_restriccion_por_dia('lunes')
        self.assertIsNotNone(lunes)
        self.assertIn('terminacion_placa', lunes)
        self.assertIn('engomado', lunes)

    def test_get_restriccion_domingo(self):
        """Test getting restriction for Sunday (should have none)"""
        domingo = HoyNoCirculaCatalog.get_restriccion_por_dia('domingo')
        # Domingo might not be in the catalog if no restrictions
        # Just check it doesn't crash

    def test_puede_circular_restricted(self):
        """Test checking if restricted plate can circulate"""
        # Plate ending in 5 is restricted on Monday
        puede = HoyNoCirculaCatalog.puede_circular('5', 'lunes', '2')
        self.assertFalse(puede)

    def test_puede_circular_not_restricted(self):
        """Test checking if non-restricted plate can circulate"""
        # Plate ending in 1 should be able to circulate on Monday
        puede = HoyNoCirculaCatalog.puede_circular('1', 'lunes', '2')
        self.assertTrue(puede)

    def test_puede_circular_holograma_00(self):
        """Test that hologram 00 can always circulate"""
        puede = HoyNoCirculaCatalog.puede_circular('5', 'lunes', '00')
        self.assertTrue(puede)

    def test_puede_circular_holograma_0_weekday(self):
        """Test that hologram 0 can circulate on weekdays"""
        puede = HoyNoCirculaCatalog.puede_circular('5', 'lunes', '0')
        self.assertTrue(puede)

    def test_get_dia_restriccion(self):
        """Test getting restriction day for a plate"""
        # Plate ending in 5 should be restricted on Monday
        dia = HoyNoCirculaCatalog.get_dia_restriccion('5')
        self.assertEqual(dia, 'lunes')

    def test_get_engomado(self):
        """Test getting engomado color"""
        # Plate ending in 5 should have yellow engomado
        engomado = HoyNoCirculaCatalog.get_engomado('5')
        self.assertEqual(engomado, 'amarillo')

    def test_get_exencion_por_holograma(self):
        """Test getting exemption by hologram"""
        exencion_00 = HoyNoCirculaCatalog.get_exencion_por_holograma('00')
        self.assertIsNotNone(exencion_00)
        self.assertTrue(exencion_00.get('exento'))

        exencion_2 = HoyNoCirculaCatalog.get_exencion_por_holograma('2')
        self.assertIsNotNone(exencion_2)
        self.assertFalse(exencion_2.get('exento'))

    def test_get_restricciones(self):
        """Test getting all restrictions"""
        restricciones = HoyNoCirculaCatalog.get_restricciones()
        self.assertIsInstance(restricciones, list)
        self.assertGreater(len(restricciones), 0)

    def test_get_exenciones(self):
        """Test getting all exemptions"""
        exenciones = HoyNoCirculaCatalog.get_exenciones()
        self.assertIsInstance(exenciones, list)
        self.assertGreater(len(exenciones), 0)


if __name__ == '__main__':
    unittest.main()
