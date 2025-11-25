import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useLocale } from '@/lib/locale';
import CatalogsSection from '@/components/CatalogsSection';
import { Download, Github, BookOpen } from 'lucide-react';

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

export default function CatalogsPage() {
  const { t } = useLocale();
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

  return (
    <div className="space-y-8 pb-10">
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
          {heroStats.map((stat, i) => (
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

      <div className="pt-4">
        <CatalogsSection showHeader={false} />
      </div>
    </div>
  );
}
