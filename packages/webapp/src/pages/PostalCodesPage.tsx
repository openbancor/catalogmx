import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, MapPin, ChevronLeft, ChevronRight, Loader2, AlertCircle } from 'lucide-react';
import { searchPostalCodes, type PostalCode, type PaginatedResult } from '@/lib/database';

export default function PostalCodesPage() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(100);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PaginatedResult<PostalCode> | null>(null);

  const handleSearch = async (newPage = 1) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchPostalCodes(search, newPage, pageSize);
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

  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <h1 className="text-2xl font-bold">Postal Codes (SEPOMEX)</h1>
        <p className="text-muted-foreground mt-1">
          Search Mexican postal codes with settlement, municipality, and state information
        </p>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by postal code, settlement, city, municipality, or state..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch(1)}
                className="pl-10"
              />
            </div>
            <div className="flex items-center gap-2">
              <label className="text-xs text-muted-foreground">Rows/page</label>
              <select
                className="h-10 rounded-md border bg-background px-3 text-sm"
                value={pageSize}
                onChange={(e) => {
                  const next = Number(e.target.value) || 50;
                  setPageSize(next);
                  setPage(1);
                  handleSearch(1);
                }}
              >
                {[25, 50, 100, 250, 500].map((size) => (
                  <option key={size} value={size}>
                    {size}
                  </option>
                ))}
              </select>
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
              {' · '}No sampling: full catalog with pagination
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
                      <th className="text-left p-3 font-medium">Postal Code</th>
                      <th className="text-left p-3 font-medium">Settlement</th>
                      <th className="text-left p-3 font-medium">Type</th>
                      <th className="text-left p-3 font-medium">Municipality</th>
                      <th className="text-left p-3 font-medium">State</th>
                      <th className="text-left p-3 font-medium">City</th>
                      <th className="text-left p-3 font-medium">Zone</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {result.data.map((cp, i) => (
                    <tr key={i} className="hover:bg-muted/50">
                      <td className="p-3">
                        <Badge variant="secondary" className="font-mono">
                          {cp.cp}
                        </Badge>
                      </td>
                      <td className="p-3 font-medium">{cp.asentamiento}</td>
                      <td className="p-3 text-muted-foreground">{cp.tipo_asentamiento}</td>
                      <td className="p-3">{cp.municipio}</td>
                      <td className="p-3">{cp.estado}</td>
                      <td className="p-3 text-muted-foreground">{cp.ciudad || '-'}</td>
                      <td className="p-3">
                        <Badge variant="outline">{cp.zona ?? '-'}</Badge>
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
            <MapPin className="h-5 w-5" />
            About SEPOMEX Data
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            This database contains the official postal code catalog from SEPOMEX (Servicio Postal Mexicano).
            It includes ~145,000 settlements with their postal codes, types, and geographic hierarchy.
          </p>
          <p>
            <strong>Settlement Types:</strong> Colonia, Fraccionamiento, Pueblo, Barrio, Unidad Habitacional,
            Ejido, Zona Industrial, Aeropuerto, and more.
          </p>
          <p>
            <strong>Zones:</strong> Urbano (Urban), Rural, Semiurbano (Semi-urban)
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
