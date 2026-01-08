import { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Calculator, AlertCircle, CheckCircle2, Info, Shield } from 'lucide-react';
import { calculateModalidad10, type IMSSYear, type Modalidad10Result } from '@/lib/calculators';

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const formatPercent = (value: number): string => {
  return `${(value * 100).toFixed(3)}%`;
};

export default function Modalidad10Page() {
  const [salario, setSalario] = useState<string>('15000');
  const [year, setYear] = useState<IMSSYear>(2026);

  const result: Modalidad10Result | null = useMemo(() => {
    const salarioNum = parseFloat(salario);
    if (isNaN(salarioNum) || salarioNum <= 0) return null;
    return calculateModalidad10(salarioNum, year);
  }, [salario, year]);

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-blue-600/15 text-blue-600">
          <Calculator className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">IMSS Modalidad 10</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Incorporación voluntaria al régimen obligatorio para trabajadores independientes.
          </p>
        </div>
      </div>

      {/* Info Card */}
      <Card className="border-blue-200 bg-blue-50/50 dark:bg-blue-950/20 dark:border-blue-800">
        <CardContent className="pt-4">
          <div className="flex gap-3">
            <Info className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
            <div className="text-sm space-y-2">
              <p className="font-medium text-blue-900 dark:text-blue-100">Requisitos de elegibilidad:</p>
              <ul className="list-disc list-inside text-blue-800 dark:text-blue-200 space-y-1">
                <li>Edad entre 16 y 60 años</li>
                <li>No estar cotizando en régimen obligatorio</li>
                <li>Ser mexicano o extranjero residente en México</li>
                <li>Presentar solicitud de inscripción</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Calculator */}
      <Card>
        <CardHeader>
          <CardTitle>Calculadora de Cuotas</CardTitle>
          <CardDescription>
            Ingresa tu salario base de cotización para calcular la cuota mensual
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Input Fields */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="salario">Salario Base de Cotización (diario)</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                <Input
                  id="salario"
                  type="number"
                  value={salario}
                  onChange={(e) => setSalario(e.target.value)}
                  className="pl-8"
                  placeholder="Ej: 500.00"
                  min="0"
                  step="0.01"
                />
              </div>
              <p className="text-xs text-muted-foreground">
                Rango: 1 a 25 UMAs (${result?.uma?.toFixed(2) || '113.14'} - ${((result?.uma || 113.14) * 25).toFixed(2)} diarios)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="year">Año de cálculo</Label>
              <select
                id="year"
                value={year}
                onChange={(e) => setYear(parseInt(e.target.value) as IMSSYear)}
                className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              >
                <option value={2024}>2024</option>
                <option value={2025}>2025</option>
                <option value={2026}>2026</option>
              </select>
            </div>
          </div>

          {/* Results */}
          {result && (
            <>
              <Separator />

              {/* Status Badge */}
              <div className="flex items-center gap-2">
                {result.dentroDeLimites ? (
                  <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    Dentro del rango permitido
                  </Badge>
                ) : (
                  <Badge variant="destructive">
                    <AlertCircle className="h-3 w-3 mr-1" />
                    Salario ajustado al límite
                  </Badge>
                )}
                <Badge variant="outline">
                  {result.salarioEnUMAs.toFixed(2)} UMAs
                </Badge>
              </div>

              {/* Summary */}
              <div className="grid grid-cols-2 gap-4">
                <Card className="bg-primary/5">
                  <CardContent className="pt-4">
                    <p className="text-sm text-muted-foreground">Cuota Mensual</p>
                    <p className="text-2xl font-bold text-primary">{formatCurrency(result.cuotaMensual)}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Fija: {formatCurrency(result.cuotaFijaUMA)} + Variable: {formatCurrency(result.cuotaVariable)}
                    </p>
                  </CardContent>
                </Card>
                <Card className="bg-primary/5">
                  <CardContent className="pt-4">
                    <p className="text-sm text-muted-foreground">Cuota Anual</p>
                    <p className="text-2xl font-bold text-primary">{formatCurrency(result.cuotaAnual)}</p>
                  </CardContent>
                </Card>
              </div>

              {/* Breakdown */}
              <div className="space-y-3">
                <h4 className="font-semibold">Desglose de Componentes</h4>
                <div className="rounded-lg border overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-3">Concepto</th>
                        <th className="text-right p-3">Base</th>
                        <th className="text-right p-3">Monto</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y">
                      <tr className="bg-amber-50/50 dark:bg-amber-950/20">
                        <td className="p-3 font-medium">Prestaciones en Especie (Cuota Fija)</td>
                        <td className="text-right p-3">3.3 UMAs</td>
                        <td className="text-right p-3">{formatCurrency(result.componentes.prestacionesEspecieFija)}</td>
                      </tr>
                      <tr>
                        <td className="p-3">Cesantía y Vejez</td>
                        <td className="text-right p-3">{formatPercent(0.04275)}</td>
                        <td className="text-right p-3">{formatCurrency(result.componentes.cesantiaVejez)}</td>
                      </tr>
                      <tr>
                        <td className="p-3">Invalidez y Vida</td>
                        <td className="text-right p-3">{formatPercent(0.02375)}</td>
                        <td className="text-right p-3">{formatCurrency(result.componentes.invalidezVida)}</td>
                      </tr>
                      <tr>
                        <td className="p-3">Gastos Médicos Pensionados</td>
                        <td className="text-right p-3">{formatPercent(0.01425)}</td>
                        <td className="text-right p-3">{formatCurrency(result.componentes.gastosMedicos)}</td>
                      </tr>
                      <tr>
                        <td className="p-3">Prestaciones en Dinero</td>
                        <td className="text-right p-3">{formatPercent(0.0095)}</td>
                        <td className="text-right p-3">{formatCurrency(result.componentes.prestacionesDinero)}</td>
                      </tr>
                      <tr>
                        <td className="p-3">Guarderías</td>
                        <td className="text-right p-3">{formatPercent(0.01)}</td>
                        <td className="text-right p-3">{formatCurrency(result.componentes.guarderias)}</td>
                      </tr>
                      <tr className="bg-muted/30 font-semibold">
                        <td className="p-3">Total</td>
                        <td className="text-right p-3">Fijo + ~10.47%</td>
                        <td className="text-right p-3">{formatCurrency(result.cuotaMensual)}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Base Calculation Info */}
              <div className="text-sm text-muted-foreground space-y-1">
                <p>Salario Base de Cotización (ajustado): {formatCurrency(result.salarioBaseCotizacion * 30)} mensual</p>
                <p>UMA {year}: ${result.uma.toFixed(2)} diaria / ${(result.uma * 30.4).toFixed(2)} mensual</p>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Benefits - Full coverage */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Los 5 Seguros Incluidos
          </CardTitle>
          <CardDescription>
            Modalidad 10 incluye cobertura completa de los 5 seguros del IMSS
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-sm">Enfermedades y Maternidad</p>
                  <p className="text-xs text-muted-foreground">Atención médica y subsidios</p>
                </div>
              </div>
              <div className="flex gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-sm">Riesgos de Trabajo</p>
                  <p className="text-xs text-muted-foreground">Accidentes y enfermedades laborales</p>
                </div>
              </div>
              <div className="flex gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-sm">Invalidez y Vida</p>
                  <p className="text-xs text-muted-foreground">Pensión por invalidez o muerte</p>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-sm">Retiro, Cesantía y Vejez</p>
                  <p className="text-xs text-muted-foreground">Pensión al retiro y AFORE</p>
                </div>
              </div>
              <div className="flex gap-2">
                <CheckCircle2 className="h-4 w-4 text-green-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-sm">Guarderías y Prestaciones Sociales</p>
                  <p className="text-xs text-muted-foreground">Servicios de guardería</p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Comparison with Mod 40 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Modalidad 10 vs Modalidad 40</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg border overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-3">Característica</th>
                  <th className="text-center p-3">Mod. 10</th>
                  <th className="text-center p-3">Mod. 40</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                <tr>
                  <td className="p-3">Atención médica</td>
                  <td className="text-center p-3 text-green-600">
                    <CheckCircle2 className="h-4 w-4 inline" />
                  </td>
                  <td className="text-center p-3 text-muted-foreground">
                    <AlertCircle className="h-4 w-4 inline" />
                  </td>
                </tr>
                <tr>
                  <td className="p-3">Riesgos de trabajo</td>
                  <td className="text-center p-3 text-green-600">
                    <CheckCircle2 className="h-4 w-4 inline" />
                  </td>
                  <td className="text-center p-3 text-muted-foreground">
                    <AlertCircle className="h-4 w-4 inline" />
                  </td>
                </tr>
                <tr>
                  <td className="p-3">Pensión (Cesantía/Vejez)</td>
                  <td className="text-center p-3 text-green-600">
                    <CheckCircle2 className="h-4 w-4 inline" />
                  </td>
                  <td className="text-center p-3 text-green-600">
                    <CheckCircle2 className="h-4 w-4 inline" />
                  </td>
                </tr>
                <tr>
                  <td className="p-3">Guarderías</td>
                  <td className="text-center p-3 text-green-600">
                    <CheckCircle2 className="h-4 w-4 inline" />
                  </td>
                  <td className="text-center p-3 text-muted-foreground">
                    <AlertCircle className="h-4 w-4 inline" />
                  </td>
                </tr>
                <tr>
                  <td className="p-3">Semanas previas requeridas</td>
                  <td className="text-center p-3">0</td>
                  <td className="text-center p-3">52</td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Nota legal */}
      <p className="text-xs text-muted-foreground text-center">
        Los cálculos son informativos. Consulta directamente con el IMSS para información oficial.
      </p>
    </div>
  );
}
