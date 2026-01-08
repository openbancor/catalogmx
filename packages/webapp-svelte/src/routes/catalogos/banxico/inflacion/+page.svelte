<script lang="ts">
	import { ChevronRight, TrendingUp, Percent } from 'lucide-svelte';
	import { onMount } from 'svelte';

	interface Value {
		date: string;
		rate: number;
	}

	interface Data {
		metadata: {
			source: string;
			series: string;
			description: string;
			unit: string;
			last_updated: string;
		};
		values: Value[];
	}

	let data = $state<Data | null>(null);
	let loading = $state(true);
	let displayLimit = $state(30);

	const displayedValues = $derived(data?.values.slice(0, displayLimit) ?? []);

	onMount(async () => {
		try {
			const res = await fetch('/data/banxico/inflacion.json');
			data = await res.json();
		} catch (error) {
			console.error('Error loading data:', error);
		} finally {
			loading = false;
		}
	});

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
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
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
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
		<div class="text-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500 mx-auto"></div>
			<p class="mt-4 text-slate-500 dark:text-slate-400">Cargando datos...</p>
		</div>
	{:else if data && data.values.length > 0}
		<!-- Current rate card -->
		<div class="card p-6 mb-8 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-800">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-green-600 dark:text-green-400 font-medium">Inflación anual más reciente</p>
					<p class="text-4xl font-bold text-green-700 dark:text-green-300 mt-1">
						{data.values[0].rate.toFixed(2)}%
					</p>
					<p class="text-sm text-slate-500 dark:text-slate-400 mt-2">
						{formatDate(data.values[0].date)}
					</p>
				</div>
				<div class="text-right text-sm text-slate-500 dark:text-slate-400">
					<p>Serie: {data.metadata.series}</p>
					<p>Fuente: {data.metadata.source}</p>
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
				<p class="text-sm text-slate-500 dark:text-slate-400">{data.values.length} registros</p>
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
								<td class="py-3 px-4 text-slate-700 dark:text-slate-300">{formatDate(item.date)}</td>
								<td class="py-3 px-4 text-right font-mono text-slate-900 dark:text-white">
									<span class="{item.rate > 4 ? 'text-red-600 dark:text-red-400' : item.rate > 3 ? 'text-amber-600 dark:text-amber-400' : 'text-green-600 dark:text-green-400'}">
										{item.rate.toFixed(2)}%
									</span>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>

		<!-- Load more -->
		{#if displayedValues.length < data.values.length}
			<div class="text-center mt-6">
				<button onclick={loadMore} class="btn-primary">
					Cargar más ({data.values.length - displayedValues.length} restantes)
				</button>
			</div>
		{/if}
	{:else}
		<div class="text-center py-12">
			<p class="text-slate-500 dark:text-slate-400">No hay datos de inflación disponibles</p>
		</div>
	{/if}
</div>
