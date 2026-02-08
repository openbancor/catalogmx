<script lang="ts">
	import { ChevronRight, Percent, Loader2, AlertCircle } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface Tasa {
		tipo: string;
		tasa: number;
		vigencia_inicio: string;
		vigencia_fin: string | null;
		descripcion: string;
		aplica_en: string;
		estados_frontera?: string[];
		categorias?: string[];
	}

	interface Exencion {
		concepto: string;
		descripcion: string;
		articulo: string;
	}

	interface ProductoTasaCero {
		categoria: string;
		descripcion: string;
	}

	interface IVAData {
		metadata: {
			catalog: string;
			description: string;
			source: string;
			last_updated: string;
			notes: string;
		};
		tasas: Tasa[];
		exenciones: Exencion[];
		tasa_cero_productos: ProductoTasaCero[];
	}

	let data = $state<IVAData | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const currentTasas = $derived(
		data ? data.tasas.filter((t) => t.vigencia_fin === null) : []
	);
	const historicalTasas = $derived(
		data ? data.tasas.filter((t) => t.vigencia_fin !== null) : []
	);

	function formatPercent(value: number): string {
		return `${value}%`;
	}

	function formatDate(date: string): string {
		return new Date(date).toLocaleDateString('es-MX', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load canonical IVA catalog JSON from SQLite
			const result = await query<{ payload: string }>(
				'SELECT payload FROM catalog_json WHERE path = ? LIMIT 1',
				['sat/impuestos/iva_tasas.json']
			);
			if (result.length === 0) {
				throw new Error('No se encontro sat/impuestos/iva_tasas.json en catalog_json');
			}
			const parsed = JSON.parse(result[0].payload) as IVAData;
			data = {
				...parsed,
				tasas: [...parsed.tasas].sort((a, b) => b.vigencia_inicio.localeCompare(a.vigencia_inicio))
			};
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading IVA data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Tasas de IVA - catalogmx</title>
	<meta
		name="description"
		content="Tasas históricas del Impuesto al Valor Agregado (IVA) en México."
	/>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat/impuestos" class="hover:text-brand-500">Impuestos</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Tasas IVA</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<Percent class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Tasas de IVA (Impuesto al Valor Agregado)
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Tasas históricas y vigentes del IVA en México
				</p>
			</div>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catálogo desde SQLite...</span>
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
		<!-- Current Rates -->
		<div class="mb-8">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
				Tasas vigentes
			</h2>
			<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{#each currentTasas as tasa}
					<div class="card p-4">
						<div class="flex justify-between items-start mb-2">
							<span class="text-sm font-medium text-slate-500 dark:text-slate-400 uppercase">
								{tasa.tipo}
							</span>
							<span class="text-2xl font-bold text-green-600 dark:text-green-400 tabular-nums">
								{formatPercent(tasa.tasa)}
							</span>
						</div>
						<p class="text-sm text-slate-600 dark:text-slate-300 mb-2">
							{tasa.descripcion}
						</p>
						<p class="text-xs text-slate-500 dark:text-slate-400">
							Vigente desde {formatDate(tasa.vigencia_inicio)}
						</p>
						{#if tasa.estados_frontera}
							<div class="mt-2">
								<p class="text-xs text-slate-500 dark:text-slate-400">
									Estados: {tasa.estados_frontera.join(', ')}
								</p>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		</div>

		<!-- Historical Rates Table -->
		<div class="mb-8">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
				Tasas históricas
			</h2>
			<div class="card overflow-hidden">
				<div class="overflow-x-auto">
					<table class="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
						<thead class="bg-slate-50 dark:bg-slate-800">
							<tr>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider"
								>
									Tipo
								</th>
								<th
									class="px-4 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider"
								>
									Tasa
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider"
								>
									Vigencia
								</th>
								<th
									class="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider"
								>
									Descripción
								</th>
							</tr>
						</thead>
						<tbody class="bg-white dark:bg-slate-900 divide-y divide-slate-200 dark:divide-slate-700">
							{#each historicalTasas as tasa}
								<tr class="hover:bg-slate-50 dark:hover:bg-slate-800">
									<td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-slate-900 dark:text-white">
										{tasa.tipo}
									</td>
									<td class="px-4 py-3 whitespace-nowrap text-sm text-right font-semibold text-slate-900 dark:text-white tabular-nums">
										{formatPercent(tasa.tasa)}
									</td>
									<td class="px-4 py-3 whitespace-nowrap text-sm text-slate-600 dark:text-slate-400">
										{formatDate(tasa.vigencia_inicio)} - {tasa.vigencia_fin ? formatDate(tasa.vigencia_fin) : 'Actual'}
									</td>
									<td class="px-4 py-3 text-sm text-slate-600 dark:text-slate-300">
										{tasa.descripcion}
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		</div>

		<!-- Exenciones -->
		<div class="mb-8">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
				Exenciones de IVA
			</h2>
			<div class="grid gap-4 sm:grid-cols-2">
				{#each data.exenciones as exencion}
					<div class="card p-4">
						<h3 class="font-medium text-slate-900 dark:text-white mb-1">
							{exencion.concepto.replace(/_/g, ' ').toUpperCase()}
						</h3>
						<p class="text-sm text-slate-600 dark:text-slate-300 mb-2">
							{exencion.descripcion}
						</p>
						<p class="text-xs text-slate-500 dark:text-slate-400">
							{exencion.articulo}
						</p>
					</div>
				{/each}
			</div>
		</div>

		<!-- Tasa Cero Productos -->
		<div class="mb-8">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
				Productos con tasa 0%
			</h2>
			<div class="card p-6">
				<div class="grid gap-4 sm:grid-cols-2">
					{#each ['alimentos', 'agropecuarios', 'medicinas', 'libros'] as categoria}
						<div>
							<h3 class="font-medium text-slate-900 dark:text-white mb-2 uppercase text-sm">
								{categoria}
							</h3>
							<ul class="space-y-1 text-sm text-slate-600 dark:text-slate-300">
								{#each data.tasa_cero_productos.filter(p => p.categoria === categoria) as producto}
									<li class="flex items-start gap-2">
										<span class="text-green-500 mt-1">•</span>
										{producto.descripcion}
									</li>
								{/each}
							</ul>
						</div>
					{/each}
				</div>
			</div>
		</div>

		<!-- Info section -->
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca del IVA
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>Impuesto al Valor Agregado (IVA):</strong> Es un impuesto indirecto que grava
					la enajenación de bienes, la prestación de servicios independientes, el otorgamiento del
					uso o goce temporal de bienes y la importación de bienes y servicios.
				</p>
				<p>
					<strong>Cambios históricos:</strong>
				</p>
				<ul class="list-disc list-inside ml-4 space-y-1">
					<li>
						<strong>2010:</strong> Incremento de tasa general de 15% a 16%
					</li>
					<li>
						<strong>2021:</strong> Reducción de tasa fronteriza de 10% a 8%
					</li>
					<li>
						<strong>1995:</strong> Incremento de tasa general de 10% a 15%
					</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Ley del Impuesto al Valor Agregado
				</p>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-4">
					Última actualización: {data.metadata.last_updated}
				</p>
			</div>
		</div>
	{/if}
</div>
