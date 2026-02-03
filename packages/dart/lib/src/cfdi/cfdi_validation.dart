/// CFDI validation and cadena original generation
library;

import 'dart:convert';

import 'package:xml/xml.dart';

class XsdValidationResult {
  final bool valid;
  final List<String> errors;

  const XsdValidationResult({required this.valid, required this.errors});
}

class CadenaOriginalResult {
  final String cadena;

  const CadenaOriginalResult({required this.cadena});
}

/// NOTE: Dart does not include native XSLT/XSD engines.
/// These helpers are stubs intended to be implemented via platform-specific
/// integrations (e.g., native Kotlin/Swift, or server-side validation).
class CfdiValidation {
  static CadenaOriginalResult generateCadenaOriginal(
    String xml,
    String xslt, {
    String Function(String xml, String xslt)? transformer,
  }) {
    // Basic XML sanity check
    XmlDocument.parse(xml);
    if (xslt.trim().isEmpty) {
      throw ArgumentError('XSLT content is empty');
    }
    if (transformer == null) {
      throw UnsupportedError(
        'XSLT transformation is not available in pure Dart. '
        'Provide a transformer or use a native/platform implementation.',
      );
    }
    return CadenaOriginalResult(cadena: transformer(xml, xslt).trim());
  }

  static XsdValidationResult validateXsd(
    String xml,
    String xsd, {
    XsdValidationResult Function(String xml, String xsd)? validator,
  }) {
    XmlDocument.parse(xml);
    if (xsd.trim().isEmpty) {
      return const XsdValidationResult(valid: false, errors: ['XSD is empty']);
    }
    if (validator == null) {
      return const XsdValidationResult(
        valid: false,
        errors: ['XSD validation requires a native/platform implementation'],
      );
    }
    return validator(xml, xsd);
  }

  static String prettyPrintXml(String xml) {
    final document = XmlDocument.parse(xml);
    return document.toXmlString(pretty: true, indent: '  ', newLine: '\n');
  }

  static String normalizeXml(String xml) {
    final document = XmlDocument.parse(xml);
    return document.toXmlString(pretty: false, indent: '', newLine: '');
  }

  static String base64EncodeXml(String xml) {
    return base64.encode(utf8.encode(xml));
  }
}
