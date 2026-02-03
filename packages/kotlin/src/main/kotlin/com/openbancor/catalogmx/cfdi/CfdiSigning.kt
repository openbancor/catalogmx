package com.openbancor.catalogmx.cfdi

import java.security.KeyFactory
import java.security.PrivateKey
import java.security.Signature
import java.security.spec.PKCS8EncodedKeySpec
import java.util.Base64

object CfdiSigning {
    fun signCadenaOriginal(cadena: String, privateKeyPem: String): String {
        val privateKey = parsePrivateKey(privateKeyPem)
        val signature = Signature.getInstance("SHA256withRSA")
        signature.initSign(privateKey)
        signature.update(cadena.toByteArray(Charsets.UTF_8))
        return Base64.getEncoder().encodeToString(signature.sign())
    }

    private fun parsePrivateKey(pem: String): PrivateKey {
        val cleaned = pem
            .replace("-----BEGIN PRIVATE KEY-----", "")
            .replace("-----END PRIVATE KEY-----", "")
            .replace("-----BEGIN RSA PRIVATE KEY-----", "")
            .replace("-----END RSA PRIVATE KEY-----", "")
            .replace("\n", "")
            .replace("\r", "")
        val keySpec = PKCS8EncodedKeySpec(Base64.getDecoder().decode(cleaned))
        return KeyFactory.getInstance("RSA").generatePrivate(keySpec)
    }

    fun applySelloToXml(
        xml: String,
        sello: String,
        certificado: String? = null,
        noCertificado: String? = null,
    ): String {
        val regex = Regex("<cfdi:Comprobante\\b([^>]*)>")
        val match = regex.find(xml) ?: throw IllegalArgumentException("No se encontró cfdi:Comprobante")
        var attrs = match.groupValues[1]

        fun setAttr(name: String, value: String?) {
            if (value.isNullOrBlank()) return
            val attrRegex = Regex("$name=\"[^\"]*\"")
            attrs = if (attrRegex.containsMatchIn(attrs)) {
                attrs.replace(attrRegex, "$name=\"$value\"")
            } else {
                "$attrs $name=\"$value\""
            }
        }

        setAttr("Sello", sello)
        setAttr("Certificado", certificado)
        setAttr("NoCertificado", noCertificado)

        return xml.replaceFirst(regex, "<cfdi:Comprobante$attrs>")
    }
}
