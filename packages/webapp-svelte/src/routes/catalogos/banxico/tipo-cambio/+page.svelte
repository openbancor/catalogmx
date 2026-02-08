<script lang="ts">
	import { ChevronRight, DollarSign, Loader2, AlertCircle } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { query, queryOne } from '$lib/db';
	const SITE_URL = 'https://catalogmx.openbancor.com';
	const canonicalUrl = `${SITE_URL}/catalogos/banxico/tipo-cambio`;
	const tipoCambioCatalogJsonLd = {
		'@context': 'https://schema.org',
		'@type': 'WebPage',
		name: 'Dolar FIX Banxico historico',
		url: canonicalUrl,
		description:
			'Historico del tipo de cambio FIX de Banxico (USD/MXN) con registros por fecha.',
		mainEntity: {
			'@type': 'Dataset',
			name: 'Historico tipo de cambio FIX Banxico',
			description: 'Serie de tipo de cambio FIX diario en pesos por dolar.'
		}
	};

	interface TipoCambio {
		fecha: string;
		tipo_cambio: number;
		fuente: string;
	}

	let data = $state<TipoCambio[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let displayLimit = $state(30);
	let totalRecords = $state(0);

	const displayedRates = $derived(data.slice(0, displayLimit));
	const latestRate = $derived(data[0] ?? null);

	onMount(async () => {
		try {
			loading = true;
			error = null;

			// Get total count first
			const countResult = await queryOne<{ cnt: number }>('SELECT COUNT(*) as cnt FROM banxico_tipo_cambio');
			totalRecords = countResult?.cnt ?? 0;

			// Load data from SQLite ordered by date descending
			const results = await query<TipoCambio>(
				'SELECT fecha, tipo_cambio, fuente FROM banxico_tipo_cambio ORDER BY fecha DESC LIMIT 500'
			);
			data = results;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading tipo de cambio data:', e);
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
		const moreData = await query<TipoCambio>(
			'SELECT fecha, tipo_cambio, fuente FROM banxico_tipo_cambio ORDER BY fecha DESC LIMIT 500 OFFSET ?',
			[offset]
		);
		data = [...data, ...moreData];
		displayLimit += 30;
	}
</script>

<svelte:head>
	<title>Dolar FIX Banxico (USD/MXN) historico - catalogmx</title>
	<meta name="description" content="Historico del tipo de cambio FIX de Banxico (USD/MXN). Consulta fecha, precio del dolar y fuente oficial." />
	<meta name="keywords" content="dolar FIX Banxico, tipo de cambio Banxico, USD MXN historico, precio del dolar en Mexico" />
	<meta name="robots" content="index, follow, max-image-preview:large" />
	<link rel="canonical" href={canonicalUrl} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="Dolar FIX Banxico (USD/MXN) historico - catalogmx" />
	<meta property="og:description" content="Serie historica del dolar FIX de Banxico por fecha." />
	<meta property="og:url" content={canonicalUrl} />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Dolar FIX Banxico - catalogmx" />
	<meta name="twitter:description" content="Consulta el tipo de cambio FIX USD/MXN de Banxico." />
	{@html `<script type="application/ld+json">${JSON.stringify(tipoCambioCatalogJsonLd)}</script>`}
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
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
					Dolar FIX Banxico (USD/MXN)
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Historico del tipo de cambio pesos por dolar
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
	{:else if latestRate}
		<!-- Current rate card -->
		<div class="card p-6 mb-8 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-200 dark:border-green-800">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-sm text-green-600 dark:text-green-400 font-medium">Tipo de cambio actual</p>
					<p class="text-4xl font-bold text-green-700 dark:text-green-300 mt-1">
						${latestRate.tipo_cambio.toFixed(4)} MXN
					</p>
					<p class="text-sm text-slate-500 dark:text-slate-400 mt-2">
						{formatDate(latestRate.fecha)}
					</p>
				</div>
				<div class="text-right text-sm text-slate-500 dark:text-slate-400">
					<p>Fuente: {latestRate.fuente}</p>
					<p>Total: {totalRecords.toLocaleString('es-MX')} registros</p>
				</div>
			</div>
		</div>

		<!-- Historical data table -->
		<div class="card overflow-hidden">
			<div class="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
				<h2 class="font-semibold text-slate-900 dark:text-white">Histórico de tipos de cambio</h2>
				<p class="text-sm text-slate-500 dark:text-slate-400">{totalRecords.toLocaleString('es-MX')} registros</p>
			</div>
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead class="bg-slate-50 dark:bg-slate-800">
						<tr>
							<th class="text-left py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Fecha</th>
							<th class="text-right py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Tipo de Cambio (MXN)</th>
							<th class="text-right py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Fuente</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-200 dark:divide-slate-700">
						{#each displayedRates as rate}
							<tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50">
								<td class="py-3 px-4 text-slate-700 dark:text-slate-300">{formatDate(rate.fecha)}</td>
								<td class="py-3 px-4 text-right font-mono text-slate-900 dark:text-white">${rate.tipo_cambio.toFixed(4)}</td>
								<td class="py-3 px-4 text-right text-slate-500 dark:text-slate-400">{rate.fuente}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>

		<!-- Load more -->
		{#if displayedRates.length < totalRecords}
			<div class="text-center mt-6">
				<button onclick={loadMore} class="btn btn-primary">
					Cargar más ({(totalRecords - displayedRates.length).toLocaleString('es-MX')} restantes)
				</button>
			</div>
		{/if}
	{/if}

	<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
		<p class="text-xs text-slate-500 dark:text-slate-400">
			<strong>Herramientas relacionadas:</strong>
			<a href="{base}/calculadoras/tipo-cambio" class="text-brand-600 dark:text-brand-400 hover:underline">
				calculadora dolar FIX
			</a>,
			<a href="{base}/calculadoras/tasas-interes" class="text-brand-600 dark:text-brand-400 hover:underline">
				calculadora CETES/TIIE
			</a>
			y
			<a href="{base}/catalogos/banxico/udis" class="text-brand-600 dark:text-brand-400 hover:underline">
				catalogo de UDI
			</a>.
		</p>
	</div>
</div>
