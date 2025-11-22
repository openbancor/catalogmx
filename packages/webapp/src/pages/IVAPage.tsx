import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DollarSign, Calculator, ArrowRight } from 'lucide-react';
import { calculateIVA } from '@/lib/calculators';

export default function IVAPage() {
  const [base, setBase] = useState('');
  const [rate, setRate] = useState(16);
  const [result, setResult] = useState<ReturnType<typeof calculateIVA> | null>(null);

  // Reverse calculator
  const [total, setTotal] = useState('');
  const [reverseRate, setReverseRate] = useState(16);
  const [reverseResult, setReverseResult] = useState<{ base: number; iva: number; total: number } | null>(null);

  const handleCalculate = () => {
    const value = parseFloat(base);
    if (!isNaN(value) && value > 0) {
      setResult(calculateIVA(value, rate));
    }
  };

  const handleReverseCalculate = () => {
    const value = parseFloat(total);
    if (!isNaN(value) && value > 0) {
      const baseAmount = value / (1 + reverseRate / 100);
      const ivaAmount = value - baseAmount;
      setReverseResult({
        base: baseAmount,
        iva: ivaAmount,
        total: value
      });
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">IVA Calculator</h1>
        <p className="text-muted-foreground mt-1">
          Impuesto al Valor Agregado - Mexican Value Added Tax
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Standard Calculator */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Calculate IVA from Base
            </CardTitle>
            <CardDescription>
              Enter base amount to calculate IVA and total
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1 block">Base Amount (MXN)</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="number"
                    placeholder="1000"
                    value={base}
                    onChange={(e) => setBase(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">IVA Rate</label>
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

            <Button onClick={handleCalculate} className="w-full">
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

        {/* Reverse Calculator */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ArrowRight className="h-5 w-5 rotate-180" />
              Extract IVA from Total
            </CardTitle>
            <CardDescription>
              Enter total amount to extract base and IVA
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1 block">Total Amount (MXN)</label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="number"
                    placeholder="1160"
                    value={total}
                    onChange={(e) => setTotal(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium mb-1 block">IVA Rate</label>
                <select
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={reverseRate}
                  onChange={(e) => setReverseRate(parseInt(e.target.value))}
                >
                  <option value={16}>16% (Standard)</option>
                  <option value={8}>8% (Border Zone)</option>
                </select>
              </div>
            </div>

            <Button onClick={handleReverseCalculate} className="w-full">
              Extract
            </Button>

            {reverseResult && (
              <div className="space-y-2 p-4 bg-primary/10 rounded-lg font-mono text-sm">
                <div className="flex justify-between">
                  <span>Base (Subtotal)</span>
                  <span>${reverseResult.base.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span>IVA ({reverseRate}%)</span>
                  <span>${reverseResult.iva.toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-bold pt-2 border-t">
                  <span>Total</span>
                  <span>${reverseResult.total.toFixed(2)}</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Documentation */}
      <div className="grid lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Badge className="bg-blue-600">16%</Badge>
              Standard Rate
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            <p>
              The general IVA rate in Mexico is 16%. This applies to most goods and services
              throughout the country.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Badge className="bg-green-600">8%</Badge>
              Border Zone Rate
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            <p>
              A reduced rate of 8% applies in the northern and southern border zones
              (franja fronteriza) as an economic stimulus measure.
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Badge variant="outline">0%</Badge>
              Zero Rate / Exempt
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            <p>
              Certain essential goods are taxed at 0% rate, including basic food items,
              medicines, and books. Exempt items include housing sales and medical services.
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>IVA Calculation Formula</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid sm:grid-cols-2 gap-4 text-sm">
            <div className="p-4 bg-muted rounded-lg">
              <div className="font-medium mb-2">From Base to Total</div>
              <div className="font-mono space-y-1">
                <div>IVA = Base x Rate</div>
                <div>Total = Base + IVA</div>
                <div className="text-muted-foreground">Total = Base x (1 + Rate)</div>
              </div>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <div className="font-medium mb-2">From Total to Base</div>
              <div className="font-mono space-y-1">
                <div>Base = Total / (1 + Rate)</div>
                <div>IVA = Total - Base</div>
                <div className="text-muted-foreground">IVA = Total x Rate / (1 + Rate)</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
