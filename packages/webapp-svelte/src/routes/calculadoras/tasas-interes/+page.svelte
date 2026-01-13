<script lang="ts">
	import { Calculator, Info, Percent, TrendingUp, Calendar, BarChart3 } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface TasaRate {
		fecha: string;
		valor: number;
	}

	// State
	let principal = $state<number>(100000);
	let tipoTasa = $state<'cetes_28' | 'tiie_28'>('cetes_28');
	let fechaInicial = $state<string>('');
	let fechaFinal = $state<string>('');
	let tasaPromedio = $state<number>(0);
	let interes = $state<number | null>(null);
	let valorFinal = $state<number | null>(null);
	let cetesRates = $state<TasaRate[]>([]);
	let tiieRates = $state<TasaRate[]>([]);
	let loading = $state<boolean>(true);

	// Comparison state
	let tasaCETES = $state<number>(0);
	let tasaTIIE = $state<number>(0);
	let diferencia = $state<number>(0);
	let interesCETES = $state<number>(0);
	let interesTIIE = $state<number>(0);

	// Derived
	let fechasDisponiblesCETES = $derived(
		cetesRates.map((r) => r.fecha).sort((a, b) => b.localeCompare(a))
	);

	let fechasDisponiblesTIIE = $derived(
		tiieRates.map((r) => r.fecha).sort((a, b) => b.localeCompare(a))
	);

	let fechasDisponibles = $derived(
		tipoTasa === 'cetes_28' ? fechasDisponiblesCETES : fechasDisponiblesTIIE
	);

	let tasaActual = $derived.by(() => {
		const rates = tipoTasa === 'cetes_28' ? cetesRates : tiieRates;
		return rates[0]?.valor || 0;
	});

	onMount(async () => {
		try {
			// Load CETES and TIIE rates from SQLite
			const [cetes, tiie] = await Promise.all([
				query<TasaRate>('SELECT fecha, tasa as valor FROM banxico_cetes WHERE plazo = 28 ORDER BY fecha DESC'),
				query<TasaRate>('SELECT fecha, tasa as valor FROM banxico_tiie WHERE plazo = 28 ORDER BY fecha DESC')
			]);

			cetesRates = cetes;
			tiieRates = tiie;

			// Set initial dates
			if (cetesRates.length > 0) {
				fechaInicial = cetesRates[cetesRates.length - 1].fecha;
				fechaFinal = cetesRates[0].fecha;
			}
		} catch (error) {
			console.error('Error loading tasas data:', error);
		} finally {
			loading = false;
		}
	});

	function calcularInteres() {
		if (!principal || principal <= 0 || !fechaInicial || !fechaFinal) {
			interes = null;
			valorFinal = null;
			return;
		}

		const rates = tipoTasa === 'cetes_28' ? cetesRates : tiieRates;

		// Get rates between dates
		const ratesInRange = rates.filter((r) => r.fecha >= fechaInicial && r.fecha <= fechaFinal);

		if (ratesInRange.length === 0) {
			interes = null;
			valorFinal = null;
			return;
		}

		// Calculate average rate
		const avgRate = ratesInRange.reduce((sum, r) => sum + r.valor, 0) / ratesInRange.length;
		tasaPromedio = avgRate;

		// Calculate days
		const startDate = new Date(fechaInicial);
		const endDate = new Date(fechaFinal);
		const days = Math.floor((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

		// Calculate simple interest
		const interesCalculado = (principal * avgRate * days) / (100 * 360);
		interes = interesCalculado;
		valorFinal = principal + interesCalculado;
	}

	function compararTasas() {
		if (cetesRates.length === 0 || tiieRates.length === 0 || !fechaInicial || !fechaFinal || !principal) return;

		// Get CETES rates
		const ceteRatesInRange = cetesRates.filter(
			(r) => r.fecha >= fechaInicial && r.fecha <= fechaFinal
		);
		const avgCETES =
			ceteRatesInRange.length > 0
				? ceteRatesInRange.reduce((sum, r) => sum + r.valor, 0) / ceteRatesInRange.length
				: 0;
		tasaCETES = avgCETES;

		// Get TIIE rates
		const tiieRatesInRange = tiieRates.filter(
			(r) => r.fecha >= fechaInicial && r.fecha <= fechaFinal
		);
		const avgTIIE =
			tiieRatesInRange.length > 0
				? tiieRatesInRange.reduce((sum, r) => sum + r.valor, 0) / tiieRatesInRange.length
				: 0;
		tasaTIIE = avgTIIE;

		diferencia = avgTIIE - avgCETES;

		// Calculate days
		const startDate = new Date(fechaInicial);
		const endDate = new Date(fechaFinal);
		const days = Math.floor((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

		// Calculate interest for both
		interesCETES = (principal * avgCETES * days) / (100 * 360);
		interesTIIE = (principal * avgTIIE * days) / (100 * 360);
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
		return `${value.toFixed(2)}%`;
	}

	function formatNumber(value: number, decimals: number = 2): string {
		return value.toFixed(decimals);
	}

	// Auto-calculate when inputs change
	$effect(() => {
		if (principal > 0 && fechaInicial && fechaFinal) {
			calcularInteres();
			compararTasas();
		}
	});
</script>

<svelte:head>
	<title>Calculadora Tasas de Interes CETES/TIIE - catalogmx</title>
	<meta
		name="description"
		content="Calcula intereses con tasas CETES 28 y TIIE 28 de Banxico. Compara rendimientos entre diferentes instrumentos de renta fija."
	/>
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a
				href="{base}/calculadoras"
				class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500"
			>
				Calculadoras
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium"
				>Tasas de Interes</span
			>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-emerald-100 dark:bg-emerald-900/30">
				<Percent class="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Tasas de Interes CETES/TIIE
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Calcula intereses y compara rendimientos - Banco de Mexico
				</p>
			</div>
		</div>

		<div
			class="flex items-start gap-2 p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800"
		>
			<Info class="h-5 w-5 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-emerald-900 dark:text-emerald-300">
				<p class="font-medium mb-1">Tasas de referencia</p>
				<p>
					<strong>CETES 28:</strong> Certificados de la Tesoreria (renta fija gubernamental).
					<strong>TIIE 28:</strong> Tasa de Interes Interbancaria de Equilibrio (referencia bancaria).
				</p>
			</div>
		</div>
	</div>
</section>

<!-- Calculator -->
<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		{#if loading}
			<div class="flex items-center justify-center py-12">
				<div class="text-center">
					<div
						class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-slate-300 border-t-brand-500 mb-3"
					></div>
					<p class="text-sm text-slate-500">Cargando datos desde SQLite...</p>
				</div>
			</div>
		{:else}
			<div class="grid gap-6 lg:grid-cols-2">
				<!-- Input Form -->
				<div class="card p-6">
					<h2
						class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2"
					>
						<Calculator class="h-5 w-5 text-brand-500" />
						Datos de entrada
					</h2>

					<div class="space-y-5">
						<!-- Tipo de tasa -->
						<div>
							<label
								for="tipoTasa"
								class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
							>
								Instrumento
							</label>
							<select id="tipoTasa" bind:value={tipoTasa} class="input">
								<option value="cetes_28">CETES 28 dias</option>
								<option value="tiie_28">TIIE 28 dias</option>
							</select>
						</div>

						<!-- Principal -->
						<div>
							<label
								for="principal"
								class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
							>
								Capital inicial
							</label>
							<div class="relative">
								<span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
								<input
									id="principal"
									type="number"
									bind:value={principal}
									min="0"
									step="1000"
									class="input pl-8 tabular-nums"
									placeholder="100000"
								/>
							</div>
						</div>

						<!-- Fecha inicial -->
						<div>
							<label
								for="fechaInicial"
								class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
							>
								<Calendar class="h-4 w-4 inline mr-1" />
								Fecha inicial
							</label>
							<select id="fechaInicial" bind:value={fechaInicial} class="input">
								{#each fechasDisponibles.slice().reverse() as fecha}
									<option value={fecha}>{fecha}</option>
								{/each}
							</select>
						</div>

						<!-- Fecha final -->
						<div>
							<label
								for="fechaFinal"
								class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
							>
								<Calendar class="h-4 w-4 inline mr-1" />
								Fecha final
							</label>
							<select id="fechaFinal" bind:value={fechaFinal} class="input">
								{#each fechasDisponibles as fecha}
									<option value={fecha}>{fecha}</option>
								{/each}
							</select>
						</div>

						<!-- Tasa promedio -->
						{#if tasaPromedio > 0}
							<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
								<div class="text-sm text-slate-600 dark:text-slate-400 mb-1">Tasa promedio</div>
								<div class="text-2xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
									{formatPercent(tasaPromedio)}
								</div>
								<div class="text-xs text-slate-500 mt-1">
									{tipoTasa === 'cetes_28' ? 'CETES 28' : 'TIIE 28'} anual
								</div>
							</div>
						{/if}
					</div>
				</div>

				<!-- Results -->
				<div class="card p-6">
					<h2
						class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2"
					>
						<TrendingUp class="h-5 w-5 text-emerald-500" />
						Resultados
					</h2>

					{#if interes !== null && valorFinal !== null}
						<div class="space-y-4">
							<!-- Valor final destacado -->
							<div
								class="p-4 bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20 rounded-lg border border-emerald-200 dark:border-emerald-800"
							>
								<div class="text-sm font-medium text-emerald-700 dark:text-emerald-300 mb-1">
									Valor final
								</div>
								<div class="text-3xl font-bold text-emerald-900 dark:text-emerald-100 tabular-nums">
									{formatCurrency(valorFinal)}
								</div>
							</div>

							<!-- Desglose -->
							<div class="space-y-3">
								<h3
									class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2"
								>
									Desglose
								</h3>

								<div class="space-y-2 text-sm">
									<div
										class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800"
									>
										<span class="text-slate-600 dark:text-slate-400">Capital inicial</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(principal)}
										</span>
									</div>

									<div
										class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800"
									>
										<span class="text-slate-600 dark:text-slate-400">Tasa promedio</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatPercent(tasaPromedio)}
										</span>
									</div>

									<div
										class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800"
									>
										<span class="text-emerald-600 dark:text-emerald-400">Intereses ganados</span>
										<span
											class="font-medium text-emerald-600 dark:text-emerald-400 tabular-nums"
										>
											+ {formatCurrency(interes)}
										</span>
									</div>

									<div
										class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800"
									>
										<span class="text-slate-600 dark:text-slate-400 font-medium">Valor final</span
										>
										<span class="font-semibold text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(valorFinal)}
										</span>
									</div>
								</div>
							</div>

							<!-- Rendimiento porcentual -->
							<div class="pt-3 border-t-2 border-slate-200 dark:border-slate-700">
								<div class="flex justify-between items-center">
									<span class="text-sm font-medium text-slate-700 dark:text-slate-300">
										Rendimiento total
									</span>
									<span class="text-xl font-bold text-emerald-600 dark:text-emerald-400 tabular-nums">
										{formatPercent((interes / principal) * 100)}
									</span>
								</div>
							</div>
						</div>
					{:else}
						<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
							<div class="text-center">
								<Calculator class="h-12 w-12 mx-auto mb-3 opacity-50" />
								<p class="text-sm">Ingresa los datos para calcular</p>
							</div>
						</div>
					{/if}
				</div>
			</div>

			<!-- Comparacion CETES vs TIIE -->
			{#if tasaCETES > 0 && tasaTIIE > 0}
				<div class="mt-8 card p-6">
					<h2
						class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2"
					>
						<BarChart3 class="h-5 w-5 text-brand-500" />
						Comparacion CETES 28 vs TIIE 28
					</h2>

					<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-6">
						<div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
							<div class="text-sm text-blue-700 dark:text-blue-300 mb-1">CETES 28</div>
							<div class="text-2xl font-bold text-blue-900 dark:text-blue-100 tabular-nums">
								{formatPercent(tasaCETES)}
							</div>
						</div>

						<div class="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
							<div class="text-sm text-purple-700 dark:text-purple-300 mb-1">TIIE 28</div>
							<div class="text-2xl font-bold text-purple-900 dark:text-purple-100 tabular-nums">
								{formatPercent(tasaTIIE)}
							</div>
						</div>

						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
							<div class="text-sm text-slate-600 dark:text-slate-400 mb-1">Diferencia</div>
							<div
								class="text-2xl font-bold tabular-nums {diferencia >= 0
									? 'text-green-600 dark:text-green-400'
									: 'text-red-600 dark:text-red-400'}"
							>
								{diferencia >= 0 ? '+' : ''}{formatPercent(diferencia)}
							</div>
						</div>

						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
							<div class="text-sm text-slate-600 dark:text-slate-400 mb-1">Diferencia interes</div>
							<div
								class="text-2xl font-bold tabular-nums {interesTIIE - interesCETES >= 0
									? 'text-green-600 dark:text-green-400'
									: 'text-red-600 dark:text-red-400'}"
							>
								{formatCurrency(Math.abs(interesTIIE - interesCETES))}
							</div>
						</div>
					</div>

					<div class="grid gap-4 sm:grid-cols-2">
						<div class="p-5 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
							<h3 class="font-semibold text-blue-900 dark:text-blue-100 mb-3">
								Inversion en CETES 28
							</h3>
							<div class="space-y-2 text-sm">
								<div class="flex justify-between">
									<span class="text-blue-700 dark:text-blue-300">Capital</span>
									<span class="font-medium text-blue-900 dark:text-blue-100 tabular-nums">
										{formatCurrency(principal)}
									</span>
								</div>
								<div class="flex justify-between">
									<span class="text-blue-700 dark:text-blue-300">Intereses</span>
									<span class="font-medium text-blue-900 dark:text-blue-100 tabular-nums">
										{formatCurrency(interesCETES)}
									</span>
								</div>
								<div class="flex justify-between pt-2 border-t border-blue-300 dark:border-blue-700">
									<span class="font-semibold text-blue-900 dark:text-blue-100">Total</span>
									<span class="font-bold text-blue-900 dark:text-blue-100 tabular-nums">
										{formatCurrency(principal + interesCETES)}
									</span>
								</div>
							</div>
						</div>

						<div class="p-5 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
							<h3 class="font-semibold text-purple-900 dark:text-purple-100 mb-3">
								Inversion en TIIE 28
							</h3>
							<div class="space-y-2 text-sm">
								<div class="flex justify-between">
									<span class="text-purple-700 dark:text-purple-300">Capital</span>
									<span class="font-medium text-purple-900 dark:text-purple-100 tabular-nums">
										{formatCurrency(principal)}
									</span>
								</div>
								<div class="flex justify-between">
									<span class="text-purple-700 dark:text-purple-300">Intereses</span>
									<span class="font-medium text-purple-900 dark:text-purple-100 tabular-nums">
										{formatCurrency(interesTIIE)}
									</span>
								</div>
								<div class="flex justify-between pt-2 border-t border-purple-300 dark:border-purple-700">
									<span class="font-semibold text-purple-900 dark:text-purple-100">Total</span>
									<span class="font-bold text-purple-900 dark:text-purple-100 tabular-nums">
										{formatCurrency(principal + interesTIIE)}
									</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			{/if}

			<!-- Info adicional -->
			<div class="mt-8 grid gap-4 sm:grid-cols-3">
				<div class="card p-5">
					<h3 class="font-semibold text-slate-900 dark:text-white mb-2">CETES</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Certificados de la Tesoreria emitidos por el gobierno federal. Instrumento de renta fija
						de bajo riesgo.
					</p>
				</div>

				<div class="card p-5">
					<h3 class="font-semibold text-slate-900 dark:text-white mb-2">TIIE</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Tasa de Interes Interbancaria de Equilibrio. Referencia para creditos y productos
						bancarios en Mexico.
					</p>
				</div>

				<div class="card p-5">
					<h3 class="font-semibold text-slate-900 dark:text-white mb-2">Fuente oficial</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Datos oficiales del Banco de Mexico. CETES (SF43936) y TIIE (SF43878) actualizados
						periodicamente.
					</p>
				</div>
			</div>

			<!-- Nota legal -->
			<div
				class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700"
			>
				<p class="text-xs text-slate-500 dark:text-slate-400">
					<strong>Nota:</strong> Esta calculadora es informativa y utiliza tasas historicas de
					Banxico. Los calculos son aproximados usando interes simple a 360 dias. Los rendimientos
					reales pueden variar segun el instrumento especifico. Para inversiones formales, consulta
					con tu institucion financiera. No considera ISR ni otras retenciones.
				</p>
			</div>
		{/if}
	</div>
</section>
