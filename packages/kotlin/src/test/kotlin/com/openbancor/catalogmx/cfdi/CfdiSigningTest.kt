package com.openbancor.catalogmx.cfdi

import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class CfdiSigningTest {

    @Test
    fun `applySelloToXml injects attributes`() {
        val xml = "<cfdi:Comprobante Version=\"4.0\"><cfdi:Emisor /></cfdi:Comprobante>"
        val signed = CfdiSigning.applySelloToXml(
            xml = xml,
            sello = "abc123",
            certificado = "CERT",
            noCertificado = "000010000",
        )

        assertTrue(signed.contains("Sello=\"abc123\""))
        assertTrue(signed.contains("Certificado=\"CERT\""))
        assertTrue(signed.contains("NoCertificado=\"000010000\""))
    }
}
