<script lang="ts">
	import { base } from '$app/paths';
	import ServerDataTable from '$lib/components/ServerDataTable.svelte';
	import { ChevronRight, Ruler, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query, count } from '$lib/db';

	interface Unidad {
		id: string;
		nombre: string;
		descripcion: string;
		simbolo: string;
		fechaDeInicioDeVigencia: string;
		fechaDeFinDeVigencia: string;
	}

	let data = $state<Unidad[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let totalCount = $state(0);

	// Pagination state
	let currentPage = $state(1);
	let pageSize = $state(25);
	let searchTerm = $state('');

	const columns: ColumnDef<Unidad, unknown>[] = [
		{
			accessorKey: 'id',
			header: 'Clave',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'nombre',
			header: 'Nombre',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'simbolo',
			header: 'Simbolo',
			cell: ({ getValue }) => (getValue() as string) || '-',
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

				const normId = sqlNormalize('id');
				const normNombre = sqlNormalize('nombre');
				const normSimbolo = sqlNormalize('simbolo');

				// Get count for search
				const countResult = await query<{ count: number }>(
					`SELECT COUNT(*) as count FROM sat_cfdi_4_0_clave_unidad
					 WHERE ${normId} LIKE '${searchPattern}'
					    OR ${normNombre} LIKE '${searchPattern}'
					    OR ${normSimbolo} LIKE '${searchPattern}'`
				);
				totalCount = countResult[0]?.count || 0;

				// Get data for search
				data = await query<Unidad>(
					`SELECT id, nombre, descripcion, simbolo, fechaDeInicioDeVigencia, fechaDeFinDeVigencia
					 FROM sat_cfdi_4_0_clave_unidad
					 WHERE ${normId} LIKE '${searchPattern}'
					    OR ${normNombre} LIKE '${searchPattern}'
					    OR ${normSimbolo} LIKE '${searchPattern}'
					 ORDER BY id
					 LIMIT ${limitNum} OFFSET ${offsetNum}`
				);
			} else {
				// Normal mode with pagination
				data = await query<Unidad>(
					`SELECT id, nombre, descripcion, simbolo, fechaDeInicioDeVigencia, fechaDeFinDeVigencia
					 FROM sat_cfdi_4_0_clave_unidad
					 ORDER BY id
					 LIMIT ${limitNum} OFFSET ${offsetNum}`
				);
			}

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading unidades data:', e);
		} finally {
			loading = false;
		}
	}

	async function loadCounts() {
		try {
			totalCount = await count('sat_cfdi_4_0_clave_unidad');
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
	<title>Claves de Unidad SAT - catalogmx</title>
	<meta name="description" content="Catalogo de claves de unidad de medida del SAT para CFDI 4.0. Mas de 2,800 unidades." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Claves de Unidad</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg">
				<Ruler class="h-6 w-6 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Claves de Unidad de Medida
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catalogo c_ClaveUnidad del SAT para CFDI 4.0
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-1 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total unidades</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if totalCount === 0}
					<span class="animate-pulse">--</span>
				{:else}
					{totalCount.toLocaleString('es-MX')}
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
		searchPlaceholder="Buscar por clave, nombre o simbolo..."
		onPageChange={handlePageChange}
		onPageSizeChange={handlePageSizeChange}
		onSearch={handleSearch}
	/>
</div>
