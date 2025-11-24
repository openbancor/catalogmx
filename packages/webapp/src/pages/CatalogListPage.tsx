import CatalogsSection from '@/components/CatalogsSection';

export default function CatalogListPage() {
  return (
    <div className="space-y-6">
      <div className="text-center max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Catálogos completos</h1>
        <p className="text-muted-foreground">
          Explora los 58 catálogos oficiales con búsqueda por nombre y descripción.
        </p>
      </div>
      <CatalogsSection showHeader={false} />
    </div>
  );
}
