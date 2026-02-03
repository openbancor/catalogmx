/// CFDI signing helpers (sello)
library;

import 'dart:convert';

class SelloResult {
  final String sello;

  const SelloResult(this.sello);
}

/// Provide a signer function (cadena -> sello base64) from native/platform code.
typedef CadenaSigner = String Function(String cadena);

class CfdiSigning {
  static SelloResult signCadenaOriginal(String cadena, CadenaSigner signer) {
    final sello = signer(cadena).trim();
    if (sello.isEmpty) {
      throw ArgumentError('Signer returned empty sello');
    }
    return SelloResult(sello);
  }

  static String applySelloToXml({
    required String xml,
    required String sello,
    String? certificado,
    String? noCertificado,
  }) {
    final openTag = RegExp(r'<cfdi:Comprobante\b([^>]*)>');
    final match = openTag.firstMatch(xml);
    if (match == null) {
      throw ArgumentError('No se encontró el nodo cfdi:Comprobante');
    }
    var attrs = match.group(1) ?? '';

    String setAttr(String name, String? value) {
      if (value == null || value.isEmpty) return attrs;
      final re = RegExp('$name="[^"]*"');
      if (re.hasMatch(attrs)) {
        attrs = attrs.replaceAll(re, '$name="$value"');
      } else {
        attrs = '$attrs $name="$value"';
      }
      return attrs;
    }

    setAttr('Sello', sello);
    setAttr('Certificado', certificado);
    setAttr('NoCertificado', noCertificado);

    return xml.replaceFirst(openTag, '<cfdi:Comprobante$attrs>');
  }

  static String base64EncodeDer(List<int> derBytes) {
    return base64.encode(derBytes);
  }
}
