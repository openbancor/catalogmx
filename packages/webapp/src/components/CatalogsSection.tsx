import { useState, useMemo } from 'react';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Database, ArrowRight, ChevronDown, ChevronUp, MapPin, FileText, Building2, Star } from 'lucide-react';
import { datasetConfigs, type DatasetConfig } from '@/data/datasets';
import { emitNavigation } from '@/lib/navigation';
import { useLocale } from '@/lib/locale';
import { cn } from '@/lib/utils';

interface CatalogsSectionProps {
  showHeader?: boolean;
}

// Featured catalogs for quick access
const FEATURED_IDS = [
  'sepomex-codigos-postales',
  'inegi-localidades', 
  'sat-productos',
  'banxico-banks',
  'inegi-estados',
  'sat-regimen'
];

const CATEGORY_META: Record<string, { icon: typeof Database, color: string, label: string }> = {
  'SEPOMEX': { icon: MapPin, color: 'text-blue-600 dark:text-blue-400', label: 'Códigos Postales' },
  'INEGI': { icon: MapPin, color: 'text-green-600 dark:text-green-400', label: 'Geografía' },
  'SAT': { icon: FileText, color: 'text-orange-600 dark:text-orange-400', label: 'Fiscal (SAT)' },
  'BANXICO': { icon: Building2, color: 'text-purple-600 dark:text-purple-400', label: 'Bancario' },
  'IFT': { icon: Database, color: 'text-pink-600 dark:text-pink-400', label: 'Telecomunicaciones' },
};

export default function CatalogsSection({ showHeader = true }: CatalogsSectionProps) {
  const { t } = useLocale();
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set(['SEPOMEX', 'SAT']));

  const featuredCatalogs = useMemo(() => {
    return FEATURED_IDS.map(id => datasetConfigs.find(c => c.id === id)).filter(Boolean) as DatasetConfig[];
  }, []);

  const filteredCatalogs = useMemo(() => {
    if (!searchQuery) return datasetConfigs;
    const q = searchQuery.toLowerCase();
    return datasetConfigs.filter(c =>
      c.label.toLowerCase().includes(q) ||
      c.table.toLowerCase().includes(q) ||
      (c.description && c.description.toLowerCase().includes(q))
    );
  }, [searchQuery]);

  const catalogsByCategory = useMemo(() => {
    const map = new Map<string, DatasetConfig[]>();
    
    filteredCatalogs.forEach(catalog => {
      const prefix = catalog.id.split('-')[0].toUpperCase();
      const category = ['SAT', 'BANXICO', 'INEGI', 'SEPOMEX', 'IFT'].includes(prefix) 
        ? prefix 
        : 'OTROS';
      
      if (!map.has(category)) map.set(category, []);
      map.get(category)?.push(catalog);
    });
    
    // Sort categories by importance
    const order = ['SEPOMEX', 'SAT', 'INEGI', 'BANXICO', 'IFT', 'OTROS'];
    return new Map([...map.entries()].sort((a, b) => 
      order.indexOf(a[0]) - order.indexOf(b[0])
    ));
  }, [filteredCatalogs]);

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => {
      const next = new Set(prev);
      if (next.has(category)) {
        next.delete(category);
      } else {
        next.add(category);
      }
      return next;
    });
  };

  return (
    <div className="space-y-6">
      {showHeader && (
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold mb-2">{t('catalogs.main.title')}</h2>
          <p className="text-muted-foreground mb-6">
            {t('catalogs.list.subtitle')}
          </p>
        </div>
      )}

      {/* Search bar */}
      <div className="relative max-w-xl mx-auto">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-muted-foreground" />
        <Input
          placeholder={t('tables.search.placeholder')}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 h-12 text-base"
        />
      </div>

      {/* Featured Catalogs - Always visible */}
      <div className="bg-gradient-to-br from-primary/5 to-emerald-500/5 border border-primary/10 rounded-2xl p-4 sm:p-6">
        <div className="flex items-center gap-2 mb-4">
          <Star className="h-5 w-5 text-primary fill-primary" />
          <h3 className="text-lg font-bold">Catálogos más usados</h3>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {featuredCatalogs.map(catalog => (
            <button
              key={catalog.id}
              onClick={() => emitNavigation(`dataset-${catalog.id}`)}
              className="flex flex-col text-left p-4 rounded-xl border-2 border-primary/20 bg-background hover:bg-primary/5 hover:border-primary/40 transition-all group shadow-sm active:scale-[0.98]"
            >
              <div className="flex items-start justify-between w-full mb-2">
                <div className="p-2 rounded-lg bg-primary/15 text-primary">
                  <Database className="h-5 w-5" />
                </div>
                <ArrowRight className="h-4 w-4 text-primary opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
              </div>
              
              <div className="font-bold text-base leading-tight mb-2">
                {catalog.label}
              </div>
              
              <div className="text-xs text-muted-foreground line-clamp-2 mb-3">
                {catalog.description || 'Catálogo oficial'}
              </div>

              <code className="text-[10px] bg-muted px-2 py-1 rounded font-mono text-muted-foreground">
                {catalog.table}
              </code>
            </button>
          ))}
        </div>
      </div>

      {/* All Catalogs by Category - Collapsible */}
      <div className="space-y-3">
        <h3 className="text-xl font-bold px-2">Todos los catálogos</h3>
        
        {Array.from(catalogsByCategory.entries()).map(([category, catalogs]) => {
          const isExpanded = expandedCategories.has(category);
          const meta = CATEGORY_META[category] || { icon: Database, color: 'text-gray-600', label: category };
          const Icon = meta.icon;
          
          return (
            <Card key={category} className="overflow-hidden">
              <button
                onClick={() => toggleCategory(category)}
                className="w-full px-4 sm:px-6 py-4 flex items-center justify-between hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Icon className={cn("h-5 w-5", meta.color)} />
                  <div className="text-left">
                    <div className="font-bold text-lg">{meta.label}</div>
                    <div className="text-xs text-muted-foreground">
                      {catalogs.length} catálogo{catalogs.length !== 1 ? 's' : ''}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Badge variant="secondary" className="hidden sm:inline-flex">
                    {catalogs.length}
                  </Badge>
                  {isExpanded ? (
                    <ChevronUp className="h-5 w-5 text-muted-foreground" />
                  ) : (
                    <ChevronDown className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>
              </button>

              {isExpanded && (
                <div className="px-4 sm:px-6 pb-4 pt-2 border-t">
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                    {catalogs.map(catalog => (
                      <button
                        key={catalog.id}
                        onClick={() => emitNavigation(`dataset-${catalog.id}`)}
                        className="flex flex-col text-left p-3 sm:p-4 rounded-lg border bg-card hover:bg-accent/50 hover:border-primary/50 transition-all group shadow-sm active:scale-[0.98]"
                      >
                        <div className="flex items-center justify-between w-full mb-2">
                          <Badge variant="outline" className="text-[10px] px-1.5 py-0.5 bg-muted/50">
                            {catalog.id.split('-')[0].toUpperCase()}
                          </Badge>
                          <ArrowRight className="h-3 w-3 text-muted-foreground opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                        </div>
                        
                        <div className="font-semibold text-sm leading-tight mb-2 group-hover:text-primary transition-colors">
                          {catalog.label}
                        </div>
                        
                        <div className="text-xs text-muted-foreground mb-3 line-clamp-2 min-h-[2.5em]">
                          {catalog.description || 'Catálogo oficial'}
                        </div>

                        <code className="text-[10px] bg-muted/70 px-1.5 py-1 rounded font-mono text-muted-foreground block truncate">
                          {catalog.table}
                        </code>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </Card>
          );
        })}

        {filteredCatalogs.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            {t('tables.empty')}
          </div>
        )}
      </div>
    </div>
  );
}
