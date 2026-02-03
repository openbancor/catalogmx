/// PAC timbrado interface
library;

class TimbradoResult {
  final String xmlTimbrado;
  final String? uuid;
  final String? fechaTimbrado;

  const TimbradoResult({
    required this.xmlTimbrado,
    this.uuid,
    this.fechaTimbrado,
  });
}

abstract class PacTimbrador {
  Future<TimbradoResult> timbrar(String xml);
}

class PacTimbradorMock implements PacTimbrador {
  @override
  Future<TimbradoResult> timbrar(String xml) async {
    return TimbradoResult(xmlTimbrado: xml);
  }
}
