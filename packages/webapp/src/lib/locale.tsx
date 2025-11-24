import React, { createContext, useContext, useMemo, useState } from 'react';

type Locale = 'es' | 'en';

type Messages = Record<string, string>;

const TRANSLATIONS: Record<Locale, Messages> = {
  es: {
    'nav.validators.title': 'Validadores',
    'nav.catalogs.title': 'Catálogos',
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
    'catalogs.main.title': 'Catálogos principales',
    'catalogs.toggle.full': 'Ver catálogos completos',
  },
  en: {
    'nav.validators.title': 'Validators',
    'nav.catalogs.title': 'Catalogs',
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
    'catalogs.main.title': 'Featured catalogs',
    'catalogs.toggle.full': 'View all catalogs',
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
