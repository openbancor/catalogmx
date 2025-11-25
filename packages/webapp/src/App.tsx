import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import {
  Menu, X, Download, Database, Github
} from 'lucide-react';
import { Button, buttonVariants } from '@/components/ui/button';
import ThemeToggle from '@/components/ThemeToggle';
import { NAVIGATION_EVENT } from '@/lib/navigation';
import DatasetPage from '@/pages/DatasetPage';
import { datasetConfigs, type DatasetPageId } from '@/data/datasets';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { navigation, type PageId } from '@/lib/routes';
import MobileNav from '@/components/MobileNav';

// Pages
import ValidatorsPage from '@/pages/ValidatorsPage';
import CalculatorsPage from '@/pages/CalculatorsPage';
import CatalogsPage from '@/pages/CatalogsPage';
import ReferencePage from '@/pages/ReferencePage';
import CatalogListPage from '@/pages/CatalogListPage';
import { LocaleProvider, useLocale } from '@/lib/locale';

const datasetPageComponents = Object.fromEntries(
  datasetConfigs.map((d) => [`dataset-${d.id}`, () => <DatasetPage datasetId={d.id} />] as const)
) as unknown as Record<DatasetPageId, React.ComponentType>;

const pageComponents: Record<PageId, React.ComponentType> = {
  'home': CatalogsPage,
  'catalogs': CatalogsPage, // Alias
  'validators': ValidatorsPage,
  'calculators': CalculatorsPage,
  'reference': ReferencePage,
  'catalog-list': CatalogListPage,
  // Individual pages still available if needed, but primary nav uses grouped pages
  'rfc': ValidatorsPage, 
  'curp': ValidatorsPage,
  'clabe': ValidatorsPage,
  'nss': ValidatorsPage,
  'isr': CalculatorsPage,
  'iva': CalculatorsPage,
  'ieps': CalculatorsPage,
  // Legacy mappings
  'tables': CatalogsPage, 
  'postal-codes': CatalogsPage,
  'localidades': CatalogsPage,
  'productos': CatalogsPage,
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
  const [currentPage, setCurrentPage] = useState<PageId>('home');
  const [sidebarOpen, setSidebarOpen] = useState(() => {
    if (typeof window === 'undefined') return true;
    return window.innerWidth >= 1024; // Only open on large screens by default
  });
  const [catalogQuickOpen, setCatalogQuickOpen] = useState(false);
  const [catalogSearch, setCatalogSearch] = useState('');
  
  // Flatten navigation for sidebar
  const flatNavigation = navigation.flatMap(s => s.items);
  const currentNavItem = flatNavigation.find(i => i.id === currentPage);
  const catalogQuickLinks = datasetConfigs.slice(0, 8);

  const PageComponent = pageComponents[currentPage] || CatalogsPage;

  useEffect(() => {
    const handleResize = () => {
      if (typeof window === 'undefined') return;
      if (window.innerWidth < 1024 && sidebarOpen) {
        setSidebarOpen(false);
      }
      if (window.innerWidth >= 1024 && !sidebarOpen) {
        setSidebarOpen(true);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [sidebarOpen]);

  useEffect(() => {
    const handleNavigate = (event: Event) => {
      const detail = (event as CustomEvent<string>).detail;
      if (typeof detail === 'string') {
        // If navigating to a specific tool, mapping helps
        setCurrentPage(detail as PageId);
        if (typeof window !== 'undefined' && window.innerWidth < 1024) {
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
          className="fixed inset-0 z-[55] bg-black/40 backdrop-blur-sm lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-[60] flex flex-col border-r border-border bg-card/95 p-0 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-card/90 transition-[width,transform] duration-300",
          sidebarOpen
            ? "w-72 max-w-[80vw] lg:w-64 translate-x-0"
            : "w-16 -translate-x-full lg:translate-x-0 lg:w-16" // Collapsed on desktop
        )}
      >
        <div className="h-16 flex items-center px-4 border-b border-border/60 justify-between">
          <div className="flex items-center gap-2 overflow-hidden">
            <div className="h-9 w-9 rounded-lg bg-primary text-primary-foreground flex-shrink-0 flex items-center justify-center font-semibold tracking-tight">
              MX
            </div>
            {sidebarOpen && <span className="text-base font-semibold truncate">catalogmx</span>}
          </div>
          {sidebarOpen && (
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden rounded-full"
              onClick={() => setSidebarOpen(false)}
              aria-label="Cerrar navegación"
            >
              <X className="h-5 w-5" />
            </Button>
          )}
        </div>

        <nav className="flex-1 overflow-y-auto py-4">
          {navigation.map((section, idx) => (
            <div key={idx} className="mb-5">
              {section.title && sidebarOpen && (
                <h3 className="px-4 mb-2 text-xs font-semibold uppercase tracking-widest text-muted-foreground/80">
                  {t(section.title)}
                </h3>
              )}
              <div className="space-y-1 px-2">
                {section.items.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setCurrentPage(item.id)}
                    title={t(item.label)}
                    className={cn(
                      "w-full flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      currentPage === item.id
                        ? "bg-primary/15 text-primary"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground",
                      !sidebarOpen && "justify-center px-0"
                    )}
                  >
                    <item.icon className="h-5 w-5 flex-shrink-0" />
                    {sidebarOpen && <span>{t(item.label)}</span>}
                  </button>
                ))}
              </div>
            </div>
          ))}
          
          {/* Quick links only visible when sidebar is expanded */}
          {sidebarOpen && (
            <div className="mt-6 px-3">
              <div className="text-xs font-semibold uppercase tracking-widest text-muted-foreground/80 mb-2">
                {t('nav.catalogs.quick')}
              </div>
              <div className="space-y-1">
                {catalogQuickLinks.slice(0, 5).map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setCurrentPage(`dataset-${cat.id}` as PageId)}
                    className={cn(
                      "w-full rounded-lg px-3 py-1.5 text-left text-xs font-medium hover:bg-muted truncate",
                      currentPage === `dataset-${cat.id}` ? "bg-primary/10 text-primary" : "text-muted-foreground"
                    )}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </nav>

        <div className={cn("border-t border-border/60 p-4 text-xs text-muted-foreground", !sidebarOpen && "flex flex-col items-center")}>
           <a href="https://github.com/openbancor/catalogmx" target="_blank" rel="noopener" className="hover:text-foreground flex items-center justify-center">
              {sidebarOpen ? 'GitHub' : <Github className="h-4 w-4" />}
            </a>
            {sidebarOpen && (
              <div className="mt-2 flex gap-2 justify-center">
                 <a href="https://www.npmjs.com/package/catalogmx" target="_blank" rel="noopener" className="hover:text-foreground">npm</a>
                 {' · '}
                 <a href="https://pypi.org/project/catalogmx/" target="_blank" rel="noopener" className="hover:text-foreground">PyPI</a>
              </div>
            )}
        </div>
      </aside>

      {/* Main area */}
      <main className={cn(
        "flex-1 bg-background pb-20 md:pb-0 min-w-0 transition-all duration-300",
        sidebarOpen ? "lg:ml-64" : "lg:ml-16"
      )}>
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/80">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen((prev) => !prev)}
            className="hidden lg:flex rounded-full border border-transparent hover:border-border"
          >
             {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>

          <div className="flex flex-col min-w-0">
            <span className="text-xs uppercase tracking-widest text-muted-foreground">catalogmx</span>
            <span className="text-base font-semibold truncate">
               {currentNavItem ? t(currentNavItem.label) : (currentPage.startsWith('dataset') ? 'Catálogo' : '')}
            </span>
          </div>

          <div className="ml-auto flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              className="hidden sm:flex"
              onClick={() => setCatalogQuickOpen(true)}
            >
              <Database className="h-4 w-4 mr-2" />
              <span>Buscar</span>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="sm:hidden"
              onClick={() => setCatalogQuickOpen(true)}
            >
              <Database className="h-4 w-4" />
            </Button>
            
            <a
              href={`${import.meta.env.BASE_URL}data/mexico.sqlite3`}
              target="_blank"
              rel="noopener noreferrer"
              className={cn(buttonVariants({ variant: 'outline', size: 'sm' }), 'hidden md:inline-flex rounded-full gap-2')}
            >
              <Download className="h-4 w-4" />
              <span>DB</span>
            </a>
            
            <ThemeToggle />
            <Button variant="ghost" size="sm" onClick={() => setLocale(locale === 'es' ? 'en' : 'es')} className="w-9 px-0">
              {locale === 'es' ? 'EN' : 'ES'}
            </Button>
          </div>
        </header>

        <div className="p-4 sm:p-6 lg:p-8">
          <div className="mx-auto w-full max-w-7xl">
            <PageComponent />
          </div>
        </div>
      </main>

      <MobileNav
        currentPage={currentPage}
        onNavigate={setCurrentPage}
      />

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
