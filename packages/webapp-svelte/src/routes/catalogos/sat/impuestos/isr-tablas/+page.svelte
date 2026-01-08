<script lang="ts">
	import { ChevronRight, Calculator, Loader2, AlertCircle } from 'lucide-svelte';
	import { onMount } from 'svelte';

	interface Tramo {
		limite_inferior: number;
		limite_superior: number | null;
		cuota_fija: number;
		tasa_excedente: number;
	}

	interface Tabla {
		año: number;
		periodicidad: string;
		vigencia_inicio: string;
		vigencia_fin: string | null;
		notas?: string;
		tramos: Tramo[];
	}

	interface ISRData {
		metadata: {
			catalog: string;
			description: string;
			source: string;
			last_updated: string;
			notes: string;
		};
		tablas: Tabla[];
	}

	let data = $state<ISRData | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let selectedYear = $state<number | null>(null);

	const selectedTable = $derived(
		data && selectedYear ? data.tablas.find((t) => t.año === selectedYear) : null
	);

	function formatCurrency(value: number | null): string {
		if (value === null) return 'En adelante';
		return value.toLocaleString('es-MX', {
			style: 'currency',
			currency: 'MXN',
			minimumFractionDigits: 2
		});
	}

	function formatPercent(value: number): string {
		return `${value.toFixed(2)}%`;
	}

	async function loadData() {
		try {
			loading = true;
			error = null;

			const response = await fetch('/data/sat/impuestos/isr_tablas.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const json = await response.json();
			data = json;
			// Select the most recent year by default
			if (data && data.tablas.length > 0) {
				selectedYear = data.tablas[0].año;
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading ISR data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Tablas de ISR - catalogmx</title>
	<meta
		name="description"
		content="Tablas históricas del Impuesto Sobre la Renta (ISR) en México desde 2002."
	/>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/sat/impuestos" class="hover:text-brand-500">Impuestos</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Tablas ISR</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
				<Calculator class="h-6 w-6 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Tablas de ISR (Impuesto Sobre la Renta)
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Tarifas mensuales históricas desde 2002 - Art. 96 LISR
				</p>
			</div>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catálogo...</span>
		</div>
	{:else if error}
		<div
			class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
		>
			<div class="flex items-start gap-3">
				<AlertCircle class="h-5 w-5 text-red-500 mt-0.5" />
				<div>
					<p class="font-medium text-red-800 dark:text-red-200">Error al cargar datos</p>
					<p class="text-sm text-red-600 dark:text-red-300 mt-1">{error}</p>
					<button onclick={loadData} class="btn btn-secondary mt-3 text-sm"> Reintentar </button>
				</div>
			</div>
		</div>
	{:else if data}
		<!-- Year selector -->
		<div class="mb-6">
			<label for="year" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
				Seleccionar año fiscal:
			</label>
			<select
				id="year"
				bind:value={selectedYear}
				class="input max-w-xs"
			>
				{#each data.tablas as tabla}
					<option value={tabla.año}>
						{tabla.año}
						{tabla.notas ? ` - ${tabla.notas}` : ''}
					</option>
				{/each}
			</select>
		</div>

		<!-- Stats -->
		{#if selectedTable}
			<div class="grid gap-4 sm:grid-cols-3 mb-6">
				<div class="card p-4">
					<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Año fiscal</p>
					<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
						{selectedTable.año}
					</p>
				</div>
				<div class="card p-4">
					<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Tramos</p>
					<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
						{selectedTable.tramos.length}
					</p>
				</div>
				<div class="card p-4">
					<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Tasa máxima</p>
					<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
						{Math.max(...selectedTable.tramos.map((t) => t.tasa_excedente))}%
					</p>
				</div>
			</div>

			<!-- Table -->
			<div class="card overflow-hidden">
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
						<thead class="bg-slate-50 dark:bg-slate-800">
							<tr>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider"
								>
									Límite inferior
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider"
								>
									Límite superior
								</th>
								<th
									class="px-4 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider"
								>
									Cuota fija
								</th>
								<th
									class="px-4 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider"
								>
									% Excedente
								</th>
							</tr>
						</thead>
						<tbody class="bg-white dark:bg-slate-900 divide-y divide-slate-200 dark:divide-slate-700">
							{#each selectedTable.tramos as tramo, i}
								<tr class="hover:bg-slate-50 dark:hover:bg-slate-800">
									<td class="px-4 py-3 whitespace-nowrap text-sm text-slate-900 dark:text-white tabular-nums">
										{formatCurrency(tramo.limite_inferior)}
									</td>
									<td class="px-4 py-3 whitespace-nowrap text-sm text-slate-900 dark:text-white tabular-nums">
										{formatCurrency(tramo.limite_superior)}
									</td>
									<td class="px-4 py-3 whitespace-nowrap text-sm text-right text-slate-900 dark:text-white tabular-nums">
										{formatCurrency(tramo.cuota_fija)}
									</td>
									<td class="px-4 py-3 whitespace-nowrap text-sm text-right font-medium text-blue-600 dark:text-blue-400 tabular-nums">
										{formatPercent(tramo.tasa_excedente)}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>

			<!-- Notes -->
			{#if selectedTable.notas}
				<div class="mt-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
					<p class="text-sm text-blue-800 dark:text-blue-200">
						<strong>Nota:</strong>
						{selectedTable.notas}
					</p>
				</div>
			{/if}
		{/if}

		<!-- Info section -->
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de las tablas de ISR
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>Impuesto Sobre la Renta (ISR):</strong> Es un impuesto directo que grava los
					ingresos de personas físicas y morales en México.
				</p>
				<p>
					<strong>Cálculo:</strong> ISR = Cuota Fija + [(Ingresos - Límite Inferior) × Tasa
					Excedente / 100]
				</p>
				<p>
					<strong>Cambios históricos:</strong>
				</p>
				<ul class="list-disc list-inside ml-4 space-y-1">
					<li>
						<strong>2014:</strong> Incremento de tasa máxima de 30% a 35% (Reforma Hacendaria)
					</li>
					<li>
						<strong>2002-presente:</strong> Estructura de 11 tramos se mantiene, con ajustes anuales
						por inflación
					</li>
					<li>
						<strong>Actualización:</strong> Los montos se ajustan cuando la inflación acumulada supera
						el 10% (Art. 152 LISR)
					</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Ley del Impuesto Sobre la Renta - Artículo 96
				</p>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-4">
					Última actualización: {data.metadata.last_updated}
				</p>
			</div>
		</div>
	{/if}
</div>
