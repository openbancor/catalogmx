import { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Search, Database, ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react';
import { CATALOG_CATEGORIES, CATALOGS, searchInCatalog, type CatalogItem } from '@/data/catalogs';

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
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const pageSize = 10;

  const filteredData = useMemo(() => {
    if (!catalog) return [];
    if (!search) return catalog.data;
    return searchInCatalog(catalog, search);
  }, [catalog, search]);

  const paginatedData = useMemo(() => {
    const start = page * pageSize;
    return filteredData.slice(start, start + pageSize);
  }, [filteredData, page]);

  const totalPages = Math.ceil(filteredData.length / pageSize);

  if (!catalog) return null;

  const columns = Object.keys(catalog.data[0] || {});

  return (
    <Dialog open={!!catalog} onOpenChange={() => onClose()}>
      <DialogContent className="max-w-5xl max-h-[85vh] flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {catalog.name}
            <Badge variant="outline">{catalog.recordCount}</Badge>
          </DialogTitle>
          <DialogDescription className="flex items-center gap-2">
            {catalog.description}
            <span className="text-xs">•</span>
            <span className="text-xs">Source: {catalog.source}</span>
          </DialogDescription>
        </DialogHeader>

        <div className="flex items-center gap-4 py-3 border-b">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search within catalog..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(0); }}
              className="pl-10"
            />
          </div>
          <div className="text-sm text-muted-foreground">
            {filteredData.length} records
          </div>
        </div>

        <div className="flex-1 overflow-auto">
          <table className="data-table">
            <thead>
              <tr>
                {columns.map(col => (
                  <th key={col} className="capitalize">
                    {col.replace(/_/g, ' ')}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {paginatedData.map((row, i) => (
                <tr key={i}>
                  {columns.map(col => (
                    <td key={col}>
                      {typeof row[col] === 'boolean'
                        ? (row[col] ? '✓' : '✗')
                        : String(row[col] ?? '')}
                    </td>
                  ))}
                </tr>
              ))}
              {paginatedData.length === 0 && (
                <tr>
                  <td colSpan={columns.length} className="text-center py-8 text-muted-foreground">
                    No results found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between pt-4 border-t">
          <div className="text-sm text-muted-foreground">
            Showing {page * pageSize + 1}-{Math.min((page + 1) * pageSize, filteredData.length)} of {filteredData.length}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm px-2">
              Page {page + 1} of {totalPages || 1}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="pt-3 border-t text-xs text-muted-foreground">
          <ExternalLink className="h-3 w-3 inline mr-1" />
          Full catalog available in the library with {catalog.recordCount} records
        </div>
      </DialogContent>
    </Dialog>
  );
}
