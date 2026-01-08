<script lang="ts">
	import { Calculator, Info, TrendingUp, Receipt } from 'lucide-svelte';
	import isrTablesData from '../../../../../shared-data/isr-tables.json';

	// Types
	interface ISRBracket {
		limiteInferior: number;
		limiteSuperior: number | null;
		cuotaFija: number;
		tasa: number;
	}

	interface SubsidyTier {
		desde: number;
		hasta: number | null;
		subsidio: number;
	}

	interface SubsidyFlat {
		amount: number;
		maxIncome: number;
	}

	interface CalculationResult {
		ingresoGravable: number;
		limiteInferior: number;
		excedente: number;
		cuotaFija: number;
		impuestoMarginal: number;
		isrCausado: number;
		subsidioEmpleo: number;
		isrRetener: number;
		tasaEfectiva: number;
	}

	// State
	let ingreso = $state<number>(15000);
	let periodo = $state<'daily' | 'weekly' | 'biweekly' | 'monthly' | 'annual'>('monthly');
	let year = $state<2024 | 2025 | 2026>(2025);
	let aplicarSubsidio = $state<boolean>(true);
	let resultado = $state<CalculationResult | null>(null);

	const periodos = [
		{ value: 'daily', label: 'Diario' },
		{ value: 'weekly', label: 'Semanal' },
		{ value: 'biweekly', label: 'Quincenal' },
		{ value: 'monthly', label: 'Mensual' },
		{ value: 'annual', label: 'Anual' }
	] as const;

	const years = [2024, 2025, 2026] as const;

	// Functions
	function findBracket(income: number, brackets: ISRBracket[]): ISRBracket | null {
		for (const bracket of brackets) {
			if (income >= bracket.limiteInferior) {
				if (bracket.limiteSuperior === null || income <= bracket.limiteSuperior) {
					return bracket;
				}
			}
		}
		return null;
	}

	function calculateSubsidy(income: number, year: number, period: string): number {
		if (!aplicarSubsidio) return 0;

		const subsidyData = isrTablesData.subsidies[year.toString() as '2024' | '2025' | '2026'];

		if (!subsidyData) return 0;

		// For 2024, use tiered system
		if (subsidyData.type === 'tiered') {
			// Only monthly subsidy available in 2024
			if (period !== 'monthly') return 0;

			const tiers = subsidyData.monthly as SubsidyTier[];
			for (const tier of tiers) {
				if (income >= tier.desde) {
					if (tier.hasta === null || income <= tier.hasta) {
						return tier.subsidio;
					}
				}
			}
			return 0;
		}

		// For 2025/2026, use flat system
		if (subsidyData.type === 'flat') {
			const flat = subsidyData.monthly as SubsidyFlat;

			// Convert income to monthly equivalent if needed
			let monthlyIncome = income;
			switch (period) {
				case 'daily':
					monthlyIncome = income * 30;
					break;
				case 'weekly':
					monthlyIncome = income * 4.33;
					break;
				case 'biweekly':
					monthlyIncome = income * 2;
					break;
				case 'annual':
					monthlyIncome = income / 12;
					break;
			}

			// Check if income qualifies
			if (monthlyIncome <= flat.maxIncome) {
				// Return subsidy proportional to the period
				switch (period) {
					case 'daily':
						return flat.amount / 30;
					case 'weekly':
						return flat.amount / 4.33;
					case 'biweekly':
						return flat.amount / 2;
					case 'annual':
						return flat.amount * 12;
					default:
						return flat.amount;
				}
			}
		}

		return 0;
	}

	function calculateISR() {
		if (!ingreso || ingreso <= 0) {
			resultado = null;
			return;
		}

		const yearKey = year.toString() as '2024' | '2025' | '2026';
		const brackets = isrTablesData.brackets[yearKey][periodo] as ISRBracket[];

		const bracket = findBracket(ingreso, brackets);

		if (!bracket) {
			resultado = null;
			return;
		}

		const limiteInferior = bracket.limiteInferior;
		const excedente = ingreso - limiteInferior;
		const cuotaFija = bracket.cuotaFija;
		const tasa = bracket.tasa;

		const impuestoMarginal = (excedente * tasa) / 100;
		const isrCausado = cuotaFija + impuestoMarginal;

		const subsidioEmpleo = calculateSubsidy(ingreso, year, periodo);
		const isrRetener = Math.max(0, isrCausado - subsidioEmpleo);

		const tasaEfectiva = (isrRetener / ingreso) * 100;

		resultado = {
			ingresoGravable: ingreso,
			limiteInferior,
			excedente,
			cuotaFija,
			impuestoMarginal,
			isrCausado,
			subsidioEmpleo,
			isrRetener,
			tasaEfectiva
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
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		}).format(value / 100);
	}

	// Auto-calculate when inputs change
	$effect(() => {
		if (ingreso > 0) {
			calculateISR();
		}
	});
</script>

<svelte:head>
	<title>Calculadora ISR - catalogmx</title>
	<meta name="description" content="Calcula el ISR (Impuesto Sobre la Renta) con tarifas oficiales 2024-2026 y subsidio al empleo. Periodos: mensual, anual, quincenal, semanal." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="/calculadoras" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Calculadoras
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">ISR</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-red-100 dark:bg-red-900/30">
				<Receipt class="h-8 w-8 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Calculadora ISR
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Calcula el Impuesto Sobre la Renta con tarifas oficiales del SAT
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
			<Info class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-blue-900 dark:text-blue-300">
				<p class="font-medium mb-1">Datos oficiales SAT</p>
				<p>Tarifas ISR 2024-2026 del Anexo 8 de la Resolución Miscelánea Fiscal. Incluye subsidio al empleo.</p>
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
							Ingreso gravable
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
								placeholder="15000.00"
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

					<!-- Subsidio -->
					<div class="flex items-start gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<input
							id="subsidio"
							type="checkbox"
							bind:checked={aplicarSubsidio}
							class="mt-1 h-4 w-4 rounded border-slate-300 text-brand-500 focus:ring-brand-500"
						/>
						<label for="subsidio" class="text-sm text-slate-700 dark:text-slate-300 cursor-pointer">
							<span class="font-medium block mb-1">Aplicar subsidio al empleo</span>
							<span class="text-slate-500 dark:text-slate-400">
								Reducción del ISR para ingresos bajos y medios
							</span>
						</label>
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
					<div class="space-y-4">
						<!-- ISR final (destacado) -->
						<div class="p-4 bg-gradient-to-br from-brand-50 to-brand-100 dark:from-brand-900/20 dark:to-brand-800/20 rounded-lg border border-brand-200 dark:border-brand-800">
							<div class="text-sm font-medium text-brand-700 dark:text-brand-300 mb-1">
								ISR a retener
							</div>
							<div class="text-3xl font-bold text-brand-900 dark:text-brand-100 tabular-nums">
								{formatCurrency(resultado.isrRetener)}
							</div>
							<div class="text-sm text-brand-600 dark:text-brand-400 mt-1">
								Tasa efectiva: {formatPercent(resultado.tasaEfectiva)}
							</div>
						</div>

						<!-- Desglose -->
						<div class="space-y-3">
							<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2">
								Desglose del cálculo
							</h3>

							<div class="space-y-2 text-sm">
								<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
									<span class="text-slate-600 dark:text-slate-400">Ingreso gravable</span>
									<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.ingresoGravable)}
									</span>
								</div>

								<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
									<span class="text-slate-600 dark:text-slate-400">Límite inferior</span>
									<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.limiteInferior)}
									</span>
								</div>

								<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
									<span class="text-slate-600 dark:text-slate-400">Excedente</span>
									<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.excedente)}
									</span>
								</div>

								<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
									<span class="text-slate-600 dark:text-slate-400">Cuota fija</span>
									<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.cuotaFija)}
									</span>
								</div>

								<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
									<span class="text-slate-600 dark:text-slate-400">Impuesto marginal</span>
									<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.impuestoMarginal)}
									</span>
								</div>

								<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
									<span class="text-slate-600 dark:text-slate-400 font-medium">ISR causado</span>
									<span class="font-semibold text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.isrCausado)}
									</span>
								</div>

								{#if aplicarSubsidio && resultado.subsidioEmpleo > 0}
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-green-600 dark:text-green-400">Subsidio al empleo</span>
										<span class="font-medium text-green-600 dark:text-green-400 tabular-nums">
											- {formatCurrency(resultado.subsidioEmpleo)}
										</span>
									</div>
								{/if}
							</div>
						</div>

						<!-- Ingreso neto -->
						<div class="pt-3 border-t-2 border-slate-200 dark:border-slate-700">
							<div class="flex justify-between items-center">
								<span class="text-sm font-medium text-slate-700 dark:text-slate-300">
									Ingreso neto estimado
								</span>
								<span class="text-xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
									{formatCurrency(resultado.ingresoGravable - resultado.isrRetener)}
								</span>
							</div>
						</div>
					</div>
				{:else}
					<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
						<div class="text-center">
							<Calculator class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Ingresa un monto para calcular el ISR</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info adicional -->
		<div class="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
			<div class="card p-5">
				<h3 class="font-semibold text-slate-900 dark:text-white mb-2">
					Tarifas 2024
				</h3>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					Tarifas base sin actualización. Subsidio escalonado con 11 rangos de ingreso.
				</p>
			</div>

			<div class="card p-5">
				<h3 class="font-semibold text-slate-900 dark:text-white mb-2">
					Tarifas 2025
				</h3>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					Tarifas sin cambios (inflación &lt;10%). Subsidio fijo de $475.00 mensuales.
				</p>
			</div>

			<div class="card p-5">
				<h3 class="font-semibold text-slate-900 dark:text-white mb-2">
					Tarifas 2026
				</h3>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					Actualizadas 13.21% por inflación. Subsidio fijo de $536.21 mensuales (15.02% UMA).
				</p>
			</div>
		</div>

		<!-- Nota legal -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Esta calculadora es informativa y utiliza tarifas oficiales del SAT (Anexo 8 RMF).
				Los resultados son estimados y pueden variar según deducciones personales y otras consideraciones fiscales.
				Consulta con un contador para casos específicos.
			</p>
		</div>
	</div>
</section>
