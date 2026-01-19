<script lang="ts">
	import { base } from '$app/paths';
	import ServerDataTable from '$lib/components/ServerDataTable.svelte';
	import { ChevronRight, MapPin, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query, count } from '$lib/db';

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
	let totalCount = $state(0);
	let estadosCount = $state(0);
	let municipiosCount = $state(0);

	// Pagination state
	let currentPage = $state(1);
	let pageSize = $state(25);
	let searchTerm = $state('');

	const columns: ColumnDef<CodigoPostal, unknown>[] = [
		{
			accessorKey: 'cp',
			header: 'CP',
			cell: ({ getValue }) => getValue() as string,
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

	function escapeSQL(str: string): string {
		return str.replace(/'/g, "''");
	}

	function removeAccents(str: string): string {
		return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
	}

	function sqlNormalize(column: string): string {
		return `REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LOWER(${column}),'á','a'),'é','e'),'í','i'),'ó','o'),'ú','u'),'ü','u'),'ñ','n'),'Á','a'),'É','e'),'Í','i'),'Ó','o'),'Ú','u')`;
	}

	async function loadData() {
		try {
			loading = true;
			error = null;

			const limitNum = Number(pageSize);
			const offsetNum = Number((currentPage - 1) * pageSize);

			if (searchTerm.trim()) {
				const searchNormalized = removeAccents(escapeSQL(searchTerm.toLowerCase()));
				const searchPattern = `%${searchNormalized}%`;

				const normCp = sqlNormalize('cp');
				const normAsentamiento = sqlNormalize('asentamiento');
				const normMunicipio = sqlNormalize('municipio');
				const normEstado = sqlNormalize('estado');

				// Get count for search
				const countResult = await query<{ count: number }>(
					`SELECT COUNT(*) as count FROM codigos_postales
					 WHERE ${normCp} LIKE '${searchPattern}'
					    OR ${normAsentamiento} LIKE '${searchPattern}'
					    OR ${normMunicipio} LIKE '${searchPattern}'
					    OR ${normEstado} LIKE '${searchPattern}'`
				);
				totalCount = countResult[0]?.count || 0;

				// Get data for search
				data = await query<CodigoPostal>(
					`SELECT cp, asentamiento, tipo_asentamiento, municipio, estado, ciudad, cp_oficina, codigo_estado, codigo_municipio
					 FROM codigos_postales
					 WHERE ${normCp} LIKE '${searchPattern}'
					    OR ${normAsentamiento} LIKE '${searchPattern}'
					    OR ${normMunicipio} LIKE '${searchPattern}'
					    OR ${normEstado} LIKE '${searchPattern}'
					 ORDER BY cp
					 LIMIT ${limitNum} OFFSET ${offsetNum}`
				);
			} else {
				// Normal mode with pagination
				data = await query<CodigoPostal>(
					`SELECT cp, asentamiento, tipo_asentamiento, municipio, estado, ciudad, cp_oficina, codigo_estado, codigo_municipio
					 FROM codigos_postales
					 ORDER BY cp
					 LIMIT ${limitNum} OFFSET ${offsetNum}`
				);
			}

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading postal codes data:', e);
		} finally {
			loading = false;
		}
	}

	async function loadCounts() {
		try {
			totalCount = await count('codigos_postales');
			// Count distinct estados
			const estadosResult = await query<{ cnt: number }>(
				`SELECT COUNT(DISTINCT estado) as cnt FROM codigos_postales`
			);
			estadosCount = estadosResult[0]?.cnt || 0;
			// Count distinct municipios
			const municipiosResult = await query<{ cnt: number }>(
				`SELECT COUNT(DISTINCT municipio) as cnt FROM codigos_postales`
			);
			municipiosCount = municipiosResult[0]?.cnt || 0;
		} catch (e) {
			console.error('Error loading counts:', e);
		}
	}

	function handlePageChange(page: number) {
		currentPage = page;
		loadData();
	}

	function handlePageSizeChange(size: number) {
		pageSize = size;
		currentPage = 1;
		loadData();
	}

	function handleSearch(term: string) {
		searchTerm = term;
		currentPage = 1;
		loadData();
	}

	onMount(() => {
		loadCounts();
		loadData();
	});
</script>

<svelte:head>
	<title>Codigos Postales - SEPOMEX - catalogmx</title>
	<meta name="description" content="Catalogo completo de codigos postales de Mexico con informacion de asentamientos, municipios y estados. Mas de 145,000 registros." />
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
					Catalogo oficial de codigos postales del Servicio Postal Mexicano
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-3 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total codigos postales</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if totalCount === 0}
					<span class="animate-pulse">--</span>
				{:else}
					{totalCount.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Estados</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if totalCount === 0}
					<span class="animate-pulse">--</span>
				{:else}
					{estadosCount.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Municipios</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if totalCount === 0}
					<span class="animate-pulse">--</span>
				{:else}
					{municipiosCount.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
	</div>

	<!-- Error state -->
	{#if error}
		<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-8">
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
	{/if}

	<!-- Data table with server-side pagination -->
	<ServerDataTable
		{data}
		{columns}
		{pageSize}
		totalRows={totalCount}
		{currentPage}
		{loading}
		searchPlaceholder="Buscar por CP, asentamiento, municipio o estado..."
		onPageChange={handlePageChange}
		onPageSizeChange={handlePageSizeChange}
		onSearch={handleSearch}
	/>

	<!-- Info section -->
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
		</div>
	</div>
</div>
