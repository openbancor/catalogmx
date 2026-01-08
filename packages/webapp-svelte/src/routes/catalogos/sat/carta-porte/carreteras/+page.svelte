<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Map, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface Carretera {
		code: string;
		nombre: string;
		origen: string;
		destino: string;
		tipo: string;
	}

	let data = $state<Carretera[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const columns: ColumnDef<Carretera, unknown>[] = [
		{
			accessorKey: 'code',
			header: 'Código',
			cell: ({ getValue }) => {
				const code = getValue() as string;
				return code;
			},
		},
		{
			accessorKey: 'nombre',
			header: 'Nombre de la Carretera',
			cell: ({ getValue }) => {
				const nombre = getValue() as string;
				return nombre;
			},
		},
		{
			accessorKey: 'origen',
			header: 'Origen',
			cell: ({ getValue }) => {
				const origen = getValue() as string;
				return origen;
			},
		},
		{
			accessorKey: 'destino',
			header: 'Destino',
			cell: ({ getValue }) => {
				const destino = getValue() as string;
				return destino;
			},
		},
		{
			accessorKey: 'tipo',
			header: 'Tipo',
			cell: ({ getValue }) => {
				const tipo = getValue() as string;
				return `<span class="px-2 py-1 rounded text-xs font-medium ${
					tipo === 'Cuota'
						? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
						: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
				}">${tipo}</span>`;
			},
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load carreteras data from SQLite
			const carreteras = await query<Carretera>('SELECT * FROM sat_carta_porte_3_carreteras ORDER BY code');
			data = carreteras;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading carreteras data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Carreteras (SAT Carta Porte 3.0) - catalogmx</title>
	<meta name="description" content="Catálogo de carreteras del SAT para Carta Porte 3.0." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat/carta-porte" class="hover:text-brand-500">Carta Porte 3.0</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Carreteras</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-orange-100 dark:bg-orange-900/30 p-3 rounded-lg">
				<Map class="h-6 w-6 text-orange-600 dark:text-orange-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogo de Carreteras
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Principales carreteras federales de cuota y libre para transporte terrestre (Carta Porte 3.0)
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-3 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total carreteras</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{data.length.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Carreteras de cuota</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{data.filter(c => c.tipo === 'Cuota').length.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Versión</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white">
				Carta Porte 3.0
			</p>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catálogo desde SQLite...</span>
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
			searchPlaceholder="Buscar carretera (código, nombre, origen, destino...)..."
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
					<strong>Carreteras:</strong> Este catálogo contiene las principales carreteras federales
					autorizadas para el transporte de mercancías por vía terrestre, conforme al Complemento
					Carta Porte 3.0.
				</p>
				<p>
					<strong>Tipos de carretera:</strong>
				</p>
				<ul class="list-disc list-inside ml-4 space-y-1">
					<li><strong>Cuota:</strong> Autopistas de cuota administradas por CAPUFE u organismos concesionados</li>
					<li><strong>Libre:</strong> Carreteras federales sin cobro de peaje</li>
				</ul>
				<p>
					<strong>Principales corredores:</strong> México-Querétaro, México-Puebla, Monterrey-Reynosa,
					Guadalajara-Tepic, Tijuana-Ensenada, entre otros.
				</p>
				<p>
					<strong>Fuente:</strong> Servicio de Administración Tributaria (SAT)
				</p>
				<p>
					<strong>Uso:</strong> Campo requerido cuando la modalidad de transporte es autotransporte
					en el Complemento Carta Porte 3.0, para identificar las vías por las que circula la mercancía.
				</p>
			</div>
		</div>
	{/if}
</div>
