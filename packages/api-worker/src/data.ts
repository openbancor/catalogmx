import banks from '../../shared-data/banxico/banks.json';
import imssCatalogs from '../../shared-data/imss-catalogs.json';
import imssTables from '../../shared-data/imss-tables.json';
import municipalities from '../../shared-data/inegi/municipios.json';
import states from '../../shared-data/inegi/states.json';
import isrTables from '../../shared-data/isr-tables.json';
import postalCodes from '../../shared-data/sepomex/codigos_postales.json';
import bancoNomina from '../../shared-data/sat/nomina_1.2/banco.json';
import periodicidadPago from '../../shared-data/sat/nomina_1.2/periodicidad_pago.json';
import riesgoPuesto from '../../shared-data/sat/nomina_1.2/riesgo_puesto.json';
import tipoContrato from '../../shared-data/sat/nomina_1.2/tipo_contrato.json';
import tipoJornada from '../../shared-data/sat/nomina_1.2/tipo_jornada.json';
import tipoNomina from '../../shared-data/sat/nomina_1.2/tipo_nomina.json';
import tipoRegimen from '../../shared-data/sat/nomina_1.2/tipo_regimen.json';
import cExportacion from '../../shared-data/sat/cfdi_4.0/c_Exportacion.json';
import cFormaPago from '../../shared-data/sat/cfdi_4.0/c_FormaPago.json';
import cImpuesto from '../../shared-data/sat/cfdi_4.0/c_Impuesto.json';
import cMeses from '../../shared-data/sat/cfdi_4.0/c_Meses.json';
import cMetodoPago from '../../shared-data/sat/cfdi_4.0/c_MetodoPago.json';
import cMoneda from '../../shared-data/sat/cfdi_4.0/c_Moneda.json';
import cObjetoImp from '../../shared-data/sat/cfdi_4.0/c_ObjetoImp.json';
import cPais from '../../shared-data/sat/cfdi_4.0/c_Pais.json';
import cPeriodicidad from '../../shared-data/sat/cfdi_4.0/c_Periodicidad.json';
import cRegimenFiscal from '../../shared-data/sat/cfdi_4.0/c_RegimenFiscal.json';
import cTasaOCuota from '../../shared-data/sat/cfdi_4.0/c_TasaOCuota.json';
import cTipoDeComprobante from '../../shared-data/sat/cfdi_4.0/c_TipoDeComprobante.json';
import cTipoFactor from '../../shared-data/sat/cfdi_4.0/c_TipoFactor.json';
import cTipoRelacion from '../../shared-data/sat/cfdi_4.0/c_TipoRelacion.json';
import cUsoCFDI from '../../shared-data/sat/cfdi_4.0/c_UsoCFDI.json';
import { setCatalogJsonData } from '../../typescript/src/utils/catalog-backend';

export const CATALOG_VERSION = '2026-01-05';
export const CURRENT_FISCAL_VALIDITY = 2026;

export interface SmallCatalogSource {
  readonly path: string;
  readonly data: unknown;
}

const smallData: readonly SmallCatalogSource[] = [
  { path: 'banxico/banks.json', data: banks },
  { path: 'imss-catalogs.json', data: imssCatalogs },
  { path: 'imss-tables.json', data: imssTables },
  { path: 'inegi/municipios.json', data: municipalities },
  { path: 'inegi/states.json', data: states },
  { path: 'isr-tables.json', data: isrTables },
  { path: 'sepomex/codigos_postales.json', data: postalCodes },
  { path: 'sat/nomina_1.2/banco.json', data: bancoNomina },
  { path: 'sat/nomina_1.2/periodicidad_pago.json', data: periodicidadPago },
  { path: 'sat/nomina_1.2/riesgo_puesto.json', data: riesgoPuesto },
  { path: 'sat/nomina_1.2/tipo_contrato.json', data: tipoContrato },
  { path: 'sat/nomina_1.2/tipo_jornada.json', data: tipoJornada },
  { path: 'sat/nomina_1.2/tipo_nomina.json', data: tipoNomina },
  { path: 'sat/nomina_1.2/tipo_regimen.json', data: tipoRegimen },
  { path: 'sat/cfdi_4.0/c_Exportacion.json', data: cExportacion },
  { path: 'sat/cfdi_4.0/c_FormaPago.json', data: cFormaPago },
  { path: 'sat/cfdi_4.0/c_Impuesto.json', data: cImpuesto },
  { path: 'sat/cfdi_4.0/c_Meses.json', data: cMeses },
  { path: 'sat/cfdi_4.0/c_MetodoPago.json', data: cMetodoPago },
  { path: 'sat/cfdi_4.0/c_Moneda.json', data: cMoneda },
  { path: 'sat/cfdi_4.0/c_ObjetoImp.json', data: cObjetoImp },
  { path: 'sat/cfdi_4.0/c_Pais.json', data: cPais },
  { path: 'sat/cfdi_4.0/c_Periodicidad.json', data: cPeriodicidad },
  { path: 'sat/cfdi_4.0/c_RegimenFiscal.json', data: cRegimenFiscal },
  { path: 'sat/cfdi_4.0/c_TasaOCuota.json', data: cTasaOCuota },
  { path: 'sat/cfdi_4.0/c_TipoDeComprobante.json', data: cTipoDeComprobante },
  { path: 'sat/cfdi_4.0/c_TipoFactor.json', data: cTipoFactor },
  { path: 'sat/cfdi_4.0/c_TipoRelacion.json', data: cTipoRelacion },
  { path: 'sat/cfdi_4.0/c_UsoCFDI.json', data: cUsoCFDI },
];

export const SAT_NOMINA_CATALOGS: Readonly<Record<string, SmallCatalogSource>> = {
  banco: { path: 'sat/nomina_1.2/banco.json', data: bancoNomina },
  'periodicidad-pago': {
    path: 'sat/nomina_1.2/periodicidad_pago.json',
    data: periodicidadPago,
  },
  'riesgo-puesto': { path: 'sat/nomina_1.2/riesgo_puesto.json', data: riesgoPuesto },
  'tipo-contrato': { path: 'sat/nomina_1.2/tipo_contrato.json', data: tipoContrato },
  'tipo-jornada': { path: 'sat/nomina_1.2/tipo_jornada.json', data: tipoJornada },
  'tipo-nomina': { path: 'sat/nomina_1.2/tipo_nomina.json', data: tipoNomina },
  'tipo-regimen': { path: 'sat/nomina_1.2/tipo_regimen.json', data: tipoRegimen },
};

export const SAT_CFDI_CATALOGS: Readonly<Record<string, SmallCatalogSource>> = {
  exportacion: { path: 'sat/cfdi_4.0/c_Exportacion.json', data: cExportacion },
  'forma-pago': { path: 'sat/cfdi_4.0/c_FormaPago.json', data: cFormaPago },
  impuesto: { path: 'sat/cfdi_4.0/c_Impuesto.json', data: cImpuesto },
  meses: { path: 'sat/cfdi_4.0/c_Meses.json', data: cMeses },
  'metodo-pago': { path: 'sat/cfdi_4.0/c_MetodoPago.json', data: cMetodoPago },
  moneda: { path: 'sat/cfdi_4.0/c_Moneda.json', data: cMoneda },
  'objeto-imp': { path: 'sat/cfdi_4.0/c_ObjetoImp.json', data: cObjetoImp },
  pais: { path: 'sat/cfdi_4.0/c_Pais.json', data: cPais },
  periodicidad: { path: 'sat/cfdi_4.0/c_Periodicidad.json', data: cPeriodicidad },
  'regimen-fiscal': { path: 'sat/cfdi_4.0/c_RegimenFiscal.json', data: cRegimenFiscal },
  'tasa-o-cuota': { path: 'sat/cfdi_4.0/c_TasaOCuota.json', data: cTasaOCuota },
  'tipo-comprobante': {
    path: 'sat/cfdi_4.0/c_TipoDeComprobante.json',
    data: cTipoDeComprobante,
  },
  'tipo-factor': { path: 'sat/cfdi_4.0/c_TipoFactor.json', data: cTipoFactor },
  'tipo-relacion': { path: 'sat/cfdi_4.0/c_TipoRelacion.json', data: cTipoRelacion },
  'uso-cfdi': { path: 'sat/cfdi_4.0/c_UsoCFDI.json', data: cUsoCFDI },
};

let isPreloaded = false;

export function preloadSmallData(): void {
  if (isPreloaded) return;
  for (const source of smallData) {
    setCatalogJsonData(source.path, source.data);
  }
  isPreloaded = true;
}
