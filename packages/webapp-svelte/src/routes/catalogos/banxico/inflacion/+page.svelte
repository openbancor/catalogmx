<script lang="ts">
	import { ChevronRight, TrendingUp, Loader2, AlertCircle } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { query, queryOne } from '$lib/db';

	interface InflacionRecord {
		fecha: string;
		valor: number;
	}

	let data = $state<InflacionRecord[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let displayLimit = $state(30);
	let totalRecords = $state(0);

	const displayedValues = $derived(data.slice(0, displayLimit));
	const latestValue = $derived(data[0] ?? null);

	onMount(async () => {
		try {
			loading = true;
			error = null;

			// Get total count
			const countResult = await queryOne<{ cnt: number }>('SELECT COUNT(*) as cnt FROM banxico_inflacion');
			totalRecords = countResult?.cnt ?? 0;

			// Load inflation data from SQLite
			const results = await query<InflacionRecord>(
				'SELECT fecha, valor FROM banxico_inflacion ORDER BY fecha DESC LIMIT 500'
			);
			data = results;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading inflacion data:', e);
		} finally {
			loading = false;
		}
	});

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr + 'T00:00:00');
		return date.toLocaleDateString('es-MX', {
			year: 'numeric',
			month: 'long'
		});
	}

	function loadMore() {
		displayLimit += 30;
	}
</script>

<svelte:head>
	<title>Inflación - catalogmx</title>
	<meta name="description" content="Histórico de la inflación anual en México (INPC)" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Inflación</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<TrendingUp class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Inflación Anual (INPC)
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Histórico del Índice Nacional de Precios al Consumidor
				</p>
			</div>
		</div>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando datos desde SQLite...</span>
		</div>
	{:else if error}
		<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
			<div class="flex items-start gap-3">
				<AlertCircle class="h-5 w-5 text-red-500 mt-0.5" />
				<div>
					<p class="font-medium text-red-800 dark:text-red-200">Error al cargar datos</p>
					<p class="text-sm text-red-600 dark:text-red-300 mt-1">{error}</p>
				</div>
			</div>
		</div>
	{:else if latestValue}
		<!-- Current rate card -->
		<div class="card p-6 mb-8 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-800">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-green-600 dark:text-green-400 font-medium">Inflación anual más reciente</p>
					<p class="text-4xl font-bold text-green-700 dark:text-green-300 mt-1">
						{latestValue.valor.toFixed(2)}%
					</p>
					<p class="text-sm text-slate-500 dark:text-slate-400 mt-2">
						{formatDate(latestValue.fecha)}
					</p>
				</div>
				<div class="text-right text-sm text-slate-500 dark:text-slate-400">
					<p>Fuente: Banco de México</p>
					<p>Total: {totalRecords.toLocaleString('es-MX')} registros</p>
				</div>
			</div>
		</div>

		<!-- Info card -->
		<div class="card p-6 mb-6">
			<h2 class="font-semibold text-slate-900 dark:text-white mb-2">¿Qué es el INPC?</h2>
			<p class="text-sm text-slate-600 dark:text-slate-300">
				El <strong>Índice Nacional de Precios al Consumidor (INPC)</strong> mide la variación
				de los precios de una canasta de bienes y servicios representativa del consumo de los hogares mexicanos.
				La inflación anual indica el cambio porcentual respecto al mismo mes del año anterior.
			</p>
		</div>

		<!-- Historical data table -->
		<div class="card overflow-hidden">
			<div class="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
				<h2 class="font-semibold text-slate-900 dark:text-white">Histórico de inflación</h2>
				<p class="text-sm text-slate-500 dark:text-slate-400">{totalRecords.toLocaleString('es-MX')} registros</p>
			</div>
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead class="bg-slate-50 dark:bg-slate-800">
						<tr>
							<th class="text-left py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Periodo</th>
							<th class="text-right py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Inflación Anual (%)</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-200 dark:divide-slate-700">
						{#each displayedValues as item}
							<tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50">
								<td class="py-3 px-4 text-slate-700 dark:text-slate-300">{formatDate(item.fecha)}</td>
								<td class="py-3 px-4 text-right font-mono text-slate-900 dark:text-white">
									<span class="{item.valor > 4 ? 'text-red-600 dark:text-red-400' : item.valor > 3 ? 'text-amber-600 dark:text-amber-400' : 'text-green-600 dark:text-green-400'}">
										{item.valor.toFixed(2)}%
									</span>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>

		<!-- Load more -->
		{#if displayedValues.length < totalRecords}
			<div class="text-center mt-6">
				<button onclick={loadMore} class="btn btn-primary">
					Cargar más ({(totalRecords - displayedValues.length).toLocaleString('es-MX')} restantes)
				</button>
			</div>
		{/if}
	{:else}
		<div class="text-center py-12">
			<p class="text-slate-500 dark:text-slate-400">No hay datos de inflación disponibles</p>
		</div>
	{/if}
</div>
