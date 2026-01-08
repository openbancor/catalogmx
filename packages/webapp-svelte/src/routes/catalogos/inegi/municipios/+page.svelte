<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, MapPin, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface Municipio {
		cve_entidad: string;
		nom_entidad: string;
		cve_municipio: string;
		nom_municipio: string;
		cve_completa: string;
	}

	let data = $state<Municipio[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let selectedEstado = $state<string | null>(null);

	const columns: ColumnDef<Municipio, unknown>[] = [
		{
			accessorKey: 'cve_completa',
			header: 'Clave',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'nom_municipio',
			header: 'Municipio',
		},
		{
			accessorKey: 'nom_entidad',
			header: 'Estado',
		},
		{
			accessorKey: 'cve_municipio',
			header: 'Clave Mpio',
		},
	];

	const estados = $derived([...new Set(data.map(m => m.nom_entidad))].sort());

	const filteredData = $derived(
		selectedEstado
			? data.filter(m => m.nom_entidad === selectedEstado)
			: data
	);

	const estadoCounts = $derived(
		estados.map(estado => ({
			estado,
			count: data.filter(m => m.nom_entidad === estado).length
		}))
	);

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load municipios data from SQLite
			data = await query<Municipio>('SELECT * FROM inegi_municipios ORDER BY cve_completa');

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading INEGI municipios data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Municipios (INEGI) - catalogmx</title>
	<meta name="description" content="Catalogo oficial de municipios de Mexico segun INEGI. Incluye claves y nombres de todos los municipios del pais." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/inegi" class="hover:text-brand-500">INEGI</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Municipios</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-3">
			<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
				<MapPin class="h-6 w-6 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Municipios de Mexico
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catalogo oficial de municipios y demarcaciones territoriales segun INEGI
				</p>
			</div>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando municipios desde SQLite...</span>
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
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total municipios</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{data.length.toLocaleString('es-MX')}
				</p>
			</div>
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Estados</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{estados.length}
				</p>
			</div>
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-2">Filtrar por estado</p>
				<select
					class="input w-full text-sm"
					bind:value={selectedEstado}
				>
					<option value={null}>Todos los estados</option>
					{#each estadoCounts as { estado, count }}
						<option value={estado}>
							{estado} ({count})
						</option>
					{/each}
				</select>
			</div>
		</div>

		<!-- Data table -->
		<div class="card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
				{#if selectedEstado}
					Municipios de {selectedEstado}
				{:else}
					Todos los Municipios
				{/if}
			</h2>
			<DataTable
				data={filteredData}
				{columns}
				searchPlaceholder="Buscar por clave, municipio o estado..."
				pageSize={50}
			/>
		</div>

		<!-- Info section -->
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de este catalogo
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>Municipios:</strong> Mexico esta dividido en 32 entidades federativas que, a su vez,
					se subdividen en 2,469 municipios (2,465 municipios + 1 Ciudad de Mexico + 16 demarcaciones territoriales + 1 Isla Guadalupe).
				</p>
				<p>
					<strong>Fuente:</strong> Instituto Nacional de Estadistica y Geografia (INEGI)
				</p>
				<p>
					<strong>Uso:</strong> Las claves de municipio se utilizan en el CURP, codigos postales,
					y diversos sistemas oficiales de identificacion geografica.
				</p>
			</div>
		</div>
	{/if}
</div>
