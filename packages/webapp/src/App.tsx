import { useState } from 'react';
import { cn } from '@/lib/utils';
import {
  Database, Code, Menu, X,
  CreditCard, User, Building2, Shield, MapPin, Package,
  Receipt, Percent, DollarSign, ChevronRight
} from 'lucide-react';
import { Button, buttonVariants } from '@/components/ui/button';

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

type PageId =
  | 'rfc' | 'curp' | 'clabe' | 'nss'
  | 'catalogs' | 'postal-codes' | 'localidades' | 'productos'
  | 'isr' | 'iva' | 'ieps'
  | 'reference';

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
    title: 'Validators',
    items: [
      { id: 'rfc', label: 'RFC', icon: Building2 },
      { id: 'curp', label: 'CURP', icon: User },
      { id: 'clabe', label: 'CLABE', icon: CreditCard },
      { id: 'nss', label: 'NSS', icon: Shield },
    ]
  },
  {
    title: 'Catalogs',
    items: [
      { id: 'catalogs', label: 'Browse All', icon: Database },
      { id: 'postal-codes', label: 'Postal Codes', icon: MapPin },
      { id: 'localidades', label: 'Localities', icon: MapPin },
      { id: 'productos', label: 'Products/Services', icon: Package },
    ]
  },
  {
    title: 'Calculators',
    items: [
      { id: 'isr', label: 'ISR', icon: Receipt },
      { id: 'iva', label: 'IVA', icon: Percent },
      { id: 'ieps', label: 'IEPS', icon: DollarSign },
    ]
  },
  {
    title: 'Reference',
    items: [
      { id: 'reference', label: 'Code Examples', icon: Code },
    ]
  }
];

const pageComponents: Record<PageId, React.ComponentType> = {
  'rfc': RFCPage,
  'curp': CURPPage,
  'clabe': CLABEPage,
  'nss': NSSPage,
  'catalogs': CatalogsPage,
  'postal-codes': PostalCodesPage,
  'localidades': LocalidadesPage,
  'productos': ProductosPage,
  'isr': ISRPage,
  'iva': IVAPage,
  'ieps': IEPSPage,
  'reference': ReferencePage,
};

const heroHighlights = [
  {
    value: '58',
    label: 'Government catalogs',
    detail: 'SAT · INEGI · Banxico'
  },
  {
    value: '12',
    label: 'Validators & calculators',
    detail: 'RFC · CURP · CLABE · ISR'
  },
  {
    value: '93.78%',
    label: 'Test coverage',
    detail: '1,250+ automated checks'
  }
];

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('rfc');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const flatNavigation = navigation.flatMap(s => s.items);
  const currentNavItem = flatNavigation.find(i => i.id === currentPage);

  const PageComponent = pageComponents[currentPage];

  return (
    <div className="relative min-h-screen bg-background overflow-hidden">
      <div className="pointer-events-none absolute -top-32 -left-24 h-96 w-96 bg-primary/25 blur-[140px]" />
      <div className="pointer-events-none absolute top-1/3 right-0 h-[28rem] w-[28rem] bg-emerald-400/20 dark:bg-emerald-900/40 blur-[180px]" />
      <div className="pointer-events-none absolute bottom-0 left-1/2 h-64 w-64 -translate-x-1/2 bg-sky-400/10 dark:bg-sky-900/30 blur-[160px]" />

      <div className="relative z-10 flex min-h-screen">
        {/* Sidebar */}
        <aside className={cn(
          "fixed inset-y-0 left-0 z-50 flex flex-col border-r border-white/20 bg-white/80 p-0 backdrop-blur-xl shadow-2xl transition-all duration-300 dark:border-white/10 dark:bg-slate-950/70",
          sidebarOpen ? "w-64" : "w-0 -translate-x-full md:w-16 md:translate-x-0"
        )}>
        {/* Logo */}
        <div className="h-14 flex items-center px-4 border-b">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-primary flex items-center justify-center text-primary-foreground font-bold text-sm">
              MX
            </div>
            {sidebarOpen && (
              <span className="font-semibold">catalogmx</span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          {navigation.map((section) => (
            <div key={section.title} className="mb-6">
              {sidebarOpen && (
                <h3 className="px-4 mb-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  {section.title}
                </h3>
              )}
              <div className="space-y-1 px-2">
                {section.items.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => setCurrentPage(item.id)}
                    className={cn(
                      "w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                      currentPage === item.id
                        ? "bg-primary text-primary-foreground"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    )}
                  >
                    <item.icon className="h-4 w-4 flex-shrink-0" />
                    {sidebarOpen && <span>{item.label}</span>}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer */}
        {sidebarOpen && (
          <div className="p-4 border-t text-xs text-muted-foreground">
            <a href="https://github.com/openbancor/catalogmx" target="_blank" rel="noopener" className="hover:underline">
              GitHub
            </a>
            {' · '}
            <a href="https://www.npmjs.com/package/catalogmx" target="_blank" rel="noopener" className="hover:underline">
              npm
            </a>
            {' · '}
            <a href="https://pypi.org/project/catalogmx/" target="_blank" rel="noopener" className="hover:underline">
              PyPI
            </a>
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className={cn(
        "relative flex-1 transition-all duration-300",
        sidebarOpen ? "md:ml-64" : "md:ml-16"
      )}>
        {/* Header */}
        <header className="sticky top-0 z-40 h-16 border-b border-white/20 bg-white/75 px-4 backdrop-blur-xl supports-[backdrop-filter]:bg-white/65 dark:border-white/5 dark:bg-slate-950/60">
          <div className="flex h-full items-center">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="mr-4 rounded-full border border-transparent hover:border-muted-foreground/30"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            <nav className="flex items-center gap-1 text-sm text-muted-foreground">
              <span>catalogmx</span>
              <ChevronRight className="h-4 w-4" />
              <span className="text-foreground font-medium">
                {currentNavItem?.label}
              </span>
            </nav>
            <div className="ml-auto hidden gap-2 md:flex">
              <a
                href="https://github.com/openbancor/catalogmx"
                target="_blank"
                rel="noopener noreferrer"
                className={cn(buttonVariants({ variant: 'outline', size: 'sm' }), 'rounded-full')}
              >
                GitHub
              </a>
              <a
                href="https://openbancor.github.io/catalogmx/mexico.sqlite3"
                target="_blank"
                rel="noopener noreferrer"
                className={cn(buttonVariants({ variant: 'secondary', size: 'sm' }), 'rounded-full')}
              >
                Download DB
              </a>
            </div>
          </div>
        </header>

        {/* Hero */}
        <section className="px-6 pt-6">
          <div className="grid gap-4 xl:grid-cols-[2fr,1fr]">
            <div className="relative overflow-hidden rounded-3xl border bg-gradient-to-r from-primary via-emerald-500 to-emerald-400 p-6 text-primary-foreground shadow-lg">
              <div className="absolute inset-0 opacity-30" style={{ background: 'radial-gradient(circle at top, rgba(255,255,255,0.7), transparent 60%)' }} />
              <div className="relative z-10 space-y-3">
                <p className="text-xs uppercase tracking-[0.25em] text-white/70">Serverless SQLite</p>
                <h2 className="text-2xl font-semibold leading-tight">
                  Mexico&apos;s compliance catalogs in one file
                </h2>
                <p className="text-sm text-white/80 max-w-3xl">
                  We merge every SAT, INEGI, SEPOMEX, and Banxico dataset into <code className="font-mono">mexico.sqlite3</code>.
                  Query it directly from the browser with sql.js + HTTP Range requests and keep your validators fully offline.
                </p>
                <div className="flex flex-wrap gap-3">
                  <a
                    className={cn(
                      buttonVariants({ variant: 'secondary', size: 'sm' }),
                      'rounded-full font-semibold text-primary'
                    )}
                    href="https://openbancor.github.io/catalogmx/mexico.sqlite3"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Download mexico.sqlite3
                  </a>
                  <a
                    className={cn(
                      buttonVariants({ variant: 'ghost', size: 'sm' }),
                      'rounded-full border border-white/40 text-white hover:bg-white/10'
                    )}
                    href="https://github.com/OpenBancor/catalogmx/blob/main/packages/webapp/SPEC-sqlite-vfs.MD"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Read VFS spec
                  </a>
                </div>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1">
              {heroHighlights.map((stat) => (
                <div key={stat.label} className="rounded-2xl border bg-card p-5 shadow-sm backdrop-blur-md">
                  <div className="text-3xl font-semibold">{stat.value}</div>
                  <div className="mt-2 text-sm font-medium text-muted-foreground uppercase tracking-wide">
                    {stat.label}
                  </div>
                  <div className="text-sm text-muted-foreground">{stat.detail}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Page content */}
        <div className="p-6">
          <PageComponent />
        </div>
      </main>
      </div>
    </div>
  );
}
