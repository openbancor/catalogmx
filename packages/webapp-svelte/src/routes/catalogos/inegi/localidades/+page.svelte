<script lang="ts">
	import { base } from '$app/paths';
	import ServerDataTable from '$lib/components/ServerDataTable.svelte';
	import { ChevronRight, Map, AlertCircle, Users, Home, Mountain } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query, count } from '$lib/db';

	interface Localidad {
		cvegeo: string;
		cve_entidad: string;
		nom_entidad: string;
		cve_municipio: string;
		nom_municipio: string;
		cve_localidad: string;
		nom_localidad: string;
		ambito: string;
		poblacion_total: number;
		viviendas_habitadas: number;
		altitud: number;
	}

	let data = $state<Localidad[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let totalCount = $state(0);
	let estadosCount = $state(0);
	let municipiosCount = $state(0);

	// Pagination state
	let currentPage = $state(1);
	let pageSize = $state(25);
	let searchTerm = $state('');
	let filterEstado = $state('');
	let filterAmbito = $state('');

	// Estados list for filter
	let estados = $state<string[]>([]);

	const columns: ColumnDef<Localidad, unknown>[] = [
		{
			accessorKey: 'cvegeo',
			header: 'Clave',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'nom_localidad',
			header: 'Localidad',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'nom_municipio',
			header: 'Municipio',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'nom_entidad',
			header: 'Estado',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'ambito',
			header: 'Ambito',
			cell: ({ getValue }) => (getValue() === 'U' ? 'Urbano' : 'Rural'),
		},
		{
			accessorKey: 'poblacion_total',
			header: 'Poblacion',
			cell: ({ getValue }) => {
				const val = getValue() as number;
				return val ? val.toLocaleString('es-MX') : '-';
			},
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

			// Build WHERE clauses
			const whereClauses: string[] = [];

			if (filterEstado) {
				whereClauses.push(`nom_entidad = '${escapeSQL(filterEstado)}'`);
			}

			if (filterAmbito) {
				whereClauses.push(`ambito = '${escapeSQL(filterAmbito)}'`);
			}

			if (searchTerm.trim()) {
				const searchNormalized = removeAccents(escapeSQL(searchTerm.toLowerCase()));
				const searchPattern = `%${searchNormalized}%`;
				const normLocalidad = sqlNormalize('nom_localidad');
				const normMunicipio = sqlNormalize('nom_municipio');
				const normEntidad = sqlNormalize('nom_entidad');

				whereClauses.push(
					`(${normLocalidad} LIKE '${searchPattern}' OR ${normMunicipio} LIKE '${searchPattern}' OR ${normEntidad} LIKE '${searchPattern}' OR cvegeo LIKE '${searchPattern}')`
				);
			}

			const whereSQL = whereClauses.length > 0 ? `WHERE ${whereClauses.join(' AND ')}` : '';

			// Get count
			const countResult = await query<{ count: number }>(
				`SELECT COUNT(*) as count FROM localidades ${whereSQL}`
			);
			totalCount = countResult[0]?.count || 0;

			// Get data
			data = await query<Localidad>(
				`SELECT cvegeo, cve_entidad, nom_entidad, cve_municipio, nom_municipio, cve_localidad, nom_localidad, ambito, poblacion_total, viviendas_habitadas, altitud
				 FROM localidades
				 ${whereSQL}
				 ORDER BY nom_entidad, nom_municipio, nom_localidad
				 LIMIT ${limitNum} OFFSET ${offsetNum}`
			);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading localidades data:', e);
		} finally {
			loading = false;
		}
	}

	async function loadCounts() {
		try {
			totalCount = await count('localidades');

			// Count distinct estados
			const estadosResult = await query<{ nom_entidad: string }>(
				`SELECT DISTINCT nom_entidad FROM localidades ORDER BY nom_entidad`
			);
			estados = estadosResult.map((e) => e.nom_entidad);
			estadosCount = estados.length;

			// Count distinct municipios
			const municipiosResult = await query<{ cnt: number }>(
				`SELECT COUNT(DISTINCT nom_municipio) as cnt FROM localidades`
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

	function handleEstadoChange(e: Event) {
		filterEstado = (e.target as HTMLSelectElement).value;
		currentPage = 1;
		loadData();
	}

	function handleAmbitoChange(e: Event) {
		filterAmbito = (e.target as HTMLSelectElement).value;
		currentPage = 1;
		loadData();
	}

	onMount(() => {
		loadCounts();
		loadData();
	});
</script>

<svelte:head>
	<title>Localidades - INEGI - catalogmx</title>
	<meta
		name="description"
		content="Catalogo de localidades urbanas y rurales de Mexico con datos de poblacion, viviendas y ubicacion geografica del INEGI."
	/>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/inegi" class="hover:text-brand-500">INEGI</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Localidades</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
				<Map class="h-6 w-6 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Localidades de Mexico
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catalogo de localidades urbanas y rurales con datos de poblacion del INEGI
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
		<div class="card p-4">
			<div class="flex items-center gap-3">
				<Map class="h-5 w-5 text-blue-500" />
				<div>
					<p class="text-sm text-slate-500 dark:text-slate-400">Localidades</p>
					<p class="text-xl font-bold text-slate-900 dark:text-white tabular-nums">
						{#if totalCount === 0}
							<span class="animate-pulse">--</span>
						{:else}
							{totalCount.toLocaleString('es-MX')}
						{/if}
					</p>
				</div>
			</div>
		</div>
		<div class="card p-4">
			<div class="flex items-center gap-3">
				<Mountain class="h-5 w-5 text-green-500" />
				<div>
					<p class="text-sm text-slate-500 dark:text-slate-400">Estados</p>
					<p class="text-xl font-bold text-slate-900 dark:text-white tabular-nums">
						{#if totalCount === 0}
							<span class="animate-pulse">--</span>
						{:else}
							{estadosCount.toLocaleString('es-MX')}
						{/if}
					</p>
				</div>
			</div>
		</div>
		<div class="card p-4">
			<div class="flex items-center gap-3">
				<Home class="h-5 w-5 text-amber-500" />
				<div>
					<p class="text-sm text-slate-500 dark:text-slate-400">Municipios</p>
					<p class="text-xl font-bold text-slate-900 dark:text-white tabular-nums">
						{#if totalCount === 0}
							<span class="animate-pulse">--</span>
						{:else}
							{municipiosCount.toLocaleString('es-MX')}
						{/if}
					</p>
				</div>
			</div>
		</div>
		<div class="card p-4">
			<div class="flex items-center gap-3">
				<Users class="h-5 w-5 text-purple-500" />
				<div>
					<p class="text-sm text-slate-500 dark:text-slate-400">Fuente</p>
					<p class="text-xl font-bold text-slate-900 dark:text-white">INEGI</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Filters -->
	<div class="flex flex-wrap gap-4 mb-6">
		<select class="input w-auto" onchange={handleEstadoChange}>
			<option value="">Todos los estados</option>
			{#each estados as estado}
				<option value={estado}>{estado}</option>
			{/each}
		</select>
		<select class="input w-auto" onchange={handleAmbitoChange}>
			<option value="">Todos los ambitos</option>
			<option value="U">Urbano</option>
			<option value="R">Rural</option>
		</select>
	</div>

	<!-- Error state -->
	{#if error}
		<div
			class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-8"
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
	{/if}

	<!-- Data table with server-side pagination -->
	<ServerDataTable
		{data}
		{columns}
		{pageSize}
		totalRows={totalCount}
		{currentPage}
		{loading}
		searchPlaceholder="Buscar por clave, localidad, municipio o estado..."
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
				Las <strong>localidades</strong> son asentamientos humanos identificados por el INEGI en el
				territorio nacional. Se clasifican en <strong>urbanas</strong> (2,500+ habitantes) y
				<strong>rurales</strong> (menos de 2,500 habitantes).
			</p>
			<p>
				<strong>Clave geoestadistica (cvegeo):</strong> Identificador unico de 9 digitos que combina
				la clave de entidad (2), municipio (3) y localidad (4).
			</p>
			<p>
				<strong>Fuente:</strong> Instituto Nacional de Estadistica y Geografia (INEGI) - Censo de Poblacion
				y Vivienda
			</p>
		</div>
	</div>
</div>
