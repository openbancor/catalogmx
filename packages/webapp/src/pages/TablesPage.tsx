import { useEffect, useMemo, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { AlertTriangle, Database, Loader2, Search } from 'lucide-react';
import { getTableCount, listTables } from '@/lib/database';
import { useLocale } from '@/lib/locale';

export default function TablesPage() {
  const { t } = useLocale();
  const [tableCounts, setTableCounts] = useState<Record<string, number>>({});
  const [tableNames, setTableNames] = useState<string[]>([]);
  const [tableFilter, setTableFilter] = useState('');
  const [countError, setCountError] = useState<string | null>(null);
  const [countsLoading, setCountsLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setCountsLoading(true);
    setCountError(null);
    (async () => {
      try {
        const tables = await listTables('mexico');
        const entries = await Promise.all(
          tables.map(async (table) => {
            const total = await getTableCount('mexico', table);
            return [table, total] as const;
          })
        );
        if (!cancelled) {
          setTableNames(tables);
          setTableCounts(Object.fromEntries(entries));
        }
      } catch (error) {
        console.error('[tables] failed to load counts', error);
        if (!cancelled) setCountError('No se pudieron leer las tablas desde mexico.sqlite3.');
      } finally {
        if (!cancelled) setCountsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredTables = useMemo(() => {
    const q = tableFilter.trim().toLowerCase();
    return tableNames
      .filter((name) => (q ? name.toLowerCase().includes(q) : true))
      .sort((a, b) => a.localeCompare(b));
  }, [tableFilter, tableNames]);

  const formatRecordCount = (table: string) => {
    const value = tableCounts[table];
    if (countsLoading && value === undefined) return '…';
    if (typeof value !== 'number') return '—';
    return value.toLocaleString('es-MX');
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5 text-primary" />
            {t('tables.title')}
          </CardTitle>
          <CardDescription>{t('tables.subtitle')}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="relative max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 transform text-muted-foreground" />
            <Input
              value={tableFilter}
              onChange={(e) => setTableFilter(e.target.value)}
              placeholder={t('tables.search.placeholder')}
              className="pl-10"
            />
          </div>
          {countError ? (
            <div className="flex items-center gap-2 text-sm text-red-600">
              <AlertTriangle className="h-4 w-4" />
              {t('tables.error')}
            </div>
          ) : (
            <div className="max-h-[32rem] overflow-auto rounded-lg border divide-y">
              {countsLoading && !filteredTables.length ? (
                <div className="flex items-center gap-2 p-3 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  {t('tables.loading')}
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
                <div className="p-3 text-sm text-muted-foreground">{t('tables.empty')}</div>
              ) : null}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
