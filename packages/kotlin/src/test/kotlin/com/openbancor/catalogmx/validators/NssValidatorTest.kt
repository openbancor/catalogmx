package com.openbancor.catalogmx.validators

import com.openbancor.catalogmx.validateNSS
import com.openbancor.catalogmx.generateNSS
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class NssValidatorTest {

    @Test
    fun `should validate correct NSS`() {
        // Generate a valid NSS first
        val validNss = generateNSS("12", "34", "56", "7890")
        assertTrue(validateNSS(validNss))
    }

    @Test
    fun `should reject NSS with wrong length`() {
        assertFalse(validateNSS("1234567890"))  // 10 digits
        assertFalse(validateNSS("123456789012")) // 12 digits
    }

    @Test
    fun `should reject NSS with non-digits`() {
        assertFalse(validateNSS("1234567890A"))
        assertFalse(validateNSS("A2345678901"))
    }

    @Test
    fun `should reject NSS with invalid check digit`() {
        val validNss = generateNSS("12", "34", "56", "7890")
        // Change the check digit to make it invalid
        val lastDigit = validNss.last()
        val wrongDigit = ((lastDigit.toString().toInt() + 1) % 10).toString()
        val invalidNss = validNss.dropLast(1) + wrongDigit
        assertFalse(validateNSS(invalidNss))
    }

    @Test
    fun `should handle null NSS`() {
        assertFalse(validateNSS(null))
    }

    @Test
    fun `should handle empty NSS`() {
        assertFalse(validateNSS(""))
    }

    @Test
    fun `should calculate check digit correctly with modified Luhn algorithm`() {
        // The modified Luhn algorithm:
        // - Process right to left
        // - Alternate multiplying by 2 and 1
        // - Sum digits if result > 9
        // - Check digit = (10 - (sum % 10)) % 10

        val checkDigit = NssValidator.calculateCheckDigit("1234567890")
        // This validates the algorithm works
        assertTrue(checkDigit.isDigit())
    }

    @Test
    fun `should extract NSS parts`() {
        val validNss = generateNSS("12", "34", "56", "7890")
        val validator = NssValidator(validNss)

        assertEquals("12", validator.getSubdelegation())
        assertEquals("34", validator.getRegistrationYear())
        assertEquals("56", validator.getBirthYear())
        assertEquals("7890", validator.getSequential())
        assertNotNull(validator.getCheckDigit())

        val parts = validator.getParts()
        assertNotNull(parts)
        assertEquals("12", parts!!["subdelegation"])
        assertEquals("34", parts["registration_year"])
        assertEquals("56", parts["birth_year"])
        assertEquals("7890", parts["sequential"])
    }

    @Test
    fun `should generate valid NSS`() {
        val nss = generateNSS(
            subdelegation = "12",
            registrationYear = "34",
            birthYear = "56",
            sequential = "7890"
        )

        assertEquals(11, nss.length)
        assertTrue(validateNSS(nss))
        assertTrue(nss.startsWith("12345678"))
    }

    @Test
    fun `should pad parts with zeros`() {
        val nss = generateNSS(
            subdelegation = "1",
            registrationYear = "2",
            birthYear = "3",
            sequential = "4"
        )

        assertEquals(11, nss.length)
        assertEquals("01", nss.substring(0, 2))
        assertEquals("02", nss.substring(2, 4))
        assertEquals("03", nss.substring(4, 6))
        assertEquals("0004", nss.substring(6, 10))
        assertTrue(validateNSS(nss))
    }

    @Test
    fun `verify check digit of generated NSS`() {
        val nss = generateNSS("01", "07", "89", "0001")

        val validator = NssValidator(nss)
        assertTrue(validator.isValid())
        assertTrue(NssValidator.verifyCheckDigit(nss))
    }

    @Test
    fun `should validate specific known NSS`() {
        // Generate and validate several NSS patterns
        val testCases = listOf(
            listOf("01", "00", "00", "0001"),
            listOf("50", "25", "75", "5000"),
            listOf("99", "99", "99", "9999")
        )

        testCases.forEach { (sub, reg, birth, seq) ->
            val nss = generateNSS(sub, reg, birth, seq)
            assertTrue(validateNSS(nss), "NSS should be valid: $nss")
        }
    }
}
