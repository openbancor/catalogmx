import React, { createContext, useContext, useMemo, useState } from 'react';

type Locale = 'es' | 'en';

type Messages = Record<string, string>;

const TRANSLATIONS: Record<Locale, Messages> = {
  es: {
    'nav.validators.title': 'Validadores',
    'nav.catalogs.title': 'Catálogos',
    'nav.catalogs.quick': 'Catálogos',
    'nav.catalogs.quickView': 'Abrir catálogo',
    'nav.calculators.title': 'Calculadoras',
    'nav.reference.title': 'Referencia',
    'nav.items.rfc': 'RFC',
    'nav.items.curp': 'CURP',
    'nav.items.clabe': 'CLABE',
    'nav.items.nss': 'NSS',
    'nav.items.catalogs': 'Explorar todo',
    'nav.items.tables': 'Tablas SQLite',
    'nav.items.catalogList': 'Catálogos completos',
    'nav.items.postal': 'Códigos postales',
    'nav.items.localidades': 'Localidades',
    'nav.items.productos': 'Productos/Servicios',
    'nav.items.isr': 'ISR',
    'nav.items.iva': 'IVA',
    'nav.items.ieps': 'IEPS',
    'nav.items.reference': 'Ejemplos de código',
    'catalogs.hero.subtitle': 'Build SQLite unificado listo para consultas HTTP/Range sin servidor.',
    'catalogs.hero.download': 'Descargar base de datos',
    'catalogs.hero.spec': 'Leer spec de VFS',
    'catalogs.hero.size': 'Tamaño',
    'catalogs.hero.modified': 'Última modificación',
    'catalogs.hero.description': 'Copia mexico.sqlite3 en /public/data y el demo lo carga localmente con sql.js. Sin servidor, sin API keys: datos normativos deterministas.',
    'catalogs.main.title': 'Catálogos principales',
    'catalogs.toggle.full': 'Ver catálogos completos',
    'catalogs.stats.tables': 'Tablas en mexico.sqlite3',
    'catalogs.stats.rows': 'Filas totales',
    'catalogs.stats.modified': 'Última modificación',
    'catalogs.stats.detail': 'Banxico · SAT · INEGI · SEPOMEX',
    'catalogs.stats.rowsDetail': 'Datos consolidados',
    'catalogs.feature.table': 'Tabla',
    'catalogs.feature.open': 'Abrir',
    'catalogs.list.title': 'Catálogos completos',
    'catalogs.list.subtitle': 'Explora los 58 catálogos oficiales con búsqueda por nombre y descripción.',
    'tables.title': 'Tablas de mexico.sqlite3',
    'tables.subtitle': 'Busca y navega cualquier tabla del archivo consolidado.',
    'tables.search.placeholder': 'Buscar tabla (ej. sat_cfdi_4_0_c_formapago)…',
    'tables.error': 'No se pudieron leer las tablas desde mexico.sqlite3.',
    'tables.loading': 'Cargando tablas…',
    'tables.empty': 'Sin resultados',
  },
  en: {
    'nav.validators.title': 'Validators',
    'nav.catalogs.title': 'Catalogs',
    'nav.catalogs.quick': 'Catalogs',
    'nav.catalogs.quickView': 'Open catalog',
    'nav.calculators.title': 'Calculators',
    'nav.reference.title': 'Reference',
    'nav.items.rfc': 'RFC',
    'nav.items.curp': 'CURP',
    'nav.items.clabe': 'CLABE',
    'nav.items.nss': 'NSS',
    'nav.items.catalogs': 'Browse All',
    'nav.items.tables': 'SQLite Tables',
    'nav.items.catalogList': 'All Catalogs',
    'nav.items.postal': 'Postal Codes',
    'nav.items.localidades': 'Localities',
    'nav.items.productos': 'Products/Services',
    'nav.items.isr': 'ISR',
    'nav.items.iva': 'IVA',
    'nav.items.ieps': 'IEPS',
    'nav.items.reference': 'Code Examples',
    'catalogs.hero.subtitle': 'Unified SQLite build ready for serverless HTTP/Range queries.',
    'catalogs.hero.download': 'Download database',
    'catalogs.hero.spec': 'Read VFS spec',
    'catalogs.hero.size': 'Size',
    'catalogs.hero.modified': 'Last modified',
    'catalogs.hero.description': 'Copy mexico.sqlite3 into /public/data and the demo loads it locally with sql.js. No server, no API keys: deterministic regulatory data.',
    'catalogs.main.title': 'Featured catalogs',
    'catalogs.toggle.full': 'View all catalogs',
    'catalogs.stats.tables': 'Tables in mexico.sqlite3',
    'catalogs.stats.rows': 'Total rows',
    'catalogs.stats.modified': 'Last modified',
    'catalogs.stats.detail': 'Banxico · SAT · INEGI · SEPOMEX',
    'catalogs.stats.rowsDetail': 'Consolidated data',
    'catalogs.feature.table': 'Table',
    'catalogs.feature.open': 'Open',
    'catalogs.list.title': 'All catalogs',
    'catalogs.list.subtitle': 'Browse the 58 official catalogs with search by name and description.',
    'tables.title': 'Tables in mexico.sqlite3',
    'tables.subtitle': 'Search and navigate any table in the consolidated file.',
    'tables.search.placeholder': 'Search table (e.g. sat_cfdi_4_0_c_formapago)…',
    'tables.error': 'Could not read tables from mexico.sqlite3.',
    'tables.loading': 'Loading tables…',
    'tables.empty': 'No results',
  },
};

interface LocaleContextValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string) => string;
}

const LocaleContext = createContext<LocaleContextValue | undefined>(undefined);

export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocale] = useState<Locale>('es');

  const value = useMemo<LocaleContextValue>(() => {
    const messages = TRANSLATIONS[locale] || TRANSLATIONS.es;
    const t = (key: string) => messages[key] ?? TRANSLATIONS.en[key] ?? key;
    return { locale, setLocale, t };
  }, [locale]);

  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>;
}

export function useLocale(): LocaleContextValue {
  const ctx = useContext(LocaleContext);
  if (!ctx) {
    throw new Error('useLocale must be used within LocaleProvider');
  }
  return ctx;
}
