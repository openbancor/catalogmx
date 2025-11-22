import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calculator, DollarSign, Info } from 'lucide-react';
import { calculateISR, type ISRCalculationResult } from '@/lib/calculators';

export default function ISRPage() {
  const [income, setIncome] = useState('');
  const [period, setPeriod] = useState<'mensual' | 'quincenal' | 'semanal' | 'anual'>('mensual');
  const [result, setResult] = useState<ISRCalculationResult | null>(null);

  const handleCalculate = () => {
    const value = parseFloat(income);
    if (!isNaN(value) && value > 0) {
      setResult(calculateISR(value, period));
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">ISR Calculator</h1>
        <p className="text-muted-foreground mt-1">
          Impuesto Sobre la Renta - Mexican income tax with 2024 brackets and employment subsidy
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Calculator */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Calculate ISR
              <Badge variant="outline">2024</Badge>
            </CardTitle>
            <CardDescription>
              Enter taxable income to calculate ISR with step-by-step breakdown
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Taxable Income (MXN)</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="number"
                    placeholder="15000"
                    value={income}
                    onChange={(e) => setIncome(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Period</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={period}
                  onChange={(e) => setPeriod(e.target.value as typeof period)}
                >
                  <option value="mensual">Monthly (Mensual)</option>
                  <option value="quincenal">Biweekly (Quincenal)</option>
                  <option value="semanal">Weekly (Semanal)</option>
                  <option value="anual">Annual (Anual)</option>
                </select>
              </div>
            </div>

            <Button onClick={handleCalculate} className="w-full">
              <Calculator className="h-4 w-4 mr-2" />
              Calculate ISR
            </Button>

            {result && (
              <div className="space-y-4">
                {/* Summary */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-primary/10 rounded-lg text-center">
                    <div className="text-sm text-muted-foreground">ISR to Pay</div>
                    <div className="text-2xl font-bold text-primary">
                      ${result.isrFinal.toFixed(2)}
                    </div>
                  </div>
                  <div className="p-4 bg-muted rounded-lg text-center">
                    <div className="text-sm text-muted-foreground">Effective Rate</div>
                    <div className="text-2xl font-bold">
                      {result.tasaEfectiva.toFixed(2)}%
                    </div>
                  </div>
                </div>

                {/* Step by step breakdown */}
                <div className="border rounded-lg overflow-hidden">
                  <div className="bg-muted px-4 py-2 font-medium flex items-center gap-2">
                    <Info className="h-4 w-4" />
                    Step-by-Step Calculation
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
                  <div className="font-medium mb-2">Applied Bracket</div>
                  <div className="grid grid-cols-2 gap-2 text-muted-foreground">
                    <div>Lower Limit: ${result.bracket.limiteInferior.toFixed(2)}</div>
                    <div>Upper Limit: ${result.bracket.limiteSuperior === Infinity ? 'unlimited' : result.bracket.limiteSuperior.toFixed(2)}</div>
                    <div>Fixed Fee: ${result.bracket.cuotaFija.toFixed(2)}</div>
                    <div>Marginal Rate: {result.bracket.tasa}%</div>
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
              <CardTitle className="text-lg">2024 Monthly Brackets</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
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
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Employment Subsidy</CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-muted-foreground">
              <p>
                The employment subsidy (subsidio al empleo) reduces ISR for low-income workers.
                It applies to monthly incomes up to $7,382.33 and can result in zero or even
                negative ISR (refund).
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
