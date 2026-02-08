import 'package:flutter/services.dart';

class CfdiPlatformChannel {
  static const MethodChannel _channel = MethodChannel('catalogmx_cfdi');

  Future<String> generateCadenaOriginal(
      {required String xml, required String xslt}) async {
    final result =
        await _channel.invokeMethod<String>('generateCadenaOriginal', {
      'xml': xml,
      'xslt': xslt,
    });
    if (result == null) {
      throw PlatformException(code: 'NULL', message: 'Cadena original vacía');
    }
    return result;
  }

  Future<Map<String, dynamic>> validateXsd(
      {required String xml, required String xsd}) async {
    final result = await _channel.invokeMethod<Map>('validateXsd', {
      'xml': xml,
      'xsd': xsd,
    });
    if (result == null) {
      throw PlatformException(code: 'NULL', message: 'Resultado nulo');
    }
    return Map<String, dynamic>.from(result);
  }

  Future<String> signCadenaOriginal(
      {required String cadena, required String privateKeyPem}) async {
    final result = await _channel.invokeMethod<String>('signCadenaOriginal', {
      'cadena': cadena,
      'privateKeyPem': privateKeyPem,
    });
    if (result == null) {
      throw PlatformException(code: 'NULL', message: 'Sello vacío');
    }
    return result;
  }
}
