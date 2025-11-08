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
            ('Sonora Industrial Azucarera SA', 'SIA'),
            ('Constructora de Edificios Mancera SA', 'CEM'),
            ('Fábrica de Jabón La Espuma SA', 'FJE'),
            ('Fundición de Hierro y Acero SA', 'FHA'),
            ('Gutiérrez y Sánchez Hermanos SA', 'GSH'),
            ('Banco Nacional de Mexico SA', 'BNM'),
            ('Cervecería Modelo SA de CV', 'CEM'),  # 2 words: Cervecería, Modelo -> C,E,M
            ('Petróleos Mexicanos', 'PEM'),  # 2 words: Petróleos, Mexicanos -> P,E,M
            ('Comisión Federal de Electricidad', 'CFE'),
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
