<script lang="ts">
	import { Calculator, Info, TrendingUp, Calendar, LineChart } from 'lucide-svelte';
	import { onMount } from 'svelte';

	interface UDIValue {
		date: string;
		value: number;
	}

	interface UDIData {
		metadata: {
			source: string;
			series: string;
			description: string;
			unit: string;
			last_updated: string;
		};
		values: UDIValue[];
	}

	// State
	let monto = $state<number>(10000);
	let direccionConversion = $state<'udi-to-mxn' | 'mxn-to-udi'>('udi-to-mxn');
	let fechaSeleccionada = $state<string>('');
	let valorUDI = $state<number>(8.253456);
	let resultado = $state<number | null>(null);
	let udiData = $state<UDIData | null>(null);
	let loading = $state<boolean>(true);

	// Investment calculator
	let montoInicial = $state<number>(100000);
	let fechaInicial = $state<string>('');
	let fechaFinal = $state<string>('');
	let valorUDIInicial = $state<number>(0);
	let valorUDIFinal = $state<number>(0);
	let rendimiento = $state<{
		valorFinal: number;
		rendimientoTotal: number;
		rendimientoPercent: number;
		udisInicial: number;
		udisFinal: number;
	} | null>(null);

	// Derived
	let fechasDisponibles = $derived(
		udiData?.values.map((v) => v.date).sort((a, b) => b.localeCompare(a)) || []
	);

	let valorActual = $derived(udiData?.values[0]?.value || 8.253456);

	onMount(async () => {
		try {
			const response = await fetch('/data/banxico/udi.json');
			udiData = await response.json();
			if (udiData && udiData.values.length > 0) {
				fechaSeleccionada = udiData.values[0].date;
				valorUDI = udiData.values[0].value;
			}
		} catch (error) {
			console.error('Error loading UDI data:', error);
		} finally {
			loading = false;
		}
	});

	function calcular() {
		if (!monto || monto <= 0) {
			resultado = null;
			return;
		}

		if (direccionConversion === 'udi-to-mxn') {
			resultado = monto * valorUDI;
		} else {
			resultado = monto / valorUDI;
		}
	}

	function calcularRendimiento() {
		if (!montoInicial || !fechaInicial || !fechaFinal || montoInicial <= 0) {
			rendimiento = null;
			return;
		}

		const udisInicial = montoInicial / valorUDIInicial;
		const valorFinal = udisInicial * valorUDIFinal;
		const rendimientoTotal = valorFinal - montoInicial;
		const rendimientoPercent = (rendimientoTotal / montoInicial) * 100;

		rendimiento = {
			valorFinal,
			rendimientoTotal,
			rendimientoPercent,
			udisInicial,
			udisFinal: udisInicial * valorUDIFinal
		};
	}

	function onFechaChange() {
		const value = udiData?.values.find((v) => v.date === fechaSeleccionada);
		if (value) {
			valorUDI = value.value;
		}
	}

	function onFechaInicialChange() {
		const value = udiData?.values.find((v) => v.date === fechaInicial);
		if (value) {
			valorUDIInicial = value.value;
			calcularRendimiento();
		}
	}

	function onFechaFinalChange() {
		const value = udiData?.values.find((v) => v.date === fechaFinal);
		if (value) {
			valorUDIFinal = value.value;
			calcularRendimiento();
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

	function formatNumber(value: number, decimals: number = 6): string {
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
		if (fechaInicial) {
			onFechaInicialChange();
		}
	});

	$effect(() => {
		if (fechaFinal) {
			onFechaFinalChange();
		}
	});

	$effect(() => {
		if (montoInicial > 0 && valorUDIInicial > 0 && valorUDIFinal > 0) {
			calcularRendimiento();
		}
	});
</script>

<svelte:head>
	<title>Calculadora UDI - catalogmx</title>
	<meta
		name="description"
		content="Convierte entre UDIs y pesos mexicanos. Calcula rendimientos de inversiones indexadas a UDIs con datos históricos de Banxico."
	/>
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a
				href="/calculadoras"
				class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500"
			>
				Calculadoras
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">UDI</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-blue-100 dark:bg-blue-900/30">
				<TrendingUp class="h-8 w-8 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Calculadora UDI
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Unidades de Inversión - Banco de México
				</p>
			</div>
		</div>

		<div
			class="flex items-start gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800"
		>
			<Info class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-blue-900 dark:text-blue-300">
				<p class="font-medium mb-1">Unidades de Inversión (UDIs)</p>
				<p>
					Unidades de cuenta de valor real constante, basadas en el Índice Nacional de Precios al
					Consumidor (INPC). Se utilizan para créditos hipotecarios y otros instrumentos financieros.
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
					<p class="text-sm text-slate-500">Cargando datos...</p>
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
						Conversión UDI ↔ MXN
					</h2>

					<div class="space-y-5">
						<!-- Dirección conversión -->
						<div>
							<label
								for="direccion"
								class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
							>
								Tipo de conversión
							</label>
							<select id="direccion" bind:value={direccionConversion} class="input">
								<option value="udi-to-mxn">UDI → Pesos (MXN)</option>
								<option value="mxn-to-udi">Pesos (MXN) → UDI</option>
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
									{direccionConversion === 'udi-to-mxn' ? '' : '$'}
								</span>
								<input
									id="monto"
									type="number"
									bind:value={monto}
									min="0"
									step="0.01"
									class="input {direccionConversion === 'mxn-to-udi' ? 'pl-8' : ''} tabular-nums"
									placeholder="10000.00"
								/>
							</div>
							<p class="text-xs text-slate-500 mt-1">
								{direccionConversion === 'udi-to-mxn' ? 'Cantidad en UDIs' : 'Cantidad en pesos'}
							</p>
						</div>

						<!-- Fecha -->
						<div>
							<label
								for="fecha"
								class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
							>
								<Calendar class="h-4 w-4 inline mr-1" />
								Fecha del valor UDI
							</label>
							<select id="fecha" bind:value={fechaSeleccionada} class="input">
								{#each fechasDisponibles as fecha}
									<option value={fecha}>{fecha}</option>
								{/each}
							</select>
						</div>

						<!-- Valor UDI actual -->
						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
							<div class="text-sm text-slate-600 dark:text-slate-400 mb-1">Valor UDI</div>
							<div class="text-2xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
								{formatCurrency(valorUDI)}
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
						<TrendingUp class="h-5 w-5 text-blue-500" />
						Resultado
					</h2>

					{#if resultado !== null}
						<div class="space-y-4">
							<!-- Resultado destacado -->
							<div
								class="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg border border-blue-200 dark:border-blue-800"
							>
								<div class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">
									{direccionConversion === 'udi-to-mxn' ? 'Pesos (MXN)' : 'UDIs'}
								</div>
								<div class="text-3xl font-bold text-blue-900 dark:text-blue-100 tabular-nums">
									{#if direccionConversion === 'udi-to-mxn'}
										{formatCurrency(resultado)}
									{:else}
										{formatNumber(resultado, 2)} UDI
									{/if}
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
											{#if direccionConversion === 'udi-to-mxn'}
												{formatNumber(monto, 2)} UDI
											{:else}
												{formatCurrency(monto)}
											{/if}
										</span>
									</div>

									<div
										class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800"
									>
										<span class="text-slate-600 dark:text-slate-400">Valor UDI</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(valorUDI)}
										</span>
									</div>

									<div
										class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800"
									>
										<span class="text-slate-600 dark:text-slate-400 font-medium">Resultado</span>
										<span class="font-semibold text-slate-900 dark:text-slate-100 tabular-nums">
											{#if direccionConversion === 'udi-to-mxn'}
												{formatCurrency(resultado)}
											{:else}
												{formatNumber(resultado, 2)} UDI
											{/if}
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

			<!-- Investment calculator -->
			<div class="mt-8 card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<LineChart class="h-5 w-5 text-brand-500" />
					Calcular rendimiento de inversión
				</h2>

				<div class="grid gap-6 md:grid-cols-3 mb-6">
					<div>
						<label
							for="montoInicial"
							class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
						>
							Inversión inicial
						</label>
						<div class="relative">
							<span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
							<input
								id="montoInicial"
								type="number"
								bind:value={montoInicial}
								min="0"
								step="1000"
								class="input pl-8 tabular-nums"
								placeholder="100000"
							/>
						</div>
					</div>

					<div>
						<label
							for="fechaInicial"
							class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
						>
							<Calendar class="h-4 w-4 inline mr-1" />
							Fecha inicial
						</label>
						<select id="fechaInicial" bind:value={fechaInicial} class="input">
							<option value="">Selecciona fecha</option>
							{#each fechasDisponibles.slice().reverse() as fecha}
								<option value={fecha}>{fecha}</option>
							{/each}
						</select>
					</div>

					<div>
						<label
							for="fechaFinal"
							class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2"
						>
							<Calendar class="h-4 w-4 inline mr-1" />
							Fecha final
						</label>
						<select id="fechaFinal" bind:value={fechaFinal} class="input">
							<option value="">Selecciona fecha</option>
							{#each fechasDisponibles as fecha}
								<option value={fecha}>{fecha}</option>
							{/each}
						</select>
					</div>
				</div>

				{#if rendimiento}
					<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
							<div class="text-sm text-slate-600 dark:text-slate-400 mb-1">Inversión inicial</div>
							<div class="text-lg font-bold text-slate-900 dark:text-slate-100 tabular-nums">
								{formatCurrency(montoInicial)}
							</div>
							<div class="text-xs text-slate-500 mt-1">
								{formatNumber(rendimiento.udisInicial, 2)} UDIs
							</div>
						</div>

						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
							<div class="text-sm text-slate-600 dark:text-slate-400 mb-1">Valor final</div>
							<div class="text-lg font-bold text-slate-900 dark:text-slate-100 tabular-nums">
								{formatCurrency(rendimiento.valorFinal)}
							</div>
							<div class="text-xs text-slate-500 mt-1">Mismo número de UDIs</div>
						</div>

						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
							<div class="text-sm text-slate-600 dark:text-slate-400 mb-1">Rendimiento</div>
							<div
								class="text-lg font-bold tabular-nums {rendimiento.rendimientoTotal >= 0
									? 'text-green-600 dark:text-green-400'
									: 'text-red-600 dark:text-red-400'}"
							>
								{formatCurrency(rendimiento.rendimientoTotal)}
							</div>
							<div class="text-xs text-slate-500 mt-1">Por inflación</div>
						</div>

						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
							<div class="text-sm text-slate-600 dark:text-slate-400 mb-1">% Rendimiento</div>
							<div
								class="text-lg font-bold tabular-nums {rendimiento.rendimientoPercent >= 0
									? 'text-green-600 dark:text-green-400'
									: 'text-red-600 dark:text-red-400'}"
							>
								{rendimiento.rendimientoPercent >= 0 ? '+' : ''}{formatNumber(
									rendimiento.rendimientoPercent,
									2
								)}%
							</div>
							<div class="text-xs text-slate-500 mt-1">Ajuste inflación</div>
						</div>
					</div>
				{:else}
					<div class="p-8 bg-slate-50 dark:bg-slate-800/50 rounded-lg text-center">
						<p class="text-sm text-slate-500 dark:text-slate-400">
							Selecciona monto y fechas para calcular el rendimiento
						</p>
					</div>
				{/if}
			</div>

			<!-- Info adicional -->
			<div class="mt-8 grid gap-4 sm:grid-cols-3">
				<div class="card p-5">
					<h3 class="font-semibold text-slate-900 dark:text-white mb-2">¿Qué son las UDIs?</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Unidades de cuenta indexadas a la inflación (INPC), que mantienen su poder adquisitivo
						constante.
					</p>
				</div>

				<div class="card p-5">
					<h3 class="font-semibold text-slate-900 dark:text-white mb-2">Créditos hipotecarios</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Los créditos en UDIs protegen al acreedor de la inflación, pero el saldo crece con el
						INPC.
					</p>
				</div>

				<div class="card p-5">
					<h3 class="font-semibold text-slate-900 dark:text-white mb-2">Fuente oficial</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Datos oficiales del Banco de México (Serie SP68257) publicados diariamente.
					</p>
				</div>
			</div>

			<!-- Nota legal -->
			<div
				class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700"
			>
				<p class="text-xs text-slate-500 dark:text-slate-400">
					<strong>Nota:</strong> Esta calculadora es informativa y utiliza datos históricos del
					Banco de México. Para cálculos oficiales de créditos hipotecarios u otros instrumentos,
					consulta con tu institución financiera. El valor de la UDI se actualiza diariamente.
				</p>
			</div>
		{/if}
	</div>
</section>
