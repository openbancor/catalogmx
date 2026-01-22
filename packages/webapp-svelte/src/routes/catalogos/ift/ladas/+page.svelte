<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Phone, Loader2, AlertCircle, MapPin } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface CodigoLada {
		lada: string;
		ciudad: string;
		estado: string;
		tipo: string;
		region: string;
		cve_entidad: string;
		cve_municipio: string;
	}

	let data = $state<CodigoLada[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const totalCodigos = $derived(data.length);
	const metropolitanas = $derived(data.filter(c => c.tipo === 'metropolitana').length);
	const fronterizas = $derived(data.filter(c => c.tipo === 'fronteriza').length);
	const estadosCount = $derived(new Set(data.map(c => c.estado)).size);

	const columns: ColumnDef<CodigoLada, unknown>[] = [
		{
			accessorKey: 'lada',
			header: 'LADA',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'ciudad',
			header: 'Ciudad',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'estado',
			header: 'Estado',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'tipo',
			header: 'Tipo',
			cell: ({ getValue }) => {
				const tipo = getValue() as string;
				const colors: Record<string, string> = {
					metropolitana: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
					fronteriza: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
					turistica: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
					normal: 'bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-300',
				};
				return `<span class="px-2 py-0.5 rounded text-xs font-medium ${colors[tipo] || colors.normal}">${tipo}</span>`;
			},
		},
		{
			accessorKey: 'region',
			header: 'Region',
			cell: ({ getValue }) => getValue() as string,
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;
			data = await query<CodigoLada>('SELECT * FROM ift_codigos_lada ORDER BY lada');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading LADA codes:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Codigos LADA de Mexico - Claves de Larga Distancia - catalogmx</title>
	<meta name="description" content="Catalogo completo de codigos LADA (claves de larga distancia) de Mexico. Incluye 402 prefijos telefonicos con informacion de ciudad, estado y region. Encuentra el codigo LADA de cualquier ciudad mexicana." />
	<meta name="keywords" content="codigos LADA, claves LADA, prefijos telefonicos Mexico, larga distancia Mexico, LADA CDMX, LADA Guadalajara, LADA Monterrey, IFT" />
	<link rel="canonical" href="https://catalogmx.com/catalogos/ift/ladas" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/ift" class="hover:text-brand-500">IFT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Codigos LADA</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-lg">
				<Phone class="h-6 w-6 text-purple-600 dark:text-purple-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Codigos LADA de Mexico
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catalogo completo de claves de larga distancia automatica (LADA) del Plan Nacional de Numeracion
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-4 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total codigos LADA</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{totalCodigos.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Zonas metropolitanas</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{metropolitanas.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Zonas fronterizas</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{fronterizas.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Estados cubiertos</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{estadosCount.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catalogo de codigos LADA...</span>
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
			searchPlaceholder="Buscar por LADA, ciudad, estado o region..."
		/>
	{/if}

	<!-- Info section with SEO content -->
	{#if !loading && !error}
		<div class="mt-8 space-y-6">
			<!-- Main info -->
			<div class="card p-6">
				<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
					Que es un codigo LADA
				</h2>
				<div class="space-y-3 text-sm text-slate-600 dark:text-slate-300">
					<p>
						El <strong>codigo LADA</strong> (Larga Distancia Automatica) es un prefijo telefonico que identifica
						una region geografica en Mexico. Tambien conocido como <strong>clave de area</strong> o
						<strong>NIR</strong> (Numero de Identificacion de Region).
					</p>
					<p>
						A partir del 3 de agosto de 2019, todos los numeros telefonicos en Mexico se marcan con
						<strong>10 digitos</strong>: el codigo LADA (2 o 3 digitos) + el numero local (7 u 8 digitos).
					</p>
				</div>
			</div>

			<!-- Metropolitan areas -->
			<div class="card p-6">
				<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
					<MapPin class="h-5 w-5 inline mr-2 text-blue-500" />
					Principales zonas metropolitanas
				</h2>
				<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
					<div class="p-3 bg-slate-50 dark:bg-slate-800 rounded">
						<p class="font-semibold">Ciudad de Mexico (CDMX)</p>
						<p class="text-slate-500 dark:text-slate-400">LADA: 55, 56</p>
					</div>
					<div class="p-3 bg-slate-50 dark:bg-slate-800 rounded">
						<p class="font-semibold">Guadalajara, Jalisco</p>
						<p class="text-slate-500 dark:text-slate-400">LADA: 33</p>
					</div>
					<div class="p-3 bg-slate-50 dark:bg-slate-800 rounded">
						<p class="font-semibold">Monterrey, Nuevo Leon</p>
						<p class="text-slate-500 dark:text-slate-400">LADA: 81</p>
					</div>
					<div class="p-3 bg-slate-50 dark:bg-slate-800 rounded">
						<p class="font-semibold">Puebla, Puebla</p>
						<p class="text-slate-500 dark:text-slate-400">LADA: 220, 221, 222</p>
					</div>
					<div class="p-3 bg-slate-50 dark:bg-slate-800 rounded">
						<p class="font-semibold">Tijuana, Baja California</p>
						<p class="text-slate-500 dark:text-slate-400">LADA: 663, 664</p>
					</div>
					<div class="p-3 bg-slate-50 dark:bg-slate-800 rounded">
						<p class="font-semibold">Ciudad Juarez, Chihuahua</p>
						<p class="text-slate-500 dark:text-slate-400">LADA: 656, 657</p>
					</div>
					<div class="p-3 bg-slate-50 dark:bg-slate-800 rounded">
						<p class="font-semibold">Merida, Yucatan</p>
						<p class="text-slate-500 dark:text-slate-400">LADA: 990, 999</p>
					</div>
					<div class="p-3 bg-slate-50 dark:bg-slate-800 rounded">
						<p class="font-semibold">Cancun, Quintana Roo</p>
						<p class="text-slate-500 dark:text-slate-400">LADA: 998</p>
					</div>
				</div>
			</div>

			<!-- Types explanation -->
			<div class="card p-6">
				<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
					Tipos de codigos LADA
				</h2>
				<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
					<p>
						<span class="inline-block px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 mr-2">metropolitana</span>
						Ciudades con alta densidad poblacional. CDMX, Guadalajara y Monterrey tienen LADA de 2 digitos.
					</p>
					<p>
						<span class="inline-block px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 mr-2">fronteriza</span>
						Ciudades en la frontera norte con Estados Unidos (Tijuana, Juarez, Reynosa, etc.)
					</p>
					<p>
						<span class="inline-block px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300 mr-2">turistica</span>
						Destinos turisticos principales (Cancun, Puerto Vallarta, Los Cabos, etc.)
					</p>
					<p>
						<span class="inline-block px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-800 dark:bg-slate-700 dark:text-slate-300 mr-2">normal</span>
						Resto de ciudades y localidades del pais.
					</p>
				</div>
			</div>

			<!-- Source -->
			<div class="card p-6">
				<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
					Fuente de datos
				</h2>
				<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
					<p>
						<strong>Fuente:</strong> Instituto Federal de Telecomunicaciones (IFT) -
						<a href="https://www.ift.org.mx" target="_blank" rel="noopener" class="text-brand-500 hover:underline">www.ift.org.mx</a>
					</p>
					<p>
						<strong>Plan de Numeracion:</strong> Los codigos LADA son asignados y administrados por el IFT
						como parte del Plan Tecnico Fundamental de Numeracion.
					</p>
					<p>
						<strong>Actualizacion:</strong> Este catalogo incluye las expansiones metropolitanas mas recientes
						(990 Merida, 663 Tijuana, 657 Juarez, 220/221 Puebla).
					</p>
				</div>
			</div>
		</div>
	{/if}
</div>
