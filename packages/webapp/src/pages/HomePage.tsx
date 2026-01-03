import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useLocale } from '@/lib/locale';
import { Download, Github, BookOpen, Calculator, CheckCircle2, Database, TrendingUp, MapPin, Building2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import SEOHead from '@/components/SEOHead';

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

export default function HomePage() {
  const { t } = useLocale();
  const navigate = useNavigate();
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
    { label: t('catalogs.stats.tables'), value: '58', detail: t('catalogs.stats.detail') },
    { label: t('catalogs.stats.rows'), value: '470k+', detail: t('catalogs.stats.rowsDetail') },
    { label: t('catalogs.stats.modified'), value: formatDate(fileMeta.modified), detail: 'mexico.sqlite3' },
  ];

  const features = [
    {
      icon: CheckCircle2,
      title: 'Validadores',
      description: 'RFC, CURP, CLABE, NSS y más',
      href: '/validators',
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
    {
      icon: Calculator,
      title: 'Calculadoras',
      description: 'ISR, IVA, IEPS, UDI, Inflación',
      href: '/calculators',
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      icon: Database,
      title: 'Catálogos',
      description: '58 catálogos oficiales',
      href: '/catalogs',
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
    },
  ];

  const popularCatalogs = [
    {
      icon: Building2,
      title: 'Bancos SPEI',
      description: '93 instituciones financieras',
      href: '/catalogs/banxico-banks',
    },
    {
      icon: MapPin,
      title: 'Códigos Postales',
      description: '157k códigos SEPOMEX',
      href: '/catalogs/sepomex-codigos-postales',
    },
    {
      icon: TrendingUp,
      title: 'UDI Histórico',
      description: 'Desde 1995 a la fecha',
      href: '/catalogs/banxico-udis',
    },
    {
      icon: Database,
      title: 'Productos SAT',
      description: '52k productos CFDI 4.0',
      href: '/catalogs/sat-productos',
    },
  ];

  return (
    <>
      <SEOHead />
      <div className="space-y-8 pb-10">
      {/* Hero Section */}
      <section className="flex flex-col gap-6 lg:grid lg:grid-cols-[1.6fr,1fr] xl:grid-cols-[2fr,1fr]">
        <Card className="border-none bg-gradient-to-br from-zinc-900 to-zinc-800 dark:from-zinc-900 dark:to-black text-white shadow-xl overflow-hidden flex flex-col justify-center min-h-[300px] relative">
            <div className="absolute top-0 right-0 p-32 bg-primary/20 blur-[100px] rounded-full pointer-events-none" />
            <div className="absolute bottom-0 left-0 p-24 bg-blue-500/10 blur-[80px] rounded-full pointer-events-none" />

          <CardHeader className="relative z-10 pb-2">
            <div className="flex items-center gap-2 mb-2">
               <span className="px-2 py-0.5 rounded-full bg-primary/20 text-primary text-xs font-medium border border-primary/20">v0.0.1</span>
               <span className="px-2 py-0.5 rounded-full bg-white/10 text-white/70 text-xs font-medium border border-white/10">SQLite VFS</span>
            </div>
            <CardTitle className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight leading-none">
              {t('catalogs.hero.title')}
            </CardTitle>
            <CardDescription className="text-white/80 text-lg sm:text-xl font-medium mt-2 max-w-lg">
              {t('catalogs.hero.subtitle')}
            </CardDescription>
          </CardHeader>
          <CardContent className="relative z-10 space-y-6">
            <p className="text-base text-white/70 leading-relaxed max-w-xl">
              {t('catalogs.hero.description')}
            </p>
            <div className="flex flex-wrap gap-3">
              <a
                href={`${import.meta.env.BASE_URL}data/mexico.sqlite3`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 font-semibold px-5 py-2.5 text-sm transition-all shadow-lg shadow-primary/20 active:scale-95"
              >
                <Download className="mr-2 h-4 w-4" />
                {t('catalogs.hero.download')}
              </a>
              <a
                href="https://github.com/OpenBancor/catalogmx"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-lg bg-white/10 border border-white/20 text-white hover:bg-white/20 font-medium px-5 py-2.5 text-sm transition-all active:scale-95"
              >
                <Github className="mr-2 h-4 w-4" />
                GitHub
              </a>
              <a
                href="https://github.com/OpenBancor/catalogmx/blob/main/packages/webapp/SPEC-sqlite-vfs.MD"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center rounded-lg bg-transparent border border-white/10 text-white/70 hover:text-white hover:border-white/30 font-medium px-5 py-2.5 text-sm transition-all"
              >
                <BookOpen className="mr-2 h-4 w-4" />
                {t('catalogs.hero.spec')}
              </a>
            </div>

            <div className="pt-4 border-t border-white/10 flex flex-wrap gap-x-6 gap-y-2 text-xs font-mono text-white/50">
               <div className="flex items-center gap-2">
                 <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
                 <span>mexico.sqlite3</span>
               </div>
               <div>{fileMeta.size ? formatBytes(fileMeta.size) : '...'}</div>
               <div>{formatDate(fileMeta.modified)}</div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-2 lg:grid-cols-1 gap-4 lg:gap-4 h-full">
          {heroStats.map((stat) => (
            <Card key={stat.label} className="flex flex-col justify-center border-none bg-card/50 shadow-sm">
              <CardContent className="py-6 px-6">
                <div className="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">{stat.value}</div>
                <div className="mt-1 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  {stat.label}
                </div>
                <div className="text-xs text-muted-foreground mt-2 border-l-2 border-primary/20 pl-2">
                    {stat.detail}
                </div>
              </CardContent>
            </Card>
          ))}
           <Card className="hidden lg:flex flex-col justify-center border-none bg-primary/5 shadow-sm">
              <CardContent className="py-6 px-6">
                <div className="text-sm font-medium text-foreground mb-2">
                    Multi-plataforma
                </div>
                <div className="flex gap-2 text-xs text-muted-foreground font-mono">
                    <span className="px-2 py-1 bg-background rounded border">Python</span>
                    <span className="px-2 py-1 bg-background rounded border">TypeScript</span>
                    <span className="px-2 py-1 bg-background rounded border">Dart</span>
                </div>
              </CardContent>
            </Card>
        </div>
      </section>

      {/* Features */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Funcionalidades</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map((feature) => (
            <Card
              key={feature.title}
              className="hover:shadow-lg transition-shadow cursor-pointer border-border/50"
              onClick={() => navigate(feature.href)}
            >
              <CardHeader>
                <div className={`w-12 h-12 rounded-lg ${feature.bgColor} flex items-center justify-center mb-3`}>
                  <feature.icon className={`h-6 w-6 ${feature.color}`} />
                </div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
                <CardDescription>{feature.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      {/* Popular Catalogs */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">Catálogos Populares</h2>
          <Button variant="ghost" onClick={() => navigate('/catalogs')}>
            Ver todos →
          </Button>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {popularCatalogs.map((catalog) => (
            <Card
              key={catalog.title}
              className="hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => navigate(catalog.href)}
            >
              <CardHeader className="pb-3">
                <catalog.icon className="h-5 w-5 text-muted-foreground mb-2" />
                <CardTitle className="text-base">{catalog.title}</CardTitle>
                <CardDescription className="text-xs">{catalog.description}</CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </section>

      {/* Quick Links */}
      <section>
        <Card>
          <CardHeader>
            <CardTitle>Inicio Rápido</CardTitle>
            <CardDescription>
              Instala catalogmx en tu lenguaje favorito y comienza a validar datos mexicanos
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <div className="text-sm font-semibold">Python</div>
                <code className="block p-3 bg-muted rounded text-xs font-mono">
                  pip install catalogmx
                </code>
              </div>
              <div className="space-y-2">
                <div className="text-sm font-semibold">TypeScript</div>
                <code className="block p-3 bg-muted rounded text-xs font-mono">
                  npm install catalogmx
                </code>
              </div>
              <div className="space-y-2">
                <div className="text-sm font-semibold">Dart/Flutter</div>
                <code className="block p-3 bg-muted rounded text-xs font-mono">
                  flutter pub add catalogmx
                </code>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
      </div>
    </>
  );
}
