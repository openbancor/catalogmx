package com.openbancor.catalogmx

import io.flutter.plugin.common.MethodCall
import io.flutter.plugin.common.MethodChannel
import javax.xml.XMLConstants
import javax.xml.transform.TransformerFactory
import javax.xml.transform.stream.StreamResult
import javax.xml.transform.stream.StreamSource
import javax.xml.validation.SchemaFactory
import java.io.StringReader
import java.io.StringWriter
import java.security.KeyFactory
import java.security.Signature
import java.security.spec.PKCS8EncodedKeySpec
import java.util.Base64

class CfdiChannel : MethodChannel.MethodCallHandler {
    override fun onMethodCall(call: MethodCall, result: MethodChannel.Result) {
        when (call.method) {
            "generateCadenaOriginal" -> {
                val xml = call.argument<String>("xml") ?: return result.error("ARG", "xml requerido", null)
                val xslt = call.argument<String>("xslt") ?: return result.error("ARG", "xslt requerido", null)
                try {
                    val transformer = TransformerFactory.newInstance()
                        .newTransformer(StreamSource(StringReader(xslt)))
                    val writer = StringWriter()
                    transformer.transform(StreamSource(StringReader(xml)), StreamResult(writer))
                    result.success(writer.toString().trim())
                } catch (e: Exception) {
                    result.error("XSLT", e.message, null)
                }
            }
            "validateXsd" -> {
                val xml = call.argument<String>("xml") ?: return result.error("ARG", "xml requerido", null)
                val xsd = call.argument<String>("xsd") ?: return result.error("ARG", "xsd requerido", null)
                val errors = mutableListOf<String>()
                try {
                    val schemaFactory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI)
                    val schema = schemaFactory.newSchema(StreamSource(StringReader(xsd)))
                    val validator = schema.newValidator()
                    val handler = object : org.xml.sax.helpers.DefaultHandler() {
                        override fun error(e: org.xml.sax.SAXParseException) { errors.add(e.message ?: "error") }
                        override fun fatalError(e: org.xml.sax.SAXParseException) { errors.add(e.message ?: "fatal") }
                        override fun warning(e: org.xml.sax.SAXParseException) { errors.add(e.message ?: "warning") }
                    }
                    validator.errorHandler = handler
                    validator.validate(StreamSource(StringReader(xml)))
                    result.success(mapOf("valid" to errors.isEmpty(), "errors" to errors))
                } catch (e: Exception) {
                    errors.add(e.message ?: "validation error")
                    result.success(mapOf("valid" to false, "errors" to errors))
                }
            }
            "signCadenaOriginal" -> {
                val cadena = call.argument<String>("cadena") ?: return result.error("ARG", "cadena requerida", null)
                val keyPem = call.argument<String>("privateKeyPem") ?: return result.error("ARG", "privateKeyPem requerido", null)
                try {
                    val clean = keyPem
                        .replace("-----BEGIN PRIVATE KEY-----", "")
                        .replace("-----END PRIVATE KEY-----", "")
                        .replace("-----BEGIN RSA PRIVATE KEY-----", "")
                        .replace("-----END RSA PRIVATE KEY-----", "")
                        .replace("\n", "")
                        .replace("\r", "")
                    val keySpec = PKCS8EncodedKeySpec(Base64.getDecoder().decode(clean))
                    val privateKey = KeyFactory.getInstance("RSA").generatePrivate(keySpec)
                    val signature = Signature.getInstance("SHA256withRSA")
                    signature.initSign(privateKey)
                    signature.update(cadena.toByteArray(Charsets.UTF_8))
                    val sello = Base64.getEncoder().encodeToString(signature.sign())
                    result.success(sello)
                } catch (e: Exception) {
                    result.error("SIGN", e.message, null)
                }
            }
            else -> result.notImplemented()
        }
    }
}
