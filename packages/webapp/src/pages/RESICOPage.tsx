import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calculator, DollarSign, Info, AlertCircle, CheckCircle2 } from 'lucide-react';
import { calculateRESICO, type RESICOCalculationResult, type RESICOYear, type RESICOPeriod } from '@/lib/calculators';
export default function RESICOPage() {
  const [income, setIncome] = useState('');
  const [period, setPeriod] = useState<RESICOPeriod>('mensual');
  const [year, setYear] = useState<RESICOYear>(2026);
  const [result, setResult] = useState<RESICOCalculationResult | null>(null);

  const handleCalculate = () => {
    const value = parseFloat(income);
    if (!isNaN(value) && value > 0) {
      setResult(calculateRESICO(value, period, year));
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const yearComparison = income && parseFloat(income) > 0 ? {
    2024: calculateRESICO(parseFloat(income), period, 2024),
    2025: calculateRESICO(parseFloat(income), period, 2025),
    2026: calculateRESICO(parseFloat(income), period, 2026)
  } : null;

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">Calculadora RESICO</h1>
        <p className="text-muted-foreground mt-1">
          Régimen Simplificado de Confianza (Artículo 113-E LISR)
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Calculator */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Calculadora RESICO
              <Badge variant={year === 2026 ? 'default' : 'outline'}>{year}</Badge>
              {year === 2026 && <Badge variant="secondary" className="text-xs">Vigente</Badge>}
            </CardTitle>
            <CardDescription>
              {year === 2026 && 'Tarifas vigentes desde enero 2026. Sistema de tasa directa sobre ingresos totales.'}
              {year === 2025 && 'Tarifas 2025. Sistema de tasa directa sin deducciones.'}
              {year === 2024 && 'Tarifas 2024. Régimen simplificado para personas físicas.'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid sm:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Ingreso Total</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="number"
                    placeholder="50000"
                    value={income}
                    onChange={(e) => setIncome(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleCalculate()}
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Período</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={period}
                  onChange={(e) => setPeriod(e.target.value as RESICOPeriod)}
                >
                  <option value="mensual">Mensual</option>
                  <option value="anual">Anual</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Año fiscal</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-medium"
                  value={year}
                  onChange={(e) => setYear(parseInt(e.target.value) as RESICOYear)}
                >
                  <option value="2026">2026 (Vigente)</option>
                  <option value="2025">2025</option>
                  <option value="2024">2024</option>
                </select>
              </div>
            </div>

            <Button
              onClick={handleCalculate}
              disabled={!income || parseFloat(income) <= 0}
              className="w-full"
              size="lg"
            >
              <Calculator className="mr-2 h-4 w-4" />
              Calcular RESICO
            </Button>

            {/* Results */}
            {result && (
              <div className="space-y-4 pt-4 border-t">
                {/* Limit warning */}
                {!result.dentroDeLimite && (
                  <div className="flex items-start gap-2 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                    <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
                    <div className="text-sm">
                      <p className="font-medium text-destructive">Ingreso excede límite RESICO</p>
                      <p className="text-muted-foreground">
                        Límite {period === 'mensual' ? 'mensual' : 'anual'}: {formatCurrency(result.limiteMaximo)}
                      </p>
                    </div>
                  </div>
                )}

                {result.dentroDeLimite && (
                  <div className="flex items-start gap-2 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                    <CheckCircle2 className="h-5 w-5 text-green-600 mt-0.5" />
                    <div className="text-sm">
                      <p className="font-medium text-green-700 dark:text-green-400">Dentro del límite RESICO</p>
                      <p className="text-muted-foreground">
                        Límite {period === 'mensual' ? 'mensual' : 'anual'}: {formatCurrency(result.limiteMaximo)}
                      </p>
                    </div>
                  </div>
                )}

                {/* Main result */}
                <div className="bg-primary/5 border border-primary/20 rounded-xl p-6">
                  <div className="text-sm text-muted-foreground mb-1">ISR RESICO a pagar</div>
                  <div className="text-4xl font-bold text-primary mb-4">
                    {formatCurrency(result.resicoCalculado)}
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Ingreso base:</span>
                      <p className="font-semibold">{formatCurrency(result.ingreso)}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Tasa aplicada:</span>
                      <p className="font-semibold">{result.bracket.tasa}%</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Tasa efectiva:</span>
                      <p className="font-semibold">{result.tasaEfectiva.toFixed(2)}%</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Neto después de ISR:</span>
                      <p className="font-semibold text-green-600 dark:text-green-400">
                        {formatCurrency(result.ingreso - result.resicoCalculado)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Bracket details */}
                <div className="bg-muted/50 rounded-lg p-4">
                  <div className="text-sm font-medium mb-2 flex items-center gap-2">
                    <Info className="h-4 w-4" />
                    Bracket aplicado
                  </div>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p>Rango: {formatCurrency(result.bracket.limiteInferior)} - {formatCurrency(result.bracket.limiteSuperior)}</p>
                    <p>Tasa directa: {result.bracket.tasa}%</p>
                    <p className="pt-2 border-t border-border/50">
                      <strong>Cálculo:</strong> {formatCurrency(result.ingreso)} × {result.bracket.tasa}% = {formatCurrency(result.resicoCalculado)}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info & Comparison */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">¿Qué es RESICO?</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              <p>
                El <strong>Régimen Simplificado de Confianza</strong> (RESICO) es un esquema fiscal opcional para personas físicas y morales con ingresos menores a $3.5M anuales.
              </p>
              <div className="pt-2 border-t space-y-1">
                <p className="font-medium text-foreground">Características:</p>
                <ul className="list-disc list-inside space-y-1 pl-2">
                  <li>Tasa directa sobre ingresos (sin deducciones)</li>
                  <li>No hay cuota fija ni cálculo marginal</li>
                  <li>Tasas progresivas: 1.0%, 1.1%, 1.5%, 2.0%, 2.5%</li>
                  <li>Límite: $291,666/mes o $3.5M/año</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          {/* Year comparison */}
          {yearComparison && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Comparación anual</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[2026, 2025, 2024].map((y) => {
                  const r = yearComparison[y as RESICOYear];
                  return (
                    <div key={y} className={`p-3 rounded-lg border ${y === year ? 'bg-primary/5 border-primary/30' : 'bg-muted/30'}`}>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-semibold">{y}</span>
                        {y === year && <Badge variant="default" className="text-xs">Actual</Badge>}
                      </div>
                      <div className="text-xs text-muted-foreground space-y-0.5">
                        <div className="flex justify-between">
                          <span>Tasa:</span>
                          <span className="font-medium text-foreground">{r.bracket.tasa}%</span>
                        </div>
                        <div className="flex justify-between">
                          <span>ISR:</span>
                          <span className="font-semibold">{formatCurrency(r.resicoCalculado)}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
