import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, MapPin, ChevronLeft, ChevronRight, Loader2, AlertCircle, Navigation } from 'lucide-react';
import { searchLocalidades, type Localidad, type PaginatedResult } from '@/lib/database';

export default function LocalidadesPage() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PaginatedResult<Localidad> | null>(null);

  const handleSearch = async (newPage = 1) => {
    setLoading(true);
    setError(null);
    try {
      const data = await searchLocalidades(search, newPage, 25);
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

  const formatCoordinate = (value: number | null, type: 'lat' | 'lon') => {
    if (value === null || value === undefined) return '-';
    const direction = type === 'lat' ? (value >= 0 ? 'N' : 'S') : (value >= 0 ? 'E' : 'W');
    return `${Math.abs(value).toFixed(4)}${direction}`;
  };

  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <h1 className="text-2xl font-bold">Localities (INEGI)</h1>
        <p className="text-muted-foreground mt-1">
          Search Mexican localities with GPS coordinates and population data from INEGI
        </p>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by locality name, municipality, or state..."
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
                      <th className="text-left p-3 font-medium">Locality</th>
                      <th className="text-left p-3 font-medium">Municipality</th>
                      <th className="text-left p-3 font-medium">State</th>
                      <th className="text-right p-3 font-medium">Population</th>
                      <th className="text-right p-3 font-medium">Altitude</th>
                      <th className="text-left p-3 font-medium">Coordinates</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {result.data.map((loc, i) => (
                      <tr key={i} className="hover:bg-muted/50">
                        <td className="p-3">
                          <Badge variant="secondary" className="font-mono text-xs">
                            {loc.cve_ent}-{loc.cve_mun}-{loc.cve_loc}
                          </Badge>
                        </td>
                        <td className="p-3 font-medium">{loc.nom_loc}</td>
                        <td className="p-3">{loc.nom_mun}</td>
                        <td className="p-3">{loc.nom_ent}</td>
                        <td className="p-3 text-right font-mono">
                          {loc.pob_total?.toLocaleString() || '-'}
                        </td>
                        <td className="p-3 text-right font-mono">
                          {loc.altitud ? `${loc.altitud}m` : '-'}
                        </td>
                        <td className="p-3">
                          {loc.lat_decimal && loc.lon_decimal ? (
                            <a
                              href={`https://www.google.com/maps?q=${loc.lat_decimal},${loc.lon_decimal}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 text-primary hover:underline text-xs font-mono"
                            >
                              <Navigation className="h-3 w-3" />
                              {formatCoordinate(loc.lat_decimal, 'lat')}, {formatCoordinate(loc.lon_decimal, 'lon')}
                            </a>
                          ) : '-'}
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
            About INEGI Localities
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            This database contains the official catalog of localities from INEGI (Instituto Nacional
            de Estadistica y Geografia). It includes ~300,000 localities with geographic data.
          </p>
          <p>
            <strong>Data includes:</strong> Geographic codes (state-municipality-locality), population
            from the latest census, altitude in meters, and decimal GPS coordinates.
          </p>
          <p>
            <strong>Use cases:</strong> Geographic validation, address verification, demographic
            analysis, mapping applications.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
