/**
 * catalogmx - Catalogs
 * Mexican official catalogs
 */

// Banxico
export { BankCatalog } from './banxico/banks';
export { InstitucionesFinancieras } from './banxico/instituciones-financieras';
export { MonedasDivisas } from './banxico/monedas-divisas';
export { UDICatalog } from './banxico/udis';

// IFT (Instituto Federal de Telecomunicaciones)
export { OperadoresMoviles } from './ift/operadores-moviles';
export { CodigosLADA } from './ift/codigos-lada';

// INEGI
export { StateCatalog } from './inegi/states';
export { MunicipiosCatalog } from './inegi/municipios';
export { MunicipiosCompletoCatalog } from './inegi/municipios-completo';
export { LocalidadesCatalog } from './inegi/localidades';

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
  ClaveProdServCatalog
} from './sat/cfdi_4';

// SAT CFDI 4.0 - Hybrid SQLite/JSON (for large catalogs)
export { ClaveProdServCatalogHybrid } from './sat/cfdi_4/clave-prod-serv-hybrid';

// SAT Comercio Exterior 2.0
export {
  IncotermsValidator,
  ClavePedimentoCatalog,
  MonedaCatalog,
  PaisCatalog,
  EstadoCatalog,
  MotivoTrasladoCatalog,
  RegistroIdentTribCatalog,
  UnidadAduanaCatalog
} from './sat/comercio_exterior';

// SAT Carta Porte 3.0
export {
  AeropuertosCatalog,
  PuertosMaritimos,
  TipoPermisoCatalog,
  ConfigAutotransporteCatalog,
  CarreterasCatalog,
  MaterialPeligrosoCatalog,
  TipoEmbalajeCatalog
} from './sat/carta_porte';

// SAT Nómina 1.2
export {
  TipoNominaCatalog,
  TipoContratoCatalog,
  TipoJornadaCatalog,
  TipoRegimenCatalog,
  PeriodicidadPagoCatalog,
  RiesgoPuestoCatalog,
  BancoNominaCatalog
} from './sat/nomina';

// Mexico - National Catalogs
export { PlacasFormatosCatalog } from './mexico/placas-formatos';
export { SalariosMinimos } from './mexico/salarios-minimos';
export { UMACatalog } from './mexico/uma';
export { HoyNoCirculaCDMX } from './mexico/hoy-no-circula';
