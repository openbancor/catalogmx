/// Minimal CFDI 4.0 XML builder (unsigned)
library;

class CfdiEmisor {
  final String rfc;
  final String nombre;
  final String regimenFiscal;

  const CfdiEmisor({
    required this.rfc,
    required this.nombre,
    required this.regimenFiscal,
  });
}

class CfdiReceptor {
  final String rfc;
  final String nombre;
  final String usoCfdi;
  final String regimenFiscalReceptor;
  final String domicilioFiscalReceptor;

  const CfdiReceptor({
    required this.rfc,
    required this.nombre,
    required this.usoCfdi,
    required this.regimenFiscalReceptor,
    required this.domicilioFiscalReceptor,
  });
}

class CfdiConcepto {
  final String claveProdServ;
  final String cantidad;
  final String claveUnidad;
  final String descripcion;
  final String valorUnitario;
  final String importe;
  final String? objetoImp;
  final String? noIdentificacion;
  final String? unidad;
  final String? descuento;

  const CfdiConcepto({
    required this.claveProdServ,
    required this.cantidad,
    required this.claveUnidad,
    required this.descripcion,
    required this.valorUnitario,
    required this.importe,
    this.objetoImp,
    this.noIdentificacion,
    this.unidad,
    this.descuento,
  });
}

class CfdiComprobanteInput {
  final String version;
  final String? serie;
  final String? folio;
  final String? fecha;
  final String moneda;
  final String tipoDeComprobante;
  final String lugarExpedicion;
  final String subTotal;
  final String total;
  final String? exportacion;
  final String? metodoPago;
  final String? formaPago;
  final String? noCertificado;
  final String? certificado;
  final String? sello;
  final CfdiEmisor emisor;
  final CfdiReceptor receptor;
  final List<CfdiConcepto> conceptos;

  const CfdiComprobanteInput({
    this.version = '4.0',
    this.serie,
    this.folio,
    this.fecha,
    required this.moneda,
    required this.tipoDeComprobante,
    required this.lugarExpedicion,
    required this.subTotal,
    required this.total,
    this.exportacion,
    this.metodoPago,
    this.formaPago,
    this.noCertificado,
    this.certificado,
    this.sello,
    required this.emisor,
    required this.receptor,
    required this.conceptos,
  });
}

class CfdiBuilder {
  static String buildUnsignedXml(CfdiComprobanteInput data) {
    final fecha =
        data.fecha ?? DateTime.now().toIso8601String().substring(0, 19);

    String attr(String name, String? value) {
      if (value == null || value.isEmpty) return '';
      return ' $name="${_escapeXml(value)}"';
    }

    final comprobanteAttrs = [
      attr('Version', data.version),
      attr('Serie', data.serie),
      attr('Folio', data.folio),
      attr('Fecha', fecha),
      attr('Moneda', data.moneda),
      attr('TipoDeComprobante', data.tipoDeComprobante),
      attr('LugarExpedicion', data.lugarExpedicion),
      attr('SubTotal', data.subTotal),
      attr('Total', data.total),
      attr('Exportacion', data.exportacion),
      attr('MetodoPago', data.metodoPago),
      attr('FormaPago', data.formaPago),
      attr('NoCertificado', data.noCertificado),
      attr('Certificado', data.certificado),
      attr('Sello', data.sello),
    ].join('');

    final emisor = '<cfdi:Emisor'
        '${attr('Rfc', data.emisor.rfc)}'
        '${attr('Nombre', data.emisor.nombre)}'
        '${attr('RegimenFiscal', data.emisor.regimenFiscal)}/>';

    final receptor = '<cfdi:Receptor'
        '${attr('Rfc', data.receptor.rfc)}'
        '${attr('Nombre', data.receptor.nombre)}'
        '${attr('UsoCFDI', data.receptor.usoCfdi)}'
        '${attr('RegimenFiscalReceptor', data.receptor.regimenFiscalReceptor)}'
        '${attr('DomicilioFiscalReceptor', data.receptor.domicilioFiscalReceptor)}/>';

    final conceptos = data.conceptos.map((c) {
      final conceptoAttrs = [
        attr('ClaveProdServ', c.claveProdServ),
        attr('Cantidad', c.cantidad),
        attr('ClaveUnidad', c.claveUnidad),
        attr('Descripcion', c.descripcion),
        attr('ValorUnitario', c.valorUnitario),
        attr('Importe', c.importe),
        attr('ObjetoImp', c.objetoImp),
        attr('NoIdentificacion', c.noIdentificacion),
        attr('Unidad', c.unidad),
        attr('Descuento', c.descuento),
      ].join('');
      return '<cfdi:Concepto$conceptoAttrs/>';
    }).join('');

    return [
      '<?xml version="1.0" encoding="UTF-8"?>',
      '<cfdi:Comprobante'
          ' xmlns:cfdi="http://www.sat.gob.mx/cfd/4"'
          ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
          ' xsi:schemaLocation="http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd"'
          '$comprobanteAttrs>',
      emisor,
      receptor,
      '<cfdi:Conceptos>$conceptos</cfdi:Conceptos>',
      '</cfdi:Comprobante>',
    ].join('');
  }

  static String _escapeXml(String value) {
    return value
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&apos;');
  }
}
