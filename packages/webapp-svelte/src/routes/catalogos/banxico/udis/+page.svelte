<script lang="ts">
	import { ChevronRight, Coins, Loader2, AlertCircle } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { query, queryOne } from '$lib/db';

	interface UDIRecord {
		fecha: string;
		valor: number;
	}

	let data = $state<UDIRecord[]>([]);
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

			// Get today's date in YYYY-MM-DD format for filtering
			const today = new Date().toISOString().split('T')[0];

			// Get total count (only dates up to today - Banxico publishes future dates)
			const countResult = await queryOne<{ cnt: number }>(
				`SELECT COUNT(*) as cnt FROM banxico_udis WHERE fecha <= '${today}'`
			);
			totalRecords = countResult?.cnt ?? 0;

			// Load UDI data from SQLite (only dates up to today)
			const results = await query<UDIRecord>(
				`SELECT fecha, valor FROM banxico_udis WHERE fecha <= '${today}' ORDER BY fecha DESC LIMIT 500`
			);
			data = results;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading UDI data:', e);
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

	async function loadMore() {
		const offset = data.length;
		const today = new Date().toISOString().split('T')[0];
		const moreData = await query<UDIRecord>(
			`SELECT fecha, valor FROM banxico_udis WHERE fecha <= '${today}' ORDER BY fecha DESC LIMIT 500 OFFSET ${offset}`
		);
		data = [...data, ...moreData];
		displayLimit += 30;
	}
</script>

<svelte:head>
	<title>Valor de la UDI - catalogmx</title>
	<meta name="description" content="Histórico del valor de las Unidades de Inversión (UDIs) del Banco de México" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">UDIs</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<Coins class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Unidades de Inversión (UDIs)
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Histórico del valor de la UDI en pesos mexicanos
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
		<!-- Current value card -->
		<div class="card p-6 mb-8 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-800">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-green-600 dark:text-green-400 font-medium">Valor actual de la UDI</p>
					<p class="text-4xl font-bold text-green-700 dark:text-green-300 mt-1">
						${latestValue.valor.toFixed(6)} MXN
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
			<h2 class="font-semibold text-slate-900 dark:text-white mb-2">¿Qué es la UDI?</h2>
			<p class="text-sm text-slate-600 dark:text-slate-300">
				La <strong>Unidad de Inversión (UDI)</strong> es una unidad de cuenta cuyo valor se actualiza
				diariamente en función de la inflación. Fue creada en 1995 para proteger el valor real de
				las inversiones y créditos hipotecarios. El Banco de México publica diariamente su valor.
			</p>
		</div>

		<!-- Calculator link -->
		<div class="card p-4 mb-6 bg-brand-50 dark:bg-brand-900/20 border-brand-200 dark:border-brand-800">
			<div class="flex items-center justify-between">
				<div>
					<p class="font-medium text-brand-800 dark:text-brand-200">Calculadora de UDIs</p>
					<p class="text-sm text-brand-600 dark:text-brand-300">Convierte entre pesos y UDIs para cualquier fecha</p>
				</div>
				<a href="{base}/calculadoras/udi" class="btn btn-primary">
					Ir a calculadora
				</a>
			</div>
		</div>

		<!-- Historical data table -->
		<div class="card overflow-hidden">
			<div class="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
				<h2 class="font-semibold text-slate-900 dark:text-white">Histórico de valores UDI</h2>
				<p class="text-sm text-slate-500 dark:text-slate-400">{totalRecords.toLocaleString('es-MX')} registros</p>
			</div>
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead class="bg-slate-50 dark:bg-slate-800">
						<tr>
							<th class="text-left py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Fecha</th>
							<th class="text-right py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Valor UDI (MXN)</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-200 dark:divide-slate-700">
						{#each displayedValues as item}
							<tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50">
								<td class="py-3 px-4 text-slate-700 dark:text-slate-300">{formatDate(item.fecha)}</td>
								<td class="py-3 px-4 text-right font-mono text-slate-900 dark:text-white">${item.valor.toFixed(6)}</td>
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
	{/if}
</div>
