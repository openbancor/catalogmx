import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Loader2, Search, ChevronLeft, ChevronRight, Database, X, Download, ExternalLink, Info } from 'lucide-react';
import { datasetConfigs, type DatasetId, type DatasetConfig } from '@/data/datasets';
import { queryJsonArrayTable, querySqlTable, type FieldFilter } from '@/lib/database';
import AdvancedFilters from '@/components/AdvancedFilters';

type AnyRow = Record<string, unknown>;

interface DatasetPageProps {
  datasetId: DatasetId;
}

const renderValue = (value: unknown): React.ReactNode => {
  if (typeof value === 'boolean') {
    return value ? 'Sí' : 'No';
  }
  if (value === null || value === undefined) {
    return '-';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return value as React.ReactNode;
};

// CSV Export function
const exportToCSV = (rows: AnyRow[], config: DatasetConfig) => {
  if (rows.length === 0) return;

  // Get column headers
  const headers = config.columns.map(c => c.label);
  const keys = config.columns.map(c => c.key);

  // Build CSV content
  const csvContent = [
    headers.join(','),
    ...rows.map(row =>
      keys.map(key => {
        const value = row[key];
        const stringValue = value === null || value === undefined ? '' : String(value);
        // Escape quotes and wrap in quotes if contains comma, quote, or newline
        return /[",\n]/.test(stringValue)
          ? `"${stringValue.replace(/"/g, '""')}"`
          : stringValue;
      }).join(',')
    )
  ].join('\n');

  // Create download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${config.id}-${new Date().toISOString().split('T')[0]}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
};

export default function DatasetPage({ datasetId }: DatasetPageProps) {
  const config = datasetConfigs.find((d) => d.id === datasetId) as DatasetConfig | undefined;
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // Get search from URL, but clear it when datasetId changes
  const [search, setSearch] = useState(searchParams.get('q') || '');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(100);
  const [rows, setRows] = useState<AnyRow[]>([]);
  const [total, setTotal] = useState(0);
  const [totalUnfiltered, setTotalUnfiltered] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldFilters, setFieldFilters] = useState<FieldFilter[]>([]);

  // Clear search and field filters when dataset changes
  useEffect(() => {
    setSearch('');
    setSearchParams({});
    setFieldFilters([]);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [datasetId]);

  if (!config) {
    return (
      <div className="p-6">
        <Card>
          <CardContent className="flex items-center gap-2 py-4 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            <span>Catálogo no encontrado.</span>
          </CardContent>
        </Card>
      </div>
    );
  }

  const load = async (targetPage = 1) => {
    setLoading(true);
    setError(null);
    try {
      const result =
        config.type === 'sql'
          ? await querySqlTable('mexico', config.table, {
              page: targetPage,
              pageSize,
              search,
              searchColumns: config.searchColumns,
              orderBy: config.orderBy,
              fieldFilters,
            })
          : await queryJsonArrayTable('mexico', config.table, config.column ?? 'data', {
              page: targetPage,
              pageSize,
              search,
              searchColumns: config.searchColumns,
              fieldFilters,
            });
      setRows(result.data as AnyRow[]);
      setTotal(result.total);
      setPage(result.page);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar el catálogo');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [datasetId, pageSize]);

  // Load total count without filters on mount
  useEffect(() => {
    const loadTotal = async () => {
      try {
        const result = config.type === 'sql'
          ? await querySqlTable('mexico', config.table, { page: 1, pageSize: 1 })
          : await queryJsonArrayTable('mexico', config.table, config.column ?? 'data', { page: 1, pageSize: 1 });
        setTotalUnfiltered(result.total);
      } catch {
        // Ignore errors
      }
    };
    loadTotal();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [datasetId]);

  const handleFieldFilters = (filters: FieldFilter[]) => {
    setFieldFilters(filters);
    load(1);
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <div className="flex items-start gap-3 mb-3">
          <div className="p-2 rounded-lg bg-primary/15 text-primary">
            <Database className="h-6 w-6" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 flex-wrap mb-2">
              <h1 className="text-2xl font-bold">{config.label}</h1>
              {config.source && (
                <Badge variant="secondary" className="font-mono text-xs">
                  {config.source}
                </Badge>
              )}
              {config.subcategory && (
                <Badge variant="outline" className="text-xs">
                  {config.subcategory === 'cfdi' ? 'CFDI 4.0' :
                   config.subcategory === 'carta-porte' ? 'Carta Porte' :
                   config.subcategory === 'comercio-exterior' ? 'Comercio Ext.' :
                   config.subcategory === 'nomina' ? 'Nómina' :
                   config.subcategory}
                </Badge>
              )}
            </div>
            <p className="text-muted-foreground text-sm">
              {config.description || 'Catálogo completo en mexico.sqlite3.'}
            </p>
            {config.helpText && (
              <div className="mt-2 p-3 rounded-md bg-muted/50 border border-muted-foreground/20">
                <div className="flex items-start gap-2">
                  <Info className="h-4 w-4 text-muted-foreground mt-0.5 flex-shrink-0" />
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {config.helpText}
                  </p>
                </div>
              </div>
            )}
            <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground flex-wrap">
              <span>
                Tabla: <code className="font-mono bg-muted px-1.5 py-0.5 rounded">{config.table}</code>
              </span>
              {totalUnfiltered > 0 && (
                <span className="font-medium text-foreground">
                  {totalUnfiltered.toLocaleString()} registros
                </span>
              )}
            </div>
            {config.relatedCatalogs && config.relatedCatalogs.length > 0 && (
              <div className="mt-3 flex items-center gap-2 flex-wrap">
                <span className="text-xs text-muted-foreground">Ver también:</span>
                {config.relatedCatalogs.map(relatedId => {
                  const related = datasetConfigs.find(d => d.id === relatedId);
                  return related ? (
                    <button
                      key={relatedId}
                      onClick={() => navigate(`/catalogs/${relatedId}`)}
                      className="text-xs bg-muted hover:bg-muted/70 px-2 py-1 rounded flex items-center gap-1 transition-colors"
                    >
                      {related.label}
                      <ExternalLink className="h-3 w-3" />
                    </button>
                  ) : null;
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-muted-foreground" />
              <Input
                placeholder="Buscar (sin acentos)..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    setSearchParams(search ? { q: search } : {});
                    load(1);
                  }
                }}
                className="pl-10 pr-10"
              />
              {search && (
                <button
                  onClick={() => {
                    setSearch('');
                    setSearchParams({});
                    load(1);
                  }}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>
            <div className="flex items-center gap-2">
              <label className="text-xs text-muted-foreground">Filas/página</label>
              <select
                className="h-10 rounded-md border bg-background px-3 text-sm"
                value={pageSize}
                onChange={(e) => {
                  const next = Number(e.target.value) || 50;
                  setPageSize(next);
                  setPage(1);
                  load(1);
                }}
              >
                {[25, 50, 100, 250, 500].map((size) => (
                  <option key={size} value={size}>
                    {size}
                  </option>
                ))}
              </select>
            </div>
            <Button onClick={() => {
              setSearchParams(search ? { q: search } : {});
              load(1);
            }} disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Buscar'}
            </Button>
            <Button
              variant="outline"
              onClick={() => exportToCSV(rows, config)}
              disabled={rows.length === 0 || loading}
              className="flex items-center gap-2"
            >
              <Download className="h-4 w-4" />
              <span className="hidden sm:inline">CSV</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      <AdvancedFilters
        columns={config.columns}
        searchColumns={config.searchColumns}
        onFilter={handleFieldFilters}
        disabled={loading}
      />

      {error && (
        <Card className="border-destructive">
          <CardContent className="flex items-center gap-3 py-4 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            <div>
              <div className="font-medium">Error</div>
              <div className="text-sm">{error}</div>
            </div>
          </CardContent>
        </Card>
      )}

      {!error && (
        <>
          {/* Mobile Card View */}
          <div className="md:hidden space-y-4">
            {rows.map((row, idx) => (
              <Card key={idx} className="overflow-hidden">
                <CardContent className="p-0">
                  <div className="divide-y">
                    {config.columns.map((col) => (
                      <div key={col.key} className="flex flex-col p-3">
                        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-1">
                          {col.label}
                        </span>
                        <span className="text-sm break-words">
                          {renderValue(row[col.key])}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
            {rows.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                {loading ? 'Cargando...' : 'Sin resultados'}
              </div>
            )}
            
            {/* Mobile Pagination */}
            <div className="flex flex-col items-center gap-3 py-4 text-sm text-muted-foreground">
              <span>
                {rows.length ? (page - 1) * pageSize + 1 : 0}-{Math.min(page * pageSize, total)} de {total.toLocaleString()}
              </span>
              <div className="flex items-center gap-2 w-full justify-center">
                <Button variant="outline" size="sm" onClick={() => load(page - 1)} disabled={page <= 1 || loading} className="flex-1">
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Anterior
                </Button>
                <span className="mx-2">
                   {page}/{totalPages}
                </span>
                <Button variant="outline" size="sm" onClick={() => load(page + 1)} disabled={page >= totalPages || loading} className="flex-1">
                  Siguiente
                  <ChevronRight className="h-4 w-4 ml-1" />
                </Button>
              </div>
            </div>
          </div>

          {/* Desktop Table View */}
          <Card className="hidden md:block">
        <CardContent className="p-0 overflow-x-auto">
          <div className="min-w-full">
            <table className="w-full min-w-[720px] text-sm table-auto">
              <thead className="bg-muted">
                <tr>
                  {config.columns.map((col) => (
                    <th key={col.key} className="p-3 text-left font-medium whitespace-nowrap">
                      {col.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y">
                {rows.map((row, idx) => (
                  <tr key={idx} className="hover:bg-muted/50">
                        {config.columns.map((col) => (
                        <td key={col.key} className="p-3 align-top break-words">
                            {renderValue(row[col.key])}
                        </td>
                        ))}
                  </tr>
                ))}
                  {rows.length === 0 && (
                    <tr>
                      <td colSpan={config.columns.length} className="p-4 text-center text-muted-foreground">
                        {loading ? 'Cargando...' : 'Sin resultados'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div className="flex items-center justify-between px-4 py-3 text-sm text-muted-foreground">
              <span>
                Mostrando {rows.length ? (page - 1) * pageSize + 1 : 0}-{Math.min(page * pageSize, total)} de {total.toLocaleString()}
              </span>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => load(page - 1)} disabled={page <= 1 || loading}>
                  <ChevronLeft className="h-4 w-4" />
                  Anterior
                </Button>
                <span>
                  Página {page} de {totalPages}
                </span>
                <Button variant="outline" size="sm" onClick={() => load(page + 1)} disabled={page >= totalPages || loading}>
                  Siguiente
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
        </>
      )}
    </div>
  );
}
