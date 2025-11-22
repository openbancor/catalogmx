import { useState } from 'react';
import { cn } from '@/lib/utils';
import {
  Database, Code, Menu, X,
  CreditCard, User, Building2, Shield, MapPin, Package,
  Receipt, Percent, DollarSign, ChevronRight
} from 'lucide-react';
import { Button } from '@/components/ui/button';

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

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('rfc');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const PageComponent = pageComponents[currentPage];

  return (
    <div className="min-h-screen bg-background flex">
      {/* Sidebar */}
      <aside className={cn(
        "fixed inset-y-0 left-0 z-50 flex flex-col bg-card border-r transition-all duration-300",
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
        "flex-1 transition-all duration-300",
        sidebarOpen ? "md:ml-64" : "md:ml-16"
      )}>
        {/* Header */}
        <header className="h-14 border-b bg-card flex items-center px-4 sticky top-0 z-40">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="mr-4"
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <nav className="flex items-center gap-1 text-sm text-muted-foreground">
            <span>catalogmx</span>
            <ChevronRight className="h-4 w-4" />
            <span className="text-foreground font-medium">
              {navigation.flatMap(s => s.items).find(i => i.id === currentPage)?.label}
            </span>
          </nav>
        </header>

        {/* Page content */}
        <div className="p-6">
          <PageComponent />
        </div>
      </main>
    </div>
  );
}
