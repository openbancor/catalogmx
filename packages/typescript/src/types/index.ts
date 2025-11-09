/**
 * Common types for catalogmx
 */

// Validator types
export interface RfcPersonaFisicaInput {
  nombre: string;
  apellidoPaterno: string;
  apellidoMaterno: string;
  fechaNacimiento: string; // YYYY-MM-DD
}

export interface RfcPersonaMoralInput {
  razonSocial: string;
  fechaConstitucion: string; // YYYY-MM-DD
}

export interface CurpInput {
  nombre: string;
  apellidoPaterno: string;
  apellidoMaterno: string;
  fechaNacimiento: string; // YYYY-MM-DD
  sexo: 'H' | 'M';
  estado: string;
  differentiator?: string;
}

export interface ValidationResult {
  valid: boolean;
  error?: string;
  details?: Record<string, any>;
}

// Catalog types
export interface Bank {
  code: string;
  name: string;
  short_name: string;
  spei: boolean;
  razon_social?: string;
}

export interface State {
  code: string; // CURP code
  name: string;
  clave_inegi: string;
  abreviatura: string;
  abreviatura_iso?: string;
}

export interface Municipality {
  cve_entidad: string;
  cve_municipio: string;
  nom_municipio: string;
  nom_entidad: string;
  cve_completa: string;
}

export interface Localidad {
  cvegeo: string;
  cve_entidad: string;
  nom_entidad: string;
  nom_abr_entidad: string;
  cve_municipio: string;
  nom_municipio: string;
  cve_localidad: string;
  nom_localidad: string;
  ambito: 'U' | 'R'; // Urbano o Rural
  latitud: number | null;
  longitud: number | null;
  altitud: number | null;
  poblacion_total: number;
  poblacion_masculina: number;
  poblacion_femenina: number;
  viviendas_habitadas: number;
  distancia_km?: number; // Agregado por búsqueda de coordenadas
}

export interface PostalCode {
  codigo_postal: string;
  asentamiento: string;
  tipo_asentamiento: string;
  municipio: string;
  estado: string;
  ciudad?: string;
  zona: 'Urbano' | 'Rural';
}

// SAT CFDI 4.0 types
export interface RegimenFiscal {
  code: string;
  description: string;
  persona_fisica: boolean;
  persona_moral: boolean;
}

export interface UsoCfdi {
  code: string;
  description: string;
  persona_fisica: boolean;
  persona_moral: boolean;
  regimen_fiscal?: string[];
}

export interface FormaPago {
  code: string;
  description: string;
  bancarizado?: boolean;
}

export interface MetodoPago {
  code: string;
  description: string;
}

export interface TipoComprobante {
  code: string;
  description: string;
  valor_max?: number;
}

export interface Impuesto {
  code: string;
  description: string;
  retencion: boolean;
  traslado: boolean;
}

export interface Exportacion {
  code: string;
  description: string;
}

export interface TipoRelacion {
  code: string;
  description: string;
}

export interface ObjetoImp {
  code: string;
  description: string;
}

// SAT Comercio Exterior types
export interface Incoterm {
  code: string;
  name: string;
  description: string;
  transport_mode: 'any' | 'maritime' | 'multimodal';
  seller_responsibility: string;
  buyer_responsibility: string;
  insurance_paid_by: 'seller' | 'buyer';
  risk_transfer_point: string;
}

export interface ClavePedimento {
  clave: string;
  descripcion: string;
  tipo: 'importacion' | 'exportacion' | 'transito';
}

export interface Moneda {
  code: string;
  name: string;
  decimals: number;
  countries?: string[];
}

export interface Pais {
  code: string; // ISO 3166-1 alpha-3
  name: string;
  agrupacion?: string;
}

export interface UnidadAduana {
  code: string;
  name: string;
  descripcion: string;
}

export interface RegistroIdentTrib {
  code: string;
  pais: string;
  descripcion: string;
  formato?: string;
  regex_pattern?: string;
}

export interface MotivoTraslado {
  code: string;
  descripcion: string;
}

export interface EstadoUSACanada {
  code: string;
  name: string;
  country: 'USA' | 'CAN';
}

// SAT Carta Porte types
export interface Aeropuerto {
  code: string;
  name: string;
  iata: string;
  icao: string;
  ciudad: string;
  estado: string;
}

export interface PuertoMaritimo {
  code: string;
  name: string;
  estado: string;
  coast: string;
}

export interface Carretera {
  code: string;
  nombre: string;
  origen: string;
  destino: string;
  tipo: string;
}

export interface TipoPermiso {
  code: string;
  descripcion: string;
  tipo_transporte: string;
}

export interface ConfigAutotransporte {
  code: string;
  descripcion: string;
  remolque: boolean;
  num_ejes?: number;
}

export interface TipoEmbalaje {
  code: string;
  descripcion: string;
  categoria_onu: string;
}

export interface MaterialPeligroso {
  code: string;
  descripcion: string;
  clase_riesgo: string;
  clase_division?: string;
  grupo_embalaje?: string;
}

// SAT Nómina types
export interface TipoNomina {
  code: string;
  descripcion: string;
}

export interface TipoContrato {
  code: string;
  descripcion: string;
}

export interface TipoJornada {
  code: string;
  descripcion: string;
}

export interface TipoRegimen {
  code: string;
  descripcion: string;
}

export interface PeriodicidadPago {
  code: string;
  descripcion: string;
  days: number;
}

export interface RiesgoPuesto {
  code: string;
  descripcion: string;
  prima_minima: number;
  prima_media: number;
  prima_maxima: number;
}

export interface BancoNomina {
  code: string;
  name: string;
  razon_social: string;
}
