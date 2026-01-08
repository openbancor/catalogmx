<script lang="ts">
	import { Calculator, Info, DollarSign, TrendingUp, Calendar } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface ExchangeRate {
		fecha: string;
		tipo_cambio: number;
	}

	// State
	let monto = $state<number>(1000);
	let monedaOrigen = $state<'USD' | 'MXN'>('USD');
	let fechaSeleccionada = $state<string>('');
	let tasaCambio = $state<number>(18.45);
	let resultado = $state<number | null>(null);
	let exchangeRates = $state<ExchangeRate[]>([]);
	let loading = $state<boolean>(true);
	let fechaComparacion = $state<string>('');
	let tasaComparacion = $state<number>(0);

	// Derived
	let fechasDisponibles = $derived(
		exchangeRates.map((r) => r.fecha).sort((a, b) => b.localeCompare(a))
	);

	let tasaActual = $derived(exchangeRates[0]?.tipo_cambio || 18.45);

	let diferenciaTasas = $derived.by(() => {
		if (!fechaComparacion || !tasaComparacion) return null;
		const diff = tasaCambio - tasaComparacion;
		const diffPercent = ((diff / tasaComparacion) * 100);
		return { diff, diffPercent };
	});

	onMount(async () => {
		try {
			// Load exchange rates from SQLite
			const rates = await query<ExchangeRate>(
				'SELECT fecha, tipo_cambio FROM banxico_tipo_cambio ORDER BY fecha DESC'
			);

			exchangeRates = rates;

			if (exchangeRates.length > 0) {
				fechaSeleccionada = exchangeRates[0].fecha;
				tasaCambio = exchangeRates[0].tipo_cambio;
			}
		} catch (error) {
			console.error('Error loading exchange data:', error);
		} finally {
			loading = false;
		}
	});

	function calcular() {
		if (!monto || monto <= 0) {
			resultado = null;
			return;
		}

		if (monedaOrigen === 'USD') {
			resultado = monto * tasaCambio;
		} else {
			resultado = monto / tasaCambio;
		}
	}

	function onFechaChange() {
		const rate = exchangeRates.find((r) => r.fecha === fechaSeleccionada);
		if (rate) {
			tasaCambio = rate.tipo_cambio;
		}
	}

	function onFechaComparacionChange() {
		const rate = exchangeRates.find((r) => r.fecha === fechaComparacion);
		if (rate) {
			tasaComparacion = rate.tipo_cambio;
		}
	}

	function formatCurrency(value: number, currency: 'USD' | 'MXN'): string {
		return new Intl.NumberFormat('es-MX', {
			style: 'currency',
			currency: currency,
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		}).format(value);
	}

	function formatNumber(value: number, decimals: number = 4): string {
		return value.toFixed(decimals);
	}

	// Auto-calculate when inputs change
	$effect(() => {
		if (monto > 0) {
			calcular();
		}
	});

	$effect(() => {
		if (fechaSeleccionada) {
			onFechaChange();
		}
	});

	$effect(() => {
		if (fechaComparacion) {
			onFechaComparacionChange();
		}
	});
</script>

<svelte:head>
	<title>Calculadora Tipo de Cambio USD/MXN - catalogmx</title>
	<meta
		name="description"
		content="Convierte entre dolares (USD) y pesos mexicanos (MXN) con tipos de cambio historicos de Banxico. Calcula diferencias entre fechas."
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
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">Tipo de Cambio</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-purple-100 dark:bg-purple-900/30">
				<DollarSign class="h-8 w-8 text-purple-600 dark:text-purple-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Tipo de Cambio USD/MXN
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Conversion y datos historicos del Banco de Mexico
				</p>
			</div>
		</div>

		<div
			class="flex items-start gap-2 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800"
		>
			<Info class="h-5 w-5 text-purple-600 dark:text-purple-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-purple-900 dark:text-purple-300">
				<p class="font-medium mb-1">Tipo de Cambio FIX</p>
				<p>
					Tipo de cambio para solventar obligaciones en moneda extranjera publicado diariamente por
					Banxico (Serie SF43718).
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
					<div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-slate-300 border-t-brand-500 mb-3"></div>
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
						<!-- Moneda Origen -->
						<div>
							<label
								for="monedaOrigen"
								class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
							>
								Convertir de
							</label>
							<select id="monedaOrigen" bind:value={monedaOrigen} class="input">
								<option value="USD">Dolares (USD)</option>
								<option value="MXN">Pesos mexicanos (MXN)</option>
							</select>
						</div>

						<!-- Monto -->
						<div>
							<label
								for="monto"
								class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
							>
								Monto
							</label>
							<div class="relative">
								<span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">
									{monedaOrigen === 'USD' ? '$' : '$'}
								</span>
								<input
									id="monto"
									type="number"
									bind:value={monto}
									min="0"
									step="0.01"
									class="input pl-8 tabular-nums"
									placeholder="1000.00"
								/>
							</div>
						</div>

						<!-- Fecha -->
						<div>
							<label
								for="fecha"
								class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
							>
								<Calendar class="h-4 w-4 inline mr-1" />
								Fecha del tipo de cambio
							</label>
							<select id="fecha" bind:value={fechaSeleccionada} class="input">
								{#each fechasDisponibles as fecha}
									<option value={fecha}>{fecha}</option>
								{/each}
							</select>
						</div>

						<!-- Tipo de cambio actual -->
						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
							<div class="text-sm text-slate-600 dark:text-slate-400 mb-1">Tipo de cambio</div>
							<div class="text-2xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
								{formatNumber(tasaCambio)} <span class="text-base font-normal text-slate-500"
									>MXN/USD</span
								>
							</div>
							<div class="text-xs text-slate-500 mt-1">
								{fechaSeleccionada}
							</div>
						</div>
					</div>
				</div>

				<!-- Results -->
				<div class="card p-6">
					<h2
						class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2"
					>
						<DollarSign class="h-5 w-5 text-purple-500" />
						Resultado
					</h2>

					{#if resultado !== null}
						<div class="space-y-4">
							<!-- Resultado destacado -->
							<div
								class="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg border border-purple-200 dark:border-purple-800"
							>
								<div class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">
									{monedaOrigen === 'USD' ? 'Pesos mexicanos (MXN)' : 'Dolares (USD)'}
								</div>
								<div class="text-3xl font-bold text-purple-900 dark:text-purple-100 tabular-nums">
									{formatCurrency(resultado, monedaOrigen === 'USD' ? 'MXN' : 'USD')}
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
										<span class="text-slate-600 dark:text-slate-400">Monto original</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(monto, monedaOrigen)}
										</span>
									</div>

									<div
										class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800"
									>
										<span class="text-slate-600 dark:text-slate-400">Tipo de cambio</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatNumber(tasaCambio)} MXN/USD
										</span>
									</div>

									<div
										class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800"
									>
										<span class="text-slate-600 dark:text-slate-400 font-medium">Resultado</span>
										<span class="font-semibold text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado, monedaOrigen === 'USD' ? 'MXN' : 'USD')}
										</span>
									</div>
								</div>
							</div>
						</div>
					{:else}
						<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
							<div class="text-center">
								<Calculator class="h-12 w-12 mx-auto mb-3 opacity-50" />
								<p class="text-sm">Ingresa un monto para calcular</p>
							</div>
						</div>
					{/if}
				</div>
			</div>

			<!-- Comparador de fechas -->
			<div class="mt-8 card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<TrendingUp class="h-5 w-5 text-brand-500" />
					Comparar tipos de cambio
				</h2>

				<div class="grid gap-6 md:grid-cols-2">
					<div>
						<label
							for="fechaComparacion"
							class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
						>
							Comparar con fecha
						</label>
						<select id="fechaComparacion" bind:value={fechaComparacion} class="input">
							<option value="">Selecciona una fecha</option>
							{#each fechasDisponibles as fecha}
								<option value={fecha}>{fecha}</option>
							{/each}
						</select>
					</div>

					{#if diferenciaTasas}
						<div class="space-y-3">
							<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
								<div class="text-sm text-slate-600 dark:text-slate-400 mb-2">Diferencia</div>
								<div
									class="text-2xl font-bold tabular-nums {diferenciaTasas.diff >= 0
										? 'text-green-600 dark:text-green-400'
										: 'text-red-600 dark:text-red-400'}"
								>
									{diferenciaTasas.diff >= 0 ? '+' : ''}{formatNumber(diferenciaTasas.diff)}
									<span class="text-base font-normal">MXN</span>
								</div>
								<div
									class="text-sm tabular-nums {diferenciaTasas.diff >= 0
										? 'text-green-600 dark:text-green-400'
										: 'text-red-600 dark:text-red-400'}"
								>
									{diferenciaTasas.diff >= 0 ? '+' : ''}{formatNumber(diferenciaTasas.diffPercent, 2)}%
								</div>
							</div>
						</div>
					{/if}
				</div>

				{#if fechaComparacion && diferenciaTasas}
					<div class="mt-6 grid gap-4 sm:grid-cols-2">
						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
							<div class="text-sm text-slate-600 dark:text-slate-400 mb-1">
								{fechaSeleccionada}
							</div>
							<div class="text-xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
								{formatNumber(tasaCambio)} MXN/USD
							</div>
						</div>

						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
							<div class="text-sm text-slate-600 dark:text-slate-400 mb-1">
								{fechaComparacion}
							</div>
							<div class="text-xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
								{formatNumber(tasaComparacion)} MXN/USD
							</div>
						</div>
					</div>
				{/if}
			</div>

			<!-- Info adicional -->
			<div class="mt-8 grid gap-4 sm:grid-cols-3">
				<div class="card p-5">
					<h3 class="font-semibold text-slate-900 dark:text-white mb-2">Tipo de Cambio FIX</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Publicado diariamente por Banxico, valido para solventar obligaciones en moneda
						extranjera.
					</p>
				</div>

				<div class="card p-5">
					<h3 class="font-semibold text-slate-900 dark:text-white mb-2">Dias habiles</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						El tipo de cambio se publica solo en dias habiles bancarios. Fines de semana y festivos
						no hay publicacion.
					</p>
				</div>

				<div class="card p-5">
					<h3 class="font-semibold text-slate-900 dark:text-white mb-2">Fuente oficial</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Datos oficiales del Banco de Mexico (Serie SF43718) actualizados diariamente.
					</p>
				</div>
			</div>

			<!-- Nota legal -->
			<div
				class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700"
			>
				<p class="text-xs text-slate-500 dark:text-slate-400">
					<strong>Nota:</strong> Esta calculadora utiliza datos historicos del Banco de Mexico. Los
					tipos de cambio mostrados son referenciales. Para transacciones oficiales, consulta la
					publicacion diaria del DOF o el sitio web de Banxico.
				</p>
			</div>
		{/if}
	</div>
</section>
