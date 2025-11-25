import CatalogsSection from '@/components/CatalogsSection';
import { useLocale } from '@/lib/locale';

export default function CatalogListPage() {
  const { t } = useLocale();
  return (
    <div className="space-y-6">
      <div className="text-center max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">{t('catalogs.list.title')}</h1>
        <p className="text-muted-foreground">{t('catalogs.list.subtitle')}</p>
      </div>
      <CatalogsSection showHeader={false} />
    </div>
  );
}
