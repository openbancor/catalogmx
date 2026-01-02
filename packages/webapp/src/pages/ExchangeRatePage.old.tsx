import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { ArrowRightLeft, Calculator, TrendingUp } from 'lucide-react';

interface ExchangeRate {
  fecha: string;
  tipo_cambio: number;
  tipo: string;
}

export default function ExchangeRatePage() {
  const [amount, setAmount] = useState<string>('1000');
  const [fromCurrency, setFromCurrency] = useState<'MXN' | 'USD'>('USD');
  const [toCurrency, setToCurrency] = useState<'MXN' | 'USD'>('MXN');
  const [result, setResult] = useState<number | null>(null);
  const [currentRate, setCurrentRate] = useState<ExchangeRate | null>(null);

  // Load current exchange rate
  useEffect(() => {
    const loadCurrentRate = async () => {
      try {
        const response = await fetch('/data/banxico/tipo_cambio_usd.json');
        const data: ExchangeRate[] = await response.json();

        // Get the most recent rate
        const latestRate = data
          .filter(rate => rate.tipo === 'oficial_banxico_fix')
          .sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime())[0];

        setCurrentRate(latestRate);
      } catch (error) {
        console.error('Failed to load exchange rate:', error);
      }
    };

    loadCurrentRate();
  }, []);

  const calculateConversion = () => {
    if (!currentRate || !amount) return;

    const numAmount = parseFloat(amount);
    if (isNaN(numAmount)) return;

    let convertedAmount: number;

    if (fromCurrency === 'USD' && toCurrency === 'MXN') {
      // USD to MXN
      convertedAmount = numAmount * currentRate.tipo_cambio;
    } else if (fromCurrency === 'MXN' && toCurrency === 'USD') {
      // MXN to USD
      convertedAmount = numAmount / currentRate.tipo_cambio;
    } else {
      // Same currency
      convertedAmount = numAmount;
    }

    setResult(convertedAmount);
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
      maximumFractionDigits: 2,
    }).format(value);
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-primary/15 text-primary">
          <Calculator className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Calculadora de Tipo de Cambio</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Convierte entre pesos mexicanos y dólares estadounidenses usando el tipo de cambio FIX oficial de Banxico.
          </p>
        </div>
      </div>

      {/* Current Rate Display */}
      {currentRate && (
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-lg flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Tipo de Cambio Actual
            </CardTitle>
            <CardDescription>
              Tipo de cambio FIX - Fecha de determinación
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="text-2xl font-bold">
                1 USD = {currentRate.tipo_cambio.toFixed(4)} MXN
              </div>
              <Badge variant="secondary">
                {new Date(currentRate.fecha).toLocaleDateString('es-MX', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric'
                })}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Fuente: Banco de México - Tipo de cambio FIX
            </p>
          </CardContent>
        </Card>
      )}

      {/* Calculator */}
      <Card>
        <CardHeader>
          <CardTitle>Conversión de Moneda</CardTitle>
          <CardDescription>
            Ingresa el monto a convertir y selecciona las monedas
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Amount Input */}
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

          {/* Currency Selection */}
          <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-4 items-end">
            <div className="space-y-2">
              <Label htmlFor="from-currency">De</Label>
              <select
                id="from-currency"
                value={fromCurrency}
                onChange={(e) => setFromCurrency(e.target.value as 'MXN' | 'USD')}
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="USD">USD - Dólar estadounidense</option>
                <option value="MXN">MXN - Peso mexicano</option>
              </select>
            </div>

            <div className="flex justify-center">
              <Button
                variant="outline"
                size="icon"
                onClick={swapCurrencies}
                className="rounded-full"
              >
                <ArrowRightLeft className="h-4 w-4" />
              </Button>
            </div>

            <div className="space-y-2">
              <Label htmlFor="to-currency">A</Label>
              <select
                id="to-currency"
                value={toCurrency}
                onChange={(e) => setToCurrency(e.target.value as 'MXN' | 'USD')}
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="MXN">MXN - Peso mexicano</option>
                <option value="USD">USD - Dólar estadounidense</option>
              </select>
            </div>
          </div>

          {/* Calculate Button */}
          <Button
            onClick={calculateConversion}
            className="w-full"
            disabled={!currentRate}
          >
            Convertir
          </Button>

          {/* Result */}
          {result !== null && (
            <div className="pt-4 border-t">
              <div className="text-center space-y-2">
                <p className="text-sm text-muted-foreground">Resultado</p>
                <p className="text-3xl font-bold">
                  {formatCurrency(result, toCurrency)}
                </p>
                <p className="text-sm text-muted-foreground">
                  {formatCurrency(parseFloat(amount), fromCurrency)} = {formatCurrency(result, toCurrency)}
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Additional Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Información Importante</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <p>
            <strong>Tipo de cambio FIX:</strong> Es el tipo de cambio de referencia que utiliza Banxico para operaciones oficiales.
          </p>
          <p>
            <strong>Fecha de determinación:</strong> Se calcula el día hábil anterior y se utiliza para operaciones del día siguiente.
          </p>
          <p>
            <strong>Uso en facturación:</strong> Para efectos fiscales y contables, utiliza el tipo de cambio del día de la operación.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
