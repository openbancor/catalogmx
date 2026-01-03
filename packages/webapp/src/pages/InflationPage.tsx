import { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Calculator, TrendingUp, Calendar, Share2, Loader2, BarChart3 } from 'lucide-react';
import { format, subYears, differenceInMonths } from 'date-fns';
import { es } from 'date-fns/locale';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface InflationRecord {
  fecha: string;
  inflacion_anual: number;
  inflacion_mensual?: number;
  inpc?: number;
  indice: string;
  año: number;
  mes: number;
}

export default function InflationPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [inflationData, setInflationData] = useState<InflationRecord[]>([]);
  const [latestRecord, setLatestRecord] = useState<InflationRecord | null>(null);

  // Calculator
  const [amount, setAmount] = useState<string>(searchParams.get('amount') || '10000');
  const [startDate, setStartDate] = useState<string>(searchParams.get('from') || '');
  const [endDate, setEndDate] = useState<string>(searchParams.get('to') || '');
  const [result, setResult] = useState<{
    adjustedAmount: number;
    inflationAcum: number;
    monthsDiff: number;
  } | null>(null);

  // Chart range
  const [chartStartDate, setChartStartDate] = useState('');
  const [chartEndDate, setChartEndDate] = useState('');

  useEffect(() => {
    const loadInflationData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${import.meta.env.BASE_URL}data/banxico/inflacion_anual.json`);
        const data: InflationRecord[] = await response.json();

        // Sort by date
        const sortedData = data.sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());
        setInflationData(sortedData);

        // Get latest record
        const latest = sortedData[sortedData.length - 1];
        setLatestRecord(latest);

        // Set default dates
        if (!startDate) {
          const oneYearAgo = subYears(new Date(latest.fecha), 1);
          setStartDate(format(oneYearAgo, 'yyyy-MM-dd'));
        }
        if (!endDate) setEndDate(latest.fecha);

        // Set chart range (last 5 years)
        if (!chartEndDate) setChartEndDate(latest.fecha);
        if (!chartStartDate) {
          const fiveYearsAgo = subYears(new Date(latest.fecha), 5);
          setChartStartDate(format(fiveYearsAgo, 'yyyy-MM-dd'));
        }
      } catch (error) {
        console.error('Error loading inflation data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadInflationData();
  }, []);

  const chartData = useMemo(() => {
    if (!chartStartDate || !chartEndDate) return [];

    return inflationData.filter(item => {
      const itemDate = new Date(item.fecha);
      const start = new Date(chartStartDate);
      const end = new Date(chartEndDate);
      return itemDate >= start && itemDate <= end;
    });
  }, [inflationData, chartStartDate, chartEndDate]);

  const findRecordByDate = (date: string): InflationRecord | undefined => {
    return inflationData.find((item) => item.fecha === date);
  };

  const calculateInflationAdjustment = () => {
    if (!amount || !startDate || !endDate) return;

    const numAmount = parseFloat(amount);
    if (isNaN(numAmount)) return;

    const startRecord = findRecordByDate(startDate);
    const endRecord = findRecordByDate(endDate);

    if (!startRecord || !endRecord) {
      alert('No se encontraron datos para las fechas seleccionadas');
      return;
    }

    // Calculate accumulated inflation between the two dates
    const startDateObj = new Date(startDate);
    const endDateObj = new Date(endDate);
    const monthsDiff = differenceInMonths(endDateObj, startDateObj);

    // Use INPC if available, otherwise use inflation rates
    let adjustmentFactor = 1;

    if (startRecord.inpc && endRecord.inpc) {
      // More accurate: use INPC index
      adjustmentFactor = endRecord.inpc / startRecord.inpc;
    } else {
      // Approximate: compound the annual inflation rates
      // This is simplified and less accurate
      const yearsApprox = monthsDiff / 12;
      const avgInflation = (startRecord.inflacion_anual + endRecord.inflacion_anual) / 2;
      adjustmentFactor = Math.pow(1 + avgInflation / 100, yearsApprox);
    }

    const adjustedAmount = numAmount * adjustmentFactor;
    const inflationAcum = ((adjustmentFactor - 1) * 100);

    setResult({
      adjustedAmount,
      inflationAcum,
      monthsDiff,
    });

    // Update URL
    setSearchParams({
      amount,
      from: startDate,
      to: endDate,
    });
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'Calculadora de Inflación - catalogmx',
        text: `Ajuste por inflación desde ${latestRecord?.fecha}`,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('Enlace copiado al portapapeles');
    }
  };

  const setQuickChartRange = (years: number) => {
    if (!latestRecord) return;
    const end = latestRecord.fecha;
    const start = format(subYears(new Date(end), years), 'yyyy-MM-dd');
    setChartStartDate(start);
    setChartEndDate(end);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">Calculadora de Inflación Histórica</h1>
          <p className="text-muted-foreground mt-1">
            INPC - {inflationData.length} registros desde {inflationData[0]?.año}
          </p>
          {latestRecord && (
            <div className="flex gap-2 mt-2 flex-wrap">
              <Badge variant="secondary">
                Inflación anual: {latestRecord.inflacion_anual.toFixed(2)}%
              </Badge>
              <Badge variant="outline">
                {format(new Date(latestRecord.fecha), "MMMM yyyy", { locale: es })}
              </Badge>
            </div>
          )}
        </div>
        <Button variant="outline" size="sm" onClick={handleShare}>
          <Share2 className="h-4 w-4 mr-2" />
          Compartir
        </Button>
      </div>

      {/* Historical Chart */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Evolución de la Inflación Anual
              </CardTitle>
              <CardDescription>
                Índice Nacional de Precios al Consumidor (INPC)
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => setQuickChartRange(1)}>
                1A
              </Button>
              <Button variant="outline" size="sm" onClick={() => setQuickChartRange(3)}>
                3A
              </Button>
              <Button variant="outline" size="sm" onClick={() => setQuickChartRange(5)}>
                5A
              </Button>
              <Button variant="outline" size="sm" onClick={() => setQuickChartRange(10)}>
                10A
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-2 gap-4 mb-4">
            <div>
              <Label htmlFor="chart-start">Desde</Label>
              <Input
                id="chart-start"
                type="date"
                value={chartStartDate}
                onChange={(e) => setChartStartDate(e.target.value)}
                max={chartEndDate}
              />
            </div>
            <div>
              <Label htmlFor="chart-end">Hasta</Label>
              <Input
                id="chart-end"
                type="date"
                value={chartEndDate}
                onChange={(e) => setChartEndDate(e.target.value)}
                min={chartStartDate}
                max={latestRecord?.fecha}
              />
            </div>
          </div>

          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorInflation" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis
                  dataKey="fecha"
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return format(date, 'MMM yy', { locale: es });
                  }}
                  tick={{ fontSize: 12 }}
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `${value.toFixed(1)}%`}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="rounded-lg border bg-background p-3 shadow-md">
                          <div className="text-xs text-muted-foreground">
                            {format(new Date(data.fecha), "MMMM yyyy", { locale: es })}
                          </div>
                          <div className="font-bold text-primary text-lg">
                            {data.inflacion_anual.toFixed(2)}%
                          </div>
                          {data.inflacion_mensual !== undefined && (
                            <div className="text-xs text-muted-foreground mt-1">
                              Mensual: {data.inflacion_mensual.toFixed(2)}%
                            </div>
                          )}
                          {data.inpc && (
                            <div className="text-xs text-muted-foreground">
                              INPC: {data.inpc.toFixed(2)}
                            </div>
                          )}
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="inflacion_anual"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  fill="url(#colorInflation)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Current Inflation */}
        {latestRecord && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Inflación Actual
              </CardTitle>
              <CardDescription>
                Tasa de inflación anual más reciente
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-4xl font-bold">
                    {latestRecord.inflacion_anual.toFixed(2)}%
                  </div>
                  <Badge variant="secondary">
                    {format(new Date(latestRecord.fecha), "MMM yyyy", { locale: es })}
                  </Badge>
                </div>
                <div className="text-sm text-muted-foreground">
                  Variación anual del INPC
                </div>
                {latestRecord.inpc && (
                  <div className="pt-3 border-t">
                    <div className="text-xs text-muted-foreground">INPC Base 2018=100</div>
                    <div className="text-2xl font-semibold">{latestRecord.inpc.toFixed(3)}</div>
                  </div>
                )}
                <p className="text-xs text-muted-foreground pt-3 border-t">
                  <strong>Fuente:</strong> Banco de México - Índice Nacional de Precios al Consumidor
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Calculator */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Ajuste por Inflación
            </CardTitle>
            <CardDescription>
              Calcula el valor ajustado entre dos fechas
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="amount">Monto Original (MXN)</Label>
              <Input
                id="amount"
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="10000"
                step="0.01"
                min="0"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="start-date">
                  <Calendar className="inline h-4 w-4 mr-1" />
                  Desde
                </Label>
                <Input
                  id="start-date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  max={endDate}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end-date">
                  <Calendar className="inline h-4 w-4 mr-1" />
                  Hasta
                </Label>
                <Input
                  id="end-date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  min={startDate}
                  max={latestRecord?.fecha}
                />
              </div>
            </div>

            <Button onClick={calculateInflationAdjustment} className="w-full">
              Calcular Ajuste
            </Button>

            {result !== null && (
              <div className="pt-4 border-t space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-muted rounded-lg text-center">
                    <div className="text-xs text-muted-foreground">Monto Ajustado</div>
                    <div className="text-xl font-bold text-primary">
                      {formatCurrency(result.adjustedAmount)}
                    </div>
                  </div>
                  <div className="p-3 bg-muted rounded-lg text-center">
                    <div className="text-xs text-muted-foreground">Inflación Acumulada</div>
                    <div className="text-xl font-bold">
                      {result.inflationAcum > 0 ? '+' : ''}{result.inflationAcum.toFixed(2)}%
                    </div>
                  </div>
                </div>

                <div className="p-3 bg-primary/10 rounded-lg text-sm space-y-1">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Original:</span>
                    <span className="font-medium">{formatCurrency(parseFloat(amount))}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Periodo:</span>
                    <span className="font-medium">{result.monthsDiff} meses</span>
                  </div>
                  <div className="flex justify-between border-t pt-1 mt-1">
                    <span className="font-medium">Ajustado:</span>
                    <span className="font-bold text-primary">{formatCurrency(result.adjustedAmount)}</span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Sobre el INPC y la Inflación</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>
            <strong>Índice Nacional de Precios al Consumidor (INPC):</strong> Indicador económico que mide
            la variación de los precios de una canasta de bienes y servicios representativa del consumo de los
            hogares mexicanos.
          </p>
          <p>
            <strong>Inflación anual:</strong> Variación porcentual del INPC en los últimos 12 meses. Indica
            el incremento generalizado de precios en ese periodo.
          </p>
          <p>
            <strong>Usos del ajuste por inflación:</strong>
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>Actualización de salarios y pensiones</li>
            <li>Ajuste de rentas y contratos de largo plazo</li>
            <li>Cálculo de indemnizaciones</li>
            <li>Análisis de poder adquisitivo histórico</li>
            <li>Comparación de precios en el tiempo</li>
          </ul>
          <p className="pt-3 border-t">
            <strong>Datos históricos:</strong> Esta calculadora contiene {inflationData.length} registros
            desde {inflationData[0]?.año} hasta {latestRecord?.año}.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
