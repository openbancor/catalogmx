<script lang="ts">
	import { ChevronRight, TrendingUp, Calendar, DollarSign } from 'lucide-svelte';
	import { onMount } from 'svelte';

	interface Rate {
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
		rates: Rate[];
	}

	let data = $state<Data | null>(null);
	let loading = $state(true);
	let displayLimit = $state(30);

	const displayedRates = $derived(data?.rates.slice(0, displayLimit) ?? []);

	onMount(async () => {
		try {
			const res = await fetch('/data/banxico/tipo_cambio.json');
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
			weekday: 'short',
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		});
	}

	function loadMore() {
		displayLimit += 30;
	}
</script>

<svelte:head>
	<title>Tipo de Cambio USD/MXN - catalogmx</title>
	<meta name="description" content="Histórico del tipo de cambio FIX del Banco de México (pesos por dólar)" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Tipo de Cambio</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<DollarSign class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Tipo de Cambio FIX
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Histórico del tipo de cambio pesos por dólar (USD/MXN)
				</p>
			</div>
		</div>
	</div>

	{#if loading}
		<div class="text-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500 mx-auto"></div>
			<p class="mt-4 text-slate-500 dark:text-slate-400">Cargando datos...</p>
		</div>
	{:else if data}
		<!-- Current rate card -->
		<div class="card p-6 mb-8 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-800">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-green-600 dark:text-green-400 font-medium">Tipo de cambio actual</p>
					<p class="text-4xl font-bold text-green-700 dark:text-green-300 mt-1">
						${data.rates[0].rate.toFixed(4)} MXN
					</p>
					<p class="text-sm text-slate-500 dark:text-slate-400 mt-2">
						{formatDate(data.rates[0].date)}
					</p>
				</div>
				<div class="text-right text-sm text-slate-500 dark:text-slate-400">
					<p>Serie: {data.metadata.series}</p>
					<p>Fuente: {data.metadata.source}</p>
				</div>
			</div>
		</div>

		<!-- Historical data table -->
		<div class="card overflow-hidden">
			<div class="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
				<h2 class="font-semibold text-slate-900 dark:text-white">Histórico de tipos de cambio</h2>
				<p class="text-sm text-slate-500 dark:text-slate-400">{data.rates.length} registros</p>
			</div>
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead class="bg-slate-50 dark:bg-slate-800">
						<tr>
							<th class="text-left py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Fecha</th>
							<th class="text-right py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Tipo de Cambio (MXN)</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-200 dark:divide-slate-700">
						{#each displayedRates as rate}
							<tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50">
								<td class="py-3 px-4 text-slate-700 dark:text-slate-300">{formatDate(rate.date)}</td>
								<td class="py-3 px-4 text-right font-mono text-slate-900 dark:text-white">${rate.rate.toFixed(4)}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>

		<!-- Load more -->
		{#if displayedRates.length < data.rates.length}
			<div class="text-center mt-6">
				<button onclick={loadMore} class="btn-primary">
					Cargar más ({data.rates.length - displayedRates.length} restantes)
				</button>
			</div>
		{/if}
	{/if}
</div>
