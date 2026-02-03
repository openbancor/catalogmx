package com.openbancor.catalogmx.cfdi

import java.io.StringReader
import javax.xml.XMLConstants
import javax.xml.transform.TransformerFactory
import javax.xml.transform.stream.StreamResult
import javax.xml.transform.stream.StreamSource
import javax.xml.validation.SchemaFactory


data class XsdValidationResult(val valid: Boolean, val errors: List<String>)

data class CadenaOriginalResult(val cadena: String)

object CfdiValidation {
    fun generateCadenaOriginal(xml: String, xslt: String): CadenaOriginalResult {
        val transformerFactory = TransformerFactory.newInstance()
        val transformer = transformerFactory.newTransformer(StreamSource(StringReader(xslt)))
        val resultWriter = java.io.StringWriter()
        transformer.transform(StreamSource(StringReader(xml)), StreamResult(resultWriter))
        return CadenaOriginalResult(resultWriter.toString().trim())
    }

    fun validateXsd(xml: String, xsd: String): XsdValidationResult {
        val schemaFactory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI)
        val schema = schemaFactory.newSchema(StreamSource(StringReader(xsd)))
        val validator = schema.newValidator()

        val errors = mutableListOf<String>()
        val errorHandler = object : org.xml.sax.helpers.DefaultHandler() {
            override fun error(e: org.xml.sax.SAXParseException) { errors.add(e.message ?: "error") }
            override fun fatalError(e: org.xml.sax.SAXParseException) { errors.add(e.message ?: "fatal") }
            override fun warning(e: org.xml.sax.SAXParseException) { errors.add(e.message ?: "warning") }
        }
        validator.errorHandler = errorHandler

        return try {
            validator.validate(StreamSource(StringReader(xml)))
            XsdValidationResult(errors.isEmpty(), errors)
        } catch (e: Exception) {
            errors.add(e.message ?: "validation error")
            XsdValidationResult(false, errors)
        }
    }
}
