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
  short_name?: string;
  full_name?: string;
  spei: boolean;
  rfc?: string;
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
  cp: string;
  codigo_postal?: string; // Alias for backward compatibility
  asentamiento: string;
  tipo_asentamiento: string;
  municipio: string;
  estado: string;
  ciudad?: string;
  cp_oficina?: string;
  codigo_estado?: string;
  codigo_municipio?: string;
  zona?: 'Urbano' | 'Rural';
}

// SAT CFDI 4.0 types
export interface RegimenFiscal {
  code: string;
  description: string;
  fisica: boolean;
  moral: boolean;
  persona_fisica?: boolean; // Alias
  persona_moral?: boolean; // Alias
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
  name_es?: string;
  description: string;
  transport_mode: 'any' | 'maritime' | 'multimodal';
  seller_responsibility: string;
  buyer_responsibility?: string;
  seller_pays_freight: boolean;
  seller_pays_insurance: boolean;
  insurance_paid_by?: 'seller' | 'buyer'; // Computed field
  insurance_coverage?: string;
  risk_transfer_point: string;
  suitable_for?: string[];
  notes?: string;
}

export interface ClavePedimento {
  clave: string;
  descripcion: string;
  tipo: 'importacion' | 'exportacion' | 'transito';
}

export interface Moneda {
  codigo: string;
  code?: string; // Alias for backward compatibility
  nombre: string;
  name?: string; // Alias for backward compatibility
  decimales: number;
  decimals?: number; // Alias for backward compatibility
  pais?: string;
  countries?: string[];
}

export interface Pais {
  codigo: string; // ISO 3166-1 alpha-3
  code?: string; // Alias for backward compatibility
  nombre: string;
  name?: string; // Alias for backward compatibility
  iso2?: string;
  requiere_subdivision?: boolean;
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

// SAT CFDI 4.0 - Large Catalogs
export interface ClaveUnidad {
  id: string;
  nombre: string;
  descripcion: string;
  nota: string;
  fechaDeInicioDeVigencia: string;
  fechaDeFinDeVigencia: string;
  simbolo: string;
}

export interface ClaveProdServ {
  id: string; // 8 digit code
  descripcion: string;
  incluirIVATrasladado: string;
  incluirIEPSTrasladado: string;
  complementoQueDebeIncluir: string;
  fechaInicioVigencia: string;
  fechaFinVigencia: string;
  estimuloFranjaFronteriza: string;
  palabrasSimilares: string;
}

// Tax System Types
export interface ISRTramo {
  limite_inferior: number;
  limite_superior: number | null;
  cuota_fija: number;
  tasa_excedente: number;
}

export interface ISRTabla {
  año: number;
  periodicidad: 'mensual' | 'anual' | 'quincenal' | 'semanal' | 'diario';
  vigencia_inicio: string;
  vigencia_fin: string | null;
  tramos: ISRTramo[];
}

export interface SubsidioEmpleo {
  limite_inferior: number;
  limite_superior: number | null;
  subsidio: number;
}

export interface IVATasa {
  tipo: 'general' | 'frontera' | 'tasa_cero';
  tasa: number;
  vigencia_inicio: string;
  vigencia_fin: string | null;
  descripcion: string;
  aplica_en: string;
  estados_frontera?: string[];
  categorias?: string[];
}

export interface IEPSTasa {
  subcategoria: string;
  tasa: number;
  tipo: 'ad_valorem' | 'cuota_fija';
  cuota_fija_por_cigarro?: number;
  unidad?: string;
  vigencia_inicio: string;
  vigencia_fin: string | null;
  descripcion: string;
  criterio?: string;
}

export interface IEPSCategoria {
  categoria: string;
  descripcion: string;
  tasas: IEPSTasa[];
}

export interface RetencionISR {
  concepto: string;
  tasa: number | string;
  descripcion: string;
  base: string;
  articulo: string;
  vigencia_inicio?: string;
  vigencia_fin?: string | null;
  tasas_especificas?: { tipo: string; tasa: number }[];
  nota?: string;
}

export interface RetencionIVA {
  concepto: string;
  tasa: number;
  descripcion: string;
  base: string;
  articulo: string;
  vigencia_inicio: string;
  vigencia_fin: string | null;
  calculo?: string;
}

export interface ImpuestoEstatal {
  estado: string;
  cve_estado: string;
  tasa: number;
  base: string;
}

// Tax Calculation Results
export interface ISRCalculationResult {
  ingreso_gravable: number;
  limite_inferior: number;
  excedente: number;
  cuota_fija: number;
  impuesto_marginal: number;
  isr_causado: number;
  tasa_efectiva: number;
  subsidio_empleo?: number;
  isr_a_retener: number;
}

export interface IVACalculationResult {
  base: number;
  tasa: number;
  iva: number;
  total_con_iva: number;
  tipo_tasa: 'general' | 'frontera' | 'tasa_cero' | 'exento';
}

export interface IEPSCalculationResult {
  base: number;
  tasa: number;
  ieps: number;
  tipo_calculo: 'ad_valorem' | 'cuota_fija';
  unidad?: string;
  cantidad?: number;
}

export interface RetencionCalculationResult {
  concepto: string;
  base: number;
  tasa: number;
  retencion: number;
  impuesto_base?: number; // Para IVA retenido
}

// IFT - Operadores Móviles
export interface OperadorMovil {
  nombre_comercial: string;
  razon_social: string;
  tipo: 'OMR' | 'OMV';
  grupo_empresarial?: string;
  red_anfitriona?: string;
  tecnologias: string[];
  cobertura: 'nacional' | 'regional';
  servicios: string[];
  market_share_aprox: number;
  fecha_inicio_operaciones: string;
  activo: boolean;
  fecha_fin_operaciones?: string;
  notas?: string;
}

// IFT - Códigos LADA
export interface CodigoLADA {
  lada: string;
  ciudad: string;
  estado: string;
  tipo: 'metropolitana' | 'fronteriza' | 'turistica' | 'normal';
  region: string;
}

// Banxico - Instituciones Financieras
export interface TipoInstitucionFinanciera {
  codigo: string;
  tipo: string;
  descripcion: string;
  regulador: string;
  ley_aplicable: string;
  ejemplos: string[];
}

// Banxico - Monedas y Divisas
export interface MonedaDivisa {
  codigo_iso: string;
  numero_iso: string;
  moneda: string;
  pais: string;
  simbolo: string;
  decimales: number;
  moneda_nacional: boolean;
  tipo_cambio_banxico: boolean;
  tipo_cambio_fix?: boolean;
  activa: boolean;
  notas?: string;
}

// Mexico - Placas (License Plates)
export interface PlacaFormato {
  id?: number;
  estado: string;
  codigo_estado: string;
  formato: string;
  pattern: string;
  descripcion: string;
  tipo: 'particular' | 'motocicleta' | 'diplomatico' | 'consular' | 'organismo_internacional' |
        'servicio_publico_federal' | 'servicio_publico_estatal' | 'carga_federal' | 'carga_estatal' |
        'militar_ejercito' | 'militar_marina' | 'guardia_nacional' |
        'policia_federal' | 'policia_estatal' | 'policia_municipal' |
        'bomberos' | 'ambulancia' | 'proteccion_civil' |
        'remolque_federal' | 'remolque_estatal' | 'grua' | 'convertidor' |
        'antiguo' | 'ecologico' | 'demostracion' | 'capacidades_diferentes' |
        'transporte_escolar' | 'taxi' | 'exportacion' | 'importacion' | 'arrendamiento' |
        'gobierno_federal';
  activo: boolean;
  vigencia_inicio?: string;
  vigencia_fin?: string;
  dimensiones?: string;
  norma?: string;
  notas?: string;
}

// Mexico - Salarios Mínimos
export interface SalarioMinimo {
  año: number;
  vigencia_inicio: string;
  zona_frontera_norte?: number;
  resto_pais?: number;
  zona_general?: number;
  zona_a?: number;
  zona_b?: number;
  zona_c?: number;
  moneda: string;
  periodo: 'diario' | 'mensual' | 'anual';
  notas?: string;
}

// Mexico - UMA (Unidad de Medida y Actualización)
export interface UMA {
  año: number;
  vigencia_inicio: string;
  vigencia_fin: string;
  valor_diario: number;
  valor_mensual: number;
  valor_anual: number;
  moneda: string;
  publicacion_dof: string;
  incremento_porcentual: number | null;
  notas?: string;
}

// Banxico - UDI (Unidades de Inversión)
export interface UDI {
  fecha: string;
  valor: number;
  moneda: string;
  tipo: 'diario' | 'promedio_mensual' | 'promedio_anual' | 'valor_inicial';
  año: number;
  mes?: number;
  notas?: string;
}

// CDMX - Hoy No Circula
export interface HoyNoCirculaRestriccion {
  dia: string;
  terminacion_placa: string[];
  engomado: string[];
  horario_restriccion: string;
  aplica_sabados?: boolean;
  aplica_contingencia?: boolean;
  notas?: string;
}

export interface HoyNoCirculaHolograma {
  holograma: '00' | '0' | '1' | '2';
  exento: boolean;
  descripcion: string;
  restriccion_sabatina: boolean;
  dias_adicionales?: string;
  notas?: string;
}

export interface HoyNoCirculaSabado {
  mes: string;
  semana: number;
  terminaciones: string[];
  fecha_ejemplo: string;
}

export interface HoyNoCirculaContingencia {
  fase: string;
  calidad_aire: string;
  restriccion_adicional: string;
  vehiculos_exentos: string[];
}

export interface HoyNoCirculaPeriodoVerificacion {
  periodo: string;
  meses: string[];
  terminacion_placa: string[];
}

export interface HoyNoCirculaPrograma {
  metadata: {
    programa: string;
    jurisdiccion: string;
    vigencia: string;
    fuente: string;
    ultima_actualizacion: string;
  };
  restricciones_por_dia: HoyNoCirculaRestriccion[];
  exenciones_por_holograma: HoyNoCirculaHolograma[];
  calendario_sabados_holograma_2: HoyNoCirculaSabado[];
  contingencias_ambientales: HoyNoCirculaContingencia[];
  tipos_vehiculos_exentos: string[];
  zonas_aplicacion: string[];
  municipios_edomex: string[];
  verificacion_vehicular: {
    periodicidad: string;
    periodos: HoyNoCirculaPeriodoVerificacion[];
  };
}
