import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calculator, DollarSign, Info, TrendingDown, TrendingUp } from 'lucide-react';
import { calculateISR, type ISRCalculationResult, type ISRYear, type ISRPeriod } from '@/lib/calculators';
import { useLocale } from '@/lib/locale';

export default function ISRPage() {
  const { t } = useLocale();
  const [income, setIncome] = useState('');
  const [period, setPeriod] = useState<ISRPeriod>('mensual');
  const [year, setYear] = useState<ISRYear>(2026);
  const [result, setResult] = useState<ISRCalculationResult | null>(null);
  const [showComparison, setShowComparison] = useState(false);

  const handleCalculate = () => {
    const value = parseFloat(income);
    if (!isNaN(value) && value > 0) {
      setResult(calculateISR(value, period, year));
    }
  };

  const yearComparison = income && parseFloat(income) > 0 ? {
    2024: calculateISR(parseFloat(income), period, 2024),
    2025: calculateISR(parseFloat(income), period, 2025),
    2026: calculateISR(parseFloat(income), period, 2026)
  } : null;

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">{t('calculators.isr.title')}</h1>
        <p className="text-muted-foreground mt-1">
          {t('calculators.isr.subtitle')}
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Calculator */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              {t('calculators.isr.card.title')}
              <Badge variant={year === 2026 ? 'default' : 'outline'}>{year}</Badge>
              {year === 2026 && <Badge variant="secondary" className="text-xs">Vigente</Badge>}
            </CardTitle>
            <CardDescription>
              {year === 2026 && 'Tarifas actualizadas 13.21% por inflación acumulada. Vigentes desde enero 2026.'}
              {year === 2025 && 'Tarifas iguales a 2024. Subsidio al empleo: cuota fija $475 mensual.'}
              {year === 2024 && 'Tarifas base. Subsidio al empleo: sistema escalonado.'}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid sm:grid-cols-3 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">{t('calculators.isr.label.income')}</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="number"
                    placeholder="15000"
                    value={income}
                    onChange={(e) => setIncome(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleCalculate()}
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">{t('calculators.isr.label.period')}</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={period}
                  onChange={(e) => setPeriod(e.target.value as ISRPeriod)}
                >
                  <option value="diaria">Diaria</option>
                  <option value="semanal">Semanal (7 días)</option>
                  <option value="decenal">Decenal (10 días)</option>
                  <option value="quincenal">Quincenal (15 días)</option>
                  <option value="mensual">Mensual</option>
                  <option value="anual">Anual</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Año fiscal</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-medium"
                  value={year}
                  onChange={(e) => setYear(parseInt(e.target.value) as ISRYear)}
                >
                  <option value="2026">2026 (Vigente)</option>
                  <option value="2025">2025</option>
                  <option value="2024">2024</option>
                </select>
              </div>
            </div>

            <div className="flex gap-2">
              <Button onClick={handleCalculate} className="flex-1">
                <Calculator className="h-4 w-4 mr-2" />
                {t('calculators.isr.button.calculate')}
              </Button>
              {income && parseFloat(income) > 0 && (
                <Button
                  variant="outline"
                  onClick={() => setShowComparison(!showComparison)}
                  className="whitespace-nowrap"
                >
                  {showComparison ? 'Ocultar' : 'Comparar años'}
                </Button>
              )}
            </div>

            {result && (
              <div className="space-y-4">
                {/* Summary */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-primary/10 rounded-lg text-center">
                    <div className="text-sm text-muted-foreground">{t('calculators.isr.result.pay')}</div>
                    <div className="text-2xl font-bold text-primary">
                      ${result.isrFinal.toFixed(2)}
                    </div>
                  </div>
                  <div className="p-4 bg-muted rounded-lg text-center">
                    <div className="text-sm text-muted-foreground">{t('calculators.isr.result.rate')}</div>
                    <div className="text-2xl font-bold">
                      {result.tasaEfectiva.toFixed(2)}%
                    </div>
                  </div>
                </div>

                {/* Step by step breakdown */}
                <div className="border rounded-lg overflow-hidden">
                  <div className="bg-muted px-4 py-2 font-medium flex items-center gap-2">
                    <Info className="h-4 w-4" />
                    {t('calculators.isr.steps.title')}
                  </div>
                  <div className="divide-y">
                    {result.steps.map((step) => (
                      <div key={step.step} className="p-4">
                        <div className="flex items-start gap-3">
                          <div className="w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm flex items-center justify-center flex-shrink-0">
                            {step.step}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="font-medium">{step.description}</div>
                            <div className="text-sm text-muted-foreground font-mono mt-1">
                              {step.formula}
                            </div>
                            {step.details && (
                              <div className="text-xs text-muted-foreground mt-1">
                                {step.details}
                              </div>
                            )}
                          </div>
                          <div className="text-right font-mono font-medium">
                            ${step.result.toFixed(2)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Bracket info */}
                <div className="p-4 bg-muted/50 rounded-lg text-sm">
                  <div className="font-medium mb-2">{t('calculators.isr.bracket.title')}</div>
                  <div className="grid grid-cols-2 gap-2 text-muted-foreground">
                    <div>{t('calculators.isr.bracket.lower')}: ${result.bracket.limiteInferior.toFixed(2)}</div>
                    <div>{t('calculators.isr.bracket.upper')}: ${result.bracket.limiteSuperior === Infinity ? '∞' : result.bracket.limiteSuperior.toFixed(2)}</div>
                    <div>{t('calculators.isr.bracket.fixed')}: ${result.bracket.cuotaFija.toFixed(2)}</div>
                    <div>{t('calculators.isr.bracket.rate')}: {result.bracket.tasa}%</div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info Panel */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Tarifas {year}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                {year === 2026 ? (
                  <>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$0.01 - $844.59</span>
                      <span className="font-mono">1.92%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$844.60 - $7,168.51</span>
                      <span className="font-mono">6.40%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$7,168.52 - $12,598.02</span>
                      <span className="font-mono">10.88%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$12,598.03 - $14,644.64</span>
                      <span className="font-mono">16.00%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$14,644.65 - $17,533.64</span>
                      <span className="font-mono">17.92%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$17,533.65 - $35,362.83</span>
                      <span className="font-mono">21.36%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$35,362.84+</span>
                      <span className="font-mono">23.52-35%</span>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$0.01 - $746.04</span>
                      <span className="font-mono">1.92%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$746.05 - $6,332.05</span>
                      <span className="font-mono">6.40%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$6,332.06 - $11,128.01</span>
                      <span className="font-mono">10.88%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$11,128.02 - $12,935.82</span>
                      <span className="font-mono">16.00%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$12,935.83 - $15,487.71</span>
                      <span className="font-mono">17.92%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$15,487.72 - $31,236.49</span>
                      <span className="font-mono">21.36%</span>
                    </div>
                    <div className="flex justify-between p-2 bg-muted rounded">
                      <span>$31,236.50+</span>
                      <span className="font-mono">23.52-35%</span>
                    </div>
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Subsidio al empleo {year}</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground space-y-2">
              {year === 2024 && (
                <p>Sistema escalonado con 11 rangos de ingreso. El subsidio disminuye conforme aumenta el ingreso, hasta $0 para ingresos mayores a $7,382.33 mensuales.</p>
              )}
              {year === 2025 && (
                <>
                  <p><strong>Cuota fija:</strong> $475.00 mensuales</p>
                  <p><strong>Aplica hasta:</strong> $10,171.00 de ingreso mensual</p>
                  <p className="text-xs">Cambio implementado por decreto en mayo 2024.</p>
                </>
              )}
              {year === 2026 && (
                <>
                  <p><strong>Cuota fija:</strong> $536.21 mensuales</p>
                  <p><strong>Aplica hasta:</strong> $11,492.66 de ingreso mensual</p>
                  <p className="text-xs">Calculado como 15.02% del UMA mensual vigente.</p>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Year Comparison */}
      {showComparison && yearComparison && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5" />
              Comparación entre años fiscales
            </CardTitle>
            <CardDescription>
              Compara cuánto ISR pagarías en diferentes años con el mismo ingreso
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              {([2024, 2025, 2026] as const).map((y) => {
                const res = yearComparison[y];
                const isBest = res.isrFinal === Math.min(yearComparison[2024].isrFinal, yearComparison[2025].isrFinal, yearComparison[2026].isrFinal);
                const diff2024 = res.isrFinal - yearComparison[2024].isrFinal;

                return (
                  <div key={y} className={`p-4 rounded-lg border-2 ${y === year ? 'border-primary bg-primary/5' : 'border-border'} ${isBest ? 'bg-green-500/5' : ''}`}>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-lg">{y}</h3>
                        {y === 2026 && <Badge variant="secondary" className="text-xs">Vigente</Badge>}
                        {isBest && <Badge variant="default" className="text-xs bg-green-600">Menor ISR</Badge>}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div>
                        <div className="text-xs text-muted-foreground">ISR a pagar</div>
                        <div className="text-2xl font-bold">${res.isrFinal.toFixed(2)}</div>
                      </div>

                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Tasa efectiva</span>
                        <span className="font-mono font-medium">{res.tasaEfectiva.toFixed(2)}%</span>
                      </div>

                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Subsidio</span>
                        <span className="font-mono">${res.subsidio.toFixed(2)}</span>
                      </div>

                      {y !== 2024 && (
                        <div className={`flex items-center gap-1 text-sm pt-2 border-t ${diff2024 < 0 ? 'text-green-600' : diff2024 > 0 ? 'text-red-600' : 'text-muted-foreground'}`}>
                          {diff2024 < 0 ? (
                            <><TrendingDown className="h-3 w-3" /> Ahorras ${Math.abs(diff2024).toFixed(2)} vs 2024</>
                          ) : diff2024 > 0 ? (
                            <><TrendingUp className="h-3 w-3" /> Pagas ${diff2024.toFixed(2)} más vs 2024</>
                          ) : (
                            <>Igual que 2024</>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="mt-4 p-3 bg-muted/50 rounded-lg text-sm text-muted-foreground">
              <strong>Nota:</strong> Las diferencias se deben principalmente a los cambios en el subsidio al empleo y la actualización de tarifas por inflación en 2026.
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
