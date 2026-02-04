import { buildUnsignedCfdiXml } from '../src/cfdi/builder';
import { aplicarSelloAComprobante } from '../src/cfdi/signing';

describe('CFDI builder', () => {
  test('buildUnsignedCfdiXml includes core nodes and attributes', () => {
    const xml = buildUnsignedCfdiXml({
      moneda: 'MXN',
      tipoDeComprobante: 'I',
      lugarExpedicion: '64000',
      subTotal: '100.00',
      total: '116.00',
      emisor: { rfc: 'BACL891217NJ5', nombre: 'Emisor SA', regimenFiscal: '612' },
      receptor: {
        rfc: 'XAXX010101000',
        nombre: 'Publico',
        usoCfdi: 'G03',
        regimenFiscalReceptor: '616',
        domicilioFiscalReceptor: '64000',
      },
      conceptos: [
        {
          claveProdServ: '01010101',
          cantidad: '1',
          claveUnidad: 'ACT',
          descripcion: 'Servicio',
          valorUnitario: '100.00',
          importe: '100.00',
        },
      ],
    });

    expect(xml).toContain('<cfdi:Comprobante');
    expect(xml).toContain('Version="4.0"');
    expect(xml).toContain('<cfdi:Emisor');
    expect(xml).toContain('Rfc="BACL891217NJ5"');
    expect(xml).toContain('<cfdi:Receptor');
    expect(xml).toContain('<cfdi:Conceptos>');
  });

  test('aplicarSelloAComprobante sets sello and certificados', () => {
    const baseXml =
      '<cfdi:Comprobante Version="4.0"><cfdi:Emisor /></cfdi:Comprobante>';
    const signed = aplicarSelloAComprobante({
      xml: baseXml,
      sello: 'abc123',
      certificado: 'CERT',
      noCertificado: '000010000',
    });

    expect(signed).toContain('Sello="abc123"');
    expect(signed).toContain('Certificado="CERT"');
    expect(signed).toContain('NoCertificado="000010000"');
  });
});
