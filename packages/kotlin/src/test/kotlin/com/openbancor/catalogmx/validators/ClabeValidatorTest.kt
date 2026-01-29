package com.openbancor.catalogmx.validators

import com.openbancor.catalogmx.validateCLABE
import com.openbancor.catalogmx.generateCLABE
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestFactory
import java.io.File

class ClabeValidatorTest {

    @Test
    fun `should validate correct CLABE`() {
        assertTrue(validateCLABE("002010077777777771"))
    }

    @Test
    fun `should reject CLABE with wrong length`() {
        assertFalse(validateCLABE("00201007777777777"))  // 17 digits
        assertFalse(validateCLABE("0020100777777777711")) // 19 digits
    }

    @Test
    fun `should reject CLABE with non-digits`() {
        assertFalse(validateCLABE("00201007777777777A"))
        assertFalse(validateCLABE("A02010077777777771"))
    }

    @Test
    fun `should reject CLABE with invalid check digit`() {
        assertFalse(validateCLABE("002010077777777772")) // Should be 1, not 2
    }

    @Test
    fun `should handle null CLABE`() {
        assertFalse(validateCLABE(null))
    }

    @Test
    fun `should handle empty CLABE`() {
        assertFalse(validateCLABE(""))
    }

    @Test
    fun `should calculate check digit correctly`() {
        assertEquals('1', ClabeValidator.calculateCheckDigit("00201007777777777"))
        assertEquals('4', ClabeValidator.calculateCheckDigit("01418012345678901"))
        assertEquals('7', ClabeValidator.calculateCheckDigit("00200100012345678"))
        assertEquals('0', ClabeValidator.calculateCheckDigit("07250098765432109"))
    }

    @Test
    fun `should extract CLABE parts`() {
        val validator = ClabeValidator("002010077777777771")

        assertEquals("002", validator.getBankCode())
        assertEquals("010", validator.getBranchCode())
        assertEquals("07777777777", validator.getAccountNumber())
        assertEquals('1', validator.getCheckDigit())

        val parts = validator.getParts()
        assertNotNull(parts)
        assertEquals("002", parts!!["bank_code"])
        assertEquals("010", parts["branch_code"])
        assertEquals("07777777777", parts["account_number"])
        assertEquals("1", parts["check_digit"])
    }

    @Test
    fun `should generate valid CLABE`() {
        val clabe = generateCLABE(
            bankCode = "002",
            branchCode = "010",
            accountNumber = "07777777777"
        )

        assertEquals("002010077777777771", clabe)
        assertTrue(validateCLABE(clabe))
    }

    @Test
    fun `should pad bank code with zeros`() {
        val clabe = generateCLABE(
            bankCode = "2",
            branchCode = "10",
            accountNumber = "7777777777"
        )

        assertEquals("002010077777777771", clabe)
    }

    @TestFactory
    fun `should generate correct CLABE for test vectors`(): List<DynamicTest> {
        val vectorsFile = findTestVectorsFile("clabe_vectors.json")
        if (vectorsFile == null || !vectorsFile.exists()) {
            return listOf(
                DynamicTest.dynamicTest("CLABE vectors file not found - using embedded test") {
                    val clabe = generateCLABE("002", "010", "07777777777")
                    assertEquals("002010077777777771", clabe)
                }
            )
        }

        val jsonContent = vectorsFile.readText()
        val vectors = Json.parseToJsonElement(jsonContent).jsonArray

        return vectors.mapIndexed { index, element ->
            val obj = element.jsonObject
            val expectedClabe = obj["clabe"]?.jsonPrimitive?.content ?: ""
            val bankCode = obj["bank_code"]?.jsonPrimitive?.content ?: ""
            val branchCode = obj["branch_code"]?.jsonPrimitive?.content ?: ""
            val accountNumber = obj["account_number"]?.jsonPrimitive?.content ?: ""

            DynamicTest.dynamicTest("CLABE Generation #$index: $expectedClabe") {
                val generatedClabe = generateCLABE(bankCode, branchCode, accountNumber)
                assertEquals(expectedClabe, generatedClabe)
                assertTrue(validateCLABE(generatedClabe))
            }
        }
    }

    private fun findTestVectorsFile(filename: String): File? {
        val candidates = listOf(
            "../../shared-data/tests/$filename",
            "../../../shared-data/tests/$filename",
            "packages/shared-data/tests/$filename",
            "../shared-data/tests/$filename"
        )
        return candidates.map { File(it) }.firstOrNull { it.exists() }
    }
}
