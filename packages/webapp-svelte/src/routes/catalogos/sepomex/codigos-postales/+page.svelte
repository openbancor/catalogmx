<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, MapPin, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface CodigoPostal {
		cp: string;
		asentamiento: string;
		tipo_asentamiento: string;
		municipio: string;
		estado: string;
		ciudad: string;
		cp_oficina: string;
		codigo_estado: string;
		codigo_municipio: string;
	}

	let data = $state<CodigoPostal[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const totalEstados = $derived(new Set(data.map(cp => cp.estado)).size);
	const totalMunicipios = $derived(new Set(data.map(cp => cp.municipio)).size);

	const columns: ColumnDef<CodigoPostal, unknown>[] = [
		{
			accessorKey: 'cp',
			header: 'CP',
			cell: ({ getValue }) => {
				const cp = getValue() as string;
				return cp;
			},
		},
		{
			accessorKey: 'asentamiento',
			header: 'Asentamiento',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'tipo_asentamiento',
			header: 'Tipo',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'municipio',
			header: 'Municipio',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'estado',
			header: 'Estado',
			cell: ({ getValue }) => getValue() as string,
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load postal codes data from SQLite
			const postalCodes = await query<CodigoPostal>(
				'SELECT cp, asentamiento, tipo_asentamiento, municipio, estado, ciudad, cp_oficina, codigo_estado, codigo_municipio FROM codigos_postales ORDER BY cp LIMIT 500'
			);
			data = postalCodes;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading postal codes data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Codigos Postales - SEPOMEX - catalogmx</title>
	<meta name="description" content="Catalogo de codigos postales de Mexico con informacion de asentamientos, municipios y estados." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sepomex" class="hover:text-brand-500">SEPOMEX</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Codigos Postales</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
				<MapPin class="h-6 w-6 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Codigos Postales de Mexico
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catalogo oficial de codigos postales del Servicio Postal Mexicano (muestra de 500 registros)
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-3 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total codigos postales</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{data.length.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Estados representados</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{totalEstados.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Municipios representados</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{totalMunicipios.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catalogo desde SQLite...</span>
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
			searchPlaceholder="Buscar por CP, asentamiento, municipio o estado..."
		/>
	{/if}

	<!-- Info section -->
	{#if !loading && !error}
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de este catalogo
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					El <strong>codigo postal</strong> es un identificador numerico de 5 digitos que permite ubicar una localidad
					especifica dentro del territorio nacional.
				</p>
				<p>
					<strong>Fuente:</strong> Servicio Postal Mexicano (SEPOMEX)
				</p>
				<p>
					<strong>Uso:</strong> Los codigos postales se utilizan para identificar ubicaciones geograficas en envios,
					direcciones fiscales, y servicios de geolocalizacion.
				</p>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-4">
					<strong>Nota:</strong> Esta es una muestra de 500 codigos postales representativos de las principales
					ciudades de Mexico. El catalogo completo contiene mas de 145,000 codigos postales.
				</p>
			</div>
		</div>
	{/if}
</div>
