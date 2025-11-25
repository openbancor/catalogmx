import type { LucideIcon } from 'lucide-react';

export type DatasetType = 'sql' | 'json-array';
export type CategoryId = 'geographic' | 'fiscal' | 'banking' | 'telecom' | 'national';

export interface DatasetConfig {
  id: string;
  label: string;
  type: DatasetType;
  table: string;
  column?: string;
  columns: { key: string; label: string }[];
  searchColumns: string[];
  orderBy?: string;
  icon?: LucideIcon;
  description?: string;
  category: CategoryId;
}

export const DATASET_CATEGORIES = [
  { id: 'geographic' as CategoryId, label: 'Geográficos', emoji: '🗺️' },
  { id: 'fiscal' as CategoryId, label: 'Fiscales (SAT)', emoji: '📋' },
  { id: 'banking' as CategoryId, label: 'Bancarios', emoji: '🏦' },
  { id: 'telecom' as CategoryId, label: 'Telecomunicaciones', emoji: '📡' },
  { id: 'national' as CategoryId, label: 'Nacionales', emoji: '🇲🇽' },
];

export const datasetConfigs = [
  // ========== GEOGRÁFICOS ==========
  {
    id: 'sepomex-codigos-postales',
    label: 'Códigos Postales',
    type: 'sql',
    table: 'codigos_postales',
    category: 'geographic',
    searchColumns: ['cp', 'asentamiento', 'municipio', 'estado'],
    orderBy: 'cp',
    columns: [
      { key: 'cp', label: 'C.P.' },
      { key: 'asentamiento', label: 'Asentamiento' },
      { key: 'tipo_asentamiento', label: 'Tipo' },
      { key: 'municipio', label: 'Municipio' },
      { key: 'estado', label: 'Estado' },
      { key: 'zona', label: 'Zona' },
    ],
    description: '157k códigos postales SEPOMEX.',
  },
  {
    id: 'inegi-estados',
    label: 'Estados',
    type: 'sql',
    table: 'inegi_states',
    category: 'geographic',
    searchColumns: ['name', 'abbreviation', 'code'],
    orderBy: 'name',
    columns: [
      { key: 'code', label: 'CURP' },
      { key: 'name', label: 'Nombre' },
      { key: 'abbreviation', label: 'Abrev.' },
      { key: 'clave_inegi', label: 'INEGI' },
    ],
    description: '32 estados INEGI.',
  },
  {
    id: 'inegi-municipios',
    label: 'Municipios',
    type: 'sql',
    table: 'inegi_municipios_completo',
    category: 'geographic',
    searchColumns: ['nom_municipio', 'nom_entidad'],
    orderBy: 'nom_municipio',
    columns: [
      { key: 'cve_municipio', label: 'Clave' },
      { key: 'nom_municipio', label: 'Municipio' },
      { key: 'nom_entidad', label: 'Estado' },
      { key: 'nom_cabecera', label: 'Cabecera' },
      { key: 'poblacion_total', label: 'Población' },
    ],
    description: '2,478 municipios INEGI.',
  },
  {
    id: 'inegi-localidades',
    label: 'Localidades',
    type: 'sql',
    table: 'localidades',
    category: 'geographic',
    searchColumns: ['nom_localidad', 'nom_municipio', 'nom_entidad'],
    orderBy: 'poblacion_total DESC',
    columns: [
      { key: 'nom_localidad', label: 'Localidad' },
      { key: 'nom_municipio', label: 'Municipio' },
      { key: 'nom_entidad', label: 'Estado' },
      { key: 'poblacion_total', label: 'Población' },
      { key: 'latitud', label: 'Lat' },
      { key: 'longitud', label: 'Lng' },
    ],
    description: '10k localidades INEGI con coordenadas.',
  },

  // ========== FISCALES (SAT) ==========
  {
    id: 'sat-productos',
    label: 'Productos y Servicios',
    type: 'sql',
    table: 'clave_prod_serv',
    category: 'fiscal',
    searchColumns: ['clave', 'descripcion', 'palabras_similares'],
    orderBy: 'clave',
    columns: [
      { key: 'clave', label: 'Clave' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'incluye_iva', label: 'IVA' },
      { key: 'incluye_ieps', label: 'IEPS' },
    ],
    description: '52k productos CFDI 4.0.',
  },
  {
    id: 'sat-regimen-fiscal',
    label: 'Régimen Fiscal',
    type: 'sql',
    table: 'sat_cfdi_4_0_regimen_fiscal',
    category: 'fiscal',
    searchColumns: ['code', 'description'],
    columns: [
      { key: 'code', label: 'Clave' },
      { key: 'description', label: 'Descripción' },
      { key: 'fisica', label: 'P.F.' },
      { key: 'moral', label: 'P.M.' },
    ],
    description: 'Regímenes fiscales CFDI 4.0.',
  },
  {
    id: 'sat-forma-pago',
    label: 'Forma de Pago',
    type: 'sql',
    table: 'sat_cfdi_4_0_forma_pago',
    category: 'fiscal',
    searchColumns: ['code', 'description'],
    columns: [
      { key: 'code', label: 'Clave' },
      { key: 'description', label: 'Descripción' },
    ],
    description: 'Formas de pago CFDI 4.0.',
  },
  {
    id: 'sat-uso-cfdi',
    label: 'Uso CFDI',
    type: 'sql',
    table: 'sat_cfdi_4_0_uso_cfdi',
    category: 'fiscal',
    searchColumns: ['code', 'description'],
    columns: [
      { key: 'code', label: 'Clave' },
      { key: 'description', label: 'Descripción' },
      { key: 'fisica', label: 'P.F.' },
      { key: 'moral', label: 'P.M.' },
    ],
    description: 'Uso de CFDI 4.0.',
  },
  {
    id: 'sat-metodo-pago',
    label: 'Método de Pago',
    type: 'sql',
    table: 'sat_cfdi_4_0_metodo_pago',
    category: 'fiscal',
    searchColumns: ['code', 'description'],
    columns: [
      { key: 'code', label: 'Clave' },
      { key: 'description', label: 'Descripción' },
    ],
    description: 'Métodos de pago CFDI 4.0.',
  },
  {
    id: 'sat-tipo-contrato',
    label: 'Tipo de Contrato',
    type: 'sql',
    table: 'sat_nomina_1_2_tipo_contrato',
    category: 'fiscal',
    searchColumns: ['code', 'description'],
    columns: [
      { key: 'code', label: 'Clave' },
      { key: 'description', label: 'Tipo de Contrato' },
    ],
    description: 'Tipos de contrato laboral.',
  },
  {
    id: 'sat-tipo-jornada',
    label: 'Tipo de Jornada',
    type: 'sql',
    table: 'sat_nomina_1_2_tipo_jornada',
    category: 'fiscal',
    searchColumns: ['code', 'description'],
    columns: [
      { key: 'code', label: 'Clave' },
      { key: 'description', label: 'Tipo de Jornada' },
    ],
    description: 'Tipos de jornada laboral.',
  },

  // ========== BANCARIOS ==========
  {
    id: 'banxico-banks',
    label: 'Bancos SPEI',
    type: 'sql',
    table: 'banxico_banks',
    category: 'banking',
    orderBy: 'code',
    searchColumns: ['code', 'name', 'full_name'],
    columns: [
      { key: 'code', label: 'Código' },
      { key: 'name', label: 'Nombre' },
      { key: 'full_name', label: 'Razón Social' },
      { key: 'rfc', label: 'RFC' },
      { key: 'spei', label: 'SPEI' },
    ],
    description: '93 bancos SPEI Banxico.',
  },
  {
    id: 'banxico-monedas',
    label: 'Monedas y Divisas',
    type: 'sql',
    table: 'banxico_monedas_divisas',
    category: 'banking',
    searchColumns: ['codigo_iso', 'moneda', 'pais'],
    columns: [
      { key: 'codigo_iso', label: 'ISO' },
      { key: 'moneda', label: 'Moneda' },
      { key: 'pais', label: 'País' },
      { key: 'decimales', label: 'Decimales' },
    ],
    description: '30 monedas Banxico.',
  },
  {
    id: 'sat-nomina-bancos',
    label: 'Bancos Nómina',
    type: 'sql',
    table: 'sat_nomina_1_2_banco',
    category: 'banking',
    searchColumns: ['code', 'name', 'full_name'],
    orderBy: 'code',
    columns: [
      { key: 'code', label: 'Clave' },
      { key: 'name', label: 'Nombre' },
      { key: 'full_name', label: 'Razón Social' },
    ],
    description: 'Bancos para nómina SAT.',
  },
  {
    id: 'banxico-udis',
    label: 'UDI',
    type: 'json-array',
    table: 'banxico/udis.json',
    category: 'banking',
    searchColumns: ['fecha', 'valor', 'tipo'],
    columns: [
      { key: 'fecha', label: 'Fecha' },
      { key: 'valor', label: 'Valor' },
      { key: 'moneda', label: 'Moneda' },
      { key: 'tipo', label: 'Tipo' },
    ],
    description: 'Unidad de Inversión histórica desde 1995.',
  },
  {
    id: 'banxico-tipo-cambio-fix',
    label: 'Tipo de Cambio FIX',
    type: 'json-array',
    table: 'banxico/tipo_cambio_usd.json',
    category: 'banking',
    searchColumns: ['fecha', 'tipo_cambio', 'tipo'],
    columns: [
      { key: 'fecha', label: 'Fecha' },
      { key: 'tipo_cambio', label: 'MXN/USD' },
      { key: 'moneda_origen', label: 'Origen' },
      { key: 'moneda_destino', label: 'Destino' },
      { key: 'tipo', label: 'Tipo' },
    ],
    description: 'Tipo de cambio FIX diario desde 1991.',
  },
  {
    id: 'banxico-tipo-cambio-historico',
    label: 'Tipo de Cambio Histórico',
    type: 'json-array',
    table: 'banxico/tipo_cambio_hist.json',
    category: 'banking',
    searchColumns: ['fecha', 'tipo_cambio', 'tipo'],
    columns: [
      { key: 'fecha', label: 'Fecha' },
      { key: 'tipo_cambio', label: 'MXN/USD' },
      { key: 'moneda_origen', label: 'Origen' },
      { key: 'moneda_destino', label: 'Destino' },
      { key: 'tipo', label: 'Tipo' },
    ],
    description: 'Serie histórica completa desde 1954.',
  },
  {
    id: 'banxico-tiie-28',
    label: 'TIIE 28 días',
    type: 'json-array',
    table: 'banxico/tiie_28.json',
    category: 'banking',
    searchColumns: ['fecha', 'tasa', 'tipo'],
    columns: [
      { key: 'fecha', label: 'Fecha' },
      { key: 'tasa', label: 'Tasa (%)' },
      { key: 'plazo_dias', label: 'Plazo (días)' },
      { key: 'tipo', label: 'Tipo' },
    ],
    description: 'Tasa de Interés Interbancaria 28 días.',
  },
  {
    id: 'banxico-cetes-28',
    label: 'CETES 28 días',
    type: 'json-array',
    table: 'banxico/cetes_28.json',
    category: 'banking',
    searchColumns: ['fecha', 'tasa', 'instrumento'],
    columns: [
      { key: 'fecha', label: 'Fecha' },
      { key: 'tasa', label: 'Tasa (%)' },
      { key: 'plazo_dias', label: 'Plazo (días)' },
      { key: 'instrumento', label: 'Instrumento' },
      { key: 'tipo', label: 'Tipo' },
    ],
    description: 'Certificados de la Tesorería 28 días.',
  },
  {
    id: 'banxico-inflacion-anual',
    label: 'Inflación Anual',
    type: 'json-array',
    table: 'banxico/inflacion_anual.json',
    category: 'banking',
    searchColumns: ['fecha', 'inflacion_anual', 'indice'],
    columns: [
      { key: 'fecha', label: 'Fecha' },
      { key: 'inflacion_anual', label: 'Inflación (%)' },
      { key: 'indice', label: 'Índice' },
      { key: 'tipo', label: 'Tipo' },
    ],
    description: 'Inflación anual INPC desde 2010.',
  },
  {
    id: 'banxico-salarios-minimos',
    label: 'Salarios Mínimos Banxico',
    type: 'json-array',
    table: 'banxico/salarios_minimos.json',
    category: 'national',
    searchColumns: ['fecha', 'salario_minimo', 'zona', 'tipo'],
    columns: [
      { key: 'fecha', label: 'Fecha' },
      { key: 'salario_minimo', label: 'Salario ($)' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'zona', label: 'Zona' },
      { key: 'serie', label: 'Serie' },
      { key: 'periodo', label: 'Período' },
    ],
    description: 'Salarios mínimos históricos desde 1976.',
  },

  // ========== TELECOMUNICACIONES ==========
  {
    id: 'ift-operadores',
    label: 'Operadores Móviles',
    type: 'sql',
    table: 'ift_operadores_moviles',
    category: 'telecom',
    searchColumns: ['nombre_comercial', 'razon_social'],
    columns: [
      { key: 'nombre_comercial', label: 'Comercial' },
      { key: 'razon_social', label: 'Razón Social' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'tecnologias', label: 'Tecnologías' },
    ],
    description: '28 operadores IFT.',
  },

  // ========== NACIONALES ==========
  {
    id: 'mexico-salarios-minimos',
    label: 'Salarios Mínimos',
    type: 'sql',
    table: 'mexico_salarios_minimos',
    category: 'national',
    searchColumns: ['año'],
    orderBy: 'año DESC',
    columns: [
      { key: 'año', label: 'Año' },
      { key: 'resto_pais', label: 'General (MXN)' },
      { key: 'uma_equivalente_diario', label: 'UMA Equiv.' },
      { key: 'vigencia_inicio', label: 'Vigencia' },
    ],
    description: 'Histórico salarios mínimos.',
  },
  {
    id: 'mexico-uma',
    label: 'UMA',
    type: 'sql',
    table: 'mexico_uma',
    category: 'national',
    searchColumns: ['año'],
    orderBy: 'año DESC',
    columns: [
      { key: 'año', label: 'Año' },
      { key: 'valor_diario', label: 'Diario' },
      { key: 'valor_mensual', label: 'Mensual' },
      { key: 'valor_anual', label: 'Anual' },
      { key: 'vigencia_inicio', label: 'Vigencia' },
    ],
    description: 'Unidad de Medida y Actualización.',
  },
  {
    id: 'banxico-udis',
    label: 'UDIS',
    type: 'sql',
    table: 'banxico_udis',
    category: 'national',
    orderBy: 'fecha DESC',
    searchColumns: ['fecha'],
    columns: [
      { key: 'fecha', label: 'Fecha' },
      { key: 'valor', label: 'Valor' },
      { key: 'moneda', label: 'Moneda' },
    ],
    description: '420 valores históricos UDI.',
  },
] as const satisfies DatasetConfig[];

export type DatasetId = typeof datasetConfigs[number]['id'];
export type DatasetPageId = `dataset-${DatasetId}`;

export function getDatasetsByCategory(categoryId: CategoryId): DatasetConfig[] {
  return datasetConfigs.filter(d => d.category === categoryId);
}
