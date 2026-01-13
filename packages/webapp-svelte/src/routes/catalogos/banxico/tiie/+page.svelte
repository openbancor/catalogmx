<script lang="ts">
	import { ChevronRight, Percent, Loader2, AlertCircle } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { query, queryOne } from '$lib/db';

	interface TIIERecord {
		fecha: string;
		valor: number;
		plazo: number;
	}

	interface CETESRecord {
		fecha: string;
		valor: number;
		plazo: number;
	}

	let tiieData = $state<TIIERecord[]>([]);
	let cetesData = $state<CETESRecord[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let selectedSeries = $state<'tiie' | 'cetes'>('tiie');
	let displayLimit = $state(30);

	const currentData = $derived(selectedSeries === 'tiie' ? tiieData : cetesData);
	const displayedRates = $derived(currentData.slice(0, displayLimit));
	const latestTiie = $derived(tiieData[0] ?? null);
	const latestCetes = $derived(cetesData[0] ?? null);

	onMount(async () => {
		try {
			loading = true;
			error = null;

			// Load TIIE and CETES data (28-day rates)
			const [tiie, cetes] = await Promise.all([
				query<TIIERecord>('SELECT fecha, tasa as valor, plazo FROM banxico_tiie WHERE plazo = 28 ORDER BY fecha DESC LIMIT 500'),
				query<CETESRecord>('SELECT fecha, tasa as valor, plazo FROM banxico_cetes WHERE plazo = 28 ORDER BY fecha DESC LIMIT 500')
			]);

			tiieData = tiie;
			cetesData = cetes;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading tasas data:', e);
		} finally {
			loading = false;
		}
	});

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr + 'T00:00:00');
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
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
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
	{:else}
		<!-- Current rates cards -->
		<div class="grid md:grid-cols-2 gap-4 mb-8">
			<button
				onclick={() => { selectedSeries = 'tiie'; displayLimit = 30; }}
				class="card p-6 text-left transition-all {selectedSeries === 'tiie' ? 'ring-2 ring-green-500 bg-green-50 dark:bg-green-900/20' : 'hover:border-slate-300 dark:hover:border-slate-600'}"
			>
				<p class="text-sm text-slate-500 dark:text-slate-400 font-medium">TIIE 28 días</p>
				{#if latestTiie}
					<p class="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">
						{latestTiie.valor.toFixed(4)}%
					</p>
					<p class="text-xs text-slate-400 dark:text-slate-500 mt-2">
						{formatDate(latestTiie.fecha)}
					</p>
				{:else}
					<p class="text-xl text-slate-400 mt-1">Sin datos</p>
				{/if}
			</button>

			<button
				onclick={() => { selectedSeries = 'cetes'; displayLimit = 30; }}
				class="card p-6 text-left transition-all {selectedSeries === 'cetes' ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20' : 'hover:border-slate-300 dark:hover:border-slate-600'}"
			>
				<p class="text-sm text-slate-500 dark:text-slate-400 font-medium">CETES 28 días</p>
				{#if latestCetes}
					<p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1">
						{latestCetes.valor.toFixed(2)}%
					</p>
					<p class="text-xs text-slate-400 dark:text-slate-500 mt-2">
						{formatDate(latestCetes.fecha)}
					</p>
				{:else}
					<p class="text-xl text-slate-400 mt-1">Sin datos</p>
				{/if}
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
		{#if currentData.length > 0}
			<div class="card overflow-hidden">
				<div class="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
					<h2 class="font-semibold text-slate-900 dark:text-white">
						Histórico {selectedSeries === 'tiie' ? 'TIIE' : 'CETES'} 28 días
					</h2>
					<p class="text-sm text-slate-500 dark:text-slate-400">
						{currentData.length.toLocaleString('es-MX')} registros
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
									<td class="py-3 px-4 text-slate-700 dark:text-slate-300">{formatDate(rate.fecha)}</td>
									<td class="py-3 px-4 text-right font-mono text-slate-900 dark:text-white">{rate.valor.toFixed(4)}%</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>

			<!-- Load more -->
			{#if displayedRates.length < currentData.length}
				<div class="text-center mt-6">
					<button onclick={loadMore} class="btn btn-primary">
						Cargar más ({(currentData.length - displayedRates.length).toLocaleString('es-MX')} restantes)
					</button>
				</div>
			{/if}
		{/if}
	{/if}
</div>
