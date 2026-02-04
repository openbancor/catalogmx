import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

void main() {
  test('prettyPrintXml and normalizeXml work', () {
    const xml = '<root><child>1</child></root>';
    final pretty = CfdiValidation.prettyPrintXml(xml);
    final normalized = CfdiValidation.normalizeXml(pretty);

    expect(pretty.contains('\n'), isTrue);
    expect(normalized, equals(xml));
  });

  test('base64EncodeXml encodes content', () {
    const xml = '<root>hola</root>';
    final encoded = CfdiValidation.base64EncodeXml(xml);
    expect(encoded, isNotEmpty);
  });
}
