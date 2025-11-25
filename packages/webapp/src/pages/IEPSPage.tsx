import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DollarSign, Calculator, Wine, Cigarette, Fuel, Coffee } from 'lucide-react';
import { calculateIEPS, IEPS_RATES } from '@/lib/calculators';
import { useLocale } from '@/lib/locale';

export default function IEPSPage() {
  const { t } = useLocale();
  const [base, setBase] = useState('');
  const [product, setProduct] = useState('bebidas_azucaradas');
  const [result, setResult] = useState<ReturnType<typeof calculateIEPS> | null>(null);

  const handleCalculate = () => {
    const value = parseFloat(base);
    if (!isNaN(value) && value > 0) {
      setResult(calculateIEPS(value, product));
    }
  };

  const getIcon = (productType: string) => {
    if (productType.includes('alcohol')) return Wine;
    if (productType === 'tabaco') return Cigarette;
    if (productType === 'gasolina') return Fuel;
    return Coffee;
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">{t('calculators.ieps.title')}</h1>
        <p className="text-muted-foreground mt-1">
          {t('calculators.ieps.subtitle')}
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Calculator */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              {t('calculators.ieps.card.calc.title')}
            </CardTitle>
            <CardDescription>
              {t('calculators.ieps.card.calc.desc')}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm font-medium mb-1 block">{t('calculators.ieps.label.base')}</label>
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
                <label className="text-sm font-medium mb-1 block">{t('calculators.ieps.label.product')}</label>
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

            <Button onClick={handleCalculate} className="w-full">
              {t('calculators.ieps.button.calculate')}
            </Button>

            {result && (
              <div className="space-y-3">
                <div className="p-3 bg-muted rounded-lg text-sm">
                  <div className="text-xs text-muted-foreground mb-1">{result.product.description}</div>
                  <div className="font-medium">{result.product.name}</div>
                </div>
                <div className="space-y-2 p-4 bg-primary/10 rounded-lg font-mono text-sm">
                  <div className="flex justify-between">
                    <span>{t('calculators.ieps.result.base')}</span>
                    <span>${result.base.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>IEPS ({result.product.rate}%)</span>
                    <span>${result.ieps.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between font-bold pt-2 border-t">
                    <span>{t('calculators.ieps.result.total')}</span>
                    <span>${result.total.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Reference */}
        <Card>
          <CardHeader>
            <CardTitle>{t('calculators.ieps.info.rates')}</CardTitle>
            <CardDescription>
              Tasas actuales de IEPS por categoría
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {IEPS_RATES.map(rate => {
              const Icon = getIcon(rate.product);
              return (
                <div key={rate.product} className="p-3 bg-muted rounded-lg flex items-start gap-3">
                  <Icon className="h-5 w-5 text-muted-foreground flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">{rate.name}</span>
                      <Badge variant="secondary" className="font-mono">{rate.rate}%</Badge>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">{rate.description}</div>
                  </div>
                </div>
              );
            })}
          </CardContent>
        </Card>
      </div>

      {/* Documentation */}
      <div className="grid lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>{t('calculators.ieps.info.about')}</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-3">
            <p>{t('calculators.ieps.info.about.desc')}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('calculators.ieps.info.cascade')}</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-3">
            <p>{t('calculators.ieps.info.cascade.desc')}</p>
            <div className="p-3 bg-muted rounded-lg">
              <div className="font-medium text-foreground mb-1">Ejemplo: Tabaco</div>
              <div className="font-mono text-xs space-y-1">
                <div>Base: $100.00</div>
                <div>IEPS (160%): $160.00</div>
                <div>Subtotal: $260.00</div>
                <div>IVA (16%): $41.60</div>
                <div className="font-bold">Total: $301.60</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
