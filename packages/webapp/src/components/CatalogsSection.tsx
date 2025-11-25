import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Database, ArrowRight } from 'lucide-react';
import { datasetConfigs, type DatasetConfig } from '@/data/datasets';
import { emitNavigation } from '@/lib/navigation';
import { useLocale } from '@/lib/locale';

interface CatalogsSectionProps {
  showHeader?: boolean;
}

export default function CatalogsSection({ showHeader = true }: CatalogsSectionProps) {
  const { t } = useLocale();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCatalogs = useMemo(() => {
    if (!searchQuery) return datasetConfigs;
    const q = searchQuery.toLowerCase();
    return datasetConfigs.filter(c =>
      c.label.toLowerCase().includes(q) ||
      c.table.toLowerCase().includes(q) ||
      (c.description && c.description.toLowerCase().includes(q))
    );
  }, [searchQuery]);

  // Group by prefix (e.g. "sat", "banxico", "inegi")
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
    
    // Sort categories
    return new Map([...map.entries()].sort());
  }, [filteredCatalogs]);

  return (
    <div className="space-y-8">
      {showHeader && (
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold mb-2">{t('catalogs.main.title')}</h2>
          <p className="text-muted-foreground mb-6">
            {t('catalogs.list.subtitle')}
          </p>
        </div>
      )}

      <div className="relative max-w-xl mx-auto mb-8">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-muted-foreground" />
        <Input
          placeholder={t('tables.search.placeholder')}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      <div className="space-y-8">
        {Array.from(catalogsByCategory.entries()).map(([category, catalogs]) => (
          <div key={category}>
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Badge variant="outline" className="text-base py-1 px-3 bg-muted/50">
                {category}
              </Badge>
              <span className="text-sm text-muted-foreground font-normal">
                {catalogs.length} catálogos
              </span>
            </h3>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {catalogs.map(catalog => (
                <button
                  key={catalog.id}
                  onClick={() => emitNavigation(`dataset-${catalog.id}`)}
                  className="flex flex-col text-left h-full p-4 rounded-xl border bg-card hover:bg-accent/50 hover:border-primary/50 transition-all group shadow-sm hover:shadow-md"
                >
                  <div className="flex items-start justify-between w-full mb-2">
                    <div className="p-2 rounded-lg bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                      <Database className="h-4 w-4" />
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
                  </div>
                  
                  <div className="font-semibold leading-tight mb-1 group-hover:text-primary transition-colors">
                    {catalog.label}
                  </div>
                  
                  <div className="text-xs text-muted-foreground mb-3 line-clamp-2 min-h-[2.5em]">
                    {catalog.description || 'Catálogo oficial'}
                  </div>

                  <div className="mt-auto pt-3 border-t border-border/50 w-full flex items-center justify-between text-xs text-muted-foreground">
                    <code className="bg-muted px-1.5 py-0.5 rounded font-mono text-[10px]">
                      {catalog.table}
                    </code>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ))}

        {filteredCatalogs.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            {t('tables.empty')}
          </div>
        )}
      </div>
    </div>
  );
}
