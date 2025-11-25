import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import {
  Database, Code, Menu, X, Download,
  CreditCard, User, Building2, Shield, MapPin, Package,
  Receipt, Percent, DollarSign, Layers
} from 'lucide-react';
import { Button, buttonVariants } from '@/components/ui/button';
import ThemeToggle from '@/components/ThemeToggle';
import { NAVIGATION_EVENT } from '@/lib/navigation';
import DatasetPage from '@/pages/DatasetPage';
import { datasetConfigs, type DatasetPageId } from '@/data/datasets';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';

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
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    if (typeof window === 'undefined') return true;
    return window.innerWidth >= 768;
  });
  const [catalogQuickOpen, setCatalogQuickOpen] = useState(false);
  const [catalogSearch, setCatalogSearch] = useState('');
  const flatNavigation = navigation.flatMap(s => s.items);
  const currentNavItem = flatNavigation.find(i => i.id === currentPage);
  const catalogQuickLinks = datasetConfigs.slice(0, 8);

  const PageComponent = pageComponents[currentPage];

  useEffect(() => {
    const handleResize = () => {
      if (typeof window === 'undefined') return;
      if (window.innerWidth < 768 && sidebarOpen) {
        setSidebarOpen(false);
      }
      if (window.innerWidth >= 768 && !sidebarOpen) {
        setSidebarOpen(true);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [sidebarOpen]);

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

  const filteredCatalogs = datasetConfigs.filter((cat) => {
    const q = catalogSearch.trim().toLowerCase();
    if (!q) return true;
    return (
      cat.label.toLowerCase().includes(q) ||
      cat.table.toLowerCase().includes(q)
    );
  });

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 backdrop-blur-sm md:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex flex-col border-r border-border bg-card/95 p-0 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-card/90 transition-[width,transform] duration-300",
          sidebarOpen
            ? "w-72 max-w-[80vw] md:w-64 translate-x-0"
            : "w-16 -translate-x-full md:translate-x-0"
        )}
      >
        <div className="h-16 flex items-center px-4 border-b border-border/60">
          <div className="flex items-center gap-2">
            <div className="h-9 w-9 rounded-lg bg-primary text-primary-foreground flex items-center justify-center font-semibold tracking-tight">
              MX
            </div>
            {sidebarOpen && <span className="text-base font-semibold">catalogmx</span>}
          </div>
          {sidebarOpen && (
            <Button
              variant="ghost"
              size="icon"
              className="ml-auto md:hidden rounded-full"
              onClick={() => setSidebarOpen(false)}
              aria-label="Cerrar navegación"
            >
              <X className="h-5 w-5" />
            </Button>
          )}
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

          {sidebarOpen && (
            <div className="mt-6 px-3">
              <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/80 mb-2">
                {t('nav.catalogs.quick')}
              </div>
              <div className="space-y-1">
                {catalogQuickLinks.map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setCurrentPage(`dataset-${cat.id}` as PageId)}
                    className={cn(
                      "w-full rounded-lg px-3 py-2 text-left text-xs font-medium hover:bg-muted",
                      currentPage === `dataset-${cat.id}` ? "bg-primary/10 text-primary" : "text-muted-foreground"
                    )}
                  >
                    <div className="truncate">{cat.label}</div>
                  </button>
                ))}
              </div>
              <button
                onClick={() => setCurrentPage('catalog-list')}
                className={cn(
                  "mt-2 w-full text-left text-xs font-semibold text-primary hover:underline"
                )}
              >
                {t('nav.catalogs.quickView')}
              </button>
            </div>
          )}
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

          <div className="flex flex-col min-w-0">
            <span className="text-xs uppercase tracking-widest text-muted-foreground">catalogmx</span>
            <span className="text-base font-semibold truncate">
              {currentNavItem ? t(currentNavItem.label) : ''}
            </span>
          </div>

          <div className="ml-auto flex items-center gap-2 overflow-x-auto whitespace-nowrap">
            <Button
              variant="outline"
              size="sm"
              className="sm:hidden"
              onClick={() => setCatalogQuickOpen(true)}
            >
              <Database className="h-4 w-4" />
              <span className="ml-1">Catálogos</span>
            </Button>
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
              className={cn(
                buttonVariants({ variant: 'outline', size: 'sm' }),
                'rounded-full hidden sm:inline-flex'
              )}
            >
              Download DB
            </a>
            <a
              href={`${import.meta.env.BASE_URL}data/mexico.sqlite3`}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(buttonVariants({ variant: 'ghost', size: 'icon' }), 'sm:hidden rounded-full')}
            >
              <Download className="h-4 w-4" />
            </a>
            <Button variant="outline" size="sm" onClick={() => setLocale(locale === 'es' ? 'en' : 'es')}>
              {locale === 'es' ? 'EN' : 'ES'}
            </Button>
            <ThemeToggle />
          </div>
        </header>

        <div className="p-4 sm:p-6">
          <div className="mx-auto w-full max-w-6xl">
            <PageComponent />
          </div>
        </div>
      </main>

      <Dialog open={catalogQuickOpen} onOpenChange={setCatalogQuickOpen}>
        <DialogContent className="max-w-md w-[min(90vw,480px)]">
          <DialogHeader>
            <DialogTitle>{t('nav.catalogs.title')}</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <Input
              placeholder="Buscar catálogo..."
              value={catalogSearch}
              onChange={(e) => setCatalogSearch(e.target.value)}
            />
            <div className="max-h-[320px] overflow-auto divide-y rounded border">
              {filteredCatalogs.map((cat) => (
                <button
                  key={cat.id}
                  className="w-full text-left px-3 py-2 hover:bg-muted text-sm"
                  onClick={() => {
                    setCurrentPage(`dataset-${cat.id}` as PageId);
                    setCatalogQuickOpen(false);
                  }}
                >
                  <div className="font-medium">{cat.label}</div>
                  <div className="text-xs text-muted-foreground truncate">
                    {cat.description}
                  </div>
                </button>
              ))}
              {!filteredCatalogs.length && (
                <div className="px-3 py-2 text-sm text-muted-foreground">Sin resultados</div>
              )}
            </div>
            <Button variant="outline" onClick={() => {
              setCatalogQuickOpen(false);
              setCurrentPage('catalog-list');
            }}>
              {t('nav.catalogs.quickView')}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
