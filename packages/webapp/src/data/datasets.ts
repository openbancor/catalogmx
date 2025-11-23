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
  {
    id: 'banxico-banks',
    label: 'Banxico - Banks',
    type: 'sql',
    table: 'banxico_banks',
    orderBy: 'code',
    searchColumns: ['code', 'name', 'full_name', 'rfc'],
    columns: [
      { key: 'code', label: 'Code' },
      { key: 'name', label: 'Name' },
      { key: 'full_name', label: 'Full name' },
      { key: 'rfc', label: 'RFC' },
      { key: 'spei', label: 'SPEI' },
    ],
    description: 'Instituciones participantes en SPEI/TEF',
  },
  {
    id: 'banxico-udis',
    label: 'Banxico - UDIS',
    type: 'sql',
    table: 'banxico_udis',
    orderBy: 'fecha',
    searchColumns: ['fecha', 'moneda', 'notas', 'tipo'],
    columns: [
      { key: 'fecha', label: 'Fecha' },
      { key: 'valor', label: 'Valor' },
      { key: 'moneda', label: 'Moneda' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'notas', label: 'Notas' },
    ],
    description: 'Histórico de UDIS Banxico',
  },
  {
    id: 'banxico-plazas',
    label: 'Banxico - Códigos de plaza',
    type: 'json-array',
    table: 'banxico_codigos_plaza',
    column: 'plazas',
    searchColumns: ['codigo', 'plaza', 'estado', 'cve_entidad'],
    columns: [
      { key: 'codigo', label: 'Código' },
      { key: 'plaza', label: 'Plaza' },
      { key: 'estado', label: 'Estado' },
      { key: 'cve_entidad', label: 'Entidad' },
    ],
    description: 'Códigos de plaza Banxico',
  },
  {
    id: 'banxico-monedas',
    label: 'Banxico - Monedas y divisas',
    type: 'json-array',
    table: 'banxico_monedas_divisas',
    column: 'monedas',
    searchColumns: ['codigo_iso', 'moneda', 'pais', 'simbolo'],
    columns: [
      { key: 'codigo_iso', label: 'ISO' },
      { key: 'moneda', label: 'Moneda' },
      { key: 'pais', label: 'País' },
      { key: 'simbolo', label: 'Símbolo' },
      { key: 'decimales', label: 'Decimales' },
      { key: 'tipo_cambio_banxico', label: 'Tipo cambio' },
      { key: 'activa', label: 'Activa' },
    ],
    description: 'Catálogo de monedas/divisas',
  },
  {
    id: 'banxico-instituciones',
    label: 'Banxico - Tipos de institución',
    type: 'json-array',
    table: 'banxico_instituciones_financieras',
    column: 'tipos_institucion',
    searchColumns: ['codigo', 'tipo', 'descripcion', 'regulador'],
    columns: [
      { key: 'codigo', label: 'Código' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'regulador', label: 'Regulador' },
      { key: 'ley_aplicable', label: 'Ley' },
    ],
    description: 'Tipos de institución financiera',
  },
  {
    id: 'ift-lada',
    label: 'IFT - Códigos LADA',
    type: 'json-array',
    table: 'ift_codigos_lada',
    column: 'codigos',
    searchColumns: ['lada', 'ciudad', 'estado', 'region'],
    columns: [
      { key: 'lada', label: 'LADA' },
      { key: 'ciudad', label: 'Ciudad' },
      { key: 'estado', label: 'Estado' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'region', label: 'Región' },
    ],
    description: 'Códigos LADA nacionales',
  },
  {
    id: 'ift-operadores',
    label: 'IFT - Operadores móviles',
    type: 'json-array',
    table: 'ift_operadores_moviles',
    column: 'operadores',
    searchColumns: ['nombre_comercial', 'razon_social', 'tipo', 'grupo_empresarial', 'cobertura'],
    columns: [
      { key: 'nombre_comercial', label: 'Nombre comercial' },
      { key: 'razon_social', label: 'Razón social' },
      { key: 'tipo', label: 'Tipo' },
      { key: 'grupo_empresarial', label: 'Grupo' },
      { key: 'tecnologias', label: 'Tecnologías' },
      { key: 'cobertura', label: 'Cobertura' },
      { key: 'servicios', label: 'Servicios' },
      { key: 'market_share_aprox', label: 'Market share' },
      { key: 'fecha_inicio_operaciones', label: 'Inicio' },
      { key: 'activo', label: 'Activo' },
    ],
    description: 'Operadores móviles autorizados',
  },
  {
    id: 'sat-regimen',
    label: 'SAT - Régimen Fiscal',
    type: 'json-array',
    table: 'sat_cfdi_4_0_c_regimenfiscal',
    column: 'data',
    searchColumns: ['valor', 'descripcion'],
    columns: [
      { key: 'valor', label: 'Clave' },
      { key: 'descripcion', label: 'Descripción' },
    ],
    description: 'Catálogo de régimen fiscal',
  },
  {
    id: 'sat-forma-pago',
    label: 'SAT - Forma de Pago',
    type: 'json-array',
    table: 'sat_cfdi_4_0_c_formapago',
    column: 'data',
    searchColumns: ['valor', 'descripcion'],
    columns: [
      { key: 'valor', label: 'Clave' },
      { key: 'descripcion', label: 'Descripción' },
    ],
    description: 'Formas de pago CFDI 4.0',
  },
  {
    id: 'sat-uso-cfdi',
    label: 'SAT - Uso CFDI',
    type: 'json-array',
    table: 'sat_cfdi_4_0_c_usocfdi',
    column: 'data',
    searchColumns: ['valor', 'descripcion'],
    columns: [
      { key: 'valor', label: 'Clave' },
      { key: 'descripcion', label: 'Descripción' },
    ],
    description: 'Uso CFDI 4.0',
  },
  {
    id: 'sat-moneda',
    label: 'SAT - Moneda',
    type: 'json-array',
    table: 'sat_cfdi_4_0_c_moneda',
    column: 'data',
    searchColumns: ['valor', 'descripcion'],
    columns: [
      { key: 'valor', label: 'Clave' },
      { key: 'descripcion', label: 'Descripción' },
    ],
    description: 'Monedas CFDI 4.0',
  },
  {
    id: 'sat-iva-tasas',
    label: 'SAT - IVA tasas',
    type: 'json-array',
    table: 'sat_impuestos_iva_tasas',
    column: 'tasas',
    searchColumns: ['tipo', 'descripcion', 'aplica_en'],
    columns: [
      { key: 'tipo', label: 'Tipo' },
      { key: 'tasa', label: 'Tasa' },
      { key: 'descripcion', label: 'Descripción' },
      { key: 'aplica_en', label: 'Aplica en' },
      { key: 'vigencia_inicio', label: 'Vigencia inicio' },
      { key: 'vigencia_fin', label: 'Vigencia fin' },
    ],
    description: 'Tasas de IVA',
  },
  {
    id: 'sat-nomina-bancos',
    label: 'SAT - Nómina bancos',
    type: 'sql',
    table: 'sat_nomina_1_2_banco',
    orderBy: 'code',
    searchColumns: ['code', 'name', 'full_name'],
    columns: [
      { key: 'code', label: 'Código' },
      { key: 'name', label: 'Nombre' },
      { key: 'full_name', label: 'Nombre completo' },
    ],
    description: 'Bancos para nómina SAT 1.2',
  },
] as const satisfies DatasetConfig[];

export type DatasetId = typeof datasetConfigs[number]['id'];
export type DatasetPageId = `dataset-${DatasetId}`;
