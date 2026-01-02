import { useState, useEffect, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { ArrowRightLeft, Calculator, TrendingUp, Calendar, Share2, Loader2, BarChart3 } from 'lucide-react';
import { format, subMonths } from 'date-fns';
import { es } from 'date-fns/locale';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ExchangeRate {
  fecha: string;
  tipo_cambio: number;
  moneda_origen?: string;
  moneda_destino?: string;
  tipo?: string;
}

export default function ExchangeRatePageHistorical() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [exchangeData, setExchangeData] = useState<ExchangeRate[]>([]);
  const [latestRate, setLatestRate] = useState<ExchangeRate | null>(null);

  // Calculator
  const [amount, setAmount] = useState<string>(searchParams.get('amount') || '1000');
  const [fromCurrency, setFromCurrency] = useState<'MXN' | 'USD'>((searchParams.get('from') as 'MXN' | 'USD') || 'USD');
  const [toCurrency, setToCurrency] = useState<'MXN' | 'USD'>((searchParams.get('to') as 'MXN' | 'USD') || 'MXN');
  const [selectedDate, setSelectedDate] = useState(searchParams.get('fecha') || '');
  const [result, setResult] = useState<number | null>(null);

  // Historical range
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [rangeStats, setRangeStats] = useState<{
    min: number;
    max: number;
    avg: number;
    count: number;
  } | null>(null);

  useEffect(() => {
    const loadExchangeData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${import.meta.env.BASE_URL}data/banxico/tipo_cambio_usd.json`);
        const data: ExchangeRate[] = await response.json();

        // Filter and sort
        const filteredData = data
          .filter(rate => rate.tipo === 'oficial_banxico_fix' || !rate.tipo)
          .sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());

        setExchangeData(filteredData);

        // Get latest rate
        const latest = filteredData[filteredData.length - 1];
        setLatestRate(latest);

        // Set default dates
        if (!selectedDate) setSelectedDate(latest.fecha);
        if (!endDate) setEndDate(latest.fecha);
        if (!startDate) {
          const threeMonthsAgo = subMonths(new Date(latest.fecha), 3);
          setStartDate(format(threeMonthsAgo, 'yyyy-MM-dd'));
        }
      } catch (error) {
        console.error('Error loading exchange rate data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadExchangeData();
  }, []);

  const findRateByDate = (date: string): ExchangeRate | undefined => {
    return exchangeData.find((item) => item.fecha === date);
  };

  const getRangeData = useMemo(() => {
    if (!startDate || !endDate) return [];

    return exchangeData.filter(item => {
      const itemDate = new Date(item.fecha);
      const start = new Date(startDate);
      const end = new Date(endDate);
      return itemDate >= start && itemDate <= end;
    });
  }, [exchangeData, startDate, endDate]);

  useEffect(() => {
    if (getRangeData.length > 0) {
      const rates = getRangeData.map(item => item.tipo_cambio);
      setRangeStats({
        min: Math.min(...rates),
        max: Math.max(...rates),
        avg: rates.reduce((a, b) => a + b, 0) / rates.length,
        count: rates.length,
      });
    }
  }, [getRangeData]);

  const calculateConversion = () => {
    const rate = findRateByDate(selectedDate);
    if (!rate || !amount) return;

    const numAmount = parseFloat(amount);
    if (isNaN(numAmount)) return;

    let convertedAmount: number;

    if (fromCurrency === 'USD' && toCurrency === 'MXN') {
      convertedAmount = numAmount * rate.tipo_cambio;
    } else if (fromCurrency === 'MXN' && toCurrency === 'USD') {
      convertedAmount = numAmount / rate.tipo_cambio;
    } else {
      convertedAmount = numAmount;
    }

    setResult(convertedAmount);

    // Update URL
    setSearchParams({
      amount,
      from: fromCurrency,
      to: toCurrency,
      fecha: selectedDate,
    });
  };

  const swapCurrencies = () => {
    const temp = fromCurrency;
    setFromCurrency(toCurrency);
    setToCurrency(temp);
    setResult(null);
  };

  const formatCurrency = (value: number, currency: string) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: currency === 'MXN' ? 'MXN' : 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 4,
    }).format(value);
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'Calculadora de Tipo de Cambio - catalogmx',
        text: `Tipo de cambio USD/MXN desde ${latestRate?.fecha}`,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('Enlace copiado al portapapeles');
    }
  };

  const setQuickRange = (months: number) => {
    if (!latestRate) return;
    const end = latestRate.fecha;
    const start = format(subMonths(new Date(end), months), 'yyyy-MM-dd');
    setStartDate(start);
    setEndDate(end);
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
          <h1 className="text-2xl font-bold">Calculadora de Tipo de Cambio Histórico</h1>
          <p className="text-muted-foreground mt-1">
            Tipo de cambio FIX USD/MXN - {exchangeData.length.toLocaleString()} registros desde 1991
          </p>
          {latestRate && (
            <div className="flex gap-2 mt-2 flex-wrap">
              <Badge variant="secondary">
                1 USD = ${latestRate.tipo_cambio.toFixed(4)} MXN
              </Badge>
              <Badge variant="outline">
                {format(new Date(latestRate.fecha), "d 'de' MMMM, yyyy", { locale: es })}
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
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Evolución del Tipo de Cambio
              </CardTitle>
              <CardDescription>
                Tipo de cambio FIX oficial Banxico
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => setQuickRange(3)}>
                3M
              </Button>
              <Button variant="outline" size="sm" onClick={() => setQuickRange(6)}>
                6M
              </Button>
              <Button variant="outline" size="sm" onClick={() => setQuickRange(12)}>
                1A
              </Button>
              <Button variant="outline" size="sm" onClick={() => setQuickRange(60)}>
                5A
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-2 gap-4 mb-4">
            <div>
              <Label htmlFor="start-date">Desde</Label>
              <Input
                id="start-date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                max={endDate}
              />
            </div>
            <div>
              <Label htmlFor="end-date">Hasta</Label>
              <Input
                id="end-date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                min={startDate}
                max={latestRate?.fecha}
              />
            </div>
          </div>

          {rangeStats && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
              <div className="p-3 bg-muted rounded-lg">
                <div className="text-xs text-muted-foreground">Mínimo</div>
                <div className="text-lg font-bold">${rangeStats.min.toFixed(4)}</div>
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <div className="text-xs text-muted-foreground">Máximo</div>
                <div className="text-lg font-bold">${rangeStats.max.toFixed(4)}</div>
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <div className="text-xs text-muted-foreground">Promedio</div>
                <div className="text-lg font-bold">${rangeStats.avg.toFixed(4)}</div>
              </div>
              <div className="p-3 bg-muted rounded-lg">
                <div className="text-xs text-muted-foreground">Días</div>
                <div className="text-lg font-bold">{rangeStats.count}</div>
              </div>
            </div>
          )}

          <div className="h-[350px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={getRangeData}>
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
                  tickFormatter={(value) => `$${value.toFixed(2)}`}
                  domain={['auto', 'auto']}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="rounded-lg border bg-background p-2 shadow-md">
                          <div className="text-xs text-muted-foreground">
                            {format(new Date(data.fecha), "d 'de' MMMM, yyyy", { locale: es })}
                          </div>
                          <div className="font-bold text-primary">
                            1 USD = ${data.tipo_cambio.toFixed(4)} MXN
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="tipo_cambio"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Current Rate */}
        {latestRate && (
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Tipo de Cambio Actual
              </CardTitle>
              <CardDescription>
                Tipo de cambio FIX oficial de Banxico
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-3xl font-bold">
                    ${latestRate.tipo_cambio.toFixed(4)}
                  </div>
                  <Badge variant="secondary">
                    {format(new Date(latestRate.fecha), "d MMM yyyy", { locale: es })}
                  </Badge>
                </div>
                <div className="text-sm text-muted-foreground">
                  1 USD = {latestRate.tipo_cambio.toFixed(4)} MXN
                </div>
                <p className="text-xs text-muted-foreground border-t pt-3">
                  <strong>Fuente:</strong> Banco de México - Tipo de cambio FIX para solventar obligaciones
                  denominadas en moneda extranjera pagaderas en la República Mexicana.
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
              Conversión Histórica
            </CardTitle>
            <CardDescription>
              Convierte usando el tipo de cambio de una fecha específica
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="amount">Monto</Label>
              <Input
                id="amount"
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Ingresa el monto"
                step="0.01"
                min="0"
              />
            </div>

            <div className="grid grid-cols-[1fr_auto_1fr] gap-3 items-end">
              <div className="space-y-2">
                <Label htmlFor="from-currency">De</Label>
                <select
                  id="from-currency"
                  value={fromCurrency}
                  onChange={(e) => setFromCurrency(e.target.value as 'MXN' | 'USD')}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="USD">USD</option>
                  <option value="MXN">MXN</option>
                </select>
              </div>

              <Button
                variant="outline"
                size="icon"
                onClick={swapCurrencies}
                className="rounded-full mb-0"
              >
                <ArrowRightLeft className="h-4 w-4" />
              </Button>

              <div className="space-y-2">
                <Label htmlFor="to-currency">A</Label>
                <select
                  id="to-currency"
                  value={toCurrency}
                  onChange={(e) => setToCurrency(e.target.value as 'MXN' | 'USD')}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="MXN">MXN</option>
                  <option value="USD">USD</option>
                </select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="selected-date">
                <Calendar className="inline h-4 w-4 mr-1" />
                Fecha de consulta
              </Label>
              <Input
                id="selected-date"
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                max={latestRate?.fecha}
              />
              {selectedDate && findRateByDate(selectedDate) && (
                <div className="text-xs text-muted-foreground">
                  Tipo de cambio: ${findRateByDate(selectedDate)!.tipo_cambio.toFixed(4)}
                </div>
              )}
            </div>

            <Button onClick={calculateConversion} className="w-full">
              Convertir
            </Button>

            {result !== null && (
              <div className="pt-4 border-t">
                <div className="text-center space-y-2">
                  <p className="text-sm text-muted-foreground">Resultado</p>
                  <p className="text-3xl font-bold">
                    {formatCurrency(result, toCurrency)}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formatCurrency(parseFloat(amount), fromCurrency)} = {formatCurrency(result, toCurrency)}
                    <br />
                    ({format(new Date(selectedDate), "d 'de' MMMM, yyyy", { locale: es })})
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Información sobre el Tipo de Cambio FIX</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>
            <strong>Tipo de cambio FIX:</strong> Es el tipo de cambio de referencia que publica Banco de México
            diariamente para solventar obligaciones denominadas en moneda extranjera pagaderas en México.
          </p>
          <p>
            <strong>Fecha de determinación:</strong> Se determina un día hábil bancario anterior a su publicación,
            con base en un promedio de cotizaciones del mercado de cambios al mayoreo.
          </p>
          <p>
            <strong>Uso en facturación y contabilidad:</strong> Para efectos fiscales, se debe utilizar el tipo
            de cambio publicado en el DOF o el determinado por el Banco de México correspondiente a la fecha
            de la operación.
          </p>
          <p>
            <strong>Datos históricos:</strong> Esta calculadora contiene {exchangeData.length.toLocaleString()} registros
            desde {exchangeData[0]?.fecha} hasta {latestRate?.fecha}.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
