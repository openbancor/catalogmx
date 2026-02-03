package com.openbancor.catalogmx.cfdi

import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter


data class CfdiEmisor(
    val rfc: String,
    val nombre: String,
    val regimenFiscal: String,
)

data class CfdiReceptor(
    val rfc: String,
    val nombre: String,
    val usoCfdi: String,
    val regimenFiscalReceptor: String,
    val domicilioFiscalReceptor: String,
)

data class CfdiConcepto(
    val claveProdServ: String,
    val cantidad: String,
    val claveUnidad: String,
    val descripcion: String,
    val valorUnitario: String,
    val importe: String,
    val objetoImp: String? = null,
    val noIdentificacion: String? = null,
    val unidad: String? = null,
    val descuento: String? = null,
)

data class CfdiComprobanteInput(
    val version: String = "4.0",
    val serie: String? = null,
    val folio: String? = null,
    val fecha: String? = null,
    val moneda: String,
    val tipoDeComprobante: String,
    val lugarExpedicion: String,
    val subTotal: String,
    val total: String,
    val exportacion: String? = null,
    val metodoPago: String? = null,
    val formaPago: String? = null,
    val noCertificado: String? = null,
    val certificado: String? = null,
    val sello: String? = null,
    val emisor: CfdiEmisor,
    val receptor: CfdiReceptor,
    val conceptos: List<CfdiConcepto>,
)

object CfdiBuilder {
    fun buildUnsignedXml(data: CfdiComprobanteInput): String {
        val fechaValue = data.fecha ?: OffsetDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME)

        fun attr(name: String, value: String?): String =
            if (value.isNullOrBlank()) "" else " $name=\"${escapeXml(value)}\""

        val comprobanteAttrs = listOf(
            attr("Version", data.version),
            attr("Serie", data.serie),
            attr("Folio", data.folio),
            attr("Fecha", fechaValue),
            attr("Moneda", data.moneda),
            attr("TipoDeComprobante", data.tipoDeComprobante),
            attr("LugarExpedicion", data.lugarExpedicion),
            attr("SubTotal", data.subTotal),
            attr("Total", data.total),
            attr("Exportacion", data.exportacion),
            attr("MetodoPago", data.metodoPago),
            attr("FormaPago", data.formaPago),
            attr("NoCertificado", data.noCertificado),
            attr("Certificado", data.certificado),
            attr("Sello", data.sello),
        ).joinToString("")

        val emisor = "<cfdi:Emisor" +
            attr("Rfc", data.emisor.rfc) +
            attr("Nombre", data.emisor.nombre) +
            attr("RegimenFiscal", data.emisor.regimenFiscal) +
            "/>"

        val receptor = "<cfdi:Receptor" +
            attr("Rfc", data.receptor.rfc) +
            attr("Nombre", data.receptor.nombre) +
            attr("UsoCFDI", data.receptor.usoCfdi) +
            attr("RegimenFiscalReceptor", data.receptor.regimenFiscalReceptor) +
            attr("DomicilioFiscalReceptor", data.receptor.domicilioFiscalReceptor) +
            "/>"

        val conceptos = data.conceptos.joinToString("") { c ->
            val conceptoAttrs = listOf(
                attr("ClaveProdServ", c.claveProdServ),
                attr("Cantidad", c.cantidad),
                attr("ClaveUnidad", c.claveUnidad),
                attr("Descripcion", c.descripcion),
                attr("ValorUnitario", c.valorUnitario),
                attr("Importe", c.importe),
                attr("ObjetoImp", c.objetoImp),
                attr("NoIdentificacion", c.noIdentificacion),
                attr("Unidad", c.unidad),
                attr("Descuento", c.descuento),
            ).joinToString("")
            "<cfdi:Concepto$conceptoAttrs/>"
        }

        return listOf(
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<cfdi:Comprobante xmlns:cfdi=\"http://www.sat.gob.mx/cfd/4\"" +
                " xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\"" +
                " xsi:schemaLocation=\"http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd\"" +
                comprobanteAttrs + ">",
            emisor,
            receptor,
            "<cfdi:Conceptos>$conceptos</cfdi:Conceptos>",
            "</cfdi:Comprobante>",
        ).joinToString("")
    }

    private fun escapeXml(value: String): String =
        value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&apos;")
}
