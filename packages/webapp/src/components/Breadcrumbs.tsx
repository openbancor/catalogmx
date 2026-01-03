import { useLocation, Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import { datasetConfigs } from '@/data/datasets';

export default function Breadcrumbs() {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  if (pathnames.length === 0) {
    return null; // Don't show breadcrumbs on home page
  }

  const getBreadcrumbLabel = (segment: string, index: number): string => {
    // Check if it's a dataset
    if (pathnames[index - 1] === 'catalogs' && index === pathnames.length - 1) {
      const dataset = datasetConfigs.find(d => d.id === segment);
      if (dataset) return dataset.label;
    }

    // Map common paths
    const labelMap: Record<string, string> = {
      'validators': 'Validadores',
      'calculators': 'Calculadoras',
      'catalogs': 'Catálogos',
      'reference': 'Referencia',
      'rfc': 'RFC',
      'curp': 'CURP',
      'clabe': 'CLABE',
      'nss': 'NSS',
      'isr': 'ISR',
      'iva': 'IVA',
      'ieps': 'IEPS',
      'udi': 'UDI',
      'exchange': 'Tipo de Cambio',
      'inflation': 'Inflación',
      'salary': 'Salario Mínimo',
    };

    return labelMap[segment] || segment.charAt(0).toUpperCase() + segment.slice(1);
  };

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
      <Link
        to="/"
        className="flex items-center hover:text-foreground transition-colors"
        aria-label="Inicio"
      >
        <Home className="h-4 w-4" />
      </Link>

      {pathnames.map((segment, index) => {
        const path = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;
        const label = getBreadcrumbLabel(segment, index);

        return (
          <div key={path} className="flex items-center gap-2">
            <ChevronRight className="h-4 w-4" />
            {isLast ? (
              <span className="font-medium text-foreground" aria-current="page">
                {label}
              </span>
            ) : (
              <Link
                to={path}
                className="hover:text-foreground transition-colors"
              >
                {label}
              </Link>
            )}
          </div>
        );
      })}
    </nav>
  );
}
