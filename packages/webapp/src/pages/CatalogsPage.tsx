import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Database, MapPin, Package, Building2 } from 'lucide-react';
import { emitNavigation } from '@/lib/navigation';

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

const featuredCatalogs = [
  {
    id: 'postal-codes',
    title: 'Códigos Postales (SEPOMEX)',
    icon: MapPin,
    description: '157k asentamientos con tipo, zona y municipio.',
    table: 'codigos_postales',
    countHint: '~157k',
  },
  {
    id: 'localidades',
    title: 'Localidades (INEGI)',
    icon: Building2,
    description: '10k+ localidades con coordenadas.',
    table: 'localidades',
    countHint: '~10k',
  },
  {
    id: 'productos',
    title: 'Productos y Servicios (SAT)',
    icon: Package,
    description: '52k conceptos CFDI 4.0 con sinónimos.',
    table: 'clave_prod_serv',
    countHint: '~52k',
  },
];

export default function CatalogsPage() {
  const [fileMeta, setFileMeta] = useState<{ size?: number; modified?: string }>({});

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${import.meta.env.BASE_URL}data/mexico.sqlite3`, { method: 'HEAD', signal: controller.signal })
      .then((res) => {
        const size = Number(res.headers.get('content-length') || undefined);
        const modified = res.headers.get('last-modified') || undefined;
        setFileMeta({ size: Number.isFinite(size) ? size : undefined, modified });
      })
      .catch(() => {
        /* ignore */
      });
    return () => controller.abort();
  }, []);

  const heroStats = [
    { label: 'Tablas en mexico.sqlite3', value: '58', detail: 'Banxico · SAT · INEGI · SEPOMEX' },
    { label: 'Filas totales', value: '470k+', detail: 'Datos consolidados' },
    { label: 'Última modificación', value: formatDate(fileMeta.modified), detail: 'Cabecera HTTP Last-Modified' },
  ];

  return (
    <div className="space-y-8">
      <section className="grid gap-4 lg:grid-cols-[2fr,1fr]">
        <Card className="border-none bg-gradient-to-r from-primary to-emerald-500 text-primary-foreground shadow-lg">
          <CardHeader>
            <CardTitle className="text-2xl">mexico.sqlite3</CardTitle>
            <CardDescription className="text-primary-foreground/80">
              Build SQLite unificado listo para consultas HTTP/Range sin servidor.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <p>
              Copia <code className="font-mono">mexico.sqlite3</code> en <code className="font-mono">/public/data</code> y el demo lo carga localmente con sql.js.
              Sin servidor, sin API keys: datos normativos deterministas.
            </p>
            <div className="flex flex-wrap gap-3">
              <a
                href={`${import.meta.env.BASE_URL}data/mexico.sqlite3`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-full bg-white/90 px-4 py-2 text-sm font-semibold text-primary shadow hover:bg-white"
              >
                Descargar base de datos
              </a>
              <a
                href="https://github.com/OpenBancor/catalogmx/blob/main/packages/webapp/SPEC-sqlite-vfs.MD"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-full border border-white/60 px-4 py-2 text-sm font-semibold text-white/90 hover:bg-white/10"
              >
                Leer spec de VFS
              </a>
            </div>
            <div className="flex flex-wrap gap-3 text-xs text-primary-foreground/80">
              <span className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1">
                Tamaño: {fileMeta.size ? formatBytes(fileMeta.size) : '—'}
              </span>
              <span className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1">
                Última modificación: {formatDate(fileMeta.modified)}
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

      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <Database className="h-5 w-5 text-primary" />
          <h2 className="text-xl font-semibold">Catálogos principales</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {featuredCatalogs.map((catalog) => (
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
                    <div className="font-medium text-foreground">Tabla</div>
                    <div className="font-mono text-xs">{catalog.table}</div>
                  </div>
                  <Badge variant="secondary">{catalog.countHint}</Badge>
                </div>
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => emitNavigation(catalog.id)}
                >
                  Abrir
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
