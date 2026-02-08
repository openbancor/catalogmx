<script lang="ts">
	import { base } from '$app/paths';
	import ServerDataTable from '$lib/components/ServerDataTable.svelte';
	import { ChevronRight, Download, Copy, Check, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query, count } from '$lib/db';

	interface ClaveProdServ {
		c_ClaveProdServ: string;
		Descripcion: string;
		IncluirIVAtrasladado: number;
		IncluirIEPStrasladado: number;
	}

	let data = $state<ClaveProdServ[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let totalCount = $state(0);
	let sectorCount = $state(0);
	let familyCount = $state(0);

	// Pagination state
	let currentPage = $state(1);
	let pageSize = $state(25);
	let searchTerm = $state('');

	const columns: ColumnDef<ClaveProdServ, unknown>[] = [
		{
			accessorKey: 'c_ClaveProdServ',
			header: 'Clave',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'Descripcion',
			header: 'Descripcion',
		},
	];

	let copied = $state(false);

	async function copyToClipboard(text: string) {
		await navigator.clipboard.writeText(text);
		copied = true;
		setTimeout(() => copied = false, 2000);
	}

	function escapeSQL(str: string): string {
		// Escape single quotes for SQL
		return str.replace(/'/g, "''");
	}

	function removeAccents(str: string): string {
		// Normalize and remove accents
		return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
	}

	// SQL expression to normalize a column (remove accents)
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
				// Search mode - normalize to remove accents for accent-insensitive search
				const searchNormalized = removeAccents(escapeSQL(searchTerm.toLowerCase()));
				const searchPattern = `%${searchNormalized}%`;

				// SQL expressions for normalized columns
				const normClave = sqlNormalize('clave');
				const normDesc = sqlNormalize('descripcion');

				// Get count for search
				const countResult = await query<{ count: number }>(
					`SELECT COUNT(*) as count FROM clave_prod_serv
					 WHERE ${normClave} LIKE '${searchPattern}'
					    OR ${normDesc} LIKE '${searchPattern}'`
				);
				totalCount = countResult[0]?.count || 0;

				// Get data for search
				data = await query<ClaveProdServ>(
					`SELECT clave AS c_ClaveProdServ, descripcion AS Descripcion
					 FROM clave_prod_serv
					 WHERE ${normClave} LIKE '${searchPattern}'
					    OR ${normDesc} LIKE '${searchPattern}'
					 ORDER BY clave
					 LIMIT ${limitNum} OFFSET ${offsetNum}`
				);
			} else {
				// Normal mode with pagination
				data = await query<ClaveProdServ>(
					`SELECT clave AS c_ClaveProdServ, descripcion AS Descripcion
					 FROM clave_prod_serv
					 ORDER BY clave
					 LIMIT ${limitNum} OFFSET ${offsetNum}`
				);
			}

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading CFDI data:', e);
		} finally {
			loading = false;
		}
	}

	async function loadCounts() {
		try {
			totalCount = await count('clave_prod_serv');
			// Count distinct sectors (first 2 digits of code)
			const sectorResult = await query<{ cnt: number }>(
				`SELECT COUNT(DISTINCT substr(clave, 1, 2)) as cnt FROM clave_prod_serv`
			);
			sectorCount = sectorResult[0]?.cnt || 0;
			// Count distinct families (first 6 digits of code)
			const familyResult = await query<{ cnt: number }>(
				`SELECT COUNT(DISTINCT substr(clave, 1, 6)) as cnt FROM clave_prod_serv`
			);
			familyCount = familyResult[0]?.cnt || 0;
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
	<title>Productos y Servicios (c_ClaveProdServ) - catalogmx</title>
	<meta name="description" content="Catalogo de claves de productos y servicios del SAT para CFDI 4.0. Mas de 52,000 claves." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat/cfdi" class="hover:text-brand-500">CFDI</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Productos y Servicios</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Productos y Servicios
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catalogo c_ClaveProdServ del SAT para CFDI 4.0
				</p>
			</div>
			<div class="flex gap-2">
				<button class="btn btn-secondary">
					<Download class="h-4 w-4" />
					Exportar CSV
				</button>
				<button
					class="btn btn-secondary"
					onclick={() => copyToClipboard('SELECT * FROM clave_prod_serv LIMIT 100')}
				>
					{#if copied}
						<Check class="h-4 w-4 text-green-500" />
					{:else}
						<Copy class="h-4 w-4" />
					{/if}
					SQL
				</button>
			</div>
		</div>
	</div>

	<!-- Info cards -->
	<div class="grid gap-4 sm:grid-cols-3 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total productos</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if totalCount === 0}
					<span class="animate-pulse">--</span>
				{:else}
					{totalCount.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Sectores</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if totalCount === 0}
					<span class="animate-pulse">--</span>
				{:else}
					{sectorCount.toLocaleString('es-MX')}
				{/if}
			</p>
			<p class="text-xs text-slate-400 mt-1">Primeros 2 digitos</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Familias</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if totalCount === 0}
					<span class="animate-pulse">--</span>
				{:else}
					{familyCount.toLocaleString('es-MX')}
				{/if}
			</p>
			<p class="text-xs text-slate-400 mt-1">Primeros 6 dígitos</p>
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
		searchPlaceholder="Buscar por clave o descripcion..."
		onPageChange={handlePageChange}
		onPageSizeChange={handlePageSizeChange}
		onSearch={handleSearch}
	/>
</div>
