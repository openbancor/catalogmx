import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, Package, ChevronLeft, ChevronRight, Loader2, AlertCircle, Check, X } from 'lucide-react';
import { searchProductos, type ProductoServicio, type PaginatedResult } from '@/lib/database';

export default function ProductosPage() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PaginatedResult<ProductoServicio> | null>(null);

  const handleSearch = async (newPage = 1) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchProductos(search, newPage, 25);
      setResult(data);
      setPage(newPage);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load database');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch(1);
  }, []);

  const renderTaxIndicator = (value: string | null) => {
    if (!value) return <span className="text-muted-foreground">-</span>;
    if (value === 'Si' || value === 'Sí') {
      return <Check className="h-4 w-4 text-green-600" />;
    }
    if (value === 'No') {
      return <X className="h-4 w-4 text-red-600" />;
    }
    return <span className="text-muted-foreground text-xs">{value}</span>;
  };

  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <h1 className="text-2xl font-bold">Products & Services (SAT)</h1>
        <p className="text-muted-foreground mt-1">
          Search SAT's CFDI 4.0 product and service codes for electronic invoicing
        </p>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by code, description, or keywords (e.g., 'computadora', '43211500')..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch(1)}
                className="pl-10"
              />
            </div>
            <Button onClick={() => handleSearch(1)} disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Search'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Error */}
      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 text-destructive">
              <AlertCircle className="h-5 w-5" />
              <div>
                <div className="font-medium">Database Error</div>
                <div className="text-sm">{error}</div>
                <div className="text-xs mt-1 text-muted-foreground">
                  Make sure the SQLite database files are in the /public/data/ folder
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {result && !error && (
        <>
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Showing {((page - 1) * result.pageSize) + 1}-{Math.min(page * result.pageSize, result.total)} of {result.total.toLocaleString()} results
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSearch(page - 1)}
                disabled={page <= 1 || loading}
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground px-2">
                Page {page} of {result.totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSearch(page + 1)}
                disabled={page >= result.totalPages || loading}
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-muted">
                    <tr>
                      <th className="text-left p-3 font-medium">Code</th>
                      <th className="text-left p-3 font-medium">Description</th>
                      <th className="text-center p-3 font-medium" title="Include IVA">IVA</th>
                      <th className="text-center p-3 font-medium" title="Include IEPS">IEPS</th>
                      <th className="text-center p-3 font-medium" title="Border Zone Stimulus">Border</th>
                      <th className="text-left p-3 font-medium">Keywords</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {result.data.map((prod, i) => (
                      <tr key={i} className="hover:bg-muted/50">
                        <td className="p-3">
                          <Badge variant="secondary" className="font-mono">
                            {prod.c_ClaveProdServ}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <div className="font-medium max-w-md">{prod.Descripcion}</div>
                          {prod.Complemento_que_debe_incluir && (
                            <div className="text-xs text-muted-foreground mt-1">
                              Complement: {prod.Complemento_que_debe_incluir}
                            </div>
                          )}
                        </td>
                        <td className="p-3 text-center">
                          {renderTaxIndicator(prod.Incluir_IVA_trasladado)}
                        </td>
                        <td className="p-3 text-center">
                          {renderTaxIndicator(prod.Incluir_IEPS_trasladado)}
                        </td>
                        <td className="p-3 text-center">
                          {renderTaxIndicator(prod.Estimulo_Franja_Fronteriza)}
                        </td>
                        <td className="p-3 text-muted-foreground text-xs max-w-xs truncate">
                          {prod.Palabras_similares || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            About c_ClaveProdServ
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            This is the official SAT catalog of product and service codes (c_ClaveProdServ) required
            for CFDI 4.0 electronic invoicing in Mexico. The catalog contains ~52,000 codes.
          </p>
          <div className="grid sm:grid-cols-2 gap-4 mt-4">
            <div className="p-3 bg-muted rounded">
              <div className="font-medium text-foreground mb-1">Code Structure</div>
              <p>8-digit codes organized hierarchically: Division (2) + Group (2) + Class (2) + Product (2)</p>
            </div>
            <div className="p-3 bg-muted rounded">
              <div className="font-medium text-foreground mb-1">Tax Indicators</div>
              <p>Codes indicate if IVA/IEPS must be included and if border zone stimulus applies</p>
            </div>
          </div>
          <p className="mt-4">
            <strong>Example codes:</strong>
          </p>
          <ul className="list-disc list-inside space-y-1">
            <li><code>43211500</code> - Computers</li>
            <li><code>81112000</code> - Professional consulting services</li>
            <li><code>50000000</code> - Food, beverages and tobacco</li>
            <li><code>84111506</code> - Accounting services</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
