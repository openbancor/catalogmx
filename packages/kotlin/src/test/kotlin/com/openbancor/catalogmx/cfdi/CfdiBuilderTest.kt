package com.openbancor.catalogmx.cfdi

import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class CfdiBuilderTest {

    @Test
    fun `buildUnsignedXml includes core nodes`() {
        val xml = CfdiBuilder.buildUnsignedXml(
            CfdiComprobanteInput(
                moneda = "MXN",
                tipoDeComprobante = "I",
                lugarExpedicion = "64000",
                subTotal = "100.00",
                total = "116.00",
                emisor = CfdiEmisor(
                    rfc = "BACL891217NJ5",
                    nombre = "Emisor SA",
                    regimenFiscal = "612",
                ),
                receptor = CfdiReceptor(
                    rfc = "XAXX010101000",
                    nombre = "Publico",
                    usoCfdi = "G03",
                    regimenFiscalReceptor = "616",
                    domicilioFiscalReceptor = "64000",
                ),
                conceptos = listOf(
                    CfdiConcepto(
                        claveProdServ = "01010101",
                        cantidad = "1",
                        claveUnidad = "ACT",
                        descripcion = "Servicio",
                        valorUnitario = "100.00",
                        importe = "100.00",
                    )
                )
            )
        )

        assertTrue(xml.contains("<cfdi:Comprobante"))
        assertTrue(xml.contains("Version=\"4.0\""))
        assertTrue(xml.contains("<cfdi:Emisor"))
        assertTrue(xml.contains("<cfdi:Receptor"))
        assertTrue(xml.contains("<cfdi:Conceptos>"))
    }
}
