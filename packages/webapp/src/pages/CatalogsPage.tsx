import { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { AlertTriangle, CheckCircle2, Database, Loader2, MapPin, Package, Building2, Search, ChevronLeft, ChevronRight } from 'lucide-react';
import CatalogsSection from '@/components/CatalogsSection';
import { emitNavigation } from '@/lib/navigation';
import { queryDatabase, queryJsonArrayTable, querySqlTable, listTables, getTableInfo, queryTable, getTableCount } from '@/lib/database';
import { datasetConfigs, type DatasetConfig } from '@/data/datasets';

const formatBytes = (bytes: number): string => {
  if (!bytes) return '-';
  const units = ['B', 'KB', 'MB', 'GB'];
  const idx = Math.min(units.length - 1, Math.floor(Math.log(bytes) / Math.log(1024)));
  const value = bytes / 1024 ** idx;
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[idx]}`;
};

const formatDate = (value?: string | null): string => {
  if (!value) return '-';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '-';
  return d.toLocaleDateString('es-MX', { year: 'numeric', month: 'short', day: 'numeric' });
};

const sqliteCatalogs = [
  {
    id: 'postal-codes',
    title: 'Postal Codes (SEPOMEX)',
    icon: MapPin,
    description: '157k settlements with type, zone, and municipality metadata.',
    table: 'codigos_postales'
  },
  {
    id: 'localidades',
    title: 'Localities (INEGI)',
    icon: Building2,
    description: '300k+ populated places with geospatial coordinates.',
    table: 'localidades'
  },
  {
    id: 'productos',
    title: 'Products & Services (SAT)',
    icon: Package,
    description: '52k CFDI 4.0 product/service concepts with synonyms.',
    table: 'clave_prod_serv'
  }
];

const datasetOptions: DatasetConfig[] = datasetConfigs;

export default function CatalogsPage() {
  const [fileMeta, setFileMeta] = useState<{ size?: number; modified?: string }>({});
  const [tableCounts, setTableCounts] = useState<Record<string, number>>({});
  const [tableNames, setTableNames] = useState<string[]>([]);
  const [countError, setCountError] = useState<string | null>(null);
  const [countsLoading, setCountsLoading] = useState(false);
  const [tableFilter, setTableFilter] = useState('');
  const [showAllCatalogs, setShowAllCatalogs] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${import.meta.env.BASE_URL}data/mexico.sqlite3`, { method: 'HEAD', signal: controller.signal })
      .then((res) => {
        const size = Number(res.headers.get('content-length') || undefined);
        const modified = res.headers.get('last-modified') || undefined;
        setFileMeta({ size: Number.isFinite(size) ? size : undefined, modified });
      })
      .catch(() => {
        // ignore network/head failures
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    let cancelled = false;
    setCountsLoading(true);
    setCountError(null);
    (async () => {
      try {
        const tables = await listTables('mexico');
        setTableNames(tables);
        const entries = await Promise.all(
          tables.map(async (table) => {
            const total = await getTableCount('mexico', table);
            return [table, total] as const;
          })
        );
        if (!cancelled) {
          setTableCounts(Object.fromEntries(entries));
        }
      } catch (error) {
        console.error('[catalogs] failed to load table counts', error);
        if (!cancelled) {
          setCountError('No se pudieron leer los conteos desde mexico.sqlite3.');
        }
      } finally {
        if (!cancelled) {
          setCountsLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const totalRows = useMemo(
    () => Object.values(tableCounts).reduce((sum, value) => sum + (value ?? 0), 0),
    [tableCounts]
  );

  const heroStats = useMemo(
    () => [
      {
        label: 'Tablas en mexico.sqlite3',
        value: Object.keys(tableCounts).length ? Object.keys(tableCounts).length.toLocaleString('es-MX') : countsLoading ? '…' : '—',
        detail: 'Incluye Banxico · SAT · INEGI · SEPOMEX'
      },
      {
        label: 'Filas totales',
        value: totalRows ? totalRows.toLocaleString('es-MX') : countsLoading ? '…' : '—',
        detail: 'Suma de todas las tablas'
      },
      {
        label: 'Última modificación',
        value: formatDate(fileMeta.modified),
        detail: 'Cabecera HTTP Last-Modified'
      }
    ],
    [countsLoading, fileMeta.modified, tableCounts, totalRows]
  );

  const formatRecordCount = (table: string) => {
    const value = tableCounts[table];
    if (countsLoading && value === undefined) return '…';
    if (typeof value !== 'number') return '—';
    return value.toLocaleString('es-MX');
  };

  const filteredTables = useMemo(() => {
    const q = tableFilter.trim().toLowerCase();
    return tableNames
      .filter((name) => (q ? name.toLowerCase().includes(q) : true))
      .sort((a, b) => a.localeCompare(b));
  }, [tableFilter, tableNames]);

  return (
    <div className="space-y-8">
      <section className="grid gap-4 lg:grid-cols-[2fr,1fr]">
        <Card className="border-none bg-gradient-to-r from-primary to-emerald-500 text-primary-foreground shadow-lg">
          <CardHeader>
            <CardTitle className="text-2xl">mexico.sqlite3</CardTitle>
            <CardDescription className="text-primary-foreground/80">
              Serverless SQLite build that merges every catalog into a single file ready for HTTP range queries.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <p>
              Drop <code className="font-mono">mexico.sqlite3</code> in <code className="font-mono">/public/data</code> and the demo loads it locally with sql.js.
              No server, no API keys—just deterministic compliance data.
            </p>
            <div className="flex flex-wrap gap-3">
              <a
                href={`${import.meta.env.BASE_URL}data/mexico.sqlite3`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-full bg-white/90 px-4 py-2 text-sm font-semibold text-primary shadow hover:bg-white"
              >
                Download database
              </a>
              <a
                href="https://github.com/OpenBancor/catalogmx/blob/main/packages/webapp/SPEC-sqlite-vfs.MD"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-full border border-white/60 px-4 py-2 text-sm font-semibold text-white/90 hover:bg-white/10"
              >
                Read VFS spec
              </a>
            </div>
            <div className="flex flex-wrap gap-3 text-xs text-primary-foreground/80">
              <span className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1">
                Size: {fileMeta.size ? formatBytes(fileMeta.size) : '—'}
              </span>
              <span className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1">
                Last modified: {formatDate(fileMeta.modified)}
              </span>
            </div>
          </CardContent>
        </Card>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
          {heroStats.map((stat) => (
            <Card key={stat.label}>
              <CardContent className="py-6">
                <div className="text-3xl font-semibold">{stat.value}</div>
                <div className="mt-2 text-sm font-medium text-muted-foreground uppercase tracking-wide">
                  {stat.label}
                </div>
                <div className="text-sm text-muted-foreground">{stat.detail}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5 text-primary" />
            Tablas SQLite
          </CardTitle>
          <CardDescription>Busca y navega cualquier tabla de mexico.sqlite3</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-muted-foreground" />
            <Input
              value={tableFilter}
              onChange={(e) => setTableFilter(e.target.value)}
              placeholder="Buscar tabla (ej. sat_cfdi_4_0_c_formapago)…"
              className="pl-10"
            />
          </div>
          {countError ? (
            <div className="flex items-center gap-2 text-sm text-red-600">
              <AlertTriangle className="h-4 w-4" />
              {countError}
            </div>
          ) : (
            <div className="max-h-72 overflow-auto rounded-lg border divide-y">
              {countsLoading && !filteredTables.length ? (
                <div className="flex items-center gap-2 p-3 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Cargando tablas…
                </div>
              ) : (
                filteredTables.map((table) => (
                  <div key={table} className="flex items-center justify-between px-3 py-2 text-sm">
                    <div className="font-mono">{table}</div>
                    <Badge variant="secondary">{formatRecordCount(table)}</Badge>
                  </div>
                ))
              )}
              {!countsLoading && filteredTables.length === 0 ? (
                <div className="p-3 text-sm text-muted-foreground">Sin resultados</div>
              ) : null}
            </div>
          )}
        </CardContent>
      </Card>

      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <Database className="h-5 w-5 text-primary" />
          <h2 className="text-xl font-semibold">Catálogos principales</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {sqliteCatalogs.map((catalog) => (
            <Card key={catalog.id} className="flex flex-col">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-lg">
                  <catalog.icon className="h-5 w-5 text-primary" />
                  {catalog.title}
                </CardTitle>
                <CardDescription>{catalog.description}</CardDescription>
              </CardHeader>
              <CardContent className="mt-auto space-y-3 text-sm">
                <div className="flex items-center justify-between rounded-lg border px-3 py-2">
                  <div>
                    <div className="font-medium text-foreground">Table</div>
                    <div className="font-mono text-xs">{catalog.table}</div>
                  </div>
                  <Badge variant="secondary">{formatRecordCount(catalog.table)}</Badge>
                </div>
                {countError ? (
                  <p className="text-xs text-red-500">{countError}</p>
                ) : null}
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => emitNavigation(catalog.id)}
                >
                  Open explorer
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      <ConsolidatedDatabaseCard />
      <AllTablesExplorer />
      <DatasetExplorer />

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Catálogos completos</h2>
            <p className="text-sm text-muted-foreground">Búsqueda simple por nombre/descr. de los 58 catálogos.</p>
          </div>
          <Button variant="outline" size="sm" onClick={() => setShowAllCatalogs((v) => !v)}>
            {showAllCatalogs ? 'Ocultar listado' : 'Ver listado'}
          </Button>
        </div>
        {showAllCatalogs ? <CatalogsSection showHeader={false} /> : null}
      </section>
    </div>
  );
}

function DatasetExplorer() {
  const [dataset, setDataset] = useState<DatasetConfig>(datasetOptions[0]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rows, setRows] = useState<unknown[]>([]);
  const [total, setTotal] = useState(0);

  const groupedOptions = useMemo(() => {
    return [
      { label: 'Banxico', items: datasetOptions.filter((d) => d.id.startsWith('banxico')) },
      { label: 'IFT', items: datasetOptions.filter((d) => d.id.startsWith('ift')) },
      { label: 'SAT', items: datasetOptions.filter((d) => d.id.startsWith('sat')) },
    ];
  }, []);

  const load = async (targetPage = 1) => {
    setLoading(true);
    setError(null);
    try {
      const result =
        dataset.type === 'sql'
          ? await querySqlTable('mexico', dataset.table, {
              page: targetPage,
              pageSize,
              search,
              searchColumns: dataset.searchColumns,
              orderBy: dataset.orderBy,
            })
          : await queryJsonArrayTable('mexico', dataset.table, dataset.column ?? 'data', {
              page: targetPage,
              pageSize,
              search,
              searchColumns: dataset.searchColumns,
            });
      setRows(result.data);
      setTotal(result.total);
      setPage(result.page);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading dataset');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(1);
  }, [dataset, pageSize]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Explorar catálogos (sqlite)</h2>
          <p className="text-sm text-muted-foreground">Banxico, IFT, SAT en una sola base. Sin muestras: paginación completa.</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <div className="relative">
            <select
              className="h-10 rounded-md border bg-background px-3 text-sm"
              value={dataset.id}
              onChange={(e) => {
                const next = datasetOptions.find((d) => d.id === e.target.value);
                if (next) {
                  setDataset(next);
                  setPage(1);
                  setSearch('');
                }
              }}
            >
              {groupedOptions.map((group) => (
                <optgroup key={group.label} label={group.label}>
                  {group.items.map((opt) => (
                    <option key={opt.id} value={opt.id}>
                      {opt.label}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-muted-foreground" />
            <Input
              className="pl-10"
              placeholder="Buscar..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && load(1)}
            />
          </div>
          <Button onClick={() => load(1)} disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Buscar'}
          </Button>
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
        </div>
      </div>

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
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    {dataset.columns.map((col) => (
                      <th key={col.key} className="p-3 text-left font-medium">
                        {col.label}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {rows.map((row, idx) => {
                    const record = row as Record<string, unknown>;
                    return (
                      <tr key={idx} className="hover:bg-muted/50">
                        {dataset.columns.map((col) => {
                          const value = record[col.key];
                          const rendered = typeof value === 'boolean'
                            ? value ? 'Sí' : 'No'
                            : value === null || value === undefined
                              ? '-'
                              : typeof value === 'object'
                                ? JSON.stringify(value)
                                : value;
                          return (
                            <td key={col.key} className="p-3">
                              {rendered as React.ReactNode}
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                  {rows.length === 0 && (
                    <tr>
                      <td colSpan={dataset.columns.length} className="p-4 text-center text-muted-foreground">
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
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => load(page + 1)}
                  disabled={page >= totalPages || loading}
                >
                  Siguiente
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </section>
  );
}

type AnyRow = Record<string, unknown>;

function AllTablesExplorer() {
  const [tables, setTables] = useState<string[]>([]);
  const [selected, setSelected] = useState<string>('');
  const [columns, setColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<AnyRow[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(100);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listTables('mexico').then((names) => {
      setTables(names);
      if (names.length > 0) setSelected(names[0]);
    });
  }, []);

  useEffect(() => {
    if (!selected) return;
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const info = await getTableInfo('mexico', selected);
        setColumns(info.map((c) => c.name));
        const textCols = info.filter((c) => (c.type || '').toUpperCase().includes('TEXT')).map((c) => c.name);
        const result = await queryTable('mexico', selected, {
          page,
          pageSize,
          search,
          searchColumns: textCols,
        });
        setRows(result.data);
        setTotal(result.total);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error al consultar la tabla');
      } finally {
        setLoading(false);
      }
    })();
  }, [selected, page, search, pageSize]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <section className="space-y-4">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Explorar cualquier tabla</h2>
          <p className="text-sm text-muted-foreground">Búsqueda sin acentos; todas las columnas visibles. Sin muestras.</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <select
            className="h-10 rounded-md border bg-background px-3 text-sm"
            value={selected}
            onChange={(e) => {
              setSelected(e.target.value);
              setPage(1);
              setSearch('');
            }}
          >
            {tables.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-muted-foreground" />
            <Input
              className="pl-10"
              placeholder="Buscar en columnas de texto (sin acentos)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && setPage(1)}
            />
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
              }}
            >
              {[25, 50, 100, 250, 500].map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

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
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted">
                  <tr>
                    {columns.map((col) => (
                      <th key={col} className="p-3 text-left font-medium">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {rows.map((row, idx) => {
                    const record = row as Record<string, unknown>;
                    return (
                      <tr key={idx} className="hover:bg-muted/50">
                        {columns.map((col) => {
                          const value = record[col];
                          let rendered: React.ReactNode = value as React.ReactNode;
                          if (value === null || value === undefined) {
                            rendered = '-';
                          } else if (typeof value === 'boolean') {
                            rendered = value ? 'Sí' : 'No';
                          } else if (typeof value === 'object') {
                            rendered = JSON.stringify(value);
                          }
                          return (
                            <td key={col} className="p-3 align-top">
                              {rendered}
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                  {rows.length === 0 && (
                    <tr>
                      <td colSpan={columns.length} className="p-4 text-center text-muted-foreground">
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
                <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1 || loading}>
                  <ChevronLeft className="h-4 w-4" />
                  Anterior
                </Button>
                <span>
                  Página {page} de {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages || loading}
                >
                  Siguiente
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </section>
  );
}

function ConsolidatedDatabaseCard() {
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [tables, setTables] = useState<{ name: string; type: string; rows?: number }[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [totalTables, setTotalTables] = useState<number>(0);

  useEffect(() => {
    let cancelled = false;

    async function hydrate() {
      setStatus('loading');
      setError(null);
      try {
        const master = await queryDatabase('mexico.sqlite3', "SELECT name, type FROM sqlite_master WHERE type='table' ORDER BY name");
        if (cancelled) return;
        setTotalTables(master.values.length);

        const sample = master.values.slice(0, 8).map((row) => ({
          name: row[0] as string,
          type: row[1] as string
        }));

        const withCounts = await Promise.all(
          sample.map(async (table) => {
            const safeName = /^[A-Za-z0-9_]+$/.test(table.name) ? table.name : null;
            if (!safeName) {
              return table;
            }
            try {
              const result = await queryDatabase('mexico.sqlite3', `SELECT COUNT(*) as records FROM ${safeName}`);
              const rows = Number(result.values[0]?.[0] ?? 0);
              return { ...table, rows };
            } catch {
              return table;
            }
          })
        );

        if (cancelled) return;
        setTables(withCounts);
        setStatus('ready');
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Unable to read mexico.sqlite3');
        setStatus('error');
      }
    }

    hydrate();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-5 w-5 text-primary" />
          Consolidated database status
        </CardTitle>
        <CardDescription>
          We inspect <code className="font-mono">mexico.sqlite3</code> directly in your browser to verify tables and record counts.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {status === 'loading' && (
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Connecting to mexico.sqlite3...
          </div>
        )}

        {status === 'error' && (
          <div className="flex items-center gap-3 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            <div className="text-sm">
              <div className="font-medium">Database error</div>
              <p>{error}</p>
              <p className="text-xs text-muted-foreground mt-1">
                Place <code className="font-mono">mexico.sqlite3</code> in <code className="font-mono">public/data/</code> and reload.
              </p>
            </div>
          </div>
        )}

        {status === 'ready' && (
          <>
            <div className="flex items-center gap-2 text-sm text-emerald-600 dark:text-emerald-300">
              <CheckCircle2 className="h-4 w-4" />
              {totalTables} tables detected
            </div>
            <div className="overflow-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead className="bg-muted/60">
                  <tr>
                    <th className="px-3 py-2 text-left font-medium">Table</th>
                    <th className="px-3 py-2 text-left font-medium">Type</th>
                    <th className="px-3 py-2 text-left font-medium">Rows</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {tables.map((table) => (
                    <tr key={table.name} className="hover:bg-muted/40">
                      <td className="px-3 py-2 font-mono text-xs">{table.name}</td>
                      <td className="px-3 py-2 capitalize text-muted-foreground">{table.type}</td>
                      <td className="px-3 py-2 font-semibold">{table.rows?.toLocaleString() ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
