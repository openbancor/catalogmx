import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Calculator, DollarSign, Calendar } from 'lucide-react';

interface SalaryRecord {
  fecha: string;
  salario_minimo: number;
  tipo: string;
  zona: string;
  periodo: string;
  serie: string;
  año: number;
  mes: number;
}

export default function MinimumWagePage() {
  const [selectedYear, setSelectedYear] = useState<string>('');
  const [selectedMonth, setSelectedMonth] = useState<string>('');
  const [selectedZone, setSelectedZone] = useState<'general' | 'frontera_norte'>('general');
  const [currentSalary, setCurrentSalary] = useState<SalaryRecord | null>(null);
  const [historicalSalary, setHistoricalSalary] = useState<SalaryRecord | null>(null);
  const [allSalaries, setAllSalaries] = useState<SalaryRecord[]>([]);
  const [loading, setLoading] = useState(false);

  // Load salary data
  useEffect(() => {
    const loadSalaryData = async () => {
      try {
        const response = await fetch('/data/banxico/salarios_minimos.json');
        const data: SalaryRecord[] = await response.json();
        setAllSalaries(data);

        // Set current year and month
        const now = new Date();
        setSelectedYear(now.getFullYear().toString());
        setSelectedMonth((now.getMonth() + 1).toString().padStart(2, '0'));

        // Get current salary
        const current = data
          .filter(record => record.tipo === 'nominal' && record.zona === 'general')
          .sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime())[0];

        setCurrentSalary(current);
      } catch (error) {
        console.error('Failed to load salary data:', error);
      }
    };

    loadSalaryData();
  }, []);

  const searchHistoricalSalary = () => {
    if (!selectedYear || !selectedMonth || allSalaries.length === 0) return;

    setLoading(true);

    try {
      const targetDate = new Date(parseInt(selectedYear), parseInt(selectedMonth) - 1, 1);

      // Find the salary for the selected date and zone
      const salary = allSalaries
        .filter(record => {
          return record.año === targetDate.getFullYear() &&
                 record.mes === targetDate.getMonth() + 1 &&
                 record.tipo === 'nominal' &&
                 record.zona === selectedZone;
        })
        .sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime())[0];

      setHistoricalSalary(salary || null);
    } catch (error) {
      console.error('Error searching salary:', error);
      setHistoricalSalary(null);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('es-MX', {
      year: 'numeric',
      month: 'long'
    });
  };

  const getZoneName = (zone: string) => {
    switch (zone) {
      case 'general':
        return 'Zona General';
      case 'frontera_norte':
        return 'Zona Libre de la Frontera Norte';
      default:
        return zone;
    }
  };

  // Generate year options
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: currentYear - 1975 }, (_, i) => (currentYear - i).toString());

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-primary/15 text-primary">
          <Calculator className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Salario Mínimo</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Consulta el salario mínimo oficial por zona y período histórico desde 1976.
          </p>
        </div>
      </div>

      {/* Current Salary Display */}
      {currentSalary && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Salario Mínimo Vigente
            </CardTitle>
            <CardDescription>
              Salario mínimo general actual
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="text-2xl font-bold">
                {formatCurrency(currentSalary.salario_minimo)}
              </div>
              <Badge variant="secondary">
                {getZoneName(currentSalary.zona)}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Vigente desde {formatDate(currentSalary.fecha)} - Fuente: Banco de México
            </p>
          </CardContent>
        </Card>
      )}

      {/* Historical Search */}
      <Card>
        <CardHeader>
          <CardTitle>Consulta Histórica</CardTitle>
          <CardDescription>
            Busca el salario mínimo para una fecha y zona específica
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Date and Zone Selection */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="year-select">Año</Label>
              <select
                id="year-select"
                value={selectedYear}
                onChange={(e) => setSelectedYear(e.target.value)}
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="">Selecciona año</option>
                {years.map(year => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="month-select">Mes</Label>
              <select
                id="month-select"
                value={selectedMonth}
                onChange={(e) => setSelectedMonth(e.target.value)}
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="">Selecciona mes</option>
                <option value="01">Enero</option>
                <option value="02">Febrero</option>
                <option value="03">Marzo</option>
                <option value="04">Abril</option>
                <option value="05">Mayo</option>
                <option value="06">Junio</option>
                <option value="07">Julio</option>
                <option value="08">Agosto</option>
                <option value="09">Septiembre</option>
                <option value="10">Octubre</option>
                <option value="11">Noviembre</option>
                <option value="12">Diciembre</option>
              </select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="zone-select">Zona</Label>
              <select
                id="zone-select"
                value={selectedZone}
                onChange={(e) => setSelectedZone(e.target.value as 'general' | 'frontera_norte')}
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="general">Zona General</option>
                <option value="frontera_norte">Frontera Norte</option>
              </select>
            </div>
          </div>

          {/* Search Button */}
          <Button
            onClick={searchHistoricalSalary}
            className="w-full"
            disabled={loading || !selectedYear || !selectedMonth}
          >
            {loading ? 'Buscando...' : 'Buscar Salario'}
          </Button>

          {/* Historical Result */}
          {historicalSalary && (
            <div className="pt-4 border-t">
              <div className="text-center space-y-2">
                <p className="text-sm text-muted-foreground">Salario mínimo encontrado</p>
                <p className="text-3xl font-bold">
                  {formatCurrency(historicalSalary.salario_minimo)}
                </p>
                <div className="flex justify-center gap-4 text-sm">
                  <Badge variant="outline">
                    {getZoneName(historicalSalary.zona)}
                  </Badge>
                  <Badge variant="outline">
                    {formatDate(historicalSalary.fecha)}
                  </Badge>
                </div>
              </div>
            </div>
          )}

          {selectedYear && selectedMonth && !historicalSalary && !loading && (
            <div className="pt-4 border-t">
              <div className="text-center text-muted-foreground">
                <Calendar className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No se encontraron datos para la fecha seleccionada</p>
                <p className="text-sm">Verifica que la fecha corresponda a un período de vigencia</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Zone Information */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Zonas Salariales</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="font-semibold">Zona General</h4>
              <p className="text-sm text-muted-foreground">
                Aplica en todo el territorio nacional, excepto la Zona Libre de la Frontera Norte.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-semibold">Zona Libre de la Frontera Norte</h4>
              <p className="text-sm text-muted-foreground">
                Municipios fronterizos con Estados Unidos. Tiene un salario mínimo más alto.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
