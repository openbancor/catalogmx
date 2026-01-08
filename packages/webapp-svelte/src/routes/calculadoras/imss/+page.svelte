<script lang="ts">
	import { Calculator, Info, Shield, Users } from 'lucide-svelte';
	import imssTablesData from '../../../../../shared-data/imss-tables.json';

	type TipoCalculo = 'cuotas' | 'modalidad40' | 'modalidad10';
	type ClaseRiesgo = 1 | 2 | 3 | 4 | 5;
	type Year = 2024 | 2025 | 2026;

	// State
	let tipoCalculo = $state<TipoCalculo>('cuotas');
	let salarioDiario = $state<number>(500);
	let claseRiesgo = $state<ClaseRiesgo>(1);
	let year = $state<Year>(2025);

	const tiposCalculo = [
		{ value: 'cuotas', label: 'Cuotas Obrero-Patronales', icon: Users },
		{ value: 'modalidad40', label: 'Modalidad 40 (Voluntaria)', icon: Shield },
		{ value: 'modalidad10', label: 'Modalidad 10 (Independiente)', icon: Shield }
	] as const;

	const clasesRiesgo = imssTablesData.riesgos_trabajo_clases.map(c => ({
		value: c.clase as ClaseRiesgo,
		label: `Clase ${c.clase} - ${c.descripcion.replace(`Clase ${c.clase} - `, '')}`,
		prima: c.prima,
		ejemplos: c.ejemplos
	}));

	const years = [2024, 2025, 2026] as const;

	interface CuotasResult {
		salarioDiario: number;
		salarioMensual: number;
		uma: number;
		cuotasPatron: number;
		cuotasTrabajador: number;
		cuotaTotal: number;
		desglose: {
			concepto: string;
			patron: number;
			trabajador: number;
		}[];
	}

	interface Modalidad40Result {
		salarioDiario: number;
		salarioMensual: number;
		cuotaMensual: number;
		cuotaAnual: number;
	}

	interface Modalidad10Result {
		salarioDiario: number;
		salarioMensual: number;
		cuotaFijaUMA: number;
		cuotaVariable: number;
		cuotaMensual: number;
		cuotaAnual: number;
	}

	let resultadoCuotas = $state<CuotasResult | null>(null);
	let resultadoMod40 = $state<Modalidad40Result | null>(null);
	let resultadoMod10 = $state<Modalidad10Result | null>(null);

	// UMA values from data
	function getUMA(year: Year): number {
		return imssTablesData.uma[year.toString() as '2024' | '2025' | '2026'].diaria;
	}

	function calculateCuotas() {
		const uma = getUMA(year);
		const salarioMensual = salarioDiario * 30;
		const cuotas = imssTablesData.cuotas_imss;
		const primaRiesgo = cuotas.riesgo_trabajo[`clase_${claseRiesgo}` as keyof typeof cuotas.riesgo_trabajo] as number;

		let cuotasPatron = 0;
		let cuotasTrabajador = 0;
		const desglose: CuotasResult['desglose'] = [];

		// Enfermedad y maternidad - Cuota fija (sobre UMA)
		const cuotaFijaPatron = uma * 30 * cuotas.enfermedad_maternidad.prestaciones_en_especie.patron;
		cuotasPatron += cuotaFijaPatron;
		desglose.push({
			concepto: 'E&M - Cuota fija (UMA)',
			patron: cuotaFijaPatron,
			trabajador: 0
		});

		// Enfermedad y maternidad - Excedente (si salario > 3 UMA)
		if (salarioDiario > uma * 3) {
			const excedente = salarioDiario - (uma * 3);
			const excedentePatron = excedente * 30 * cuotas.enfermedad_maternidad.prestaciones_en_especie_excedente.patron;
			const excedenteTrab = excedente * 30 * cuotas.enfermedad_maternidad.prestaciones_en_especie_excedente.trabajador;
			cuotasPatron += excedentePatron;
			cuotasTrabajador += excedenteTrab;
			desglose.push({
				concepto: 'E&M - Excedente 3 UMA',
				patron: excedentePatron,
				trabajador: excedenteTrab
			});
		}

		// Prestaciones en dinero
		const dineroPatron = salarioMensual * cuotas.enfermedad_maternidad.prestaciones_en_dinero.patron;
		const dineroTrab = salarioMensual * cuotas.enfermedad_maternidad.prestaciones_en_dinero.trabajador;
		cuotasPatron += dineroPatron;
		cuotasTrabajador += dineroTrab;
		desglose.push({
			concepto: 'E&M - Prestaciones en dinero',
			patron: dineroPatron,
			trabajador: dineroTrab
		});

		// Gastos médicos pensionados
		const gmpPatron = salarioMensual * cuotas.enfermedad_maternidad.gastos_medicos_pensionados.patron;
		const gmpTrab = salarioMensual * cuotas.enfermedad_maternidad.gastos_medicos_pensionados.trabajador;
		cuotasPatron += gmpPatron;
		cuotasTrabajador += gmpTrab;
		desglose.push({
			concepto: 'Gastos médicos pensionados',
			patron: gmpPatron,
			trabajador: gmpTrab
		});

		// Invalidez y vida
		const ivPatron = salarioMensual * cuotas.invalidez_vida.patron;
		const ivTrab = salarioMensual * cuotas.invalidez_vida.trabajador;
		cuotasPatron += ivPatron;
		cuotasTrabajador += ivTrab;
		desglose.push({
			concepto: 'Invalidez y vida',
			patron: ivPatron,
			trabajador: ivTrab
		});

		// Retiro
		const retiroPatron = salarioMensual * cuotas.retiro_cesantia_vejez.retiro.patron;
		cuotasPatron += retiroPatron;
		desglose.push({
			concepto: 'Retiro (SAR)',
			patron: retiroPatron,
			trabajador: 0
		});

		// Cesantía y vejez
		const cvPatron = salarioMensual * cuotas.retiro_cesantia_vejez.cesantia_vejez.patron;
		const cvTrab = salarioMensual * cuotas.retiro_cesantia_vejez.cesantia_vejez.trabajador;
		cuotasPatron += cvPatron;
		cuotasTrabajador += cvTrab;
		desglose.push({
			concepto: 'Cesantía y vejez',
			patron: cvPatron,
			trabajador: cvTrab
		});

		// Guarderías
		const guarderiasPatron = salarioMensual * cuotas.guarderias_prestaciones_sociales.patron;
		cuotasPatron += guarderiasPatron;
		desglose.push({
			concepto: 'Guarderías',
			patron: guarderiasPatron,
			trabajador: 0
		});

		// Riesgo de trabajo
		const riesgoPatron = salarioMensual * primaRiesgo;
		cuotasPatron += riesgoPatron;
		desglose.push({
			concepto: `Riesgo de trabajo (Clase ${claseRiesgo})`,
			patron: riesgoPatron,
			trabajador: 0
		});

		resultadoCuotas = {
			salarioDiario,
			salarioMensual,
			uma,
			cuotasPatron,
			cuotasTrabajador,
			cuotaTotal: cuotasPatron + cuotasTrabajador,
			desglose
		};
	}

	function calculateModalidad40() {
		const uma = getUMA(year);
		const salarioMensual = salarioDiario * 30;
		const maxSBC = uma * 25 * 30;
		const sbcAplicable = Math.min(salarioMensual, maxSBC);

		const cuotaMensual = sbcAplicable * imssTablesData.modalidad_40.cuota_mensual.porcentaje_total;

		resultadoMod40 = {
			salarioDiario,
			salarioMensual: sbcAplicable,
			cuotaMensual,
			cuotaAnual: cuotaMensual * 12
		};
	}

	function calculateModalidad10() {
		const uma = getUMA(year);
		const salarioMensual = salarioDiario * 30;
		const maxSBC = uma * 25 * 30;
		const sbcAplicable = Math.min(salarioMensual, maxSBC);

		// Cuota fija (3.3 UMAs mensuales para prestaciones en especie)
		const cuotaFijaUMA = uma * imssTablesData.modalidad_10.cuota_mensual.cuota_fija_uma_factor * 30;

		// Cuota variable
		const cuotaVariable = sbcAplicable * imssTablesData.modalidad_10.cuota_mensual.porcentaje_variable;

		const cuotaMensual = cuotaFijaUMA + cuotaVariable;

		resultadoMod10 = {
			salarioDiario,
			salarioMensual: sbcAplicable,
			cuotaFijaUMA,
			cuotaVariable,
			cuotaMensual,
			cuotaAnual: cuotaMensual * 12
		};
	}

	function calculate() {
		if (!salarioDiario || salarioDiario <= 0) {
			resultadoCuotas = null;
			resultadoMod40 = null;
			resultadoMod10 = null;
			return;
		}

		if (tipoCalculo === 'cuotas') {
			calculateCuotas();
		} else if (tipoCalculo === 'modalidad40') {
			calculateModalidad40();
		} else {
			calculateModalidad10();
		}
	}

	function formatCurrency(value: number): string {
		return new Intl.NumberFormat('es-MX', {
			style: 'currency',
			currency: 'MXN',
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		}).format(value);
	}

	// Auto-calculate when inputs change
	$effect(() => {
		calculate();
	});
</script>

<svelte:head>
	<title>Calculadora IMSS - catalogmx</title>
	<meta name="description" content="Calcula cuotas IMSS obrero-patronales, Modalidad 40 y Modalidad 10. Cuotas actualizadas 2024-2026." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="/calculadoras" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Calculadoras
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">IMSS</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-teal-100 dark:bg-teal-900/30">
				<Shield class="h-8 w-8 text-teal-600 dark:text-teal-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Calculadora IMSS
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Cuotas obrero-patronales y modalidades voluntarias
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-teal-50 dark:bg-teal-900/20 rounded-lg border border-teal-200 dark:border-teal-800">
			<Info class="h-5 w-5 text-teal-600 dark:text-teal-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-teal-900 dark:text-teal-300">
				<p class="font-medium mb-1">Cuotas IMSS {year}</p>
				<p>UMA {year}: {formatCurrency(getUMA(year))} diarios. Tope de cotización: 25 UMAs.</p>
			</div>
		</div>
	</div>
</section>

<!-- Calculator -->
<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Tipo de cálculo tabs -->
		<div class="mb-6">
			<div class="flex flex-wrap gap-2">
				{#each tiposCalculo as tipo}
					{@const Icon = tipo.icon}
					<button
						class="px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2
							{tipoCalculo === tipo.value
								? 'bg-teal-500 text-white'
								: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'}"
						onclick={() => tipoCalculo = tipo.value}
					>
						<Icon class="h-4 w-4" />
						{tipo.label}
					</button>
				{/each}
			</div>
		</div>

		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Input Form -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<Calculator class="h-5 w-5 text-brand-500" />
					Datos de entrada
				</h2>

				<div class="space-y-5">
					<!-- Salario diario -->
					<div>
						<label for="salarioDiario" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Salario diario integrado (SDI)
						</label>
						<div class="relative">
							<span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
							<input
								id="salarioDiario"
								type="number"
								bind:value={salarioDiario}
								min="0"
								step="0.01"
								class="input pl-8 tabular-nums"
								placeholder="500.00"
							/>
						</div>
						<p class="text-xs text-slate-500 mt-1">
							Salario mensual: {formatCurrency(salarioDiario * 30)}
						</p>
					</div>

					<!-- Año -->
					<div>
						<label for="year" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Año
						</label>
						<select
							id="year"
							bind:value={year}
							class="input"
						>
							{#each years as y}
								<option value={y}>{y}</option>
							{/each}
						</select>
					</div>

					{#if tipoCalculo === 'cuotas'}
						<!-- Clase de riesgo -->
						<div>
							<label for="claseRiesgo" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Clase de riesgo de trabajo
							</label>
							<select
								id="claseRiesgo"
								bind:value={claseRiesgo}
								class="input"
							>
								{#each clasesRiesgo as clase}
									<option value={clase.value}>{clase.label}</option>
								{/each}
							</select>
							{#each clasesRiesgo.filter(c => c.value === claseRiesgo) as selectedClase}
								<p class="text-xs text-slate-500 mt-1">
									Prima: {(selectedClase.prima * 100).toFixed(3)}% | Ejemplos: {selectedClase.ejemplos.join(', ')}
								</p>
							{/each}
						</div>
					{/if}

					{#if tipoCalculo === 'modalidad40'}
						<div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
							<p class="text-sm text-blue-800 dark:text-blue-300">
								<strong>Modalidad 40:</strong> Continuación voluntaria para personas que dejaron de cotizar. Permite mantener o aumentar semanas cotizadas para mejorar la pensión.
							</p>
						</div>
					{/if}

					{#if tipoCalculo === 'modalidad10'}
						<div class="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
							<p class="text-sm text-purple-800 dark:text-purple-300">
								<strong>Modalidad 10:</strong> Incorporación voluntaria para trabajadores independientes, freelancers y profesionistas que no tienen patrón.
							</p>
						</div>
					{/if}
				</div>
			</div>

			<!-- Results -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<Shield class="h-5 w-5 text-teal-500" />
					Resultados
				</h2>

				{#if tipoCalculo === 'cuotas' && resultadoCuotas}
					<div class="space-y-4">
						<!-- Totales destacados -->
						<div class="grid grid-cols-2 gap-4">
							<div class="p-4 bg-gradient-to-br from-teal-50 to-teal-100 dark:from-teal-900/20 dark:to-teal-800/20 rounded-lg border border-teal-200 dark:border-teal-800">
								<div class="text-sm font-medium text-teal-700 dark:text-teal-300 mb-1">
									Cuota patronal
								</div>
								<div class="text-2xl font-bold text-teal-900 dark:text-teal-100 tabular-nums">
									{formatCurrency(resultadoCuotas.cuotasPatron)}
								</div>
							</div>
							<div class="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg border border-blue-200 dark:border-blue-800">
								<div class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">
									Cuota trabajador
								</div>
								<div class="text-2xl font-bold text-blue-900 dark:text-blue-100 tabular-nums">
									{formatCurrency(resultadoCuotas.cuotasTrabajador)}
								</div>
							</div>
						</div>

						<!-- Desglose -->
						<div class="space-y-2">
							<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2">
								Desglose mensual
							</h3>
							<div class="max-h-64 overflow-y-auto">
								<table class="w-full text-xs">
									<thead class="sticky top-0 bg-white dark:bg-slate-900">
										<tr class="border-b border-slate-200 dark:border-slate-700">
											<th class="text-left py-2 text-slate-600 dark:text-slate-400">Concepto</th>
											<th class="text-right py-2 text-slate-600 dark:text-slate-400">Patrón</th>
											<th class="text-right py-2 text-slate-600 dark:text-slate-400">Trabajador</th>
										</tr>
									</thead>
									<tbody>
										{#each resultadoCuotas.desglose as item}
											<tr class="border-b border-slate-100 dark:border-slate-800">
												<td class="py-2 text-slate-700 dark:text-slate-300">{item.concepto}</td>
												<td class="py-2 text-right tabular-nums">{formatCurrency(item.patron)}</td>
												<td class="py-2 text-right tabular-nums">{formatCurrency(item.trabajador)}</td>
											</tr>
										{/each}
									</tbody>
								</table>
							</div>
						</div>

						<!-- Total -->
						<div class="pt-3 border-t-2 border-slate-200 dark:border-slate-700">
							<div class="flex justify-between items-center">
								<span class="text-sm font-medium text-slate-700 dark:text-slate-300">
									Cuota total mensual
								</span>
								<span class="text-xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
									{formatCurrency(resultadoCuotas.cuotaTotal)}
								</span>
							</div>
						</div>
					</div>

				{:else if tipoCalculo === 'modalidad40' && resultadoMod40}
					<div class="space-y-4">
						<div class="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg border border-blue-200 dark:border-blue-800">
							<div class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">
								Cuota mensual Modalidad 40
							</div>
							<div class="text-3xl font-bold text-blue-900 dark:text-blue-100 tabular-nums">
								{formatCurrency(resultadoMod40.cuotaMensual)}
							</div>
							<div class="text-sm text-blue-600 dark:text-blue-400 mt-1">
								Cuota anual: {formatCurrency(resultadoMod40.cuotaAnual)}
							</div>
						</div>

						<div class="space-y-2 text-sm">
							<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
								<span class="text-slate-600 dark:text-slate-400">SBC mensual aplicable</span>
								<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
									{formatCurrency(resultadoMod40.salarioMensual)}
								</span>
							</div>
							<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
								<span class="text-slate-600 dark:text-slate-400">Tasa total</span>
								<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
									{(imssTablesData.modalidad_40.cuota_mensual.porcentaje_total * 100).toFixed(2)}%
								</span>
							</div>
						</div>
					</div>

				{:else if tipoCalculo === 'modalidad10' && resultadoMod10}
					<div class="space-y-4">
						<div class="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg border border-purple-200 dark:border-purple-800">
							<div class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">
								Cuota mensual Modalidad 10
							</div>
							<div class="text-3xl font-bold text-purple-900 dark:text-purple-100 tabular-nums">
								{formatCurrency(resultadoMod10.cuotaMensual)}
							</div>
							<div class="text-sm text-purple-600 dark:text-purple-400 mt-1">
								Cuota anual: {formatCurrency(resultadoMod10.cuotaAnual)}
							</div>
						</div>

						<div class="space-y-2 text-sm">
							<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
								<span class="text-slate-600 dark:text-slate-400">Cuota fija (UMA)</span>
								<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
									{formatCurrency(resultadoMod10.cuotaFijaUMA)}
								</span>
							</div>
							<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
								<span class="text-slate-600 dark:text-slate-400">Cuota variable</span>
								<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
									{formatCurrency(resultadoMod10.cuotaVariable)}
								</span>
							</div>
							<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
								<span class="text-slate-600 dark:text-slate-400">SBC mensual aplicable</span>
								<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
									{formatCurrency(resultadoMod10.salarioMensual)}
								</span>
							</div>
						</div>
					</div>

				{:else}
					<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
						<div class="text-center">
							<Calculator class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Ingresa un salario para calcular las cuotas</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Nota legal -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Las cuotas IMSS se basan en la Ley del Seguro Social vigente.
				La prima de riesgo de trabajo puede variar según la siniestralidad de la empresa.
				Consulta con un especialista en seguridad social para casos específicos.
			</p>
		</div>
	</div>
</section>
