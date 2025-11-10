#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for IFT catalogs (Códigos LADA and Operadores Móviles)"""

import unittest
from catalogmx.catalogs.ift import CodigosLADACatalog, OperadoresMovilesCatalog


class TestCodigosLADACatalog(unittest.TestCase):
    """Test LADA codes catalog"""

    def test_get_all(self):
        """Test getting all LADA codes"""
        codigos = CodigosLADACatalog.get_all()
        self.assertIsInstance(codigos, list)
        self.assertGreater(len(codigos), 200)  # At least 231 codes currently

    def test_buscar_por_lada_exists(self):
        """Test searching for existing LADA codes"""
        # Test major city codes
        cdmx = CodigosLADACatalog.buscar_por_lada("55")
        self.assertIsNotNone(cdmx)
        self.assertEqual(cdmx['lada'], "55")
        self.assertIn("México", cdmx['ciudad'])

        guadalajara = CodigosLADACatalog.buscar_por_lada("33")
        self.assertIsNotNone(guadalajara)
        self.assertEqual(guadalajara['lada'], "33")
        self.assertEqual(guadalajara['ciudad'], "Guadalajara")
        self.assertEqual(guadalajara['estado'], "Jalisco")

        monterrey = CodigosLADACatalog.buscar_por_lada("81")
        self.assertIsNotNone(monterrey)
        self.assertEqual(monterrey['lada'], "81")
        self.assertEqual(monterrey['ciudad'], "Monterrey")

    def test_buscar_por_lada_not_found(self):
        """Test searching for non-existent LADA code"""
        codigo = CodigosLADACatalog.buscar_por_lada("00")
        self.assertIsNone(codigo)

    def test_buscar_por_ciudad(self):
        """Test searching by city name"""
        # Test partial search
        guadalajara = CodigosLADACatalog.buscar_por_ciudad("Guadalajara")
        self.assertIsInstance(guadalajara, list)
        self.assertGreater(len(guadalajara), 0)
        self.assertEqual(guadalajara[0]['ciudad'], "Guadalajara")

        # Test partial match
        san = CodigosLADACatalog.buscar_por_ciudad("San")
        self.assertIsInstance(san, list)
        self.assertGreater(len(san), 5)  # Multiple cities start with "San"

    def test_buscar_por_ciudad_case_insensitive(self):
        """Test case-insensitive city search"""
        upper = CodigosLADACatalog.buscar_por_ciudad("GUADALAJARA")
        lower = CodigosLADACatalog.buscar_por_ciudad("guadalajara")
        self.assertEqual(len(upper), len(lower))

    def test_get_por_estado(self):
        """Test getting LADA codes by state"""
        jalisco = CodigosLADACatalog.get_por_estado("Jalisco")
        self.assertIsInstance(jalisco, list)
        self.assertGreater(len(jalisco), 5)  # Jalisco has multiple LADA codes

        for codigo in jalisco:
            self.assertEqual(codigo['estado'], "Jalisco")

    def test_get_por_estado_case_insensitive(self):
        """Test case-insensitive state search"""
        upper = CodigosLADACatalog.get_por_estado("JALISCO")
        lower = CodigosLADACatalog.get_por_estado("jalisco")
        self.assertEqual(len(upper), len(lower))

    def test_get_por_tipo(self):
        """Test getting LADA codes by type"""
        metropolitanas = CodigosLADACatalog.get_por_tipo("metropolitana")
        self.assertIsInstance(metropolitanas, list)
        self.assertGreater(len(metropolitanas), 0)
        for codigo in metropolitanas:
            self.assertEqual(codigo['tipo'], "metropolitana")

        fronterizas = CodigosLADACatalog.get_por_tipo("fronteriza")
        self.assertIsInstance(fronterizas, list)
        for codigo in fronterizas:
            self.assertEqual(codigo['tipo'], "fronteriza")

    def test_get_por_region(self):
        """Test getting LADA codes by region"""
        occidente = CodigosLADACatalog.get_por_region("occidente")
        self.assertIsInstance(occidente, list)
        self.assertGreater(len(occidente), 0)
        for codigo in occidente:
            self.assertEqual(codigo['region'], "occidente")

        norte = CodigosLADACatalog.get_por_region("norte")
        self.assertIsInstance(norte, list)
        self.assertGreater(len(norte), 0)

    def test_get_metropolitanas(self):
        """Test getting metropolitan LADA codes"""
        metropolitanas = CodigosLADACatalog.get_metropolitanas()
        self.assertIsInstance(metropolitanas, list)
        self.assertGreater(len(metropolitanas), 0)
        # Verify major metropolitan areas are included
        ladas = [c['lada'] for c in metropolitanas]
        self.assertIn("55", ladas)  # CDMX
        self.assertIn("33", ladas)  # Guadalajara
        self.assertIn("81", ladas)  # Monterrey

    def test_get_fronterizas(self):
        """Test getting border LADA codes"""
        fronterizas = CodigosLADACatalog.get_fronterizas()
        self.assertIsInstance(fronterizas, list)
        self.assertGreater(len(fronterizas), 0)
        for codigo in fronterizas:
            self.assertEqual(codigo['tipo'], "fronteriza")

    def test_get_turisticas(self):
        """Test getting tourist destination LADA codes"""
        turisticas = CodigosLADACatalog.get_turisticas()
        self.assertIsInstance(turisticas, list)
        # May or may not have tourist codes depending on data
        for codigo in turisticas:
            self.assertEqual(codigo['tipo'], "turistica")

    def test_validar_numero_valid_10_digits(self):
        """Test validating valid 10-digit phone numbers"""
        # Guadalajara number (33 + 8 digits)
        result = CodigosLADACatalog.validar_numero("3312345678")
        self.assertTrue(result['valid'])
        self.assertEqual(result['lada'], "33")
        self.assertEqual(result['numero_local'], "12345678")
        self.assertEqual(result['ciudad'], "Guadalajara")
        self.assertEqual(result['estado'], "Jalisco")
        self.assertIsNone(result['error'])

    def test_validar_numero_with_spaces(self):
        """Test validating numbers with spaces"""
        result = CodigosLADACatalog.validar_numero("33 1234 5678")
        self.assertTrue(result['valid'])
        self.assertEqual(result['lada'], "33")
        self.assertEqual(result['numero_local'], "12345678")

    def test_validar_numero_with_dashes(self):
        """Test validating numbers with dashes"""
        result = CodigosLADACatalog.validar_numero("33-1234-5678")
        self.assertTrue(result['valid'])
        self.assertEqual(result['lada'], "33")

    def test_validar_numero_invalid_length(self):
        """Test validating numbers with invalid length"""
        # Too short
        result = CodigosLADACatalog.validar_numero("123456")
        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])

        # Too long
        result = CodigosLADACatalog.validar_numero("123456789012")
        self.assertFalse(result['valid'])

    def test_validar_numero_invalid_characters(self):
        """Test validating numbers with invalid characters"""
        result = CodigosLADACatalog.validar_numero("33-ABCD-5678")
        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])

    def test_validar_numero_unknown_lada(self):
        """Test validating number with unknown LADA code"""
        result = CodigosLADACatalog.validar_numero("0012345678")
        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])
        self.assertIn("no encontrado", result['error'])

    def test_formatear_numero_2_digit_lada(self):
        """Test formatting number with 2-digit LADA"""
        formatted = CodigosLADACatalog.formatear_numero("3312345678")
        self.assertIn("33", formatted)
        self.assertIn("1234", formatted)
        self.assertIn("5678", formatted)

    def test_formatear_numero_3_digit_lada(self):
        """Test formatting number with 3-digit LADA"""
        # Find a 3-digit LADA code for testing
        codigos = CodigosLADACatalog.get_all()
        lada_3_digitos = None
        for codigo in codigos:
            if len(codigo['lada']) == 3:
                lada_3_digitos = codigo['lada']
                break

        if lada_3_digitos:
            numero = lada_3_digitos + "1234567"
            formatted = CodigosLADACatalog.formatear_numero(numero)
            self.assertIn(lada_3_digitos, formatted)

    def test_formatear_numero_invalid(self):
        """Test formatting invalid number returns original"""
        invalid = "123"
        formatted = CodigosLADACatalog.formatear_numero(invalid)
        self.assertEqual(formatted, invalid)

    def test_get_info_numero_valid(self):
        """Test getting full info for valid number"""
        info = CodigosLADACatalog.get_info_numero("3312345678")
        self.assertIsNotNone(info)
        self.assertEqual(info['lada'], "33")
        self.assertEqual(info['ciudad'], "Guadalajara")
        self.assertEqual(info['estado'], "Jalisco")
        self.assertIn('tipo', info)
        self.assertIn('region', info)

    def test_get_info_numero_invalid(self):
        """Test getting info for invalid number"""
        info = CodigosLADACatalog.get_info_numero("123")
        self.assertIsNone(info)

        info = CodigosLADACatalog.get_info_numero("0012345678")
        self.assertIsNone(info)

    def test_get_estadisticas(self):
        """Test getting catalog statistics"""
        stats = CodigosLADACatalog.get_estadisticas()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_codigos', stats)
        self.assertIn('codigos_metropolitanos', stats)
        self.assertIn('codigos_fronterizos', stats)
        self.assertIn('codigos_turisticos', stats)
        self.assertIn('estados_cubiertos', stats)
        self.assertIn('regiones', stats)
        self.assertIn('tipos', stats)

        # Verify reasonable values
        self.assertGreater(stats['total_codigos'], 200)
        self.assertGreaterEqual(stats['estados_cubiertos'], 32)  # At least 32 states (may have CDMX separately)


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
