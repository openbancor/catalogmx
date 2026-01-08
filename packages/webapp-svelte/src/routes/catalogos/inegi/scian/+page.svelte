<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Building2, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface Sector {
		codigo: string;
		nombre: string;
		nombre_corto: string;
		subsectores: number;
		ramas: number;
		descripcion: string;
	}

	let data = $state<Sector[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const totalSubsectores = $derived(data.reduce((sum, s) => sum + s.subsectores, 0));
	const totalRamas = $derived(data.reduce((sum, s) => sum + s.ramas, 0));

	const columns: ColumnDef<Sector, unknown>[] = [
		{
			accessorKey: 'codigo',
			header: 'Codigo',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'nombre_corto',
			header: 'Nombre',
		},
		{
			accessorKey: 'subsectores',
			header: 'Subsectores',
			cell: ({ getValue }) => (getValue() as number).toString(),
		},
		{
			accessorKey: 'ramas',
			header: 'Ramas',
			cell: ({ getValue }) => (getValue() as number).toString(),
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load SCIAN sectores data from SQLite
			data = await query<Sector>('SELECT * FROM inegi_scian_sectores ORDER BY codigo');

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading SCIAN data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>SCIAN - Sectores Economicos (INEGI) - catalogmx</title>
	<meta name="description" content="Sistema de Clasificacion Industrial de America del Norte (SCIAN). Catalogo de sectores economicos segun INEGI." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/inegi" class="hover:text-brand-500">INEGI</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">SCIAN</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-3">
			<div class="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-lg">
				<Building2 class="h-6 w-6 text-purple-600 dark:text-purple-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					SCIAN - Sectores Economicos
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Sistema de Clasificacion Industrial de America del Norte (SCIAN) 2023
				</p>
			</div>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando sectores desde SQLite...</span>
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
		<!-- Stats -->
		<div class="grid gap-4 sm:grid-cols-3 mb-8">
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Sectores</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{data.length}
				</p>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Nivel 1 (2 digitos)</p>
			</div>
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Subsectores</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{totalSubsectores}
				</p>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Nivel 2 (3 digitos)</p>
			</div>
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Ramas</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{totalRamas}
				</p>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Nivel 3 (4 digitos)</p>
			</div>
		</div>

		<!-- Data table -->
		<div class="card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
				Sectores Economicos
			</h2>
			<DataTable
				{data}
				{columns}
				searchPlaceholder="Buscar por codigo o nombre..."
				pageSize={20}
			/>
		</div>

		<!-- Info section -->
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca del SCIAN
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>SCIAN</strong> (Sistema de Clasificacion Industrial de America del Norte) es un
					clasificador de actividades economicas compatible entre Mexico, Estados Unidos y Canada.
				</p>
				<p>
					<strong>Estructura jerarquica:</strong> Sectores - Subsectores - Ramas - Subramas - Clases
				</p>
				<p>
					<strong>Fuente:</strong> INEGI - Instituto Nacional de Estadistica y Geografia
				</p>
				<p>
					<strong>Version:</strong> SCIAN 2023
				</p>
				<p>
					<strong>Uso:</strong> El SCIAN se utiliza para censos economicos, estadisticas de establecimientos,
					clasificacion de empresas, y analisis sectoriales de la economia mexicana.
				</p>
			</div>
		</div>
	{/if}
</div>
