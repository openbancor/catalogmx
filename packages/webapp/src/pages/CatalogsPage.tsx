import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertTriangle, CheckCircle2, Database, Loader2, MapPin, Package, Building2 } from 'lucide-react';
import CatalogsSection from '@/components/CatalogsSection';
import { emitNavigation } from '@/lib/navigation';
import { queryDatabase } from '@/lib/database';

const heroStats = [
  { label: '58 government catalogs', value: '58', detail: 'Banxico · SAT · INEGI · SEPOMEX' },
  { label: '470k+ rows', value: '470k+', detail: 'Normalized + indexed' },
  { label: '93.78% coverage', value: '93.78%', detail: '1,250+ automated tests' },
];

const sqliteCatalogs = [
  {
    id: 'postal-codes',
    title: 'Postal Codes (SEPOMEX)',
    icon: MapPin,
    description: '145k settlements with type, zone, and municipality metadata.',
    table: 'codigos_postales',
    records: '~145k'
  },
  {
    id: 'localidades',
    title: 'Localities (INEGI)',
    icon: Building2,
    description: '300k+ populated places with geospatial coordinates.',
    table: 'localidades',
    records: '~300k'
  },
  {
    id: 'productos',
    title: 'Products & Services (SAT)',
    icon: Package,
    description: '52k CFDI 4.0 product/service concepts with synonyms.',
    table: 'c_ClaveProdServ',
    records: '~52k'
  }
];

export default function CatalogsPage() {
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
                href="https://openbancor.github.io/catalogmx/mexico.sqlite3"
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

      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-semibold">Search every catalog</h2>
          <p className="text-sm text-muted-foreground">
            Banxico banks, currencies, SAT CFDI catalogs, tax regimes, Nómina, UMA, and more—all normalized and searchable.
          </p>
        </div>
        <CatalogsSection showHeader={false} />
      </section>

      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <Database className="h-5 w-5 text-primary" />
          <h2 className="text-xl font-semibold">Large SQLite catalogs</h2>
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
                  <Badge variant="secondary">{catalog.records}</Badge>
                </div>
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
    </div>
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
