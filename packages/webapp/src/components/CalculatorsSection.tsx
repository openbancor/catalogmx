import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calculator, DollarSign, Percent, Info } from 'lucide-react';
import { calculateISR, calculateIVA, calculateIEPS, IEPS_RATES, type ISRCalculationResult } from '@/lib/calculators';

export default function CalculatorsSection() {
  return (
    <div className="space-y-8">
      <div className="text-center max-w-2xl mx-auto">
        <h2 className="text-3xl font-bold mb-2">Tax Calculators</h2>
        <p className="text-muted-foreground">
          Calculate Mexican taxes with step-by-step breakdowns: ISR, IVA, IEPS
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <ISRCalculator />
        <div className="space-y-6">
          <IVACalculator />
          <IEPSCalculator />
        </div>
      </div>
    </div>
  );
}

function ISRCalculator() {
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
    <Card className="lg:row-span-2">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="h-5 w-5" />
          ISR Calculator
          <Badge variant="outline">2024</Badge>
        </CardTitle>
        <CardDescription>
          Impuesto Sobre la Renta with step-by-step breakdown and subsidy calculation
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
              <option value="mensual">Monthly</option>
              <option value="quincenal">Biweekly</option>
              <option value="semanal">Weekly</option>
              <option value="anual">Annual</option>
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
                <div>Upper Limit: ${result.bracket.limiteSuperior === Infinity ? '∞' : result.bracket.limiteSuperior.toFixed(2)}</div>
                <div>Fixed Fee: ${result.bracket.cuotaFija.toFixed(2)}</div>
                <div>Marginal Rate: {result.bracket.tasa}%</div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function IVACalculator() {
  const [base, setBase] = useState('');
  const [rate, setRate] = useState(16);
  const [result, setResult] = useState<ReturnType<typeof calculateIVA> | null>(null);

  const handleCalculate = () => {
    const value = parseFloat(base);
    if (!isNaN(value) && value > 0) {
      setResult(calculateIVA(value, rate));
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Percent className="h-4 w-4" />
          IVA Calculator
        </CardTitle>
        <CardDescription>Impuesto al Valor Agregado (Value Added Tax)</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-sm font-medium mb-1 block">Base Amount</label>
            <Input
              type="number"
              placeholder="1000"
              value={base}
              onChange={(e) => setBase(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Rate</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={rate}
              onChange={(e) => setRate(parseInt(e.target.value))}
            >
              <option value={16}>16% (Standard)</option>
              <option value={8}>8% (Border Zone)</option>
              <option value={0}>0% (Exempt)</option>
            </select>
          </div>
        </div>

        <Button onClick={handleCalculate} size="sm" className="w-full">
          Calculate
        </Button>

        {result && (
          <div className="space-y-2 p-4 bg-muted rounded-lg font-mono text-sm">
            {result.desglose.map((item, i) => (
              <div key={i} className={`flex justify-between ${i === result.desglose.length - 1 ? 'font-bold pt-2 border-t' : ''}`}>
                <span>{item.concepto}</span>
                <span>${item.monto.toFixed(2)}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function IEPSCalculator() {
  const [base, setBase] = useState('');
  const [product, setProduct] = useState('bebidas_azucaradas');
  const [result, setResult] = useState<ReturnType<typeof calculateIEPS> | null>(null);

  const handleCalculate = () => {
    const value = parseFloat(base);
    if (!isNaN(value) && value > 0) {
      setResult(calculateIEPS(value, product));
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <DollarSign className="h-4 w-4" />
          IEPS Calculator
        </CardTitle>
        <CardDescription>Impuesto Especial sobre Producción y Servicios</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-sm font-medium mb-1 block">Base Amount</label>
            <Input
              type="number"
              placeholder="1000"
              value={base}
              onChange={(e) => setBase(e.target.value)}
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Product</label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={product}
              onChange={(e) => setProduct(e.target.value)}
            >
              {IEPS_RATES.map(r => (
                <option key={r.product} value={r.product}>
                  {r.name} ({r.rate}%)
                </option>
              ))}
            </select>
          </div>
        </div>

        <Button onClick={handleCalculate} size="sm" className="w-full">
          Calculate
        </Button>

        {result && (
          <div className="space-y-3">
            <div className="p-3 bg-muted rounded-lg text-sm">
              <div className="text-xs text-muted-foreground mb-1">{result.product.description}</div>
              <div className="font-medium">{result.product.name}</div>
            </div>
            <div className="space-y-2 p-4 bg-primary/10 rounded-lg font-mono text-sm">
              <div className="flex justify-between">
                <span>Base</span>
                <span>${result.base.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>IEPS ({result.product.rate}%)</span>
                <span>${result.ieps.toFixed(2)}</span>
              </div>
              <div className="flex justify-between font-bold pt-2 border-t">
                <span>Total</span>
                <span>${result.total.toFixed(2)}</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
