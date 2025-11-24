import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import {
  Database, Code, Menu, X,
  CreditCard, User, Building2, Shield, MapPin, Package,
  Receipt, Percent, DollarSign, Layers
} from 'lucide-react';
import { Button, buttonVariants } from '@/components/ui/button';
import ThemeToggle from '@/components/ThemeToggle';
import { NAVIGATION_EVENT } from '@/lib/navigation';
import DatasetPage from '@/pages/DatasetPage';
import { datasetConfigs, type DatasetPageId } from '@/data/datasets';

// Pages
import RFCPage from '@/pages/RFCPage';
import CURPPage from '@/pages/CURPPage';
import CLABEPage from '@/pages/CLABEPage';
import NSSPage from '@/pages/NSSPage';
import CatalogsPage from '@/pages/CatalogsPage';
import PostalCodesPage from '@/pages/PostalCodesPage';
import LocalidadesPage from '@/pages/LocalidadesPage';
import ProductosPage from '@/pages/ProductosPage';
import ISRPage from '@/pages/ISRPage';
import IVAPage from '@/pages/IVAPage';
import IEPSPage from '@/pages/IEPSPage';
import ReferencePage from '@/pages/ReferencePage';
import TablesPage from '@/pages/TablesPage';
import CatalogListPage from '@/pages/CatalogListPage';
import { LocaleProvider, useLocale } from '@/lib/locale';

type PageId =
  | 'rfc' | 'curp' | 'clabe' | 'nss'
  | 'catalogs' | 'tables' | 'catalog-list'
  | 'postal-codes' | 'localidades' | 'productos'
  | 'isr' | 'iva' | 'ieps'
  | 'reference'
  | DatasetPageId;

interface NavItem {
  id: PageId;
  label: string;
  icon: React.ElementType;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const navigation: NavSection[] = [
  {
    title: 'nav.validators.title',
    items: [
      { id: 'rfc', label: 'nav.items.rfc', icon: Building2 },
      { id: 'curp', label: 'nav.items.curp', icon: User },
      { id: 'clabe', label: 'nav.items.clabe', icon: CreditCard },
      { id: 'nss', label: 'nav.items.nss', icon: Shield },
    ]
  },
  {
    title: 'nav.catalogs.title',
    items: [
      { id: 'catalogs', label: 'nav.items.catalogs', icon: Database },
      { id: 'tables', label: 'nav.items.tables', icon: Database },
      { id: 'catalog-list', label: 'nav.items.catalogList', icon: Layers },
      { id: 'postal-codes', label: 'nav.items.postal', icon: MapPin },
      { id: 'localidades', label: 'nav.items.localidades', icon: MapPin },
      { id: 'productos', label: 'nav.items.productos', icon: Package },
    ]
  },
  {
    title: 'nav.calculators.title',
    items: [
      { id: 'isr', label: 'nav.items.isr', icon: Receipt },
      { id: 'iva', label: 'nav.items.iva', icon: Percent },
      { id: 'ieps', label: 'nav.items.ieps', icon: DollarSign },
    ]
  },
  {
    title: 'nav.reference.title',
    items: [
      { id: 'reference', label: 'nav.items.reference', icon: Code },
    ]
  }
];

const datasetPageComponents = Object.fromEntries(
  datasetConfigs.map((d) => [`dataset-${d.id}`, () => <DatasetPage datasetId={d.id} />] as const)
) as unknown as Record<DatasetPageId, React.ComponentType>;

const pageComponents: Record<PageId, React.ComponentType> = {
  'rfc': RFCPage,
  'curp': CURPPage,
  'clabe': CLABEPage,
  'nss': NSSPage,
  'catalogs': CatalogsPage,
  'tables': TablesPage,
  'catalog-list': CatalogListPage,
  'postal-codes': PostalCodesPage,
  'localidades': LocalidadesPage,
  'productos': ProductosPage,
  'isr': ISRPage,
  'iva': IVAPage,
  'ieps': IEPSPage,
  'reference': ReferencePage,
  ...datasetPageComponents,
};

export default function App() {
  return (
    <LocaleProvider>
      <AppInner />
    </LocaleProvider>
  );
}

function AppInner() {
  const { locale, setLocale, t } = useLocale();
  const [currentPage, setCurrentPage] = useState<PageId>('catalogs');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const flatNavigation = navigation.flatMap(s => s.items);
  const currentNavItem = flatNavigation.find(i => i.id === currentPage);

  const PageComponent = pageComponents[currentPage];

  useEffect(() => {
    const handleNavigate = (event: Event) => {
      const detail = (event as CustomEvent<string>).detail;
      if (typeof detail === 'string' && detail in pageComponents) {
        setCurrentPage(detail as PageId);
        if (typeof window !== 'undefined' && window.innerWidth < 768) {
          setSidebarOpen(false);
        }
      }
    };

    window.addEventListener(NAVIGATION_EVENT, handleNavigate as EventListener);
    return () => {
      window.removeEventListener(NAVIGATION_EVENT, handleNavigate as EventListener);
    };
  }, []);

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex flex-col border-r border-border bg-card/95 p-0 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-card/90 transition-[width,transform] duration-300",
          sidebarOpen ? "w-64 translate-x-0" : "w-16 -translate-x-full md:translate-x-0"
        )}
      >
        <div className="h-16 flex items-center px-4 border-b border-border/60">
          <div className="flex items-center gap-2">
            <div className="h-9 w-9 rounded-lg bg-primary text-primary-foreground flex items-center justify-center font-semibold tracking-tight">
              MX
            </div>
            {sidebarOpen && <span className="text-base font-semibold">catalogmx</span>}
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto py-4">
          {navigation.map((section) => (
            <div key={section.title} className="mb-5">
              {sidebarOpen && (
                <h3 className="px-4 mb-2 text-xs font-semibold uppercase tracking-widest text-muted-foreground/80">
                  {t(section.title)}
                </h3>
              )}
              <div className="space-y-1 px-2">
                {section.items.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setCurrentPage(item.id)}
                    className={cn(
                      "w-full flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      currentPage === item.id
                        ? "bg-primary/15 text-primary"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    )}
                  >
                    <item.icon className="h-4 w-4 flex-shrink-0" />
                    {sidebarOpen && <span>{t(item.label)}</span>}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </nav>

        {sidebarOpen && (
          <div className="border-t border-border/60 p-4 text-xs text-muted-foreground">
            <a href="https://github.com/openbancor/catalogmx" target="_blank" rel="noopener" className="hover:text-foreground">
              GitHub
            </a>
            {' · '}
            <a href="https://www.npmjs.com/package/catalogmx" target="_blank" rel="noopener" className="hover:text-foreground">
              npm
            </a>
            {' · '}
            <a href="https://pypi.org/project/catalogmx/" target="_blank" rel="noopener" className="hover:text-foreground">
              PyPI
            </a>
          </div>
        )}
      </aside>

      {/* Main area */}
      <main className={cn("flex-1 bg-background", sidebarOpen ? "md:ml-64" : "md:ml-16")}>
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/80">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen((prev) => !prev)}
            className="rounded-full border border-transparent hover:border-border"
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>

          <div className="flex flex-col">
            <span className="text-xs uppercase tracking-widest text-muted-foreground">catalogmx</span>
            <span className="text-base font-semibold">{currentNavItem?.label}</span>
          </div>

          <div className="ml-auto flex items-center gap-2">
            <a
              href="https://github.com/openbancor/catalogmx"
              target="_blank"
              rel="noopener noreferrer"
              className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }), 'hidden sm:inline-flex rounded-full')}
            >
              Docs
            </a>
            <a
              href={`${import.meta.env.BASE_URL}data/mexico.sqlite3`}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(buttonVariants({ variant: 'outline', size: 'sm' }), 'rounded-full')}
            >
              Download DB
            </a>
            <Button variant="outline" size="sm" onClick={() => setLocale(locale === 'es' ? 'en' : 'es')}>
              {locale === 'es' ? 'EN' : 'ES'}
            </Button>
            <ThemeToggle />
          </div>
        </header>

        <div className="p-4 sm:p-6">
          <PageComponent />
        </div>
      </main>
    </div>
  );
}
