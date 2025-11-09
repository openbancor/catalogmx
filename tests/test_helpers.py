#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the modern helper API"""

import unittest
import datetime
from rfcmx import (
    # RFC helpers
    generate_rfc_persona_fisica,
    generate_rfc_persona_moral,
    validate_rfc,
    detect_rfc_type,
    is_valid_rfc,
    # CURP helpers
    generate_curp,
    validate_curp,
    get_curp_info,
    is_valid_curp,
)


class TestRFCHelpers(unittest.TestCase):
    """Test RFC helper functions"""

    def test_generate_rfc_persona_fisica_with_string_date(self):
        """Test generating RFC with string date"""
        rfc = generate_rfc_persona_fisica(
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            fecha_nacimiento='1990-05-15'
        )
        self.assertEqual(len(rfc), 13)
        self.assertTrue(rfc.startswith('PEGJ900515'))

    def test_generate_rfc_persona_fisica_with_date_object(self):
        """Test generating RFC with datetime.date object"""
        rfc = generate_rfc_persona_fisica(
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            fecha_nacimiento=datetime.date(1990, 5, 15)
        )
        self.assertEqual(len(rfc), 13)
        self.assertTrue(rfc.startswith('PEGJ900515'))

    def test_generate_rfc_persona_moral_string_date(self):
        """Test generating company RFC with string date"""
        rfc = generate_rfc_persona_moral(
            razon_social='Grupo Bimbo S.A.B. de C.V.',
            fecha_constitucion='1981-06-15'
        )
        self.assertEqual(rfc, 'GBI810615945')

    def test_validate_rfc_valid(self):
        """Test validating a valid RFC"""
        self.assertTrue(validate_rfc('PEGJ900515LN5'))
        self.assertTrue(validate_rfc('GBI810615945'))

    def test_validate_rfc_invalid(self):
        """Test validating an invalid RFC"""
        self.assertFalse(validate_rfc('INVALID'))
        self.assertFalse(validate_rfc(''))

    def test_detect_rfc_type_fisica(self):
        """Test detecting RFC type for persona física"""
        self.assertEqual(detect_rfc_type('PEGJ900515LN5'), 'fisica')

    def test_detect_rfc_type_moral(self):
        """Test detecting RFC type for persona moral"""
        self.assertEqual(detect_rfc_type('GBI810615945'), 'moral')

    def test_detect_rfc_type_generico(self):
        """Test detecting generic RFC"""
        self.assertEqual(detect_rfc_type('XAXX010101000'), 'generico')

    def test_detect_rfc_type_invalid(self):
        """Test detecting invalid RFC"""
        self.assertIsNone(detect_rfc_type('INVALID'))

    def test_is_valid_rfc_alias(self):
        """Test is_valid_rfc alias function"""
        self.assertTrue(is_valid_rfc('PEGJ900515LN5'))
        self.assertFalse(is_valid_rfc('INVALID'))


class TestCURPHelpers(unittest.TestCase):
    """Test CURP helper functions"""

    def test_generate_curp_with_string_date(self):
        """Test generating CURP with string date"""
        curp = generate_curp(
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            fecha_nacimiento='1990-05-15',
            sexo='H',
            estado='Jalisco'
        )
        self.assertEqual(len(curp), 18)
        self.assertTrue(curp.startswith('PEGJ900515H'))

    def test_generate_curp_with_date_object(self):
        """Test generating CURP with datetime.date object"""
        curp = generate_curp(
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            fecha_nacimiento=datetime.date(1990, 5, 15),
            sexo='H',
            estado='Jalisco'
        )
        self.assertEqual(len(curp), 18)
        self.assertTrue(curp.startswith('PEGJ900515H'))

    def test_generate_curp_without_materno(self):
        """Test generating CURP without apellido materno"""
        curp = generate_curp(
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='',
            fecha_nacimiento='1990-05-15',
            sexo='H',
            estado='Jalisco'
        )
        self.assertEqual(len(curp), 18)
        # Third letter should be X when no apellido materno
        self.assertEqual(curp[2], 'X')

    def test_generate_curp_with_custom_differentiator(self):
        """Test generating CURP with custom differentiator for homonyms"""
        base_data = {
            'nombre': 'Juan',
            'apellido_paterno': 'Pérez',
            'apellido_materno': 'García',
            'fecha_nacimiento': '1990-05-15',
            'sexo': 'H',
            'estado': 'Jalisco'
        }

        # Generate multiple CURPs with different differentiators
        curp0 = generate_curp(**base_data, differentiator='0')
        curp1 = generate_curp(**base_data, differentiator='1')
        curp2 = generate_curp(**base_data, differentiator='2')

        # All should be valid
        self.assertTrue(validate_curp(curp0))
        self.assertTrue(validate_curp(curp1))
        self.assertTrue(validate_curp(curp2))

        # First 16 characters should be the same
        self.assertEqual(curp0[:16], curp1[:16])
        self.assertEqual(curp1[:16], curp2[:16])

        # Position 17 (differentiator) should be different
        self.assertEqual(curp0[16], '0')
        self.assertEqual(curp1[16], '1')
        self.assertEqual(curp2[16], '2')

        # Position 18 (check digit) should be different
        self.assertNotEqual(curp0[17], curp1[17])
        self.assertNotEqual(curp1[17], curp2[17])

    def test_generate_curp_with_alphanumeric_differentiator(self):
        """Test generating CURP with alphanumeric differentiator (for post-2000)"""
        curp_a = generate_curp(
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            fecha_nacimiento='2010-05-15',
            sexo='H',
            estado='Jalisco',
            differentiator='A'
        )
        curp_b = generate_curp(
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            fecha_nacimiento='2010-05-15',
            sexo='H',
            estado='Jalisco',
            differentiator='B'
        )

        # Both should be valid
        self.assertTrue(validate_curp(curp_a))
        self.assertTrue(validate_curp(curp_b))

        # Differentiators should be as specified
        self.assertEqual(curp_a[16], 'A')
        self.assertEqual(curp_b[16], 'B')

    def test_validate_curp_valid(self):
        """Test validating a valid CURP"""
        curp = generate_curp(
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            fecha_nacimiento='1990-05-15',
            sexo='H',
            estado='Jalisco'
        )
        self.assertTrue(validate_curp(curp))

    def test_validate_curp_invalid(self):
        """Test validating an invalid CURP"""
        self.assertFalse(validate_curp('INVALID'))
        self.assertFalse(validate_curp(''))
        self.assertFalse(validate_curp('PEGJ900515'))  # Too short

    def test_validate_curp_invalid_check_digit(self):
        """Test validating CURP with invalid check digit"""
        # Generate valid CURP and corrupt the check digit
        curp = generate_curp(
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            fecha_nacimiento='1990-05-15',
            sexo='H',
            estado='Jalisco'
        )
        # Replace check digit with wrong value
        corrupted_curp = curp[:17] + '9' if curp[17] != '9' else curp[:17] + '0'

        # Should fail validation
        self.assertFalse(validate_curp(corrupted_curp))

    def test_get_curp_info(self):
        """Test extracting information from CURP"""
        curp = generate_curp(
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            fecha_nacimiento='1990-05-15',
            sexo='H',
            estado='Jalisco'
        )

        info = get_curp_info(curp)

        self.assertIsNotNone(info)
        self.assertEqual(info['fecha_nacimiento'], '1990-05-15')
        self.assertEqual(info['sexo'], 'Hombre')
        self.assertEqual(info['sexo_code'], 'H')
        self.assertEqual(info['estado_code'], 'JC')
        self.assertTrue(info['check_digit_valid'])

    def test_get_curp_info_female(self):
        """Test extracting information from female CURP"""
        curp = generate_curp(
            nombre='María',
            apellido_paterno='Ramírez',
            apellido_materno='Sánchez',
            fecha_nacimiento='1995-03-20',
            sexo='M',
            estado='Jalisco'
        )

        info = get_curp_info(curp)

        self.assertEqual(info['sexo'], 'Mujer')
        self.assertEqual(info['sexo_code'], 'M')

    def test_get_curp_info_invalid(self):
        """Test get_curp_info with invalid CURP"""
        info = get_curp_info('INVALID')
        self.assertIsNone(info)

    def test_is_valid_curp_alias(self):
        """Test is_valid_curp alias function"""
        curp = generate_curp(
            nombre='Juan',
            apellido_paterno='Pérez',
            apellido_materno='García',
            fecha_nacimiento='1990-05-15',
            sexo='H',
            estado='Jalisco'
        )
        self.assertTrue(is_valid_curp(curp))
        self.assertFalse(is_valid_curp('INVALID'))


class TestIntegrationScenarios(unittest.TestCase):
    """Test real-world integration scenarios"""

    def test_complete_workflow_persona_fisica(self):
        """Test complete workflow for persona física"""
        # Generate RFC
        rfc = generate_rfc_persona_fisica(
            nombre='Ana María',
            apellido_paterno='López',
            apellido_materno='Castillo',
            fecha_nacimiento='1985-12-25'
        )

        # Validate
        self.assertTrue(validate_rfc(rfc))

        # Detect type
        self.assertEqual(detect_rfc_type(rfc), 'fisica')

    def test_complete_workflow_curp(self):
        """Test complete workflow for CURP"""
        # Generate CURP
        curp = generate_curp(
            nombre='Ana María',
            apellido_paterno='López',
            apellido_materno='Castillo',
            fecha_nacimiento='1985-12-25',
            sexo='M',
            estado='Ciudad de México'
        )

        # Validate
        self.assertTrue(validate_curp(curp))

        # Extract info
        info = get_curp_info(curp)
        self.assertEqual(info['fecha_nacimiento'], '1985-12-25')
        self.assertEqual(info['sexo'], 'Mujer')

    def test_homonymous_curps(self):
        """Test handling homonymous CURPs (same person data)"""
        base_data = {
            'nombre': 'Juan',
            'apellido_paterno': 'García',
            'apellido_materno': 'López',
            'fecha_nacimiento': '1990-01-01',
            'sexo': 'H',
            'estado': 'Jalisco'
        }

        # Generate 5 homonymous CURPs
        curps = []
        for i in range(5):
            curp = generate_curp(**base_data, differentiator=str(i))
            curps.append(curp)

        # All should be valid
        for curp in curps:
            self.assertTrue(validate_curp(curp))

        # All should have same first 16 characters
        base_16 = curps[0][:16]
        for curp in curps:
            self.assertEqual(curp[:16], base_16)

        # All should be unique
        self.assertEqual(len(set(curps)), len(curps))


if __name__ == '__main__':
    unittest.main()
