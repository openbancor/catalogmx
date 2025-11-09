/**
 * catalogmx - Catalogs
 * Mexican official catalogs
 */

// Banxico
export { BankCatalog } from './banxico/banks';

// INEGI
export { StateCatalog } from './inegi/states';
export { MunicipiosCatalog } from './inegi/municipios';
export { MunicipiosCompletoCatalog } from './inegi/municipios-completo';

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
  ObjetoImpCatalog
} from './sat/cfdi_4';

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
