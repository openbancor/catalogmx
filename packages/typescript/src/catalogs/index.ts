/**
 * catalogmx - Catalogs
 * Mexican official catalogs
 */

// Banxico (static catalogs)
export { BankCatalog } from './banxico/banks';
export { InstitucionesFinancieras } from './banxico/instituciones-financieras';
export { MonedasDivisas } from './banxico/monedas-divisas';

// Banxico (dynamic SQLite-backed catalogs)
export { UDICatalog } from './banxico/udis-sqlite';
export { TipoCambioUSDCatalog } from './banxico/tipo-cambio-usd-sqlite';
export { TIIE28Catalog } from './banxico/tiie-28-sqlite';
export { CETES28Catalog } from './banxico/cetes-28-sqlite';
export { InflacionAnualCatalog } from './banxico/inflacion-anual-sqlite';
export { SalariosMinimosCatalog } from './banxico/salarios-minimos-sqlite';

// IFT (Instituto Federal de Telecomunicaciones)
export { OperadoresMoviles } from './ift/operadores-moviles';

// CNBV (Comisión Nacional Bancaria y de Valores)
export { SectoresCNBVCatalog } from './cnbv/sectores';
export type { SectorCNBV, ReguladorFinanciero } from './cnbv/sectores';

// INEGI
export { StateCatalog } from './inegi/states';
export { MunicipiosCatalog } from './inegi/municipios';
export { MunicipiosCompletoCatalog } from './inegi/municipios-completo';
export { LocalidadesCatalog } from './inegi/localidades';
export { SCIANCatalog } from './inegi/scian';
export type { SectorSCIAN } from './inegi/scian';

// SEPOMEX
export { CodigosPostales } from './sepomex/codigos-postales';
export { CodigosPostalesCompleto } from './sepomex/codigos-postales-completo';

// SAT CFDI 4.0
export {
  RegimenFiscalCatalog,
  UsoCFDICatalog,
  FormaPagoCatalog,
  MetodoPagoCatalog,
  TipoComprobanteCatalog,
  ImpuestoCatalog,
  ExportacionCatalog,
  TipoRelacionCatalog,
  ObjetoImpCatalog,
  ClaveUnidadCatalog,
  ClaveProdServCatalog,
} from './sat/cfdi_4';

// SAT CFDI 4.0 - Hybrid SQLite/JSON (for large catalogs)
export { ClaveProdServCatalogHybrid } from './sat/cfdi_4/clave-prod-serv-hybrid';

// SAT Contabilidad Electrónica (Anexo 24)
export { CodigoAgrupadorSATCatalog } from './sat/contabilidad_electronica';

// SAT Comercio Exterior 2.0
export {
  IncotermsValidator,
  ClavePedimentoCatalog,
  MonedaCatalog,
  PaisCatalog,
  EstadoCatalog,
  MotivoTrasladoCatalog,
  RegistroIdentTribCatalog,
  UnidadAduanaCatalog,
} from './sat/comercio_exterior';

// SAT Carta Porte 3.0
export {
  AeropuertosCatalog,
  PuertosMaritimos,
  TipoPermisoCatalog,
  ConfigAutotransporteCatalog,
  CarreterasCatalog,
  MaterialPeligrosoCatalog,
  TipoEmbalajeCatalog,
} from './sat/carta_porte';

// SAT Nómina 1.2
export {
  TipoNominaCatalog,
  TipoContratoCatalog,
  TipoJornadaCatalog,
  TipoRegimenCatalog,
  PeriodicidadPagoCatalog,
  RiesgoPuestoCatalog,
  BancoNominaCatalog,
} from './sat/nomina';

// Mexico - National Catalogs
export { PlacasFormatosCatalog } from './mexico/placas-formatos';
export { SalariosMinimos } from './mexico/salarios-minimos';
export { UMACatalog } from './mexico/uma';
export { HoyNoCirculaCDMX } from './mexico/hoy-no-circula';
export { GirosMercantilesCatalog } from './mexico/giros-mercantiles';
export type { GiroMercantil, CategoriaGiro } from './mexico/giros-mercantiles';
