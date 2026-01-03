import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calculator, DollarSign, TrendingUp, Calendar } from 'lucide-react';

// Latest UDI value from Banxico (Nov 2025)
// Updated from Banxico API - Serie SP68257
const LATEST_UDI = 8.597109; 
const LATEST_UDI_DATE = '2025-11-23';

export default function UDIPage() {
  
  // Pesos to UDIs
  const [pesos, setPesos] = useState('');
  const [udiValue, setUdiValue] = useState(LATEST_UDI.toString());
  const [resultUDIs, setResultUDIs] = useState<number | null>(null);
  
  // UDIs to Pesos
  const [udis, setUdis] = useState('');
  const [udiValueReverse, setUdiValueReverse] = useState(LATEST_UDI.toString());
  const [resultPesos, setResultPesos] = useState<number | null>(null);
  
  // Inflation adjustment
  const [amountOld, setAmountOld] = useState('');
  const [udiValueOld, setUdiValueOld] = useState('');
  const [udiValueNew, setUdiValueNew] = useState(LATEST_UDI.toString());
  const [resultAdjusted, setResultAdjusted] = useState<{
    amountNew: number;
    inflation: number;
  } | null>(null);

  const handlePesosToUDI = () => {
    const p = parseFloat(pesos);
    const u = parseFloat(udiValue);
    if (!isNaN(p) && !isNaN(u) && u > 0) {
      setResultUDIs(p / u);
    }
  };

  const handleUDIToPesos = () => {
    const u = parseFloat(udis);
    const uv = parseFloat(udiValueReverse);
    if (!isNaN(u) && !isNaN(uv) && uv > 0) {
      setResultPesos(u * uv);
    }
  };

  const handleInflationAdjust = () => {
    const amount = parseFloat(amountOld);
    const oldUDI = parseFloat(udiValueOld);
    const newUDI = parseFloat(udiValueNew);
    
    if (!isNaN(amount) && !isNaN(oldUDI) && !isNaN(newUDI) && oldUDI > 0 && newUDI > 0) {
      // Convert to UDIs with old value, then back to pesos with new value
      const udisAmount = amount / oldUDI;
      const newAmount = udisAmount * newUDI;
      const inflation = ((newUDI - oldUDI) / oldUDI) * 100;
      
      setResultAdjusted({
        amountNew: newAmount,
        inflation
      });
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold">Calculadora de UDI</h1>
        <p className="text-muted-foreground mt-1">
          Unidad de Inversión - Conversión de pesos a UDIs y ajuste por inflación
        </p>
        <Badge variant="secondary" className="mt-2">
          UDI actual: ${LATEST_UDI.toFixed(6)} MXN ({LATEST_UDI_DATE})
        </Badge>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Pesos to UDIs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              Pesos a UDIs
            </CardTitle>
            <CardDescription>
              Convierte un monto en pesos a UDIs
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
              <label className="text-sm font-medium mb-2 block">Valor de UDI</label>
              <Input
                type="number"
                step="0.000001"
                placeholder={LATEST_UDI.toString()}
                value={udiValue}
                onChange={(e) => setUdiValue(e.target.value)}
              />
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
              Convierte UDIs a pesos mexicanos
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
              <label className="text-sm font-medium mb-2 block">Valor de UDI</label>
              <Input
                type="number"
                step="0.000001"
                placeholder={LATEST_UDI.toString()}
                value={udiValueReverse}
                onChange={(e) => setUdiValueReverse(e.target.value)}
              />
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
                  {udis} UDIs × ${udiValueReverse}
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
              <label className="text-sm font-medium mb-2 block">UDI Fecha Original</label>
              <Input
                type="number"
                step="0.000001"
                placeholder="5.0 (ej: 2015)"
                value={udiValueOld}
                onChange={(e) => setUdiValueOld(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">UDI Fecha Actual</label>
              <Input
                type="number"
                step="0.000001"
                placeholder={LATEST_UDI.toString()}
                value={udiValueNew}
                onChange={(e) => setUdiValueNew(e.target.value)}
              />
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
              
              <div className="p-4 bg-primary/10 rounded-lg text-sm font-mono">
                <div className="flex justify-between mb-2">
                  <span>Monto original:</span>
                  <span>${amountOld} MXN</span>
                </div>
                <div className="flex justify-between mb-2">
                  <span>Equivalente en UDIs:</span>
                  <span>{(parseFloat(amountOld) / parseFloat(udiValueOld)).toFixed(6)} UDIs</span>
                </div>
                <div className="flex justify-between font-bold pt-2 border-t">
                  <span>Monto ajustado:</span>
                  <span>${resultAdjusted.amountNew.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</span>
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
            <CardTitle>Ejemplo Práctico</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-3">
            <div className="p-3 bg-muted rounded-lg">
              <div className="font-medium text-foreground mb-2">Crédito Hipotecario</div>
              <p>Un crédito de <strong>1,000,000 UDIs</strong> en 1995 valía $1,000,000 MXN.</p>
              <p className="mt-2">
                Hoy (2025) esas mismas 1,000,000 UDIs equivalen a <strong>~$8,412,365 MXN</strong>.
              </p>
              <p className="mt-2 text-xs">
                La UDI protege al acreedor de la inflación (738% en 30 años).
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Valores Históricos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 text-sm">
            {[
              { year: 1995, value: 1.0, note: 'Inicio' },
              { year: 2000, value: 3.16, note: '+216%' },
              { year: 2005, value: 3.87, note: '+287%' },
              { year: 2010, value: 4.56, note: '+356%' },
              { year: 2015, value: 5.28, note: '+428%' },
              { year: 2020, value: 6.77, note: '+577%' },
              { year: 2024, value: 8.39, note: '+739%' },
              { year: 2025, value: 8.60, note: 'Nov' },
            ].map((item) => (
              <div key={item.year} className="p-3 bg-muted rounded-lg">
                <div className="flex items-center justify-between mb-1">
                  <div className="text-muted-foreground text-xs font-semibold">{item.year}</div>
                  <div className="text-[10px] text-muted-foreground">{item.note}</div>
                </div>
                <div className="font-mono font-bold text-base">${item.value.toFixed(2)}</div>
              </div>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-4">
            Valores aproximados. Consulta el catálogo de UDIS para valores exactos diarios.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

