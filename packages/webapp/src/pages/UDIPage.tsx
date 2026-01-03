import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calculator, DollarSign, TrendingUp, Calendar, Share2, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface UDIData {
  fecha: string;
  valor: number;
  moneda: string;
  tipo: string;
  año: number;
  mes: number;
}

export default function UDIPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [udiData, setUdiData] = useState<UDIData[]>([]);
  const [latestUDI, setLatestUDI] = useState<UDIData | null>(null);

  // Pesos to UDIs
  const [pesos, setPesos] = useState(searchParams.get('pesos') || '');
  const [selectedDate, setSelectedDate] = useState(searchParams.get('fecha') || '');
  const [resultUDIs, setResultUDIs] = useState<number | null>(null);

  // UDIs to Pesos
  const [udis, setUdis] = useState(searchParams.get('udis') || '');
  const [selectedDateReverse, setSelectedDateReverse] = useState(searchParams.get('fecha_reverse') || '');
  const [resultPesos, setResultPesos] = useState<number | null>(null);

  // Inflation adjustment
  const [amountOld, setAmountOld] = useState('');
  const [dateOld, setDateOld] = useState('');
  const [dateNew, setDateNew] = useState('');
  const [resultAdjusted, setResultAdjusted] = useState<{
    amountNew: number;
    inflation: number;
    udiOld: number;
    udiNew: number;
  } | null>(null);

  // Chart data
  const [chartData, setChartData] = useState<{ fecha: string; valor: number }[]>([]);

  useEffect(() => {
    const loadUDIData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${import.meta.env.BASE_URL}data/banxico/udis.json`);
        const data: UDIData[] = await response.json();
        setUdiData(data);

        // Get latest UDI
        const latest = data[data.length - 1];
        setLatestUDI(latest);

        // Set default dates to latest
        if (!selectedDate) setSelectedDate(latest.fecha);
        if (!selectedDateReverse) setSelectedDateReverse(latest.fecha);
        if (!dateNew) setDateNew(latest.fecha);

        // Prepare chart data (monthly averages for performance)
        const monthlyData: Record<string, { sum: number; count: number }> = {};
        data.forEach((item) => {
          const monthKey = item.fecha.substring(0, 7); // YYYY-MM
          if (!monthlyData[monthKey]) {
            monthlyData[monthKey] = { sum: 0, count: 0 };
          }
          monthlyData[monthKey].sum += item.valor;
          monthlyData[monthKey].count += 1;
        });

        const chart = Object.entries(monthlyData)
          .map(([fecha, { sum, count }]) => ({
            fecha: fecha + '-01',
            valor: sum / count,
          }))
          .sort((a, b) => a.fecha.localeCompare(b.fecha));

        setChartData(chart);
      } catch (error) {
        console.error('Error loading UDI data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadUDIData();
  }, []);

  const findUDIByDate = (date: string): UDIData | undefined => {
    return udiData.find((item) => item.fecha === date);
  };

  const handlePesosToUDI = () => {
    const p = parseFloat(pesos);
    const udi = findUDIByDate(selectedDate);

    if (!isNaN(p) && udi && udi.valor > 0) {
      setResultUDIs(p / udi.valor);
      // Update URL
      setSearchParams({ pesos: pesos, fecha: selectedDate });
    }
  };

  const handleUDIToPesos = () => {
    const u = parseFloat(udis);
    const udi = findUDIByDate(selectedDateReverse);

    if (!isNaN(u) && udi && udi.valor > 0) {
      setResultPesos(u * udi.valor);
      // Update URL
      setSearchParams({ udis: udis, fecha_reverse: selectedDateReverse });
    }
  };

  const handleInflationAdjust = () => {
    const amount = parseFloat(amountOld);
    const udiOld = findUDIByDate(dateOld);
    const udiNew = findUDIByDate(dateNew);

    if (!isNaN(amount) && udiOld && udiNew && udiOld.valor > 0 && udiNew.valor > 0) {
      // Convert to UDIs with old value, then back to pesos with new value
      const udisAmount = amount / udiOld.valor;
      const newAmount = udisAmount * udiNew.valor;
      const inflation = ((udiNew.valor - udiOld.valor) / udiOld.valor) * 100;

      setResultAdjusted({
        amountNew: newAmount,
        inflation,
        udiOld: udiOld.valor,
        udiNew: udiNew.valor,
      });
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: 'Calculadora de UDI - catalogmx',
        text: `Calculadora de UDI con datos desde ${latestUDI?.fecha}`,
        url: window.location.href,
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('Enlace copiado al portapapeles');
    }
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
          <h1 className="text-2xl font-bold">Calculadora de UDI Histórica</h1>
          <p className="text-muted-foreground mt-1">
            Unidad de Inversión - Datos históricos desde 1995 con {udiData.length.toLocaleString()} registros
          </p>
          {latestUDI && (
            <div className="flex gap-2 mt-2 flex-wrap">
              <Badge variant="secondary">
                UDI actual: ${latestUDI.valor.toFixed(6)} MXN
              </Badge>
              <Badge variant="outline">
                {format(new Date(latestUDI.fecha), "d 'de' MMMM, yyyy", { locale: es })}
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
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Evolución Histórica del UDI (1995-2025)
          </CardTitle>
          <CardDescription>
            Valor promedio mensual de la Unidad de Inversión
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorUdi" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis
                  dataKey="fecha"
                  tickFormatter={(value) => {
                    const date = new Date(value);
                    return format(date, 'yyyy', { locale: es });
                  }}
                  tick={{ fontSize: 12 }}
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  tickFormatter={(value) => `$${value.toFixed(1)}`}
                />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="rounded-lg border bg-background p-2 shadow-md">
                          <div className="text-xs text-muted-foreground">
                            {format(new Date(data.fecha), 'MMMM yyyy', { locale: es })}
                          </div>
                          <div className="font-bold text-primary">
                            ${data.valor.toFixed(6)} MXN
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="valor"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  fill="url(#colorUdi)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Pesos to UDIs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Pesos a UDIs
            </CardTitle>
            <CardDescription>
              Convierte un monto en pesos a UDIs para una fecha específica
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Monto en Pesos (MXN)</label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="number"
                  placeholder="100000"
                  value={pesos}
                  onChange={(e) => setPesos(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">
                <Calendar className="inline h-4 w-4 mr-1" />
                Fecha de consulta
              </label>
              <Input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                min="1995-04-04"
                max={latestUDI?.fecha}
              />
              {selectedDate && findUDIByDate(selectedDate) && (
                <div className="text-xs text-muted-foreground mt-1">
                  UDI: ${findUDIByDate(selectedDate)!.valor.toFixed(6)}
                </div>
              )}
            </div>
            <Button onClick={handlePesosToUDI} className="w-full">
              Calcular
            </Button>

            {resultUDIs !== null && (
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-sm text-muted-foreground mb-1">Resultado</div>
                <div className="text-2xl font-bold">
                  {resultUDIs.toFixed(6)} UDIs
                </div>
                <div className="text-xs text-muted-foreground mt-2">
                  ${pesos} MXN = {resultUDIs.toFixed(2)} UDIs
                  <br />
                  ({format(new Date(selectedDate), "d 'de' MMMM, yyyy", { locale: es })})
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* UDIs to Pesos */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              UDIs a Pesos
            </CardTitle>
            <CardDescription>
              Convierte UDIs a pesos mexicanos para una fecha específica
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Cantidad en UDIs</label>
              <Input
                type="number"
                placeholder="10000"
                value={udis}
                onChange={(e) => setUdis(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">
                <Calendar className="inline h-4 w-4 mr-1" />
                Fecha de consulta
              </label>
              <Input
                type="date"
                value={selectedDateReverse}
                onChange={(e) => setSelectedDateReverse(e.target.value)}
                min="1995-04-04"
                max={latestUDI?.fecha}
              />
              {selectedDateReverse && findUDIByDate(selectedDateReverse) && (
                <div className="text-xs text-muted-foreground mt-1">
                  UDI: ${findUDIByDate(selectedDateReverse)!.valor.toFixed(6)}
                </div>
              )}
            </div>
            <Button onClick={handleUDIToPesos} className="w-full">
              Calcular
            </Button>

            {resultPesos !== null && (
              <div className="p-4 bg-primary/10 rounded-lg text-center">
                <div className="text-sm text-muted-foreground mb-1">Resultado</div>
                <div className="text-2xl font-bold">
                  ${resultPesos.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN
                </div>
                <div className="text-xs text-muted-foreground mt-2">
                  {udis} UDIs × ${findUDIByDate(selectedDateReverse)?.valor.toFixed(6)}
                  <br />
                  ({format(new Date(selectedDateReverse), "d 'de' MMMM, yyyy", { locale: es })})
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Inflation Adjustment */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Ajuste por Inflación
          </CardTitle>
          <CardDescription>
            Calcula el valor equivalente de un monto entre dos fechas usando UDI
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid sm:grid-cols-3 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Monto Original (MXN)</label>
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  type="number"
                  placeholder="50000"
                  value={amountOld}
                  onChange={(e) => setAmountOld(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Fecha Original</label>
              <Input
                type="date"
                value={dateOld}
                onChange={(e) => setDateOld(e.target.value)}
                min="1995-04-04"
                max={latestUDI?.fecha}
              />
              {dateOld && findUDIByDate(dateOld) && (
                <div className="text-xs text-muted-foreground mt-1">
                  UDI: ${findUDIByDate(dateOld)!.valor.toFixed(6)}
                </div>
              )}
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Fecha Actual</label>
              <Input
                type="date"
                value={dateNew}
                onChange={(e) => setDateNew(e.target.value)}
                min="1995-04-04"
                max={latestUDI?.fecha}
              />
              {dateNew && findUDIByDate(dateNew) && (
                <div className="text-xs text-muted-foreground mt-1">
                  UDI: ${findUDIByDate(dateNew)!.valor.toFixed(6)}
                </div>
              )}
            </div>
          </div>

          <Button onClick={handleInflationAdjust} className="w-full">
            <TrendingUp className="h-4 w-4 mr-2" />
            Calcular Ajuste
          </Button>

          {resultAdjusted && (
            <div className="space-y-3">
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="p-4 bg-muted rounded-lg text-center">
                  <div className="text-sm text-muted-foreground">Monto Ajustado</div>
                  <div className="text-2xl font-bold text-primary">
                    ${resultAdjusted.amountNew.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
                  </div>
                </div>
                <div className="p-4 bg-muted rounded-lg text-center">
                  <div className="text-sm text-muted-foreground">Inflación Acumulada</div>
                  <div className="text-2xl font-bold">
                    {resultAdjusted.inflation > 0 ? '+' : ''}{resultAdjusted.inflation.toFixed(2)}%
                  </div>
                </div>
              </div>

              <div className="p-4 bg-primary/10 rounded-lg text-sm space-y-2">
                <div className="flex justify-between">
                  <span>Fecha origen:</span>
                  <span className="font-medium">{format(new Date(dateOld), "d 'de' MMMM, yyyy", { locale: es })}</span>
                </div>
                <div className="flex justify-between">
                  <span>Monto original:</span>
                  <span className="font-medium">${parseFloat(amountOld).toLocaleString()} MXN</span>
                </div>
                <div className="flex justify-between">
                  <span>UDI en {format(new Date(dateOld), 'yyyy', { locale: es })}:</span>
                  <span className="font-medium">${resultAdjusted.udiOld.toFixed(6)}</span>
                </div>
                <div className="flex justify-between text-muted-foreground">
                  <span>Equivalente en UDIs:</span>
                  <span>{(parseFloat(amountOld) / resultAdjusted.udiOld).toFixed(6)} UDIs</span>
                </div>
                <div className="border-t pt-2 mt-2">
                  <div className="flex justify-between">
                    <span>Fecha destino:</span>
                    <span className="font-medium">{format(new Date(dateNew), "d 'de' MMMM, yyyy", { locale: es })}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>UDI en {format(new Date(dateNew), 'yyyy', { locale: es })}:</span>
                    <span className="font-medium">${resultAdjusted.udiNew.toFixed(6)}</span>
                  </div>
                  <div className="flex justify-between font-bold pt-2 border-t mt-2">
                    <span>Monto ajustado:</span>
                    <span className="text-primary">${resultAdjusted.amountNew.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Documentation */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>¿Qué es la UDI?</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-3">
            <p>
              La <strong>Unidad de Inversión (UDI)</strong> es una unidad de cuenta creada por el Banco de México
              que mantiene constante el poder adquisitivo. Se ajusta diariamente según la inflación.
            </p>
            <p>
              <strong>Inicio:</strong> 4 de abril de 1995 con valor de $1.00 MXN
            </p>
            <p>
              <strong>Uso común:</strong> Créditos hipotecarios, inversiones a largo plazo, contratos indexados
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Datos Históricos</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-3">
            <div className="grid grid-cols-2 gap-3">
              {latestUDI && [
                { year: 1995, value: 1.0 },
                { year: 2000, value: 3.16 },
                { year: 2010, value: 4.56 },
                { year: 2020, value: 6.77 },
                { year: new Date(latestUDI.fecha).getFullYear(), value: latestUDI.valor },
              ].map((item) => (
                <div key={item.year} className="p-3 bg-muted rounded-lg">
                  <div className="text-xs text-muted-foreground font-semibold">{item.year}</div>
                  <div className="font-mono font-bold text-base">${item.value.toFixed(2)}</div>
                </div>
              ))}
            </div>
            <p className="text-xs mt-4">
              Fuente: Banco de México. Datos actualizados con {udiData.length.toLocaleString()} registros históricos.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
