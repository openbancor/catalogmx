package com.openbancor.catalogmx.validators

import com.openbancor.catalogmx.validateCURP
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import java.time.LocalDate

class CurpValidatorTest {

    @Test
    fun `should validate correct CURP`() {
        // Example CURPs with valid structure
        assertTrue(validateCURP("OEAF771012HMCRGR09"))
    }

    @Test
    fun `should reject CURP with invalid length`() {
        assertFalse(validateCURP("OEAF771012HMCRGR0"))  // 17 chars
        assertFalse(validateCURP("OEAF771012HMCRGR099")) // 19 chars
    }

    @Test
    fun `should reject CURP with invalid structure`() {
        assertFalse(validateCURP("1234567890123456789")) // All numbers
        assertFalse(validateCURP("ABCDEFGHIJKLMNOPQR")) // All letters
    }

    @Test
    fun `should extract gender from CURP`() {
        val validatorH = CurpValidator("OEAF771012HMCRGR09")
        assertEquals("Hombre", validatorH.getGender())

        val validatorM = CurpValidator("OEAF771012MMCRGR09")
        assertEquals("Mujer", validatorM.getGender())
    }

    @Test
    fun `should extract state code from CURP`() {
        val validator = CurpValidator("OEAF771012HMCRGR09")
        assertEquals("MC", validator.getStateCode())
    }

    @Test
    fun `should extract birth date from CURP`() {
        val validator = CurpValidator("OEAF771012HMCRGR09")
        val birthDate = validator.getBirthDate()
        assertNotNull(birthDate)
        assertEquals(1977, birthDate!!.year)
        assertEquals(10, birthDate.monthValue)
        assertEquals(12, birthDate.dayOfMonth)
    }

    @Test
    fun `should calculate check digit correctly`() {
        // The check digit calculation uses a dictionary of 37 chars
        val checkDigit = CurpGenerator.calculateCheckDigit("OEAF771012HMCRGR0")
        assertEquals('8', checkDigit)
    }

    @Test
    fun `should generate valid CURP`() {
        val curp = CurpGenerator(
            nombre = "JUAN",
            apellidoPaterno = "GARCIA",
            apellidoMaterno = "LOPEZ",
            fechaNacimiento = LocalDate.of(1990, 5, 15),
            sexo = "H",
            estado = "JALISCO"
        ).generate()

        assertEquals(18, curp.length)
        assertTrue(validateCURP(curp))

        // Check structure
        assertEquals("GALJ", curp.substring(0, 4)) // Name letters
        assertEquals("900515", curp.substring(4, 10)) // Birth date
        assertEquals("H", curp.substring(10, 11)) // Gender
        assertEquals("JC", curp.substring(11, 13)) // State code
    }

    @Test
    fun `should handle cacophonic names`() {
        val curp = CurpGenerator(
            nombre = "ANA",
            apellidoPaterno = "CACA", // Would be cacophonic but result is CALA, not CACA
            apellidoMaterno = "LOPEZ",
            fechaNacimiento = LocalDate.of(1990, 5, 15),
            sexo = "M",
            estado = "DF"
        ).generate()

        // Result is CALA (C + A vowel + L from Lopez + A from Ana)
        // CALA is not in cacophonic list, so it stays unchanged
        assertEquals("CALA", curp.substring(0, 4))
    }

    @Test
    fun `should handle names with MARIA or JOSE prefix`() {
        val curp = CurpGenerator(
            nombre = "MARIA FERNANDA",
            apellidoPaterno = "LOPEZ",
            apellidoMaterno = "HERNANDEZ",
            fechaNacimiento = LocalDate.of(1992, 1, 3),
            sexo = "M",
            estado = "DF"
        ).generate()

        // Should use FERNANDA, not MARIA
        assertEquals('F', curp[3])
    }

    @Test
    fun `should handle missing materno surname`() {
        val curp = CurpGenerator(
            nombre = "CARLOS",
            apellidoPaterno = "PEREZ",
            apellidoMaterno = null,
            fechaNacimiento = LocalDate.of(1980, 7, 9),
            sexo = "H",
            estado = "DF"
        ).generate()

        assertEquals(18, curp.length)
        assertTrue(validateCURP(curp))
        // Third position should be X when no materno
        assertEquals('X', curp[2])
    }

    @Test
    fun `state codes should be mapped correctly`() {
        val stateTests = mapOf(
            "AGUASCALIENTES" to "AS",
            "BAJA CALIFORNIA" to "BC",
            "CIUDAD DE MEXICO" to "DF",
            "CDMX" to "DF",
            "JALISCO" to "JC",
            "NUEVO LEON" to "NL",
            "EXTRANJERO" to "NE"
        )

        stateTests.forEach { (stateName, expectedCode) ->
            assertTrue(
                CurpValidator.stateCodes.containsKey(stateName),
                "State $stateName should be in stateCodes map"
            )
            assertEquals(expectedCode, CurpValidator.stateCodes[stateName])
        }
    }
}
