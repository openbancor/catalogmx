package com.openbancor.catalogmx.generators

import com.openbancor.catalogmx.validateRFC
import com.openbancor.catalogmx.validateCURP
import com.openbancor.catalogmx.validateCLABE
import com.openbancor.catalogmx.validateNSS
import com.openbancor.catalogmx.generatePersonaFisica
import com.openbancor.catalogmx.generatePersonaMoral
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import kotlin.random.Random

class IdentityGeneratorTest {

    @Test
    fun `should generate valid persona fisica`() {
        val generator = IdentityGenerator(Random(42)) // Fixed seed for reproducibility
        val persona = generator.generatePersonaFisica()

        // Verify basic fields are present
        assertTrue(persona.nombre.isNotEmpty())
        assertTrue(persona.apellidoPaterno.isNotEmpty())
        assertTrue(persona.apellidoMaterno.isNotEmpty())
        assertTrue(persona.nombreCompleto.isNotEmpty())

        // Verify RFC is valid
        assertEquals(13, persona.rfc.length)
        assertTrue(validateRFC(persona.rfc), "RFC should be valid: ${persona.rfc}")

        // Verify CURP is valid
        assertEquals(18, persona.curp.length)
        assertTrue(validateCURP(persona.curp), "CURP should be valid: ${persona.curp}")

        // Verify NSS is valid
        assertEquals(11, persona.nss.length)
        assertTrue(validateNSS(persona.nss), "NSS should be valid: ${persona.nss}")

        // Verify CLABE is valid
        assertEquals(18, persona.clabe.length)
        assertTrue(validateCLABE(persona.clabe), "CLABE should be valid: ${persona.clabe}")

        // Verify age is within expected range
        assertTrue(persona.edad in 18..65)

        // Verify sexo is valid
        assertTrue(persona.sexo in listOf("H", "M"))
    }

    @Test
    fun `should generate persona fisica with specified sex`() {
        val generator = IdentityGenerator(Random(42))

        val male = generator.generatePersonaFisica(sexo = "H")
        assertEquals("H", male.sexo)
        assertEquals("Masculino", male.sexoDescripcion)

        val female = generator.generatePersonaFisica(sexo = "M")
        assertEquals("M", female.sexo)
        assertEquals("Femenino", female.sexoDescripcion)
    }

    @Test
    fun `should generate persona fisica with specified state`() {
        val generator = IdentityGenerator(Random(42))

        val persona = generator.generatePersonaFisica(estado = "JC")
        assertEquals("JC", persona.estadoNacimientoCode)
        assertEquals("JALISCO", persona.estadoNacimiento)
    }

    @Test
    fun `should generate persona fisica with custom age range`() {
        val generator = IdentityGenerator(Random(42))

        val persona = generator.generatePersonaFisica(minAge = 25, maxAge = 30)
        assertTrue(persona.edad in 25..30, "Age ${persona.edad} should be between 25 and 30")
    }

    @Test
    fun `should generate valid persona moral`() {
        val generator = IdentityGenerator(Random(42))
        val persona = generator.generatePersonaMoral()

        // Verify basic fields are present
        assertTrue(persona.razonSocial.isNotEmpty())
        assertTrue(persona.nombreComercial.isNotEmpty())

        // Verify RFC is valid (12 chars for moral)
        assertEquals(12, persona.rfc.length)
        assertTrue(validateRFC(persona.rfc), "RFC should be valid: ${persona.rfc}")

        // Verify CLABE is valid
        assertEquals(18, persona.clabe.length)
        assertTrue(validateCLABE(persona.clabe), "CLABE should be valid: ${persona.clabe}")

        // Verify antiguedad is within expected range
        assertTrue(persona.antiguedad in 1..30)
    }

    @Test
    fun `should generate persona moral with custom age range`() {
        val generator = IdentityGenerator(Random(42))

        val persona = generator.generatePersonaMoral(minYears = 5, maxYears = 10)
        assertTrue(persona.antiguedad in 5..10, "Antiguedad ${persona.antiguedad} should be between 5 and 10")
    }

    @Test
    fun `convenience functions should work`() {
        val fisica = generatePersonaFisica()
        assertNotNull(fisica)
        assertTrue(fisica.containsKey("rfc"))
        assertTrue(fisica.containsKey("curp"))
        assertTrue(fisica.containsKey("nss"))
        assertTrue(fisica.containsKey("clabe"))

        val moral = generatePersonaMoral()
        assertNotNull(moral)
        assertTrue(moral.containsKey("rfc"))
        assertTrue(moral.containsKey("clabe"))
    }

    @Test
    fun `should include complete address`() {
        val generator = IdentityGenerator(Random(42))
        val persona = generator.generatePersonaFisica()

        val direccion = persona.direccion
        assertTrue(direccion.containsKey("calle"))
        assertTrue(direccion.containsKey("numero_exterior"))
        assertTrue(direccion.containsKey("colonia"))
        assertTrue(direccion.containsKey("codigo_postal"))
        assertTrue(direccion.containsKey("municipio"))
        assertTrue(direccion.containsKey("estado"))
    }

    @Test
    fun `should include bank information`() {
        val generator = IdentityGenerator(Random(42))
        val persona = generator.generatePersonaFisica()

        val banco = persona.banco
        assertTrue(banco.containsKey("code"))
        assertTrue(banco.containsKey("name"))
        assertTrue(banco["code"]!!.length == 3)
    }

    @Test
    fun `should include fiscal regime`() {
        val generator = IdentityGenerator(Random(42))
        val persona = generator.generatePersonaFisica()

        val regimen = persona.regimenFiscal
        assertTrue(regimen.containsKey("code"))
        assertTrue(regimen.containsKey("name"))
    }

    @Test
    fun `should generate valid email format`() {
        val generator = IdentityGenerator(Random(42))
        val persona = generator.generatePersonaFisica()

        assertTrue(persona.email.contains("@"))
        assertTrue(persona.email.contains("."))
    }

    @Test
    fun `should generate valid phone number`() {
        val generator = IdentityGenerator(Random(42))
        val persona = generator.generatePersonaFisica()

        assertEquals(10, persona.telefono.length)
        assertTrue(persona.telefono.all { it.isDigit() })
    }

    @Test
    fun `toMap should produce valid JSON-serializable structure`() {
        val generator = IdentityGenerator(Random(42))
        val persona = generator.generatePersonaFisica()

        val map = persona.toMap()

        assertEquals("persona_fisica", map["tipo"])
        assertEquals(persona.rfc, map["rfc"])
        assertEquals(persona.curp, map["curp"])
        assertEquals(persona.nss, map["nss"])
        assertEquals(persona.clabe, map["clabe"])
    }
}
