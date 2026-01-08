<script lang="ts">
	import { Calculator, Info, TrendingUp } from 'lucide-svelte';
	import resicoTablesData from '../../../../../shared-data/resico-tables.json';

	// Types
	interface RESICOBracket {
		limiteInferior: number;
		limiteSuperior: number;
		tasa: number;
	}

	interface CalculationResult {
		ingreso: number;
		tasa: number;
		isrResico: number;
		tasaEfectiva: number;
		eligible: boolean;
	}

	// State
	let ingreso = $state<number>(50000);
	let periodo = $state<'mensual' | 'anual'>('mensual');
	let year = $state<2024 | 2025 | 2026>(2025);
	let resultado = $state<CalculationResult | null>(null);

	const periodos = [
		{ value: 'mensual', label: 'Mensual' },
		{ value: 'anual', label: 'Anual' }
	] as const;

	const years = [2024, 2025, 2026] as const;

	// Limits from data
	const limits = resicoTablesData.limits.personaFisica;

	// Derived brackets for current year/periodo
	let currentBrackets = $derived(() => {
		const yearKey = year.toString() as '2024' | '2025' | '2026';
		return resicoTablesData.brackets[yearKey][periodo] as RESICOBracket[];
	});

	// Functions
	function findBracket(income: number, brackets: RESICOBracket[]): RESICOBracket | null {
		for (const bracket of brackets) {
			if (income >= bracket.limiteInferior && income <= bracket.limiteSuperior) {
				return bracket;
			}
		}
		return null;
	}

	function isEligible(income: number, period: 'mensual' | 'anual'): boolean {
		const maxIncome = period === 'mensual' ? limits.ingresoMensualMaximo : limits.ingresoAnualMaximo;
		return income <= maxIncome;
	}

	function calculateRESICO() {
		if (!ingreso || ingreso <= 0) {
			resultado = null;
			return;
		}

		const yearKey = year.toString() as '2024' | '2025' | '2026';
		const brackets = resicoTablesData.brackets[yearKey][periodo] as RESICOBracket[];

		const eligible = isEligible(ingreso, periodo);

		if (!eligible) {
			resultado = {
				ingreso,
				tasa: 0,
				isrResico: 0,
				tasaEfectiva: 0,
				eligible: false
			};
			return;
		}

		const bracket = findBracket(ingreso, brackets);

		if (!bracket) {
			resultado = null;
			return;
		}

		const tasa = bracket.tasa;
		const isrResico = (ingreso * tasa) / 100;
		const tasaEfectiva = tasa;

		resultado = {
			ingreso,
			tasa,
			isrResico,
			tasaEfectiva,
			eligible: true
		};
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
		}).format(value / 100);
	}

	// Auto-calculate when inputs change
	$effect(() => {
		if (ingreso > 0) {
			calculateRESICO();
		}
	});
</script>

<svelte:head>
	<title>Calculadora RESICO - catalogmx</title>
	<meta name="description" content="Calcula el ISR bajo el Régimen Simplificado de Confianza (RESICO) con tarifas 2024-2026. Tasas del 1% al 2.5%." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="/calculadoras" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Calculadoras
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">RESICO</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-blue-100 dark:bg-blue-900/30">
				<TrendingUp class="h-8 w-8 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Calculadora RESICO
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Régimen Simplificado de Confianza para personas físicas
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
			<Info class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-blue-900 dark:text-blue-300">
				<p class="font-medium mb-1">Régimen Simplificado</p>
				<p>RESICO aplica tasas directas sobre ingresos totales (1% a 2.5%). Sin cuota fija ni cálculo de excedente. Límite: {formatCurrency(limits.ingresoAnualMaximo)} anuales.</p>
			</div>
		</div>
	</div>
</section>

<!-- Calculator -->
<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Input Form -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<Calculator class="h-5 w-5 text-brand-500" />
					Datos de entrada
				</h2>

				<div class="space-y-5">
					<!-- Ingreso -->
					<div>
						<label for="ingreso" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Ingreso total
						</label>
						<div class="relative">
							<span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
							<input
								id="ingreso"
								type="number"
								bind:value={ingreso}
								min="0"
								step="0.01"
								class="input pl-8 tabular-nums"
								placeholder="50000.00"
							/>
						</div>
					</div>

					<!-- Periodo -->
					<div>
						<label for="periodo" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Periodo
						</label>
						<select
							id="periodo"
							bind:value={periodo}
							class="input"
						>
							{#each periodos as p}
								<option value={p.value}>{p.label}</option>
							{/each}
						</select>
					</div>

					<!-- Año -->
					<div>
						<label for="year" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Año fiscal
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

					<!-- Límites info -->
					<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<p class="text-sm text-slate-600 dark:text-slate-400">
							<span class="font-medium">Límite {periodo}:</span>
							{formatCurrency(periodo === 'mensual' ? limits.ingresoMensualMaximo : limits.ingresoAnualMaximo)}
						</p>
					</div>
				</div>
			</div>

			<!-- Results -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<TrendingUp class="h-5 w-5 text-green-500" />
					Resultados
				</h2>

				{#if resultado}
					{#if resultado.eligible}
						<div class="space-y-4">
							<!-- ISR final (destacado) -->
							<div class="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg border border-blue-200 dark:border-blue-800">
								<div class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">
									ISR RESICO a pagar
								</div>
								<div class="text-3xl font-bold text-blue-900 dark:text-blue-100 tabular-nums">
									{formatCurrency(resultado.isrResico)}
								</div>
								<div class="text-sm text-blue-600 dark:text-blue-400 mt-1">
									Tasa aplicada: {formatPercent(resultado.tasa)}
								</div>
							</div>

							<!-- Desglose -->
							<div class="space-y-3">
								<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2">
									Desglose del cálculo
								</h3>

								<div class="space-y-2 text-sm">
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Ingreso total</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.ingreso)}
										</span>
									</div>

									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Tasa RESICO</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatPercent(resultado.tasa)}
										</span>
									</div>

									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Cálculo</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.ingreso)} × {resultado.tasa}%
										</span>
									</div>
								</div>
							</div>

							<!-- Ingreso neto -->
							<div class="pt-3 border-t-2 border-slate-200 dark:border-slate-700">
								<div class="flex justify-between items-center">
									<span class="text-sm font-medium text-slate-700 dark:text-slate-300">
										Ingreso neto estimado
									</span>
									<span class="text-xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.ingreso - resultado.isrResico)}
									</span>
								</div>
							</div>
						</div>
					{:else}
						<div class="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
							<p class="text-red-800 dark:text-red-300 font-medium mb-2">No elegible para RESICO</p>
							<p class="text-sm text-red-700 dark:text-red-400">
								El ingreso {periodo} de {formatCurrency(ingreso)} excede el límite de {formatCurrency(periodo === 'mensual' ? limits.ingresoMensualMaximo : limits.ingresoAnualMaximo)}.
							</p>
							<p class="text-sm text-red-600 dark:text-red-500 mt-2">
								Debes tributar en régimen general de actividad empresarial.
							</p>
						</div>
					{/if}
				{:else}
					<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
						<div class="text-center">
							<Calculator class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Ingresa un monto para calcular el ISR RESICO</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Tabla de tasas -->
		<div class="mt-8 card p-6">
			<h3 class="font-semibold text-slate-900 dark:text-white mb-4">
				Tasas RESICO por rango de ingresos {periodo === 'mensual' ? 'mensuales' : 'anuales'}
			</h3>
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead>
						<tr class="border-b border-slate-200 dark:border-slate-700">
							<th class="text-left py-2 px-3 text-slate-600 dark:text-slate-400">Desde</th>
							<th class="text-left py-2 px-3 text-slate-600 dark:text-slate-400">Hasta</th>
							<th class="text-right py-2 px-3 text-slate-600 dark:text-slate-400">Tasa</th>
						</tr>
					</thead>
					<tbody>
						{#each currentBrackets() as bracket}
							<tr class="border-b border-slate-100 dark:border-slate-800">
								<td class="py-2 px-3 tabular-nums">{formatCurrency(bracket.limiteInferior)}</td>
								<td class="py-2 px-3 tabular-nums">{formatCurrency(bracket.limiteSuperior)}</td>
								<td class="py-2 px-3 text-right font-medium tabular-nums">{bracket.tasa}%</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>

		<!-- Nota legal -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> RESICO es un régimen fiscal simplificado para personas físicas con actividades empresariales, profesionales y arrendamiento.
				Artículo 113-E LISR. Consulta con un contador para verificar tu elegibilidad.
			</p>
		</div>
	</div>
</section>
