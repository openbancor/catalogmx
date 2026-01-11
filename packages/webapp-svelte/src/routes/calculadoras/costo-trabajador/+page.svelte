<script lang="ts">
	import { base } from '$app/paths';
	import { Calculator, Info, Users, Wallet, TrendingDown } from 'lucide-svelte';
	import {
		ImpuestosLocalesCalculator,
		WorkerCostCalculator,
		obtenerDiasVacaciones
	} from '$lib/catalogmx';
	import impuestosLocalesData from '../../../../../shared-data/sat/impuestos/impuestos_locales.json';

	type Year = 2024 | 2025 | 2026;

	// State
	let salarioMensual = $state<number>(15000);
	let antiguedadAnios = $state<number>(1);
	let year = $state<Year>(2025);
	let incluirPTU = $state<boolean>(true);
	let porcentajePTU = $state<number>(10);
	let estado = $state<string>('09');
	let diasAguinaldo = $state<number>(15);

	const estados = impuestosLocalesData.impuesto_nomina.map((e) => ({
		value: e.cve_estado,
		label: e.estado,
		tasa: e.tasa
	}));

	const years = [2024, 2025, 2026] as const;

	interface CostoResult {
		salario_bruto_mensual: number;
		cuotas_imss_patronales: number;
		infonavit: number;
		impuesto_nomina: number;
		reserva_aguinaldo: number;
		reserva_prima_vacacional: number;
		reserva_vacaciones: number;
		ptu_estimado: number;
		costo_total_mensual: number;
		costo_total_anual: number;
		factor_costo: number;
	}

	let resultado = $state<CostoResult | null>(null);
	let tasaISN = $state<number | null>(null);
	let diasVacaciones = $state<number>(0);

	function calculateCostoPatronal() {
		if (!salarioMensual || salarioMensual <= 0) {
			resultado = null;
			tasaISN = null;
			return;
		}

		const impuesto = ImpuestosLocalesCalculator.getImpuestoNomina(estado);
		tasaISN = impuesto?.tasa ?? null;
		diasVacaciones = obtenerDiasVacaciones(antiguedadAnios);

		try {
			resultado = WorkerCostCalculator.calcularCostoTotal({
				salario_mensual_bruto: salarioMensual,
				cve_estado: estado,
				antiguedad_anos: antiguedadAnios,
				dias_aguinaldo: diasAguinaldo,
				incluir_ptu: incluirPTU,
				porcentaje_ptu: porcentajePTU,
				year
			});
		} catch {
			resultado = null;
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

	function formatPercent(value: number): string {
		return new Intl.NumberFormat('es-MX', {
			style: 'percent',
			minimumFractionDigits: 1,
			maximumFractionDigits: 1
		}).format(value);
	}

	// Auto-calculate when inputs change
	$effect(() => {
		calculateCostoPatronal();
	});
</script>

<svelte:head>
	<title>Costo Total del Trabajador - catalogmx</title>
	<meta name="description" content="Calcula el costo total de un trabajador para el empleador: IMSS, Infonavit, ISN, aguinaldo, vacaciones, prima vacacional y PTU." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/calculadoras" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Calculadoras
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">Costo Total del Trabajador</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-orange-100 dark:bg-orange-900/30">
				<Users class="h-8 w-8 text-orange-600 dark:text-orange-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Costo Total del Trabajador
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Calcula el costo real para el empleador incluyendo prestaciones y cargas sociales
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
			<Info class="h-5 w-5 text-orange-600 dark:text-orange-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-orange-900 dark:text-orange-300">
				<p class="font-medium mb-1">Factor de carga laboral</p>
				<p>El costo real de un trabajador es significativamente mayor al salario nominal. Esta calculadora incluye IMSS, Infonavit, ISN y prestaciones de ley.</p>
			</div>
		</div>
	</div>
</section>

<!-- Calculator -->
<section class="py-8">
	<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 lg:grid-cols-5">
			<!-- Input Form -->
			<div class="lg:col-span-2 card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<Calculator class="h-5 w-5 text-brand-500" />
					Datos del trabajador
				</h2>

				<div class="space-y-5">
					<!-- Salario mensual -->
					<div>
						<label for="salarioMensual" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Salario mensual bruto
						</label>
						<div class="relative">
							<span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
							<input
								id="salarioMensual"
								type="number"
								bind:value={salarioMensual}
								min="0"
								step="100"
								class="input pl-8 tabular-nums"
								placeholder="15000"
							/>
						</div>
					</div>

					<!-- Antigüedad -->
					<div>
						<label for="antiguedad" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Antigüedad (años)
						</label>
						<input
							id="antiguedad"
							type="number"
							bind:value={antiguedadAnios}
							min="1"
							max="50"
							class="input tabular-nums"
						/>
						<p class="text-xs text-slate-500 mt-1">
							Días de vacaciones: {diasVacaciones} días (LFT 2023)
						</p>
					</div>

					<div class="grid grid-cols-2 gap-4">
						<!-- Año -->
						<div>
							<label for="year" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Año
							</label>
							<select id="year" bind:value={year} class="input">
								{#each years as y}
									<option value={y}>{y}</option>
								{/each}
							</select>
						</div>
					</div>

					<!-- Estado -->
					<div>
						<label for="estado" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Estado (ISN)
						</label>
						<select id="estado" bind:value={estado} class="input">
							{#each estados as e}
								<option value={e.value}>{e.label} ({e.tasa}%)</option>
							{/each}
						</select>
					</div>

					<!-- Días de aguinaldo -->
					<div>
						<label for="diasAguinaldo" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Días de aguinaldo
						</label>
						<input
							id="diasAguinaldo"
							type="number"
							bind:value={diasAguinaldo}
							min="15"
							max="90"
							class="input tabular-nums"
						/>
						<p class="text-xs text-slate-500 mt-1">Mínimo LFT: 15 días</p>
					</div>

					<!-- PTU -->
					<div class="flex items-start gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<input
							id="ptu"
							type="checkbox"
							bind:checked={incluirPTU}
							class="mt-1 h-4 w-4 rounded border-slate-300 text-brand-500 focus:ring-brand-500"
						/>
						<div class="flex-1">
							<label for="ptu" class="text-sm text-slate-700 dark:text-slate-300 cursor-pointer">
								<span class="font-medium block mb-1">Incluir PTU (estimado)</span>
							</label>
							{#if incluirPTU}
								<div class="flex items-center gap-2 mt-2">
									<input
										type="number"
										bind:value={porcentajePTU}
										min="0"
										max="100"
										class="input w-20 text-sm tabular-nums"
									/>
									<span class="text-sm text-slate-500">% del salario anual</span>
								</div>
							{/if}
						</div>
					</div>

					<!-- Reserva -->
				</div>
			</div>

			<!-- Results -->
			<div class="lg:col-span-3 space-y-6">
				{#if resultado}
					<!-- Resumen principal -->
					<div class="card p-6">
						<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
							<Wallet class="h-5 w-5 text-orange-500" />
							Costo total del trabajador
						</h2>

						<div class="grid gap-4 sm:grid-cols-3">
							<div class="p-4 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-lg border border-orange-200 dark:border-orange-800">
								<div class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">
									Costo mensual
								</div>
								<div class="text-2xl font-bold text-orange-900 dark:text-orange-100 tabular-nums">
									{formatCurrency(resultado.costo_total_mensual)}
								</div>
							</div>
							<div class="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg border border-green-200 dark:border-green-800">
								<div class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">
									Costo anual
								</div>
								<div class="text-2xl font-bold text-green-900 dark:text-green-100 tabular-nums">
									{formatCurrency(resultado.costo_total_anual)}
								</div>
							</div>
							<div class="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg border border-blue-200 dark:border-blue-800">
								<div class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">
									Factor de carga
								</div>
								<div class="text-2xl font-bold text-blue-900 dark:text-blue-100 tabular-nums">
									{formatPercent(resultado.factor_costo - 1)}
								</div>
								<div class="text-xs text-blue-600 dark:text-blue-400">
									sobre el salario
								</div>
							</div>
						</div>
					</div>

					<!-- Desglose -->
					<div class="card p-6">
						<h3 class="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
							<TrendingDown class="h-5 w-5 text-slate-500" />
							Desglose mensual
						</h3>

						<div class="space-y-4">
							<!-- Salario base -->
							<div>
								<h4 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Salario</h4>
								<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
									<span class="text-slate-600 dark:text-slate-400">Salario mensual bruto</span>
									<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.salario_bruto_mensual)}
									</span>
								</div>
							</div>

							<!-- Cargas sociales -->
							<div>
								<h4 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Cargas sociales</h4>
								<div class="space-y-1 text-sm">
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">IMSS Patrón</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.cuotas_imss_patronales)}
										</span>
									</div>
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Infonavit (5%)</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.infonavit)}
										</span>
									</div>
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">ISN ({tasaISN ?? 0}%)</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.impuesto_nomina)}
										</span>
									</div>
								</div>
							</div>

							<!-- Prestaciones -->
							<div>
								<h4 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Prestaciones (provisión mensual)</h4>
								<div class="space-y-1 text-sm">
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Aguinaldo ({diasAguinaldo} días)</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.reserva_aguinaldo)}
										</span>
									</div>
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Vacaciones ({diasVacaciones} días)</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.reserva_vacaciones)}
										</span>
									</div>
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Prima vacacional (25%)</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.reserva_prima_vacacional)}
										</span>
									</div>
									{#if incluirPTU && resultado.ptu_estimado > 0}
										<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
											<span class="text-slate-600 dark:text-slate-400">PTU ({porcentajePTU}%)</span>
											<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
												{formatCurrency(resultado.ptu_estimado)}
											</span>
										</div>
									{/if}
								</div>
							</div>

							<!-- Total -->
							<div class="pt-4 border-t-2 border-slate-200 dark:border-slate-700">
								<div class="flex justify-between items-center">
									<span class="font-bold text-slate-900 dark:text-white">
										COSTO TOTAL MENSUAL
									</span>
									<span class="text-2xl font-bold text-orange-600 dark:text-orange-400 tabular-nums">
										{formatCurrency(resultado.costo_total_mensual)}
									</span>
								</div>
							</div>
						</div>
					</div>
				{:else}
					<div class="card p-6">
						<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
							<div class="text-center">
								<Calculator class="h-12 w-12 mx-auto mb-3 opacity-50" />
								<p class="text-sm">Ingresa un salario para calcular el costo total</p>
							</div>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Nota legal -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Esta calculadora es informativa y proporciona estimaciones basadas en la LFT, LSS y disposiciones fiscales vigentes.
				Los costos reales pueden variar según situaciones específicas de cada empresa y trabajador.
				Los días de vacaciones corresponden a la reforma LFT 2023. Consulta con un especialista para cálculos precisos.
			</p>
		</div>
	</div>
</section>
