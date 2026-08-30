<script lang="ts">
	import { base } from '$app/paths';
	import { Calculator, Info, Shield, Users } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { IMSSCalculator, initCatalogmxSqlite } from '$lib/catalogmx';

	type TipoCalculo = 'cuotas' | 'modalidad40';
	type ClaseRiesgo = 1 | 2 | 3 | 4 | 5;
	type ZonaSalario = 'general' | 'frontera';
	type Year = 2024 | 2025 | 2026;

	// State
	let tipoCalculo = $state<TipoCalculo>('cuotas');
	let salarioDiario = $state<number>(500);
	let ultimoSbcDiario = $state<number>(500);
	let errorCuotas = $state<string | null>(null);
	let errorModalidad40 = $state<string | null>(null);
	let claseRiesgo = $state<ClaseRiesgo>(1);
	let zonaSalario = $state<ZonaSalario>('general');
	let year = $state<Year>(2025);
	let catalogsReady = $state(false);

	const tiposCalculo = [
		{ value: 'cuotas', label: 'Cuotas Obrero-Patronales', icon: Users },
		{ value: 'modalidad40', label: 'Modalidad 40 (Voluntaria)', icon: Shield }
	] as const;

	let clasesRiesgo = $state<
		Array<{ value: ClaseRiesgo; label: string; prima: number; ejemplos: string[] }>
	>([]);

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
		porcentajeTotal: number;
	}

	let resultadoCuotas = $state<CuotasResult | null>(null);
	let resultadoMod40 = $state<Modalidad40Result | null>(null);

	function calculateCuotas() {
		errorCuotas = null;
		resultadoCuotas = null;
		try {
			const uma = IMSSCalculator.getUMA(year).diaria;
			const salarioMensual = salarioDiario * 30;
			const result = IMSSCalculator.calcularCuotasObreroPatronales(
				salarioDiario,
				30,
				year,
				claseRiesgo,
				undefined,
				zonaSalario
			);
		const labels: Record<string, string> = {
			enfermedad_mat_cuota_fija: 'E&M - Cuota fija (UMA)',
			enfermedad_mat_excedente: 'E&M - Excedente 3 UMA',
			enfermedad_mat_dinero: 'E&M - Prestaciones en dinero',
			gastos_medicos_pensionados: 'Gastos médicos pensionados',
			invalidez_vida: 'Invalidez y vida',
			retiro: 'Retiro (SAR)',
			cesantia_vejez: 'Cesantía y vejez',
			guarderias: 'Guarderías',
			riesgo_trabajo: `Riesgo de trabajo (Clase ${claseRiesgo})`
		};

			const keys = new Set([
				...Object.keys(result.cuotas_patron),
				...Object.keys(result.cuotas_trabajador)
			]);
			const desglose: CuotasResult['desglose'] = Array.from(keys).map((key) => ({
				concepto: labels[key] ?? key.replace(/_/g, ' '),
				patron: result.cuotas_patron[key] ?? 0,
				trabajador: result.cuotas_trabajador[key] ?? 0
			}));

			resultadoCuotas = {
				salarioDiario,
				salarioMensual,
				uma,
				cuotasPatron: result.total_patron,
				cuotasTrabajador: result.total_trabajador,
				cuotaTotal: result.total_imss,
				desglose
			};
		} catch (error) {
			errorCuotas =
				error instanceof Error ? error.message : 'No fue posible calcular las cuotas IMSS.';
		}
	}

	function calculateModalidad40() {
		errorModalidad40 = null;
		resultadoMod40 = null;

		if (!ultimoSbcDiario || ultimoSbcDiario <= 0) {
			errorModalidad40 = 'Captura el último SBC diario registrado.';
			return;
		}
		if (salarioDiario < ultimoSbcDiario) {
			errorModalidad40 = 'El SBC elegido no puede ser menor al último SBC registrado.';
			return;
		}

		const uma = IMSSCalculator.getUMA(year);
		const factorMensual = uma.mensual / uma.diaria;

		try {
			const result = IMSSCalculator.calcularModalidad40(
				salarioDiario * factorMensual,
				ultimoSbcDiario * factorMensual,
				year,
				undefined,
				zonaSalario
			);

			resultadoMod40 = {
				salarioDiario: result.salario_base_cotizacion / factorMensual,
				salarioMensual: result.salario_base_cotizacion,
				cuotaMensual: result.cuota_mensual,
				cuotaAnual: result.cuota_mensual * 12,
				porcentajeTotal: result.porcentaje_total
			};
		} catch (error) {
			errorModalidad40 =
				error instanceof Error ? error.message : 'No fue posible calcular Modalidad 40.';
		}
	}

	function calculate() {
		if (!salarioDiario || salarioDiario <= 0) {
			resultadoCuotas = null;
			resultadoMod40 = null;
			errorCuotas = null;
			errorModalidad40 = null;
			return;
		}

		if (tipoCalculo === 'cuotas') {
			errorModalidad40 = null;
			calculateCuotas();
		} else if (tipoCalculo === 'modalidad40') {
			errorCuotas = null;
			calculateModalidad40();
		} else {
			const unsupportedCalculation: never = tipoCalculo;
			throw new Error(`Tipo de cálculo IMSS no compatible: ${unsupportedCalculation}`);
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
		if (catalogsReady) calculate();
	});

	onMount(async () => {
		await initCatalogmxSqlite();
		clasesRiesgo = IMSSCalculator.getClasesRiesgoTrabajo().map((item) => ({
			value: item.clase as ClaseRiesgo,
			label: `Clase ${item.clase} - ${item.descripcion.replace(`Clase ${item.clase} - `, '')}`,
			prima: item.prima,
			ejemplos: item.ejemplos
		}));
		catalogsReady = true;
	});
</script>

<svelte:head>
	<title>Calculadora IMSS - catalogmx</title>
	<meta name="description" content="Calcula cuotas IMSS obrero-patronales y Modalidad 40 con los parámetros públicos verificados." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/calculadoras" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
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
					Cuotas obrero-patronales y Modalidad 40 voluntaria
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-teal-50 dark:bg-teal-900/20 rounded-lg border border-teal-200 dark:border-teal-800">
			<Info class="h-5 w-5 text-teal-600 dark:text-teal-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-teal-900 dark:text-teal-300">
				<p class="font-medium mb-1">Cuotas IMSS {year}</p>
				<p>UMA {year}: {formatCurrency(IMSSCalculator.getUMA(year).diaria)} diarios. Tope de cotización: 25 UMAs.</p>
			</div>
		</div>

		<div class="mt-4 flex items-start gap-2 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
			<Info class="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
			<p class="text-sm text-amber-900 dark:text-amber-300">
				La modalidad administrativa para personas trabajadoras independientes no está disponible en esta calculadora;
				<a class="font-medium underline" href="https://github.com/openbancor/catalogmx/issues/97">Modalidad 10/PTI: pendiente de auditoría</a>.
			</p>
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
							{tipoCalculo === 'modalidad40' ? 'SBC diario elegido' : 'Salario diario integrado (SDI)'}
						</label>
						<div class="relative">
							<span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
							<input
								id="salarioDiario"
								type="number"
								bind:value={salarioDiario}
								min={IMSSCalculator.getSalarioMinimo(year, zonaSalario)}
								step="0.01"
								class="input pl-8 tabular-nums"
								placeholder="500.00"
							/>
						</div>
						<p class="text-xs text-slate-500 mt-1">
							{#if tipoCalculo === 'modalidad40'}
								Equivalente mensual M40: {formatCurrency(
									salarioDiario *
										(IMSSCalculator.getUMA(year).mensual / IMSSCalculator.getUMA(year).diaria)
								)}
							{:else}
								Salario mensual: {formatCurrency(salarioDiario * 30)}
							{/if}
						</p>
						{#if tipoCalculo === 'cuotas' && errorCuotas}
							<div
								data-testid="cuotas-error"
								aria-live="polite"
								class="mt-3 p-3 rounded-lg border border-red-200 bg-red-50 text-sm text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300"
							>
								{errorCuotas}
							</div>
						{/if}
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

					<div>
						<label for="zonaSalario" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Zona salarial aplicable
						</label>
						<select id="zonaSalario" bind:value={zonaSalario} class="input">
							<option value="general">General</option>
							<option value="frontera">Zona Libre de la Frontera Norte</option>
						</select>
						<p class="text-xs text-slate-500 mt-1">Se usa para identificar correctamente la fila especial CEAV de 1 salario mínimo.</p>
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
						<div>
							<label for="ultimoSbcDiario" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Último SBC diario registrado
							</label>
							<div class="relative">
								<span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
								<input
									id="ultimoSbcDiario"
									type="number"
									bind:value={ultimoSbcDiario}
									min="0.01"
									max={IMSSCalculator.getUMA(year).diaria * 25}
									step="0.01"
									class="input pl-8 tabular-nums"
								/>
							</div>
							<p class="text-xs text-slate-500 mt-1">
								Equivalente mensual: {formatCurrency(
									ultimoSbcDiario *
										(IMSSCalculator.getUMA(year).mensual / IMSSCalculator.getUMA(year).diaria)
								)}. El SBC elegido no puede ser menor; el tope es 25 UMA.
							</p>
						</div>

						{#if errorModalidad40}
							<div class="p-3 rounded-lg border border-red-200 bg-red-50 text-sm text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300">
								{errorModalidad40}
							</div>
						{/if}

						<div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
							<p class="text-sm text-blue-800 dark:text-blue-300">
								<strong>Modalidad 40:</strong> Continuación voluntaria para personas que dejaron de cotizar. Permite mantener o aumentar semanas cotizadas para mejorar la pensión.
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
									{(resultadoMod40.porcentajeTotal * 100).toFixed(2)}%
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
