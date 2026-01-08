<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, AlertTriangle, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface RiskClass {
		code: string;
		descripcion: string;
		prima_minima: number;
		prima_media: number;
		prima_maxima: number;
	}

	let data = $state<RiskClass[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const totalClasses = $derived(data.length);

	const columns: ColumnDef<RiskClass, unknown>[] = [
		{
			accessorKey: 'code',
			header: 'Clase',
			cell: ({ getValue }) => {
				const code = getValue() as string;
				return code;
			},
		},
		{
			accessorKey: 'descripcion',
			header: 'Descripción',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'prima_minima',
			header: 'Prima Mínima (%)',
			cell: ({ getValue }) => {
				const value = getValue() as number;
				return value.toFixed(5);
			},
		},
		{
			accessorKey: 'prima_media',
			header: 'Prima Media (%)',
			cell: ({ getValue }) => {
				const value = getValue() as number;
				return value.toFixed(5);
			},
		},
		{
			accessorKey: 'prima_maxima',
			header: 'Prima Máxima (%)',
			cell: ({ getValue }) => {
				const value = getValue() as number;
				return value.toFixed(5);
			},
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load risk class data from SQLite
			const classes = await query<RiskClass>('SELECT * FROM sat_nomina_1_2_riesgo_puesto ORDER BY code');
			data = classes;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading risk class data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Riesgo de Puesto (SAT Nómina) - catalogmx</title>
	<meta name="description" content="Catálogo de clases de riesgo laboral del IMSS para nómina electrónica." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat/nomina" class="hover:text-brand-500">Nómina</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Riesgo de Puesto</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg">
				<AlertTriangle class="h-6 w-6 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Riesgo de Puesto
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Clasificación de riesgo laboral del IMSS y primas asociadas
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-2 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total de clases</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{totalClasses.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Versión del catálogo</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				1.2
			</p>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catálogo...</span>
		</div>
	{:else if error}
		<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
			<div class="flex items-start gap-3">
				<AlertCircle class="h-5 w-5 text-red-500 mt-0.5" />
				<div>
					<p class="font-medium text-red-800 dark:text-red-200">Error al cargar datos</p>
					<p class="text-sm text-red-600 dark:text-red-300 mt-1">{error}</p>
					<button onclick={loadData} class="btn btn-secondary mt-3 text-sm">
						Reintentar
					</button>
				</div>
			</div>
		</div>
	{:else}
		<!-- Data table -->
		<DataTable
			{data}
			{columns}
			searchPlaceholder="Buscar por clase o descripción..."
		/>
	{/if}

	<!-- Info section -->
	{#if !loading && !error}
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de este catálogo
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>Riesgo de Puesto:</strong> El Instituto Mexicano del Seguro Social (IMSS) clasifica
					las empresas en 5 clases de riesgo según la actividad económica y el nivel de peligrosidad
					de las tareas. Cada clase tiene una prima de riesgo de trabajo asociada.
				</p>
				<p>
					<strong>Clases de Riesgo:</strong>
				</p>
				<ul class="list-disc list-inside space-y-1 ml-4">
					<li><strong>Clase I:</strong> Riesgo mínimo (ej: oficinas, comercio)</li>
					<li><strong>Clase II:</strong> Riesgo bajo (ej: manufactura ligera)</li>
					<li><strong>Clase III:</strong> Riesgo medio (ej: transporte, construcción)</li>
					<li><strong>Clase IV:</strong> Riesgo alto (ej: industria química, minería)</li>
					<li><strong>Clase V:</strong> Riesgo máximo (ej: explosivos, sustancias peligrosas)</li>
				</ul>
				<p>
					<strong>Prima de Riesgo:</strong> Las empresas pagan una prima que puede variar entre
					la mínima y máxima de su clase, dependiendo de su historial de accidentes laborales.
				</p>
				<p>
					<strong>Fuente:</strong> Instituto Mexicano del Seguro Social (IMSS) / SAT
				</p>
				<p>
					<strong>Uso:</strong> Este dato es importante para el cálculo de las cuotas obrero-patronales
					del IMSS y debe especificarse en el Complemento de Nómina cuando aplique.
				</p>
			</div>
		</div>
	{/if}
</div>
