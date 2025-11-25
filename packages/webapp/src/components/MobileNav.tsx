import { Calculator, CheckCircle2, Home, Code } from 'lucide-react';
import { cn } from '@/lib/utils';
import { type PageId } from '@/lib/routes';

interface MobileNavProps {
  currentPage: PageId;
  onNavigate: (id: PageId) => void;
}

export default function MobileNav({ currentPage, onNavigate }: MobileNavProps) {
  const tabs = [
    {
      id: 'home' as PageId,
      label: 'Inicio',
      icon: Home,
      isActive: (p: PageId) => ['home', 'catalogs', 'catalog-list'].includes(p) || p.startsWith('dataset-')
    },
    {
      id: 'validators' as PageId,
      label: 'Validar',
      icon: CheckCircle2,
      isActive: (p: PageId) => ['validators', 'rfc', 'curp', 'clabe', 'nss'].includes(p)
    },
    {
      id: 'calculators' as PageId,
      label: 'Calcular',
      icon: Calculator,
      isActive: (p: PageId) => ['calculators', 'isr', 'iva', 'ieps'].includes(p)
    },
    {
      id: 'reference' as PageId,
      label: 'Docs',
      icon: Code,
      isActive: (p: PageId) => ['reference'].includes(p)
    },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 flex h-16 items-center justify-around border-t border-border bg-background/95 backdrop-blur px-1 shadow-[0_-1px_3px_rgba(0,0,0,0.05)] md:hidden">
      {tabs.map((tab) => {
        const active = tab.isActive(currentPage);
        return (
          <button
            key={tab.label}
            onClick={() => onNavigate(tab.id)}
            className={cn(
              "flex flex-1 flex-col items-center justify-center gap-1 rounded-lg py-1 transition-colors active:scale-95",
              active ? "text-primary font-semibold" : "text-muted-foreground hover:text-foreground"
            )}
          >
            <tab.icon className={cn("h-5 w-5", active && "stroke-[2.5px]")} />
            <span className="text-[10px] tracking-tight">{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
