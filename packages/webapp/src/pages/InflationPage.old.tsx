import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Calculator, TrendingUp } from 'lucide-react';

interface InflationRecord {
  fecha: string;
  inflacion_anual: number;
  indice: string;
  año: number;
  mes: number;
}

export default function InflationPage() {
  const [amount, setAmount] = useState<string>('10000');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [adjustedAmount, setAdjustedAmount] = useState<number | null>(null);
  const [inflationRate, setInflationRate] = useState<number | null>(null);
  const [inflationData, setInflationData] = useState<InflationRecord[]>([]);
  const [loading, setLoading] = useState(false);

  // Load inflation data
  useEffect(() => {
    const loadInflationData = async () => {
      try {
        const response = await fetch('/data/banxico/inflacion_anual.json');
        const data: InflationRecord[] = await response.json();
        setInflationData(data);

        // Set default dates (current year vs previous year)
        const currentYear = new Date().getFullYear();
        setStartDate(`${currentYear - 1}-12-01`);
        setEndDate(`${currentYear}-10-01`);
      } catch (error) {
        console.error('Failed to load inflation data:', error);
      }
    };

    loadInflationData();
  }, []);

  const calculateInflationAdjustment = () => {
    if (!amount || !startDate || !endDate || inflationData.length === 0) return;

    const numAmount = parseFloat(amount);
    if (isNaN(numAmount)) return;

    setLoading(true);

    try {
      const start = new Date(startDate);
      const end = new Date(endDate);

      // Find inflation rates for the periods
      const startRecord = inflationData
        .filter(record => {
          const recordDate = new Date(record.fecha);
          return recordDate.getFullYear() === start.getFullYear() &&
                 recordDate.getMonth() === start.getMonth();
        })
        .sort((a, b) => b.inflacion_anual - a.inflacion_anual)[0];

      const endRecord = inflationData
        .filter(record => {
          const recordDate = new Date(record.fecha);
          return recordDate.getFullYear() === end.getFullYear() &&
                 recordDate.getMonth() === end.getMonth();
        })
        .sort((a, b) => b.inflacion_anual - a.inflacion_anual)[0];

      if (!startRecord || !endRecord) {
        alert('No se encontraron datos de inflación para las fechas seleccionadas');
        return;
      }

      // Calculate adjustment factor
      // If going forward in time, apply inflation
      // If going backward, deflate
      const monthsDiff = (end.getFullYear() - start.getFullYear()) * 12 +
                        (end.getMonth() - start.getMonth());

      let adjustmentFactor: number;

      if (monthsDiff > 0) {
        // Forward adjustment: apply inflation
        adjustmentFactor = (100 + endRecord.inflacion_anual) / 100;
      } else {
        // Backward adjustment: apply deflation
        adjustmentFactor = 100 / (100 + startRecord.inflacion_anual);
      }

      const adjusted = numAmount * adjustmentFactor;
      setAdjustedAmount(adjusted);
      setInflationRate(endRecord.inflacion_anual);

    } catch (error) {
      console.error('Error calculating inflation:', error);
      alert('Error al calcular el ajuste por inflación');
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

  const getCurrentInflation = () => {
    if (inflationData.length === 0) return null;

    const latestRecord = inflationData
      .sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime())[0];

    return latestRecord;
  };

  const currentInflation = getCurrentInflation();

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-primary/15 text-primary">
          <Calculator className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Calculadora de Inflación</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Ajusta montos por inflación usando el Índice Nacional de Precios al Consumidor (INPC) de Banxico.
          </p>
        </div>
      </div>

      {/* Current Inflation Display */}
      {currentInflation && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Inflación Actual
            </CardTitle>
            <CardDescription>
              Inflación anual más reciente (INPC)
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="text-2xl font-bold">
                {currentInflation.inflacion_anual.toFixed(2)}%
              </div>
              <Badge variant="secondary">
                {new Date(currentInflation.fecha).toLocaleDateString('es-MX', {
                  year: 'numeric',
                  month: 'short'
                })}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Fuente: Banco de México - INPC Inflación Anual
            </p>
          </CardContent>
        </Card>
      )}

      {/* Calculator */}
      <Card>
        <CardHeader>
          <CardTitle>Ajuste por Inflación</CardTitle>
          <CardDescription>
            Calcula el equivalente de un monto ajustado por inflación entre dos fechas
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Amount Input */}
          <div className="space-y-2">
            <Label htmlFor="amount">Monto original</Label>
            <Input
              id="amount"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="Ingresa el monto original"
              step="0.01"
              min="0"
            />
          </div>

          {/* Date Inputs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start-date">Fecha original</Label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="end-date">Fecha de ajuste</Label>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>

          {/* Calculate Button */}
          <Button
            onClick={calculateInflationAdjustment}
            className="w-full"
            disabled={loading || !amount || !startDate || !endDate}
          >
            {loading ? 'Calculando...' : 'Calcular Ajuste'}
          </Button>

          {/* Result */}
          {adjustedAmount !== null && inflationRate !== null && (
            <div className="pt-4 border-t">
              <div className="text-center space-y-2">
                <p className="text-sm text-muted-foreground">Monto ajustado por inflación</p>
                <p className="text-3xl font-bold">
                  {formatCurrency(adjustedAmount)}
                </p>
                <div className="flex justify-center gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Original:</span>
                    <span className="font-medium ml-1">{formatCurrency(parseFloat(amount))}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Inflación:</span>
                    <span className="font-medium ml-1">{inflationRate.toFixed(2)}%</span>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  Ajuste calculado usando INPC de {new Date(endDate).toLocaleDateString('es-MX', { month: 'long', year: 'numeric' })}
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Additional Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">¿Cómo funciona?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <p>
            <strong>Índice Nacional de Precios al Consumidor (INPC):</strong> Mide la evolución general de los precios de una canasta de bienes y servicios representativa del consumo de los hogares.
          </p>
          <p>
            <strong>Inflación anual:</strong> Es la variación porcentual del INPC en los últimos 12 meses.
          </p>
          <p>
            <strong>Ajuste por inflación:</strong> Permite comparar el poder adquisitivo de un monto entre diferentes fechas, útil para contratos, pensiones y ajustes salariales.
          </p>
          <p>
            <strong>Usos comunes:</strong> Ajustes salariales, contratos de largo plazo, pensiones, indemnizaciones, y cualquier obligación monetaria sujeta a actualización por inflación.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
