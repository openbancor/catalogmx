import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Database, MapPin, Package, Building2 } from 'lucide-react';

const catalogCategories = [
  {
    title: 'SEPOMEX - Postal Codes',
    icon: MapPin,
    description: 'Mexican postal code directory with settlements, cities, and municipalities',
    database: 'sepomex.db',
    records: '~145,000',
    link: 'postal-codes'
  },
  {
    title: 'INEGI - Localities',
    icon: Building2,
    description: 'Geographic localities with GPS coordinates and population data',
    database: 'localidades.db',
    records: '~300,000',
    link: 'localidades'
  },
  {
    title: 'SAT - Products & Services',
    icon: Package,
    description: 'CFDI 4.0 product and service codes for electronic invoicing',
    database: 'clave_prod_serv.db',
    records: '~52,000',
    link: 'productos'
  }
];

const jsonCatalogs = [
  { name: 'Banxico - Banks', records: 145, description: 'Mexican bank codes and names' },
  { name: 'Banxico - Currencies', records: 168, description: 'Currency codes (ISO 4217)' },
  { name: 'Banxico - UDI Values', records: 365, description: 'Daily UDI values' },
  { name: 'SAT - Tax Regimes', records: 18, description: 'Fiscal regimes for CFDI' },
  { name: 'SAT - CFDI Use', records: 22, description: 'Invoice usage codes' },
  { name: 'SAT - Payment Methods', records: 8, description: 'Payment method codes' },
  { name: 'SAT - Payment Forms', records: 18, description: 'Payment form codes' },
  { name: 'SAT - Unit of Measure', records: 2400, description: 'Unit codes for products' },
  { name: 'SAT - Countries', records: 250, description: 'Country codes' },
  { name: 'SAT - Object of Tax', records: 4, description: 'Tax object codes' },
  { name: 'SAT - Tax Export', records: 2, description: 'Export tax codes' },
  { name: 'SAT - Nomina Contract Types', records: 8, description: 'Employment contract types' },
  { name: 'SAT - Nomina Job Risk', records: 5, description: 'Job risk classification' },
  { name: 'SAT - Nomina Periodicity', records: 8, description: 'Payment periods' },
  { name: 'INEGI - States', records: 32, description: 'Mexican states' },
  { name: 'INEGI - Municipalities', records: 2469, description: 'Municipal codes' },
  { name: 'IFT - Area Codes', records: 385, description: 'Telephone area codes' },
  { name: 'Mexico - Min Wages', records: 5, description: 'Minimum wage zones' },
  { name: 'Mexico - UMA Values', records: 10, description: 'UMA (measurement unit)' },
];

export default function CatalogsPage() {
  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold">Catalog Browser</h1>
        <p className="text-muted-foreground mt-1">
          Browse 58 official Mexican government catalogs from Banxico, SAT, INEGI, SEPOMEX, and more
        </p>
      </div>

      {/* SQLite Catalogs */}
      <div>
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Database className="h-5 w-5" />
          Large Catalogs (SQLite)
        </h2>
        <div className="grid md:grid-cols-3 gap-4">
          {catalogCategories.map((cat) => (
            <Card key={cat.database} className="hover:border-primary transition-colors cursor-pointer">
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <cat.icon className="h-5 w-5" />
                  {cat.title}
                </CardTitle>
                <CardDescription>{cat.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{cat.database}</span>
                  <Badge variant="secondary">{cat.records} records</Badge>
                </div>
                <div className="mt-3">
                  <a
                    href={`#${cat.link}`}
                    className="text-sm text-primary hover:underline"
                    onClick={(e) => {
                      e.preventDefault();
                      // This would be handled by the parent navigation
                      window.dispatchEvent(new CustomEvent('navigate', { detail: cat.link }));
                    }}
                  >
                    Browse catalog
                  </a>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* JSON Catalogs */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Standard Catalogs (JSON)</h2>
        <Card>
          <CardContent className="p-0">
            <div className="divide-y">
              {jsonCatalogs.map((cat, i) => (
                <div key={i} className="p-4 flex items-center justify-between hover:bg-muted/50">
                  <div>
                    <div className="font-medium">{cat.name}</div>
                    <div className="text-sm text-muted-foreground">{cat.description}</div>
                  </div>
                  <Badge variant="outline">{cat.records}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Usage Info */}
      <Card>
        <CardHeader>
          <CardTitle>Using Catalogs in Code</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <div className="font-medium mb-2">TypeScript/JavaScript</div>
              <pre className="p-3 bg-muted rounded text-xs overflow-x-auto">
{`import { catalogs } from 'catalogmx';

// Get all banks
const banks = catalogs.banxico.banks.getAll();

// Search by code
const bank = catalogs.banxico.banks.getByCode('002');

// Validate
if (catalogs.sat.regimenes.isValid('601')) {
  // Valid tax regime
}`}
              </pre>
            </div>
            <div>
              <div className="font-medium mb-2">Python</div>
              <pre className="p-3 bg-muted rounded text-xs overflow-x-auto">
{`from catalogmx import catalogs

# Get all banks
banks = catalogs.banxico.banks.get_all()

# Search by code
bank = catalogs.banxico.banks.get_by_code('002')

# Validate
if catalogs.sat.regimenes.is_valid('601'):
    # Valid tax regime
    pass`}
              </pre>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
