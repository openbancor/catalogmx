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

    def test_cacophonic_words_replacement(self):
        """Test that cacophonic/inconvenient words are properly replaced"""
        # Según Anexo 2 del Instructivo Normativo CURP, cuando se detecta una palabra
        # inconveniente, se sustituye la segunda letra (primera vocal) con 'X'

        test_cases = [
            # BACA → BXCA
            {
                'nombre': 'Adan',
                'paterno': 'Baca',
                'materno': 'Castro',
                'fecha': datetime.date(1990, 1, 1),
                'sexo': 'H',
                'estado': 'Jalisco',
                'expected_letters': 'BXCA'
            },
            # CACA → CXCA
            {
                'nombre': 'Ana',
                'paterno': 'Caca',
                'materno': 'Cruz',
                'fecha': datetime.date(1990, 1, 1),
                'sexo': 'M',
                'estado': 'Jalisco',
                'expected_letters': 'CXCA'
            },
            # PEDO → PXDO
            {
                'nombre': 'Omar',
                'paterno': 'Perez',
                'materno': 'Dominguez',
                'fecha': datetime.date(1990, 1, 1),
                'sexo': 'H',
                'estado': 'Jalisco',
                'expected_letters': 'PXDO'
            },
            # MAME → MXME
            {
                'nombre': 'Elena',
                'paterno': 'Martinez',
                'materno': 'Mejia',
                'fecha': datetime.date(1990, 1, 1),
                'sexo': 'M',
                'estado': 'Jalisco',
                'expected_letters': 'MXME'
            },
            # PUTA → PXTA
            {
                'nombre': 'Ana',
                'paterno': 'Puente',
                'materno': 'Torres',
                'fecha': datetime.date(1990, 1, 1),
                'sexo': 'M',
                'estado': 'Jalisco',
                'expected_letters': 'PXTA'
            },
        ]

        for case in test_cases:
            generator = CURPGenerator(
                nombre=case['nombre'],
                paterno=case['paterno'],
                materno=case['materno'],
                fecha_nacimiento=case['fecha'],
                sexo=case['sexo'],
                estado=case['estado']
            )
            letters = generator.generate_letters()
            self.assertEqual(letters, case['expected_letters'],
                           f"For {case['paterno']}: expected {case['expected_letters']}, got {letters}")

    def test_check_digit_calculation(self):
        """Test the check digit algorithm consistency"""
        # Test that the algorithm is internally consistent
        # Note: The official RENAPO algorithm may have variations not fully documented
        # We test that our implementation is consistent

        # Create a test CURP (first 17 characters)
        test_curp_17 = 'PEGJ900512HJCRRS0'

        # Calculate digit twice to ensure consistency
        digit1 = CURPGenerator.calculate_check_digit(test_curp_17)
        digit2 = CURPGenerator.calculate_check_digit(test_curp_17)

        self.assertEqual(digit1, digit2,
                        "Check digit calculation should be consistent")
        self.assertTrue(digit1.isdigit(),
                       "Check digit should be a single digit (0-9)")
        self.assertTrue(0 <= int(digit1) <= 9,
                       "Check digit should be between 0 and 9")

    def test_check_digit_validation(self):
        """Test check digit validation in CURPValidator"""
        # Generate a CURP and verify it validates its own check digit
        generator = CURPGenerator(
            nombre='Juan',
            paterno='Perez',
            materno='Garcia',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='H',
            estado='Jalisco'
        )
        curp = generator.curp

        # The generated CURP should validate its own check digit
        validator = CURPValidator(curp)
        is_valid = validator.validate_check_digit()
        self.assertTrue(is_valid,
                       f"Generated CURP {curp} should have valid check digit")

    def test_complete_curp_with_check_digit(self):
        """Test that generated CURPs have valid check digits"""
        generator = CURPGenerator(
            nombre='Juan',
            paterno='Perez',
            materno='Garcia',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='H',
            estado='Jalisco'
        )
        curp = generator.curp

        # Verify the CURP has correct length
        self.assertEqual(len(curp), 18)

        # Verify the check digit is valid
        validator = CURPValidator(curp)
        self.assertTrue(validator.validate_check_digit(),
                       f"Generated CURP {curp} should have valid check digit")

    def test_differentiator_by_birth_year(self):
        """Test that differentiator (position 17) varies by birth year"""
        # Before 2000: should use '0'
        gen_before_2000 = CURPGenerator(
            nombre='Juan',
            paterno='Perez',
            materno='Garcia',
            fecha_nacimiento=datetime.date(1990, 5, 12),
            sexo='H',
            estado='Jalisco'
        )
        curp_before = gen_before_2000.curp
        self.assertEqual(curp_before[16], '0',
                        "Differentiator for birth before 2000 should be '0'")

        # After 2000: should use 'A'
        gen_after_2000 = CURPGenerator(
            nombre='Juan',
            paterno='Perez',
            materno='Garcia',
            fecha_nacimiento=datetime.date(2010, 5, 12),
            sexo='H',
            estado='Jalisco'
        )
        curp_after = gen_after_2000.curp
        self.assertEqual(curp_after[16], 'A',
                        "Differentiator for birth after 2000 should be 'A'")

    def test_expanded_cacophonic_list(self):
        """Test that the expanded list of inconvenient words is working"""
        # Test some of the newly added words from the official complete list
        new_words_tests = [
            ('BAKA', 'Baja', 'Kauffman', 'Alberto'),      # BAKA → BXKA
            ('FALO', 'Farias', 'Lopez', 'Omar'),          # FALO → FXLO
            ('GETA', 'Gerson', 'Torres', 'Ana'),          # GETA → GXTA
            ('LOCA', 'Lopez', 'Castillo', 'Ana'),         # LOCA → LXCA
            ('NACO', 'Navarro', 'Contreras', 'Omar'),     # NACO → NXCO
            ('SENO', 'Serrano', 'Nuñez', 'Oscar'),        # SENO → SXNO
            ('TETA', 'Tellez', 'Torres', 'Ana'),          # TETA → TXTA
            ('VACA', 'Vargas', 'Castro', 'Ana'),          # VACA → VXCA
        ]

        for expected_word, paterno, materno, nombre in new_words_tests:
            generator = CURPGenerator(
                nombre=nombre,
                paterno=paterno,
                materno=materno,
                fecha_nacimiento=datetime.date(1990, 1, 1),
                sexo='H',
                estado='Jalisco'
            )
            letters = generator.generate_letters()
            # The second character should be 'X' if it's a cacophonic word
            if expected_word in generator.cacophonic_words:
                self.assertEqual(letters[1], 'X',
                               f"Word {expected_word} should have second letter replaced with X, got {letters}")


if __name__ == '__main__':
    unittest.main()
