/**
 * Minimal CFDI 4.0 XML builder (unsigned)
 */

export interface CfdiEmisor {
  rfc: string;
  nombre: string;
  regimenFiscal: string;
}

export interface CfdiReceptor {
  rfc: string;
  nombre: string;
  usoCfdi: string;
  regimenFiscalReceptor: string;
  domicilioFiscalReceptor: string;
}

export interface CfdiConcepto {
  claveProdServ: string;
  cantidad: string;
  claveUnidad: string;
  descripcion: string;
  valorUnitario: string;
  importe: string;
  objetoImp?: string;
  noIdentificacion?: string;
  unidad?: string;
  descuento?: string;
}

export interface CfdiComprobanteInput {
  version?: string;
  serie?: string;
  folio?: string;
  fecha?: string;
  moneda: string;
  tipoDeComprobante: string;
  lugarExpedicion: string;
  subTotal: string;
  total: string;
  exportacion?: string;
  metodoPago?: string;
  formaPago?: string;
  noCertificado?: string;
  certificado?: string;
  sello?: string;
  emisor: CfdiEmisor;
  receptor: CfdiReceptor;
  conceptos: CfdiConcepto[];
}

function escapeXml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}

function attr(name: string, value?: string): string {
  if (value === undefined || value === null || value === '') return '';
  return ` ${name}="${escapeXml(value)}"`;
}

export function buildUnsignedCfdiXml(data: CfdiComprobanteInput): string {
  const version = data.version ?? '4.0';
  const fecha = data.fecha ?? new Date().toISOString().slice(0, 19);

  const comprobanteAttrs = [
    attr('Version', version),
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
  ]
    .filter(Boolean)
    .join('');

  const emisor = `<cfdi:Emisor${attr('Rfc', data.emisor.rfc)}${attr(
    'Nombre',
    data.emisor.nombre
  )}${attr('RegimenFiscal', data.emisor.regimenFiscal)}/>`;

  const receptor = `<cfdi:Receptor${attr('Rfc', data.receptor.rfc)}${attr(
    'Nombre',
    data.receptor.nombre
  )}${attr('UsoCFDI', data.receptor.usoCfdi)}${attr(
    'RegimenFiscalReceptor',
    data.receptor.regimenFiscalReceptor
  )}${attr(
    'DomicilioFiscalReceptor',
    data.receptor.domicilioFiscalReceptor
  )}/>`;

  const conceptos = data.conceptos
    .map((c) => {
      const conceptoAttrs = [
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
      ]
        .filter(Boolean)
        .join('');
      return `<cfdi:Concepto${conceptoAttrs}/>`;
    })
    .join('');

  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    `<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4"`,
    ` xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"`,
    ` xsi:schemaLocation="http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd"${comprobanteAttrs}>`,
    emisor,
    receptor,
    `<cfdi:Conceptos>${conceptos}</cfdi:Conceptos>`,
    `</cfdi:Comprobante>`,
  ].join('');
}
