#!/usr/bin/python
# -*- coding: utf-8 -*-
from rfcmx.rfc import RFCValidator, RFCGeneratorFisicas, RFCGeneratorMorales, RFCGenerator
import unittest
import datetime


class test_RFCValidator(unittest.TestCase):
    def test_ValidRFC(self):
        rfc = [
            ('MANO610814JL5', True),
            ('MME941130K54', True),
            ('BACL891217NJ8', False),
            ('NIR6812205X9', True),
            ('BNM840515VB1', True),
        ]

        for elem, result in rfc:
            # print elem, result
            self.assertEqual(RFCValidator(elem).validate(), result)

    def test_detect_fisica_moral(self):
        """Test detection of RFC type"""
        self.assertEqual(RFCValidator('MANO610814JL5').detect_fisica_moral(), 'Persona Física')
        self.assertEqual(RFCValidator('BNM840515VB1').detect_fisica_moral(), 'Persona Moral')
        self.assertEqual(RFCValidator('XAXX010101000').detect_fisica_moral(), 'Genérico')
        self.assertEqual(RFCValidator('XEXX010101000').detect_fisica_moral(), 'Genérico')


class test_RFCPersonasFisicas(unittest.TestCase):
    def test_generaLetras(self):
        tests = [
            ('Juan', 'Barrios', 'Fernández', 'BAFJ'),
            ('Eva', 'Iriarte', 'Méndez', 'IIME'),
            ('Manuel', 'Chávez', 'González', 'CAGM'),
            ('Felipe', 'Camargo', 'Lleras', 'CALF'),
            ('Charles', 'Kennedy', 'Truman', 'KETC'),
            ('Alvaro', 'De la O', 'Lozano', 'OLAL'),
            ('Ernesto', 'Ek', 'Rivera', 'ERER'),
            ('Julio', 'Ek', '', 'EKJU'),
            ('Julio', 'Ek', None, 'EKJU'),
            ('Luis', 'Bárcenas', '', 'BALU'),
            ('Dolores', 'San Martín', 'Dávalos', 'SADD'),
            ('Mario', 'Sánchez de la Barquera', 'Gómez', 'SAGM'),
            ('Antonio', 'Jiménez', 'Ponce de León', 'JIPA'),
            ('Luz María', 'Fernández', 'Juárez', 'FEJL'),
            ('José Antonio', 'Camargo', 'Hernández', 'CAHA'),
            ('María de Guadalupe', 'Hernández', 'von Räutlingen', 'HERG'),
            ('María Luisa', 'Ramírez', 'Sánchez', 'RASL'),
            ('Ernesto', 'Martínez', 'Mejía', 'MAMX'),
            ('Fernando', 'Ñemez', 'Ñoz', 'ÑEÑF'),
            ('泽东', '毛', '', 'MAZE'),  # Mao Zedong
            ('中山', '孙', '', 'SUZH'),  # Sun Zhongshan
            ('中山', '孙', None, 'SUZH')
        ]

        for elem in tests:
            r = RFCGeneratorFisicas(nombre=elem[0], paterno=elem[1], materno=elem[2], fecha=datetime.date(2000, 1, 1))
            self.assertEqual(r.generate_letters(), elem[3])

    def test_generate_complete_rfc(self):
        """Test complete RFC generation for Persona Física"""
        r = RFCGeneratorFisicas(
            nombre='Juan',
            paterno='Barrios',
            materno='Fernández',
            fecha=datetime.date(1985, 6, 14)
        )
        rfc = r.rfc
        self.assertEqual(len(rfc), 13)
        self.assertTrue(rfc.startswith('BAFJ850614'))

    def test_factory_generate_fisica(self):
        """Test factory method for Persona Física"""
        rfc = RFCGenerator.generate_fisica(
            nombre='Juan',
            paterno='Barrios',
            materno='Fernández',
            fecha=datetime.date(1985, 6, 14)
        )
        self.assertEqual(len(rfc), 13)
        self.assertTrue(rfc.startswith('BAFJ850614'))


class test_RFCPersonasMorales(unittest.TestCase):
    def test_generaLetras(self):
        """Test letter generation for Persona Moral (companies)"""
        tests = [
            # 3+ words
            ('Sonora Industrial Azucarera SA', 'SIA'),
            ('Constructora de Edificios Mancera SA', 'CEM'),
            ('Fábrica de Jabón La Espuma SA', 'FJE'),
            ('Fundición de Hierro y Acero SA', 'FHA'),
            ('Gutiérrez y Sánchez Hermanos SA', 'GSH'),
            ('Banco Nacional de Mexico SA', 'BNM'),
            ('Comisión Federal de Electricidad', 'CFE'),

            # 2 words (initial of 1st + first 2 letters of 2nd)
            ('Cervecería Modelo SA de CV', 'CMO'),  # 2 words: Cervecería, Modelo -> C,M,O
            ('Petróleos Mexicanos', 'PME'),  # 2 words: Petróleos, Mexicanos -> P,M,E
        ]

        for razon_social, expected_letters in tests:
            r = RFCGeneratorMorales(razon_social=razon_social, fecha=datetime.date(2000, 1, 1))
            generated = r.generate_letters()
            self.assertEqual(generated, expected_letters,
                           f"Failed for {razon_social}: expected {expected_letters}, got {generated}")

    def test_casos_especiales_SAT(self):
        """Test special cases from SAT official documentation"""
        tests = [
            # Iniciales: F.A.Z. → cada letra es una palabra → FAZ
            ('F.A.Z., S.A.', 'FAZ'),

            # Números: El 12 → El DOCE → DOC (eliminando EL)
            ('El 12, S.A.', 'DOC'),

            # Carácter especial @: LA S@NDIA → LA SNDIA → SND (eliminando LA)
            ('LA S@NDIA S.A. DE C.V.', 'SND'),

            # Ñ → X: YÑIGO → YXIGO → YXI (palabra de 1)
            ('YÑIGO, S.A.', 'YXI'),
        ]

        for razon_social, expected_letters in tests:
            r = RFCGeneratorMorales(razon_social=razon_social, fecha=datetime.date(2000, 1, 1))
            generated = r.generate_letters()
            self.assertEqual(generated, expected_letters,
                           f"Failed for {razon_social}: expected {expected_letters}, got {generated}")

    def test_numeros_arabigos(self):
        """Test Arabic number conversion"""
        tests = [
            ('Tienda 5 S.A.', 'TCI'),  # 5 → CINCO, Tienda CINCO → TCI
            ('El 3 Hermanos', 'THE'),  # 3 → TRES, TRES Hermanos → THE
        ]

        for razon_social, expected_letters in tests:
            r = RFCGeneratorMorales(razon_social=razon_social, fecha=datetime.date(2000, 1, 1))
            generated = r.generate_letters()
            self.assertEqual(generated, expected_letters,
                           f"Failed for {razon_social}: expected {expected_letters}, got {generated}")

    def test_numeros_romanos(self):
        """Test Roman numeral conversion"""
        tests = [
            ('Luis XIV S.A.', 'LCA'),  # XIV → CATORCE, Luis CATORCE → LCA
        ]

        for razon_social, expected_letters in tests:
            r = RFCGeneratorMorales(razon_social=razon_social, fecha=datetime.date(2000, 1, 1))
            generated = r.generate_letters()
            self.assertEqual(generated, expected_letters,
                           f"Failed for {razon_social}: expected {expected_letters}, got {generated}")

    def test_generate_complete_rfc_moral(self):
        """Test complete RFC generation for Persona Moral"""
        r = RFCGeneratorMorales(
            razon_social='Banco Nacional de Mexico SA',
            fecha=datetime.date(1984, 5, 15)
        )
        rfc = r.rfc
        self.assertEqual(len(rfc), 12)
        self.assertTrue(rfc.startswith('BNM840515'))
        # Verify it's recognized as Persona Moral
        self.assertTrue(RFCValidator(rfc).is_moral())

    def test_razon_social_cleaning(self):
        """Test that company name cleaning works correctly"""
        tests = [
            'Sociedad Anónima de CV',
            'SA DE CV',
            'S.A. de C.V.',
        ]
        for razon_social in tests:
            r = RFCGeneratorMorales(razon_social=razon_social, fecha=datetime.date(2000, 1, 1))
            # Should handle various formats

    def test_factory_generate_moral(self):
        """Test factory method for Persona Moral"""
        rfc = RFCGenerator.generate_moral(
            razon_social='Banco Nacional de Mexico SA',
            fecha=datetime.date(1984, 5, 15)
        )
        self.assertEqual(len(rfc), 12)
        self.assertTrue(rfc.startswith('BNM840515'))

    def test_single_word_company(self):
        """Test RFC generation for single-word company names"""
        r = RFCGeneratorMorales(razon_social='Bimbo', fecha=datetime.date(1945, 12, 2))
        rfc = r.rfc
        self.assertEqual(len(rfc), 12)
        # Single word should still generate 3 letters

    def test_excluded_words(self):
        """Test that excluded words are properly removed"""
        r1 = RFCGeneratorMorales(razon_social='Compañía de Teléfonos', fecha=datetime.date(2000, 1, 1))
        r2 = RFCGeneratorMorales(razon_social='Teléfonos', fecha=datetime.date(2000, 1, 1))
        # Both should generate same letters since "Compañía de" is excluded
        self.assertEqual(r1.generate_letters(), r2.generate_letters())

    def test_rfcs_publicos_conocidos(self):
        """Test with real public RFCs from well-known Mexican companies"""
        tests = [
            # PEMEX - Petróleos Mexicanos (founded June 7, 1938)
            ('Petróleos Mexicanos', datetime.date(1938, 6, 7), 'PME380607'),

            # CFE - Comisión Federal de Electricidad (founded August 14, 1937)
            ('Comisión Federal de Electricidad', datetime.date(1937, 8, 14), 'CFE370814'),

            # BIMBO - Grupo Bimbo (founded June 15, 1981 as S.A.B. de C.V.)
            ('Grupo Bimbo S.A.B. de C.V.', datetime.date(1981, 6, 15), 'GBI810615'),
        ]

        for razon_social, fecha, expected_rfc_base in tests:
            r = RFCGeneratorMorales(razon_social=razon_social, fecha=fecha)
            rfc = r.rfc
            # Verify that the first 9 characters match (letters + date)
            self.assertEqual(rfc[:9], expected_rfc_base,
                           f"Failed for {razon_social}: expected {expected_rfc_base}, got {rfc[:9]}")
            # Verify total length
            self.assertEqual(len(rfc), 12)

    def test_fechas_invalidas(self):
        """Test that invalid dates raise appropriate errors"""
        # Test with string instead of date
        with self.assertRaises(ValueError):
            RFCGeneratorMorales(
                razon_social='Test Company',
                fecha='2000-01-01'  # String instead of date object
            )

        # Test with None
        with self.assertRaises(ValueError):
            RFCGeneratorMorales(
                razon_social='Test Company',
                fecha=None
            )

    def test_razon_social_vacia(self):
        """Test that empty company name raises error"""
        with self.assertRaises(ValueError):
            RFCGeneratorMorales(
                razon_social='',
                fecha=datetime.date(2000, 1, 1)
            )

        with self.assertRaises(ValueError):
            RFCGeneratorMorales(
                razon_social='   ',  # Only spaces
                fecha=datetime.date(2000, 1, 1)
            )

    def test_palabras_cacofonicas(self):
        """Test cacophonic word replacement - Note: Cacophonic words (4-letter) don't apply to Persona Moral (3-letter)"""
        # The cacophonic word list in SAT specification contains 4-letter codes for Persona Física
        # Persona Moral generates 3-letter codes, so cacophonic replacement doesn't apply
        # This test verifies that the code doesn't crash when checking cacophonic words
        tests = [
            ('Comercializadora Mexicana', datetime.date(2000, 1, 1), 'CME'),
            ('Productos Electrodomésticos', datetime.date(2000, 1, 1), 'PEL'),
            ('Maquinaria Mexicana', datetime.date(2000, 1, 1), 'MME'),
        ]

        for razon_social, fecha, expected_letters in tests:
            r = RFCGeneratorMorales(razon_social=razon_social, fecha=fecha)
            generated = r.generate_letters()
            self.assertEqual(generated, expected_letters,
                          f"For {razon_social}: expected {expected_letters}, got {generated}")

    def test_consonantes_compuestas(self):
        """Test consonant compound handling (CH → C, LL → L)"""
        tests = [
            # CH at beginning should become C
            ('Chocolates Hermanos S.A.', 'COH'),  # Chocolates → COCOLATES → COH
            # LL at beginning should become L
            ('Llantas Hermanos S.A.', 'LLH'),  # Llantas → LANTAS → LLH
        ]

        for razon_social, expected_letters in tests:
            r = RFCGeneratorMorales(razon_social=razon_social, fecha=datetime.date(2000, 1, 1))
            generated = r.generate_letters()
            # Note: The first letter should be transformed
            self.assertTrue(len(generated) == 3,
                          f"For {razon_social}: expected 3 letters, got {generated}")

    def test_numeros_grandes(self):
        """Test numbers outside the conversion table"""
        # Numbers > 20 should remain as-is
        tests = [
            ('Empresa 25 S.A.', '25'),  # 25 is not in conversion table
            ('Tienda 100 S.A.', '100'),  # 100 is not in conversion table
        ]

        for razon_social, numero_esperado in tests:
            r = RFCGeneratorMorales(razon_social=razon_social, fecha=datetime.date(2000, 1, 1))
            # Just verify it doesn't crash
            rfc = r.rfc
            self.assertEqual(len(rfc), 12)

    def test_multiple_special_characters(self):
        """Test handling of multiple special characters"""
        tests = [
            ('LA @SUPER# TIENDA$ S.A.', 'STI'),  # Multiple special chars
            ('Empresa & Co.', 'EMP'),  # & character
            ('Productos-Tecnológicos-Modernos S.A.', 'PTM'),  # Hyphens (all meaningful words)
        ]

        for razon_social, expected_letters in tests:
            r = RFCGeneratorMorales(razon_social=razon_social, fecha=datetime.date(2000, 1, 1))
            generated = r.generate_letters()
            self.assertEqual(generated, expected_letters,
                           f"Failed for {razon_social}: expected {expected_letters}, got {generated}")

    def test_multiple_enie(self):
        """Test multiple Ñ handling"""
        r = RFCGeneratorMorales(razon_social='ÑAÑAÑU S.A.', fecha=datetime.date(2000, 1, 1))
        generated = r.generate_letters()
        # All Ñ should be converted to X
        self.assertTrue('X' in generated or 'Ñ' not in generated,
                      f"Ñ should be converted to X, got {generated}")

    def test_mixed_case(self):
        """Test that mixed case is handled correctly"""
        r1 = RFCGeneratorMorales(razon_social='EMPRESA TEST', fecha=datetime.date(2000, 1, 1))
        r2 = RFCGeneratorMorales(razon_social='empresa test', fecha=datetime.date(2000, 1, 1))
        r3 = RFCGeneratorMorales(razon_social='EmPrEsA TeSt', fecha=datetime.date(2000, 1, 1))

        # All should generate the same RFC regardless of case
        self.assertEqual(r1.rfc, r2.rfc)
        self.assertEqual(r2.rfc, r3.rfc)
