import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Calculator, Building2, User, AlertTriangle,
  TrendingUp, PiggyBank, ChevronDown, ChevronUp, HelpCircle
} from 'lucide-react';
import {
  calculatePayroll,
  calculateGrossFromBudget,
  STATES,
  ISN_RATES,
  getVacationDays,
  type PayrollYear,
  type RiskClass,
  type PayrollResult,
} from '@/lib/payroll-calculator';

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('es-MX', {
    style: 'currency',
    currency: 'MXN',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const formatPercent = (value: number, decimals: number = 2): string => {
  return `${value.toFixed(decimals)}%`;
};

const RISK_CLASS_DESCRIPTIONS: Record<RiskClass, { name: string; examples: string }> = {
  1: { name: 'Clase I - Mínimo', examples: 'Oficinas, comercio, servicios administrativos' },
  2: { name: 'Clase II - Bajo', examples: 'Manufactura ligera, servicios profesionales' },
  3: { name: 'Clase III - Medio', examples: 'Manufactura pesada, transporte' },
  4: { name: 'Clase IV - Alto', examples: 'Construcción, industria química' },
  5: { name: 'Clase V - Máximo', examples: 'Minería, petróleo, explosivos' },
};

export default function NominaCalculatorPage() {
  // Input state
  const [mode, setMode] = useState<'bruto-costo' | 'presupuesto-neto'>('bruto-costo');
  const [salarioBruto, setSalarioBruto] = useState<string>('25000');
  const [presupuesto, setPresupuesto] = useState<string>('40000');
  const [estado, setEstado] = useState<string>('CDMX');
  const [claseRiesgo, setClaseRiesgo] = useState<RiskClass>(1);
  const [diasAguinaldo, setDiasAguinaldo] = useState<number>(15);
  const [antiguedad, setAntiguedad] = useState<number>(1);
  const [primaVacacional, setPrimaVacacional] = useState<number>(25);
  const [incluirPTU, setIncluirPTU] = useState<boolean>(false);
  const [porcentajePTU, setPorcentajePTU] = useState<number>(10);
  const [incluirReserva, setIncluirReserva] = useState<boolean>(true);
  const [fondoAhorro, setFondoAhorro] = useState<number>(0);
  const [valesDespensa, setValesDespensa] = useState<number>(0);
  const [year, setYear] = useState<PayrollYear>(2026);

  // Collapsible sections
  const [showIMSSDetail, setShowIMSSDetail] = useState(false);
  const [showReservaDetail, setShowReservaDetail] = useState(false);

  // Calculate result
  const result: PayrollResult | null = useMemo(() => {
    const input = {
      estado,
      claseRiesgo,
      diasAguinaldo,
      antiguedadAnios: antiguedad,
      primaVacacional,
      incluirPTU,
      porcentajePTU: incluirPTU ? porcentajePTU : undefined,
      incluirReservaLiquidacion: incluirReserva,
      fondoAhorroPatron: fondoAhorro > 0 ? fondoAhorro : undefined,
      valesDespensa: valesDespensa > 0 ? valesDespensa : undefined,
      year,
    };

    if (mode === 'bruto-costo') {
      const salarioNum = parseFloat(salarioBruto);
      if (isNaN(salarioNum) || salarioNum <= 0) return null;
      return calculatePayroll({ ...input, salarioBrutoMensual: salarioNum });
    } else {
      const presupuestoNum = parseFloat(presupuesto);
      if (isNaN(presupuestoNum) || presupuestoNum <= 0) return null;
      const { result } = calculateGrossFromBudget(presupuestoNum, input);
      return result;
    }
  }, [mode, salarioBruto, presupuesto, estado, claseRiesgo, diasAguinaldo, antiguedad,
      primaVacacional, incluirPTU, porcentajePTU, incluirReserva, fondoAhorro, valesDespensa, year]);

  const diasVacaciones = getVacationDays(antiguedad);

  return (
    <div className="space-y-6">
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-primary/15 text-primary">
          <Calculator className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Calculadora de Nómina</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Calcula el costo total del empleador y el ingreso neto del trabajador
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="space-y-4">
          {/* Mode Selection */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Modo de Cálculo</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs value={mode} onValueChange={(v) => setMode(v as 'bruto-costo' | 'presupuesto-neto')}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="bruto-costo" className="text-xs sm:text-sm">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Bruto → Costo
                  </TabsTrigger>
                  <TabsTrigger value="presupuesto-neto" className="text-xs sm:text-sm">
                    <PiggyBank className="h-4 w-4 mr-2" />
                    Presupuesto → Neto
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="bruto-costo" className="mt-4">
                  <div className="space-y-2">
                    <Label htmlFor="salario-bruto">Salario Bruto Mensual</Label>
                    <div className="relative">
                      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                      <Input
                        id="salario-bruto"
                        type="number"
                        value={salarioBruto}
                        onChange={(e) => setSalarioBruto(e.target.value)}
                        className="pl-8"
                        placeholder="25000"
                      />
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Ingresa el salario mensual bruto para calcular el costo total
                    </p>
                  </div>
                </TabsContent>

                <TabsContent value="presupuesto-neto" className="mt-4">
                  <div className="space-y-2">
                    <Label htmlFor="presupuesto">Presupuesto Mensual del Empleador</Label>
                    <div className="relative">
                      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
                      <Input
                        id="presupuesto"
                        type="number"
                        value={presupuesto}
                        onChange={(e) => setPresupuesto(e.target.value)}
                        className="pl-8"
                        placeholder="40000"
                      />
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Ingresa tu presupuesto para calcular el salario posible
                    </p>
                  </div>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>

          {/* Basic Config */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Configuración Básica</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="year">Año</Label>
                  <select
                    id="year"
                    value={year}
                    onChange={(e) => setYear(parseInt(e.target.value) as PayrollYear)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    <option value={2024}>2024</option>
                    <option value={2025}>2025</option>
                    <option value={2026}>2026</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="estado">Estado (ISN)</Label>
                  <select
                    id="estado"
                    value={estado}
                    onChange={(e) => setEstado(e.target.value)}
                    className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  >
                    {STATES.map((s) => (
                      <option key={s.code} value={s.code}>
                        {s.name} ({formatPercent(ISN_RATES[s.code] * 100, 1)})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="riesgo">Clase de Riesgo IMSS</Label>
                <select
                  id="riesgo"
                  value={claseRiesgo}
                  onChange={(e) => setClaseRiesgo(parseInt(e.target.value) as RiskClass)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  {([1, 2, 3, 4, 5] as RiskClass[]).map((c) => (
                    <option key={c} value={c}>
                      {RISK_CLASS_DESCRIPTIONS[c].name}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-muted-foreground">
                  {RISK_CLASS_DESCRIPTIONS[claseRiesgo].examples}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="antiguedad">Antigüedad (años)</Label>
                  <Input
                    id="antiguedad"
                    type="number"
                    value={antiguedad}
                    onChange={(e) => setAntiguedad(Math.max(0, parseInt(e.target.value) || 0))}
                    min="0"
                  />
                  <p className="text-xs text-muted-foreground">
                    {diasVacaciones} días de vacaciones
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="aguinaldo">Días de Aguinaldo</Label>
                  <Input
                    id="aguinaldo"
                    type="number"
                    value={diasAguinaldo}
                    onChange={(e) => setDiasAguinaldo(Math.max(15, parseInt(e.target.value) || 15))}
                    min="15"
                  />
                  <p className="text-xs text-muted-foreground">
                    Mínimo legal: 15 días
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="prima">Prima Vacacional (%)</Label>
                <Input
                  id="prima"
                  type="number"
                  value={primaVacacional}
                  onChange={(e) => setPrimaVacacional(Math.max(25, parseInt(e.target.value) || 25))}
                  min="25"
                />
                <p className="text-xs text-muted-foreground">
                  Mínimo legal: 25%
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Optional Items */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Opciones Adicionales</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Reserva de Liquidación</Label>
                  <p className="text-xs text-muted-foreground">
                    Indemnización + Prima Antigüedad + 20 días/año
                  </p>
                </div>
                <Switch
                  checked={incluirReserva}
                  onCheckedChange={setIncluirReserva}
                />
              </div>

              <Separator />

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>PTU (Reparto de Utilidades)</Label>
                  <p className="text-xs text-muted-foreground">
                    Aproximado como % del salario
                  </p>
                </div>
                <Switch
                  checked={incluirPTU}
                  onCheckedChange={setIncluirPTU}
                />
              </div>

              {incluirPTU && (
                <div className="space-y-2 pl-4">
                  <Label htmlFor="ptu">% del salario como PTU</Label>
                  <Input
                    id="ptu"
                    type="number"
                    value={porcentajePTU}
                    onChange={(e) => setPorcentajePTU(Math.max(0, parseFloat(e.target.value) || 0))}
                    min="0"
                  />
                </div>
              )}

              <Separator />

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="fondo">Fondo de Ahorro Patrón (%)</Label>
                  <Input
                    id="fondo"
                    type="number"
                    value={fondoAhorro}
                    onChange={(e) => setFondoAhorro(Math.max(0, parseFloat(e.target.value) || 0))}
                    min="0"
                    placeholder="0"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="vales">Vales de Despensa ($)</Label>
                  <Input
                    id="vales"
                    type="number"
                    value={valesDespensa}
                    onChange={(e) => setValesDespensa(Math.max(0, parseFloat(e.target.value) || 0))}
                    min="0"
                    placeholder="0"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Results Section */}
        <div className="space-y-4">
          {result && (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-2 gap-4">
                <Card className="bg-red-50/50 dark:bg-red-950/20 border-red-200 dark:border-red-800">
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Building2 className="h-4 w-4 text-red-600" />
                      <span className="text-xs text-red-600 font-medium">COSTO EMPLEADOR</span>
                    </div>
                    <p className="text-2xl font-bold text-red-700 dark:text-red-400">
                      {formatCurrency(result.costoTotalMensual)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      +{formatPercent(result.porcentajeAdicionalSobreBruto)} sobre bruto
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-green-50/50 dark:bg-green-950/20 border-green-200 dark:border-green-800">
                  <CardContent className="pt-4">
                    <div className="flex items-center gap-2 mb-2">
                      <User className="h-4 w-4 text-green-600" />
                      <span className="text-xs text-green-600 font-medium">INGRESO NETO</span>
                    </div>
                    <p className="text-2xl font-bold text-green-700 dark:text-green-400">
                      {formatCurrency(result.ingresoNetoMensual)}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatPercent((result.ingresoNetoMensual / result.salarioBrutoMensual) * 100)} del bruto
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Key Metrics */}
              <Card>
                <CardContent className="pt-4">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-xs text-muted-foreground">Salario Bruto</p>
                      <p className="font-semibold">{formatCurrency(result.salarioBrutoMensual)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Relación Costo/Neto</p>
                      <p className="font-semibold">{result.relacionCostoIngresoNeto.toFixed(2)}x</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Tasa ISR Efectiva</p>
                      <p className="font-semibold">{formatPercent(result.tasaEfectivaISR)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Employer Costs Breakdown */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Building2 className="h-5 w-5" />
                    Desglose Costo Empleador
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="rounded-lg border overflow-hidden">
                    <table className="w-full text-sm">
                      <tbody className="divide-y">
                        <tr>
                          <td className="p-2 font-medium">Salario Bruto</td>
                          <td className="p-2 text-right">{formatCurrency(result.salarioBrutoMensual)}</td>
                        </tr>

                        {/* IMSS Collapsible */}
                        <tr
                          className="cursor-pointer hover:bg-muted/50"
                          onClick={() => setShowIMSSDetail(!showIMSSDetail)}
                        >
                          <td className="p-2 flex items-center gap-2">
                            {showIMSSDetail ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                            IMSS Patrón
                          </td>
                          <td className="p-2 text-right">{formatCurrency(result.imssPatron.total)}</td>
                        </tr>
                        {showIMSSDetail && (
                          <>
                            <tr className="bg-muted/30 text-xs">
                              <td className="p-2 pl-8">Enfermedad/Maternidad (Fija)</td>
                              <td className="p-2 text-right">{formatCurrency(result.imssPatron.enfermedadMaternidadFija)}</td>
                            </tr>
                            <tr className="bg-muted/30 text-xs">
                              <td className="p-2 pl-8">Enfermedad/Maternidad (Excedente)</td>
                              <td className="p-2 text-right">{formatCurrency(result.imssPatron.enfermedadMaternidadExcedente)}</td>
                            </tr>
                            <tr className="bg-muted/30 text-xs">
                              <td className="p-2 pl-8">Prestaciones en Dinero</td>
                              <td className="p-2 text-right">{formatCurrency(result.imssPatron.prestacionesDinero)}</td>
                            </tr>
                            <tr className="bg-muted/30 text-xs">
                              <td className="p-2 pl-8">Gastos Médicos Pensionados</td>
                              <td className="p-2 text-right">{formatCurrency(result.imssPatron.gastosMedicosPensionados)}</td>
                            </tr>
                            <tr className="bg-muted/30 text-xs">
                              <td className="p-2 pl-8">Invalidez y Vida</td>
                              <td className="p-2 text-right">{formatCurrency(result.imssPatron.invalidezVida)}</td>
                            </tr>
                            <tr className="bg-muted/30 text-xs">
                              <td className="p-2 pl-8">Retiro (SAR)</td>
                              <td className="p-2 text-right">{formatCurrency(result.imssPatron.retiro)}</td>
                            </tr>
                            <tr className="bg-muted/30 text-xs">
                              <td className="p-2 pl-8">Cesantía y Vejez</td>
                              <td className="p-2 text-right">{formatCurrency(result.imssPatron.cesantiaVejez)}</td>
                            </tr>
                            <tr className="bg-muted/30 text-xs">
                              <td className="p-2 pl-8">Guarderías</td>
                              <td className="p-2 text-right">{formatCurrency(result.imssPatron.guarderias)}</td>
                            </tr>
                            <tr className="bg-muted/30 text-xs">
                              <td className="p-2 pl-8">Riesgo de Trabajo (Clase {claseRiesgo})</td>
                              <td className="p-2 text-right">{formatCurrency(result.imssPatron.riesgoTrabajo)}</td>
                            </tr>
                          </>
                        )}

                        <tr>
                          <td className="p-2">INFONAVIT (5%)</td>
                          <td className="p-2 text-right">{formatCurrency(result.infonavit)}</td>
                        </tr>
                        <tr>
                          <td className="p-2">ISN ({formatPercent(result.tasaISN * 100, 1)})</td>
                          <td className="p-2 text-right">{formatCurrency(result.impuestoSobreNomina)}</td>
                        </tr>

                        <tr className="bg-muted/50 font-medium">
                          <td className="p-2">Subtotal Directo</td>
                          <td className="p-2 text-right">{formatCurrency(result.costoDirectoMensual)}</td>
                        </tr>

                        <tr>
                          <td className="p-2">Provisión Aguinaldo</td>
                          <td className="p-2 text-right">{formatCurrency(result.provisionAguinaldo)}</td>
                        </tr>
                        <tr>
                          <td className="p-2">Provisión Vacaciones</td>
                          <td className="p-2 text-right">{formatCurrency(result.provisionVacaciones)}</td>
                        </tr>
                        <tr>
                          <td className="p-2">Provisión Prima Vacacional</td>
                          <td className="p-2 text-right">{formatCurrency(result.provisionPrimaVacacional)}</td>
                        </tr>

                        {incluirPTU && (
                          <tr>
                            <td className="p-2">Provisión PTU</td>
                            <td className="p-2 text-right">{formatCurrency(result.provisionPTU)}</td>
                          </tr>
                        )}

                        {/* Reserva Collapsible */}
                        {incluirReserva && (
                          <>
                            <tr
                              className="cursor-pointer hover:bg-muted/50"
                              onClick={() => setShowReservaDetail(!showReservaDetail)}
                            >
                              <td className="p-2 flex items-center gap-2">
                                {showReservaDetail ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                                <AlertTriangle className="h-4 w-4 text-amber-500" />
                                Reserva Liquidación
                              </td>
                              <td className="p-2 text-right">{formatCurrency(result.reservaLiquidacion.provisionMensual)}</td>
                            </tr>
                            {showReservaDetail && (
                              <>
                                <tr className="bg-amber-50/50 dark:bg-amber-950/20 text-xs">
                                  <td className="p-2 pl-8">3 meses indemnización</td>
                                  <td className="p-2 text-right">{formatCurrency(result.reservaLiquidacion.indemnizacion3Meses / 12)}/mes</td>
                                </tr>
                                <tr className="bg-amber-50/50 dark:bg-amber-950/20 text-xs">
                                  <td className="p-2 pl-8">Prima antigüedad (12 días × {antiguedad} años)</td>
                                  <td className="p-2 text-right">{formatCurrency(result.reservaLiquidacion.primaAntiguedad / 12)}/mes</td>
                                </tr>
                                <tr className="bg-amber-50/50 dark:bg-amber-950/20 text-xs">
                                  <td className="p-2 pl-8">20 días × {antiguedad} años</td>
                                  <td className="p-2 text-right">{formatCurrency(result.reservaLiquidacion.veinteDiasPorAnio / 12)}/mes</td>
                                </tr>
                                <tr className="bg-amber-50/50 dark:bg-amber-950/20 text-xs font-medium">
                                  <td className="p-2 pl-8">Total Anual Reserva</td>
                                  <td className="p-2 text-right">{formatCurrency(result.reservaLiquidacion.totalAnual)}</td>
                                </tr>
                              </>
                            )}
                          </>
                        )}

                        {fondoAhorro > 0 && (
                          <tr>
                            <td className="p-2">Fondo de Ahorro Patrón</td>
                            <td className="p-2 text-right">{formatCurrency(result.fondoAhorroPatron)}</td>
                          </tr>
                        )}

                        {valesDespensa > 0 && (
                          <tr>
                            <td className="p-2">Vales de Despensa</td>
                            <td className="p-2 text-right">{formatCurrency(result.valesDespensa)}</td>
                          </tr>
                        )}

                        <tr className="bg-red-100/50 dark:bg-red-950/30 font-bold">
                          <td className="p-2">COSTO TOTAL MENSUAL</td>
                          <td className="p-2 text-right text-red-700 dark:text-red-400">{formatCurrency(result.costoTotalMensual)}</td>
                        </tr>
                        <tr className="font-medium">
                          <td className="p-2">Costo Total Anual</td>
                          <td className="p-2 text-right">{formatCurrency(result.costoTotalAnual)}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {/* Worker Income Breakdown */}
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <User className="h-5 w-5" />
                    Desglose Ingreso Trabajador
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="rounded-lg border overflow-hidden">
                    <table className="w-full text-sm">
                      <tbody className="divide-y">
                        <tr>
                          <td className="p-2 font-medium">Salario Bruto</td>
                          <td className="p-2 text-right">{formatCurrency(result.salarioBrutoMensual)}</td>
                        </tr>
                        <tr className="text-red-600">
                          <td className="p-2">(-) IMSS Trabajador</td>
                          <td className="p-2 text-right">-{formatCurrency(result.imssTrabajador.total)}</td>
                        </tr>
                        <tr className="text-red-600">
                          <td className="p-2">(-) ISR Retenido</td>
                          <td className="p-2 text-right">-{formatCurrency(result.isrRetenido)}</td>
                        </tr>
                        {result.subsidioEmpleo > 0 && (
                          <tr className="text-green-600">
                            <td className="p-2">(+) Subsidio al Empleo</td>
                            <td className="p-2 text-right">+{formatCurrency(result.subsidioEmpleo)}</td>
                          </tr>
                        )}
                        {valesDespensa > 0 && (
                          <tr className="text-green-600">
                            <td className="p-2">(+) Vales de Despensa</td>
                            <td className="p-2 text-right">+{formatCurrency(result.valesDespensa)}</td>
                          </tr>
                        )}
                        <tr className="bg-green-100/50 dark:bg-green-950/30 font-bold">
                          <td className="p-2">INGRESO NETO MENSUAL</td>
                          <td className="p-2 text-right text-green-700 dark:text-green-400">{formatCurrency(result.ingresoNetoMensual)}</td>
                        </tr>

                        <tr className="bg-muted/30">
                          <td className="p-2 font-medium" colSpan={2}>Prestaciones Anuales (netas)</td>
                        </tr>
                        <tr>
                          <td className="p-2">Aguinaldo ({diasAguinaldo} días)</td>
                          <td className="p-2 text-right">{formatCurrency(result.aguinaldoNeto)}</td>
                        </tr>
                        <tr>
                          <td className="p-2">Prima Vacacional</td>
                          <td className="p-2 text-right">{formatCurrency(result.primaVacacionalNeta)}</td>
                        </tr>
                        {incluirPTU && (
                          <tr>
                            <td className="p-2">PTU</td>
                            <td className="p-2 text-right">{formatCurrency(result.ptuNeto)}</td>
                          </tr>
                        )}
                        <tr className="bg-green-100/50 dark:bg-green-950/30 font-bold">
                          <td className="p-2">INGRESO NETO ANUAL</td>
                          <td className="p-2 text-right text-green-700 dark:text-green-400">{formatCurrency(result.ingresoNetoAnual)}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {/* Info Card */}
              <Card className="border-blue-200 bg-blue-50/50 dark:bg-blue-950/20 dark:border-blue-800">
                <CardContent className="pt-4">
                  <div className="flex gap-3">
                    <HelpCircle className="h-5 w-5 text-blue-600 shrink-0" />
                    <div className="text-sm space-y-2 text-blue-800 dark:text-blue-200">
                      <p className="font-medium">Notas importantes:</p>
                      <ul className="list-disc list-inside space-y-1 text-xs">
                        <li>SDI calculado: {formatCurrency(result.salarioDiarioIntegrado)} diario</li>
                        <li>Tope IMSS: {formatCurrency(result.salarioBaseTopeUMA)} mensual (25 UMAs)</li>
                        <li>La reserva de liquidación es un costo contingente que debe provisionarse</li>
                        <li>El PTU se estima como % del salario; el real depende de utilidades</li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}

          {!result && (
            <Card className="border-dashed">
              <CardContent className="pt-6 text-center text-muted-foreground">
                <Calculator className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Ingresa un salario válido para ver los resultados</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      <p className="text-xs text-muted-foreground text-center">
        Los cálculos son informativos y usan las tasas oficiales vigentes. Consulta con un contador para casos específicos.
      </p>
    </div>
  );
}
