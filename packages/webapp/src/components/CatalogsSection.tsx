import { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Search, Database } from 'lucide-react';
import { CATALOG_CATEGORIES, CATALOGS, type CatalogItem } from '@/data/catalogs';

interface CatalogsSectionProps {
  showHeader?: boolean;
}

export default function CatalogsSection({ showHeader = true }: CatalogsSectionProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCatalog, setSelectedCatalog] = useState<CatalogItem | null>(null);

  const filteredCatalogs = useMemo(() => {
    if (!searchQuery) return CATALOGS;
    const q = searchQuery.toLowerCase();
    return CATALOGS.filter(c =>
      c.name.toLowerCase().includes(q) ||
      c.description.toLowerCase().includes(q)
    );
  }, [searchQuery]);

  const catalogsByCategory = useMemo(() => {
    const map = new Map<string, CatalogItem[]>();
    CATALOG_CATEGORIES.forEach(cat => map.set(cat.id, []));
    filteredCatalogs.forEach(catalog => {
      const list = map.get(catalog.category);
      if (list) list.push(catalog);
    });
    return map;
  }, [filteredCatalogs]);

  return (
    <div className="space-y-8">
      {showHeader ? (
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold mb-2">Official Mexican Catalogs</h2>
          <p className="text-muted-foreground mb-6">
            Browse 58 official catalogs with 470,000+ records from SAT, Banxico, INEGI, and more
          </p>

          <div className="relative mx-auto max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-muted-foreground" />
            <Input
              placeholder="Search catalogs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
      ) : (
        <div className="relative max-w-xl">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-muted-foreground" />
          <Input
            placeholder="Search catalogs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      )}

      <div className="space-y-6">
        {CATALOG_CATEGORIES.map(category => {
          const catalogs = catalogsByCategory.get(category.id) || [];
          if (catalogs.length === 0) return null;

          return (
            <Card key={category.id}>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Database className="h-5 w-5 text-primary" />
                  {category.name}
                </CardTitle>
                <CardDescription>{category.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                  {catalogs.map(catalog => (
                    <button
                      key={catalog.id}
                      onClick={() => setSelectedCatalog(catalog)}
                      className="text-left p-4 rounded-lg border bg-card hover:bg-accent hover:border-primary transition-colors"
                    >
                      <div className="font-medium mb-1">{catalog.name}</div>
                      <div className="text-sm text-muted-foreground mb-2">{catalog.description}</div>
                      <Badge variant="secondary" className="text-xs">{catalog.recordCount}</Badge>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <CatalogDialog
        catalog={selectedCatalog}
        onClose={() => setSelectedCatalog(null)}
      />
    </div>
  );
}

function CatalogDialog({ catalog, onClose }: { catalog: CatalogItem | null; onClose: () => void }) {
  if (!catalog) return null;

  const info = [
    { label: 'Registros', value: catalog.recordCount },
    { label: 'Fuente', value: catalog.source },
    { label: 'ID', value: catalog.id },
  ];

  return (
    <Dialog open={!!catalog} onOpenChange={() => onClose()}>
      <DialogContent className="max-w-3xl space-y-4">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {catalog.name}
            <Badge variant="outline">{catalog.recordCount}</Badge>
          </DialogTitle>
          <DialogDescription>{catalog.description}</DialogDescription>
        </DialogHeader>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {info.map((item) => (
            <div key={item.label} className="rounded-lg border bg-muted/40 px-3 py-2">
              <div className="text-xs uppercase tracking-wide text-muted-foreground">{item.label}</div>
              <div className="text-sm font-medium">{item.value}</div>
            </div>
          ))}
        </div>

        <div className="rounded-lg border bg-muted/40 px-3 py-3 text-sm text-muted-foreground">
          No mostramos muestras aquí. Usa “Explorar cualquier tabla” o “Explorar catálogos (sqlite)” en la página principal para consultar el catálogo completo con paginación y búsqueda sin acentos.
        </div>
      </DialogContent>
    </Dialog>
  );
}
