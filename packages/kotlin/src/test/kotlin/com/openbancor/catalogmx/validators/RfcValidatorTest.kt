package com.openbancor.catalogmx.validators

import com.openbancor.catalogmx.validateRFC
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestFactory
import java.io.File
import java.time.LocalDate

class RfcValidatorTest {

    @Test
    fun `should validate generic RFC XAXX010101000`() {
        assertTrue(validateRFC("XAXX010101000"))
        assertTrue(RfcValidator("XAXX010101000").isGeneric())
    }

    @Test
    fun `should validate generic RFC XEXX010101000`() {
        assertTrue(validateRFC("XEXX010101000"))
        assertTrue(RfcValidator("XEXX010101000").isGeneric())
    }

    @Test
    fun `should reject invalid RFC length`() {
        assertFalse(validateRFC("XAXX01010100")) // 12 chars for fisica pattern
        assertFalse(validateRFC("XAXX0101010000")) // 14 chars
    }

    @Test
    fun `should reject RFC with invalid characters`() {
        assertFalse(validateRFC("XA1X010101000")) // number in wrong position
    }

    @Test
    fun `should reject RFC with invalid date`() {
        assertFalse(validateRFC("XAXX990231000")) // Feb 31 doesn't exist
        assertFalse(validateRFC("XAXX991301000")) // Month 13 doesn't exist
    }

    @Test
    fun `should detect persona fisica`() {
        val validator = RfcValidator("BACL891217NJ5")
        assertTrue(validator.validate())
        assertTrue(validator.isFisica())
        assertFalse(validator.isMoral())
        assertEquals("Persona Física", validator.detectType())
    }

    @Test
    fun `should detect persona moral`() {
        val validator = RfcValidator("CNO010322EY3")
        assertTrue(validator.validate())
        assertFalse(validator.isFisica())
        assertTrue(validator.isMoral())
        assertEquals("Persona Moral", validator.detectType())
    }

    @Test
    fun `should calculate checksum correctly`() {
        assertEquals('5', RfcValidator.calculateChecksum("BACL891217NJ"))
        assertEquals('4', RfcValidator.calculateChecksum("XAXX01010100"))
        assertEquals('0', RfcValidator.calculateChecksum("XEXX01010100"))
    }

    @Test
    fun `should validate checksum`() {
        val validator = RfcValidator("BACL891217NJ5")
        assertTrue(validator.validateChecksum())
    }

    @Test
    fun `should reject invalid checksum in strict mode`() {
        assertFalse(validateRFC("BACL891217NJ9", strict = true))
    }

    @Test
    fun `should accept invalid checksum in non-strict mode`() {
        assertTrue(validateRFC("BACL891217NJ9", strict = false))
    }

    @TestFactory
    fun `should generate correct RFC for test vectors`(): List<DynamicTest> {
        val vectorsFile = findTestVectorsFile("rfc_vectors.json")
        if (vectorsFile == null || !vectorsFile.exists()) {
            return listOf(
                DynamicTest.dynamicTest("RFC vectors file not found - using embedded test") {
                    // Test with embedded data
                    val rfc = RfcGeneratorFisica(
                        nombre = "Luis Fernando",
                        apellidoPaterno = "Barrera",
                        apellidoMaterno = "Castro",
                        fechaNacimiento = LocalDate.of(1989, 12, 17)
                    ).generate()
                    assertEquals("BACL891217NJ5", rfc)
                }
            )
        }

        val jsonContent = vectorsFile.readText()
        val vectors = Json.parseToJsonElement(jsonContent).jsonArray

        return vectors.mapIndexed { index, element ->
            val obj = element.jsonObject
            val type = obj["type"]?.jsonPrimitive?.content ?: ""
            val expectedRfc = obj["rfc"]?.jsonPrimitive?.content ?: ""

            DynamicTest.dynamicTest("RFC Generation #$index: $expectedRfc ($type)") {
                val fecha = LocalDate.parse(obj["fecha"]!!.jsonPrimitive.content)

                val generatedRfc = if (type == "fisica") {
                    RfcGeneratorFisica(
                        nombre = obj["nombre"]!!.jsonPrimitive.content,
                        apellidoPaterno = obj["apellido_paterno"]!!.jsonPrimitive.content,
                        apellidoMaterno = obj["apellido_materno"]?.jsonPrimitive?.content ?: "",
                        fechaNacimiento = fecha
                    ).generate()
                } else {
                    RfcGeneratorMoral(
                        razonSocial = obj["razon_social"]!!.jsonPrimitive.content,
                        fechaConstitucion = fecha
                    ).generate()
                }

                assertEquals(expectedRfc, generatedRfc, "RFC mismatch for $type")
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
