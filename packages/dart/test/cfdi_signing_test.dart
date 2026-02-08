import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

void main() {
  test('applySelloToXml injects attributes', () {
    const xml =
        '<cfdi:Comprobante Version="4.0"><cfdi:Emisor /></cfdi:Comprobante>';
    final signed = CfdiSigning.applySelloToXml(
      xml: xml,
      sello: 'abc123',
      certificado: 'CERT',
      noCertificado: '000010000',
    );

    expect(signed.contains('Sello="abc123"'), isTrue);
    expect(signed.contains('Certificado="CERT"'), isTrue);
    expect(signed.contains('NoCertificado="000010000"'), isTrue);
  });
}
