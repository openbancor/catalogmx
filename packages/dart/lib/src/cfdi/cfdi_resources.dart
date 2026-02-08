/// CFDI resources helper (paths for XSD/XSLT)
library;

class CfdiResourceLocator {
  final String basePath;

  const CfdiResourceLocator({required this.basePath});

  String satUrlToLocalPath(String url) {
    final uri = Uri.parse(url);
    return '$basePath/sat/xsd/resources/${uri.host}${uri.path}';
  }

  String cfdi40Xsd() {
    return satUrlToLocalPath(
        'http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd');
  }

  String cadenaOriginal40Xslt() {
    return satUrlToLocalPath(
      'http://www.sat.gob.mx/sitio_internet/cfd/4/cadenaoriginal_4_0/cadenaoriginal_4_0.xslt',
    );
  }
}
