#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for IFT catalogs (Operadores Móviles)"""

import unittest
from catalogmx.catalogs.ift import OperadoresMovilesCatalog


class TestOperadoresMovilesCatalog(unittest.TestCase):
    """Test mobile operators catalog"""

    def test_get_all(self):
        """Test getting all mobile operators"""
        operadores = OperadoresMovilesCatalog.get_all()
        self.assertIsInstance(operadores, list)
        self.assertGreater(len(operadores), 0)

    def test_get_activos(self):
        """Test getting active operators"""
        activos = OperadoresMovilesCatalog.get_activos()
        self.assertIsInstance(activos, list)
        self.assertGreater(len(activos), 0)
        for op in activos:
            self.assertTrue(op['activo'])

    def test_get_inactivos(self):
        """Test getting inactive operators"""
        inactivos = OperadoresMovilesCatalog.get_inactivos()
        self.assertIsInstance(inactivos, list)
        for op in inactivos:
            self.assertFalse(op['activo'])

    def test_buscar_por_nombre_exact(self):
        """Test searching operator by exact name"""
        telcel = OperadoresMovilesCatalog.buscar_por_nombre("Telcel")
        self.assertIsNotNone(telcel)
        self.assertIn("Telcel", telcel['nombre_comercial'])

    def test_buscar_por_nombre_case_insensitive(self):
        """Test case-insensitive operator search"""
        upper = OperadoresMovilesCatalog.buscar_por_nombre("TELCEL")
        lower = OperadoresMovilesCatalog.buscar_por_nombre("telcel")
        self.assertEqual(upper['nombre_comercial'], lower['nombre_comercial'])

    def test_buscar_por_nombre_partial(self):
        """Test partial name search"""
        at = OperadoresMovilesCatalog.buscar_por_nombre("AT")
        self.assertIsNotNone(at)
        # Should find AT&T

    def test_buscar_por_nombre_not_found(self):
        """Test searching for non-existent operator"""
        operator = OperadoresMovilesCatalog.buscar_por_nombre("NonExistentOperator123")
        self.assertIsNone(operator)

    def test_get_por_tipo_omr(self):
        """Test getting operators with own network (OMR)"""
        omr = OperadoresMovilesCatalog.get_por_tipo("OMR")
        self.assertIsInstance(omr, list)
        self.assertGreater(len(omr), 0)
        for op in omr:
            self.assertEqual(op['tipo'], "OMR")

    def test_get_por_tipo_omv(self):
        """Test getting virtual operators (OMV)"""
        omv = OperadoresMovilesCatalog.get_por_tipo("OMV")
        self.assertIsInstance(omv, list)
        for op in omv:
            self.assertEqual(op['tipo'], "OMV")

    def test_get_por_tipo_case_insensitive(self):
        """Test case-insensitive type search"""
        upper = OperadoresMovilesCatalog.get_por_tipo("OMR")
        lower = OperadoresMovilesCatalog.get_por_tipo("omr")
        self.assertEqual(len(upper), len(lower))

    def test_get_con_tecnologia_5g(self):
        """Test getting operators with 5G"""
        con_5g = OperadoresMovilesCatalog.get_con_tecnologia("5G")
        self.assertIsInstance(con_5g, list)
        for op in con_5g:
            self.assertIn("5G", op['tecnologias'])

    def test_get_con_tecnologia_4g(self):
        """Test getting operators with 4G"""
        con_4g = OperadoresMovilesCatalog.get_con_tecnologia("4G")
        self.assertIsInstance(con_4g, list)
        self.assertGreater(len(con_4g), 0)
        for op in con_4g:
            self.assertIn("4G", op['tecnologias'])

    def test_get_con_tecnologia_case_insensitive(self):
        """Test case-insensitive technology search"""
        upper = OperadoresMovilesCatalog.get_con_tecnologia("5G")
        lower = OperadoresMovilesCatalog.get_con_tecnologia("5g")
        self.assertEqual(len(upper), len(lower))

    def test_get_por_cobertura_nacional(self):
        """Test getting operators with national coverage"""
        nacionales = OperadoresMovilesCatalog.get_por_cobertura("nacional")
        self.assertIsInstance(nacionales, list)
        self.assertGreater(len(nacionales), 0)
        for op in nacionales:
            self.assertEqual(op['cobertura'], "nacional")

    def test_get_por_cobertura_regional(self):
        """Test getting operators with regional coverage"""
        regionales = OperadoresMovilesCatalog.get_por_cobertura("regional")
        self.assertIsInstance(regionales, list)
        for op in regionales:
            self.assertEqual(op['cobertura'], "regional")

    def test_get_por_grupo(self):
        """Test getting operators by business group"""
        # Test América Móvil group
        america_movil = OperadoresMovilesCatalog.get_por_grupo("América Móvil")
        self.assertIsInstance(america_movil, list)
        if len(america_movil) > 0:
            for op in america_movil:
                self.assertIn("américa móvil", op['grupo_empresarial'].lower())

    def test_get_por_grupo_case_insensitive(self):
        """Test case-insensitive group search"""
        upper = OperadoresMovilesCatalog.get_por_grupo("AMÉRICA")
        lower = OperadoresMovilesCatalog.get_por_grupo("américa")
        # Both should find América Móvil
        if len(upper) > 0:
            self.assertEqual(len(upper), len(lower))

    def test_get_con_servicio_prepago(self):
        """Test getting operators with prepaid service"""
        prepago = OperadoresMovilesCatalog.get_con_servicio("prepago")
        self.assertIsInstance(prepago, list)
        self.assertGreater(len(prepago), 0)
        for op in prepago:
            self.assertIn("prepago", op['servicios'])

    def test_get_con_servicio_postpago(self):
        """Test getting operators with postpaid service"""
        postpago = OperadoresMovilesCatalog.get_con_servicio("postpago")
        self.assertIsInstance(postpago, list)
        self.assertGreater(len(postpago), 0)
        for op in postpago:
            self.assertIn("postpago", op['servicios'])

    def test_get_con_servicio_datos(self):
        """Test getting operators with data service"""
        datos = OperadoresMovilesCatalog.get_con_servicio("datos")
        self.assertIsInstance(datos, list)
        for op in datos:
            self.assertIn("datos", op['servicios'])

    def test_get_top_por_market_share_default(self):
        """Test getting top operators by market share (default limit)"""
        top = OperadoresMovilesCatalog.get_top_por_market_share()
        self.assertIsInstance(top, list)
        self.assertLessEqual(len(top), 5)  # Default limit is 5

        # Verify ordered by market share descending
        if len(top) > 1:
            for i in range(len(top) - 1):
                self.assertGreaterEqual(
                    top[i]['market_share_aprox'],
                    top[i + 1]['market_share_aprox']
                )

        # Verify all are active
        for op in top:
            self.assertTrue(op['activo'])

    def test_get_top_por_market_share_custom_limit(self):
        """Test getting top operators with custom limit"""
        top3 = OperadoresMovilesCatalog.get_top_por_market_share(3)
        self.assertIsInstance(top3, list)
        self.assertLessEqual(len(top3), 3)

    def test_get_estadisticas(self):
        """Test getting catalog statistics"""
        stats = OperadoresMovilesCatalog.get_estadisticas()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_operadores', stats)
        self.assertIn('operadores_activos', stats)
        self.assertIn('operadores_inactivos', stats)
        self.assertIn('omr_count', stats)
        self.assertIn('omv_count', stats)
        self.assertIn('operadores_con_5g', stats)
        self.assertIn('cobertura_nacional', stats)
        self.assertIn('market_share_total', stats)
        self.assertIn('tecnologias_disponibles', stats)

        # Verify reasonable values
        self.assertGreater(stats['total_operadores'], 0)
        self.assertGreaterEqual(
            stats['total_operadores'],
            stats['operadores_activos'] + stats['operadores_inactivos']
        )
        self.assertEqual(stats['tecnologias_disponibles'], ['2G', '3G', '4G', '5G'])


if __name__ == '__main__':
    unittest.main()
