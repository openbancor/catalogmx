#!/usr/bin/python
# -*- coding: utf-8 -*-
from rfcmx.curp import CURPValidator, CURPGenerator, CURPException, CURPLengthError, CURPStructureError
import unittest
import datetime


class test_CURPValidator(unittest.TestCase):
    def test_valid_curp(self):
        """Test validation of valid CURPs"""
        valid_curps = [
            'HEGG560427MVZRRL04',
            'MARR890512HCSRYR09',
            'BEML920313HCMLNS09',
        ]
        for curp in valid_curps:
            validator = CURPValidator(curp)
            self.assertTrue(validator.is_valid())

    def test_invalid_length(self):
        """Test that invalid length raises error"""
        short_curp = 'HEGG560427'
        validator = CURPValidator(short_curp)
        with self.assertRaises(CURPLengthError):
            validator.validate()

    def test_invalid_structure(self):
        """Test that invalid structure raises error"""
        invalid_curp = '123456789012345678'  # 18 chars but invalid structure (all numbers)
        validator = CURPValidator(invalid_curp)
        with self.assertRaises(CURPStructureError):
            validator.validate()

    def test_is_valid_no_exception(self):
        """Test is_valid method doesn't raise exceptions"""
        invalid_curp = 'INVALID'
        validator = CURPValidator(invalid_curp)
        self.assertFalse(validator.is_valid())


class test_CURPGenerator(unittest.TestCase):
    def test_generate_letters(self):
        """Test letter generation for CURP"""
        tests = [
            # (nombre, paterno, materno, expected)
            # Format: First of paterno, first vowel of paterno, first of materno, first of nombre
            ('Juan', 'Barrios', 'Fernández', 'BAFJ'),
            ('Eva', 'Iriarte', 'Méndez', 'IIME'),
            ('Manuel', 'Chávez', 'González', 'CAGM'),
            ('Felipe', 'Camargo', 'Lleras', 'CALF'),
            ('Ernesto', 'Ek', 'Rivera', 'EXRE'),  # Ek has no vowel after E, so X
            ('Luis', 'Bárcenas', '', 'BAXL'),  # No materno
            ('Luisa', 'Ramírez', 'Sánchez', 'RASL'),  # Regular case
            ('Antonio', 'Camargo', 'Hernández', 'CAHA'),  # Regular case
        ]

        for nombre, paterno, materno, expected_letters in tests:
            generator = CURPGenerator(
                nombre=nombre,
                paterno=paterno,
                materno=materno,
                fecha_nacimiento=datetime.date(2000, 1, 1),
                sexo='H',
                estado='Jalisco'
            )
            generated = generator.generate_letters()
            self.assertEqual(generated, expected_letters,
                           f"Failed for {nombre} {paterno} {materno}: expected {expected_letters}, got {generated}")

    def test_generate_complete_curp(self):
        """Test complete CURP generation"""
        generator = CURPGenerator(
            nombre='Juan',
            paterno='Pérez',
            materno='García',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='H',
            estado='Jalisco'
        )
        curp = generator.curp
        self.assertEqual(len(curp), 18)
        self.assertTrue(curp.startswith('PEGJ900512H'))
        self.assertTrue('JC' in curp)  # Jalisco code

    def test_gender_codes(self):
        """Test gender codes"""
        male = CURPGenerator(
            nombre='Juan',
            paterno='Pérez',
            materno='García',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='H',
            estado='Jalisco'
        )
        self.assertIn('H', male.curp)

        female = CURPGenerator(
            nombre='María',
            paterno='Pérez',
            materno='García',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='M',
            estado='Jalisco'
        )
        self.assertIn('M', female.curp)

    def test_state_codes(self):
        """Test state code generation"""
        tests = [
            ('Jalisco', 'JC'),
            ('JALISCO', 'JC'),
            ('Nuevo Leon', 'NL'),
            ('Ciudad de Mexico', 'DF'),
            ('CDMX', 'DF'),
            ('Distrito Federal', 'DF'),
            ('Aguascalientes', 'AS'),
            ('Veracruz', 'VZ'),
            ('Extranjero', 'NE'),
        ]

        for estado, expected_code in tests:
            generator = CURPGenerator(
                nombre='Juan',
                paterno='Pérez',
                materno='García',
                fecha_nacimiento=datetime.date(1990, 5, 12),
                sexo='H',
                estado=estado
            )
            curp = generator.curp
            self.assertIn(expected_code, curp,
                        f"Failed for state {estado}: expected {expected_code} in {curp}")

    def test_consonants_generation(self):
        """Test internal consonant extraction"""
        generator = CURPGenerator(
            nombre='Juan',
            paterno='Pérez',
            materno='García',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='H',
            estado='Jalisco'
        )
        consonants = generator.generate_consonants()
        self.assertEqual(len(consonants), 3)
        # Pérez -> R (first internal consonant)
        # García -> R (first internal consonant)
        # Juan -> N (first internal consonant)
        self.assertEqual(consonants, 'RRN')

    def test_no_materno(self):
        """Test CURP generation without apellido materno"""
        generator = CURPGenerator(
            nombre='Juan',
            paterno='Pérez',
            materno='',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='H',
            estado='Jalisco'
        )
        curp = generator.curp
        self.assertEqual(len(curp), 18)
        # Should have X where materno would be
        self.assertTrue('PEXJ' in curp)

    def test_compound_name_jose(self):
        """Test that JOSE is skipped in compound names"""
        generator = CURPGenerator(
            nombre='José Antonio',
            paterno='Camargo',
            materno='Hernández',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='H',
            estado='Jalisco'
        )
        letters = generator.generate_letters()
        # Should use Antonio, not José
        self.assertTrue(letters.endswith('A'))  # First letter of Antonio

    def test_compound_name_maria(self):
        """Test that MARIA is skipped in compound names"""
        generator = CURPGenerator(
            nombre='María Luisa',
            paterno='Ramírez',
            materno='Sánchez',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='M',
            estado='Jalisco'
        )
        letters = generator.generate_letters()
        # Should use Luisa, not María
        self.assertTrue(letters.endswith('L'))  # First letter of Luisa

    def test_date_generation(self):
        """Test date formatting"""
        generator = CURPGenerator(
            nombre='Juan',
            paterno='Pérez',
            materno='García',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='H',
            estado='Jalisco'
        )
        date_str = generator.generate_date()
        self.assertEqual(date_str, '900512')

    def test_invalid_gender(self):
        """Test that invalid gender raises error"""
        with self.assertRaises(ValueError):
            CURPGenerator(
                nombre='Juan',
                paterno='Pérez',
                materno='García',
                fecha_nacimiento=datetime.date(1990, 5, 12),
                sexo='X',  # Invalid
                estado='Jalisco'
            )

    def test_invalid_date(self):
        """Test that invalid date raises error"""
        with self.assertRaises(ValueError):
            CURPGenerator(
                nombre='Juan',
                paterno='Pérez',
                materno='García',
                fecha_nacimiento='1990-05-12',  # Should be date object
                sexo='H',
                estado='Jalisco'
            )

    def test_missing_nombre(self):
        """Test that missing nombre raises error"""
        with self.assertRaises(ValueError):
            CURPGenerator(
                nombre='',
                paterno='Pérez',
                materno='García',
                fecha_nacimiento=datetime.date(1990, 5, 12),
                sexo='H',
                estado='Jalisco'
            )

    def test_missing_paterno(self):
        """Test that missing paterno raises error"""
        with self.assertRaises(ValueError):
            CURPGenerator(
                nombre='Juan',
                paterno='',
                materno='García',
                fecha_nacimiento=datetime.date(1990, 5, 12),
                sexo='H',
                estado='Jalisco'
            )

    def test_special_characters(self):
        """Test handling of special characters and accents"""
        generator = CURPGenerator(
            nombre='José',
            paterno='Pérez',
            materno='García',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='H',
            estado='Jalisco'
        )
        curp = generator.curp
        # Should handle accents properly
        self.assertEqual(len(curp), 18)


if __name__ == '__main__':
    unittest.main()
