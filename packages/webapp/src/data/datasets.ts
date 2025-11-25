import type { LucideIcon } from 'lucide-react';

export type DatasetType = 'sql' | 'json-array';

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
}

export const datasetConfigs = [
  // SEPOMEX
  {
    id: 'sepomex-codigos-postales',
    label: 'SEPOMEX - Códigos Postales',
    type: 'sql',
    table: 'codigos_postales',
    searchColumns: ['d_codigo', 'd_asenta', 'd_mnpio', 'd_estado'],
    columns: [
      { key: 'd_codigo', label: 'C.P.' },
      { key: 'd_asenta', label: 'Asentamiento' },
      { key: 'd_tipo_asenta', label: 'Tipo' },
      { key: 'd_mnpio', label: 'Municipio' },
      { key: 'd_estado', label: 'Estado' },
      { key: 'd_zona', label: 'Zona' },
    ],
    description: 'Catálogo nacional de códigos postales, asentamientos y municipios.',
  },
  
  // INEGI
  {
    id: 'inegi-estados',
    label: 'INEGI - Estados (AGEE)',
    type: 'sql',
    table: 'inegi_estados',
    searchColumns: ['nombre', 'abreviatura', 'cve_ent'],
    columns: [
      { key: 'cve_ent', label: 'Clave' },
      { key: 'nombre', label: 'Nombre' },
      { key: 'abreviatura', label: 'Abrev.' },
      { key: 'poblacion_total', label: 'Población' },
    ],
    description: 'Catálogo de Entidades Federativas con datos poblacionales.',
  },
  {
    id: 'inegi-municipios',
    label: 'INEGI - Municipios (AGEM)',
    type: 'sql',
    table: 'inegi_municipios',
    searchColumns: ['nombre', 'cve_ent', 'cve_mun'],
    columns: [
      { key: 'cve_ent', label: 'Edo' },
      { key: 'cve_mun', label: 'Mun' },
      { key: 'nombre', label: 'Nombre' },
      { key: 'cabecera_municipal', label: 'Cabecera' },
    ],
    description: 'Catálogo de Municipios por Estado.',
  },
  {
    id: 'inegi-localidades',
    label: 'INEGI - Localidades (AGEL)',
    type: 'sql',
    table: 'inegi_localidades',
    searchColumns: ['nombre', 'cve_ent', 'cve_mun', 'cve_loc'],
    columns: [
      { key: 'cve_ent', label: 'Edo' },
      { key: 'cve_mun', label: 'Mun' },
      { key: 'cve_loc', label: 'Loc' },
      { key: 'nombre', label: 'Nombre' },
      { key: 'ambito', label: 'Ámbito' },
      { key: 'latitud', label: 'Lat' },
      { key: 'longitud', label: 'Lng' },
    ],
    description: 'Catálogo de Localidades (Urbanas y Rurales) con coordenadas.',
  },

  // SAT
  {
    id: 'sat-productos',
    label: 'SAT - Productos y Servicios',
    type: 'sql',
    table: 'sat_cfdi_4_0_c_claveprodserv',
    searchColumns: ['c_clave_prod_serv', 'descripcion', 'palabras_similares'],
    columns: [
      { key: 'c_clave_prod_serv', label: 'Clave' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'incluir_iva_trasladado', label: 'IVA' },
      { key: 'incluir_ieps_trasladado', label: 'IEPS' },
    ],
    description: 'Catálogo de Productos y Servicios (CFDI 4.0).',
  },
  {
    id: 'sat-regimen',
    label: 'SAT - Régimen Fiscal',
    type: 'sql',
    table: 'sat_cfdi_4_0_c_regimenfiscal',
    searchColumns: ['valor', 'descripcion'],
    columns: [
      { key: 'valor', label: 'Clave' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'fisica', label: 'Física' },
      { key: 'moral', label: 'Moral' },
    ],
    description: 'Catálogo de régimen fiscal.',
  },
  {
    id: 'sat-forma-pago',
    label: 'SAT - Forma de Pago',
    type: 'sql',
    table: 'sat_cfdi_4_0_c_formapago',
    searchColumns: ['valor', 'descripcion'],
    columns: [
      { key: 'valor', label: 'Clave' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'bancarizado', label: 'Bancarizado' },
    ],
    description: 'Formas de pago CFDI 4.0.',
  },
  {
    id: 'sat-uso-cfdi',
    label: 'SAT - Uso CFDI',
    type: 'sql',
    table: 'sat_cfdi_4_0_c_usocfdi',
    searchColumns: ['valor', 'descripcion'],
    columns: [
      { key: 'valor', label: 'Clave' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'fisica', label: 'Física' },
      { key: 'moral', label: 'Moral' },
    ],
    description: 'Uso de CFDI 4.0.',
  },
  {
    id: 'sat-moneda',
    label: 'SAT - Moneda',
    type: 'sql',
    table: 'sat_cfdi_4_0_c_moneda',
    searchColumns: ['valor', 'descripcion'],
    columns: [
      { key: 'valor', label: 'Clave' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'decimales', label: 'Decimales' },
    ],
    description: 'Monedas CFDI 4.0.',
  },
  {
    id: 'sat-iva-tasas',
    label: 'SAT - IVA tasas',
    type: 'sql',
    table: 'sat_impuestos_iva_tasas',
    searchColumns: ['tipo', 'descripcion', 'aplica_en'],
    columns: [
      { key: 'tipo', label: 'Tipo' },
      { key: 'tasa', label: 'Tasa' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'aplica_en', label: 'Aplica en' },
    ],
    description: 'Tasas de IVA.',
  },
  {
    id: 'sat-nomina-bancos',
    label: 'SAT - Nómina bancos',
    type: 'sql',
    table: 'sat_nomina_1_2_c_banco',
    orderBy: 'clave',
    searchColumns: ['clave', 'descripcion'],
    columns: [
      { key: 'clave', label: 'Clave' },
      { key: 'descripcion', label: 'Nombre' },
      { key: 'razon_social', label: 'Razón Social' },
    ],
    description: 'Bancos para nómina SAT 1.2.',
  },

  // BANXICO
  {
    id: 'banxico-banks',
    label: 'Banxico - Bancos (SPEI)',
    type: 'sql',
    table: 'banxico_banks',
    orderBy: 'code',
    searchColumns: ['code', 'name', 'full_name', 'rfc'],
    columns: [
      { key: 'code', label: 'Código' },
      { key: 'name', label: 'Nombre' },
      { key: 'full_name', label: 'Razón Social' },
      { key: 'rfc', label: 'RFC' },
      { key: 'spei', label: 'SPEI' },
    ],
    description: 'Instituciones participantes en SPEI.',
  },
  {
    id: 'banxico-udis',
    label: 'Banxico - UDIS',
    type: 'sql',
    table: 'banxico_udis',
    orderBy: 'fecha DESC',
    searchColumns: ['fecha', 'valor'],
    columns: [
      { key: 'fecha', label: 'Fecha' },
      { key: 'valor', label: 'Valor' },
    ],
    description: 'Histórico de UDIS Banxico.',
  },

  // IFT
  {
    id: 'ift-operadores',
    label: 'IFT - Operadores móviles',
    type: 'sql',
    table: 'ift_operadores_moviles',
    searchColumns: ['nombre_comercial', 'razon_social', 'tipo'],
    columns: [
      { key: 'nombre_comercial', label: 'Comercial' },
      { key: 'razon_social', label: 'Razón Social' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'tecnologias', label: 'Tecnologías' },
    ],
    description: 'Operadores móviles autorizados.',
  },
] as const satisfies DatasetConfig[];

export type DatasetId = typeof datasetConfigs[number]['id'];
export type DatasetPageId = `dataset-${DatasetId}`;
