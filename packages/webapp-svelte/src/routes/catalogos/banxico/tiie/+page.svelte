<script lang="ts">
	import { ChevronRight, TrendingUp, Percent } from 'lucide-svelte';
	import { onMount } from 'svelte';

	interface Rate {
		date: string;
		rate: number;
	}

	interface Series {
		series: string;
		description: string;
		rates: Rate[];
	}

	interface Data {
		metadata: {
			source: string;
			description: string;
			unit: string;
			last_updated: string;
		};
		cetes_28: Series;
		tiie_28: Series;
	}

	let data = $state<Data | null>(null);
	let loading = $state(true);
	let selectedSeries = $state<'tiie' | 'cetes'>('tiie');
	let displayLimit = $state(30);

	const currentData = $derived(
		selectedSeries === 'tiie' ? data?.tiie_28 : data?.cetes_28
	);
	const displayedRates = $derived(currentData?.rates.slice(0, displayLimit) ?? []);

	onMount(async () => {
		try {
			const res = await fetch('/data/banxico/tasas.json');
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
	<title>TIIE y CETES - catalogmx</title>
	<meta name="description" content="Histórico de tasas de interés TIIE y CETES del Banco de México" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">TIIE / CETES</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<Percent class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Tasas de Interés de Referencia
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					TIIE y CETES - Tasas de interés del Banco de México
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
		<!-- Current rates cards -->
		<div class="grid md:grid-cols-2 gap-4 mb-8">
			<button
				onclick={() => { selectedSeries = 'tiie'; displayLimit = 30; }}
				class="card p-6 text-left transition-all {selectedSeries === 'tiie' ? 'ring-2 ring-green-500 bg-green-50 dark:bg-green-900/20' : 'hover:border-slate-300 dark:hover:border-slate-600'}"
			>
				<p class="text-sm text-slate-500 dark:text-slate-400 font-medium">TIIE 28 días</p>
				<p class="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">
					{data.tiie_28.rates[0].rate.toFixed(2)}%
				</p>
				<p class="text-xs text-slate-400 dark:text-slate-500 mt-2">
					{formatDate(data.tiie_28.rates[0].date)}
				</p>
			</button>

			<button
				onclick={() => { selectedSeries = 'cetes'; displayLimit = 30; }}
				class="card p-6 text-left transition-all {selectedSeries === 'cetes' ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'hover:border-slate-300 dark:hover:border-slate-600'}"
			>
				<p class="text-sm text-slate-500 dark:text-slate-400 font-medium">CETES 28 días</p>
				<p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1">
					{data.cetes_28.rates[0].rate.toFixed(2)}%
				</p>
				<p class="text-xs text-slate-400 dark:text-slate-500 mt-2">
					{formatDate(data.cetes_28.rates[0].date)}
				</p>
			</button>
		</div>

		<!-- Info cards -->
		<div class="grid md:grid-cols-2 gap-4 mb-6">
			<div class="card p-4">
				<h3 class="font-semibold text-slate-900 dark:text-white mb-2">¿Qué es la TIIE?</h3>
				<p class="text-sm text-slate-600 dark:text-slate-300">
					La <strong>Tasa de Interés Interbancaria de Equilibrio</strong> es la tasa a la que los bancos se prestan dinero entre sí. Se usa como referencia para créditos hipotecarios y otros productos financieros.
				</p>
			</div>
			<div class="card p-4">
				<h3 class="font-semibold text-slate-900 dark:text-white mb-2">¿Qué son los CETES?</h3>
				<p class="text-sm text-slate-600 dark:text-slate-300">
					Los <strong>Certificados de la Tesorería de la Federación</strong> son instrumentos de deuda gubernamental a corto plazo. La tasa CETES se considera una tasa libre de riesgo.
				</p>
			</div>
		</div>

		<!-- Historical data table -->
		{#if currentData}
			<div class="card overflow-hidden">
				<div class="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
					<h2 class="font-semibold text-slate-900 dark:text-white">
						Histórico {currentData.description}
					</h2>
					<p class="text-sm text-slate-500 dark:text-slate-400">
						Serie: {currentData.series} • {currentData.rates.length} registros
					</p>
				</div>
				<div class="overflow-x-auto">
					<table class="w-full text-sm">
						<thead class="bg-slate-50 dark:bg-slate-800">
							<tr>
								<th class="text-left py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Fecha</th>
								<th class="text-right py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Tasa (%)</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-slate-200 dark:divide-slate-700">
							{#each displayedRates as rate}
								<tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50">
									<td class="py-3 px-4 text-slate-700 dark:text-slate-300">{formatDate(rate.date)}</td>
									<td class="py-3 px-4 text-right font-mono text-slate-900 dark:text-white">{rate.rate.toFixed(2)}%</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>

			<!-- Load more -->
			{#if displayedRates.length < currentData.rates.length}
				<div class="text-center mt-6">
					<button onclick={loadMore} class="btn-primary">
						Cargar más ({currentData.rates.length - displayedRates.length} restantes)
					</button>
				</div>
			{/if}
		{/if}
	{/if}
</div>
