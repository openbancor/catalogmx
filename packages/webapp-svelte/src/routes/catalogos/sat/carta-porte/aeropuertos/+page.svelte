<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Plane, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';

	interface Aeropuerto {
		code: string;
		name: string;
		iata: string;
		icao: string;
		ciudad: string;
		estado: string;
	}

	let data = $state<Aeropuerto[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const columns: ColumnDef<Aeropuerto, unknown>[] = [
		{
			accessorKey: 'code',
			header: 'Código',
			cell: ({ getValue }) => {
				const code = getValue() as string;
				return code;
			},
		},
		{
			accessorKey: 'name',
			header: 'Nombre del Aeropuerto',
			cell: ({ getValue }) => {
				const name = getValue() as string;
				return name;
			},
		},
		{
			accessorKey: 'iata',
			header: 'IATA',
			cell: ({ getValue }) => {
				const iata = getValue() as string;
				return iata;
			},
		},
		{
			accessorKey: 'icao',
			header: 'ICAO',
			cell: ({ getValue }) => {
				const icao = getValue() as string;
				return icao;
			},
		},
		{
			accessorKey: 'ciudad',
			header: 'Ciudad',
			cell: ({ getValue }) => {
				const ciudad = getValue() as string;
				return ciudad;
			},
		},
		{
			accessorKey: 'estado',
			header: 'Estado',
			cell: ({ getValue }) => {
				const estado = getValue() as string;
				return estado;
			},
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			const response = await fetch('/data/sat/carta_porte_3/aeropuertos.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const json = await response.json();
			data = json;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading aeropuertos data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Aeropuertos (SAT Carta Porte 3.0) - catalogmx</title>
	<meta name="description" content="Catálogo de aeropuertos del SAT para Carta Porte 3.0." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/sat/carta-porte" class="hover:text-brand-500">Carta Porte 3.0</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Aeropuertos</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
				<Plane class="h-6 w-6 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogo de Aeropuertos
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Aeropuertos nacionales e internacionales autorizados para transporte de mercancías (Carta Porte 3.0)
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-2 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total aeropuertos</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{data.length.toLocaleString('es-MX')}
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
			searchPlaceholder="Buscar aeropuerto (código, nombre, ciudad, IATA, ICAO...)..."
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
					<strong>Aeropuertos:</strong> Este catálogo contiene los aeropuertos autorizados para el
					transporte de mercancías por vía aérea en México, conforme al Complemento Carta Porte 3.0.
				</p>
				<p>
					<strong>Códigos IATA/ICAO:</strong> Cada aeropuerto incluye sus códigos de identificación
					internacional IATA (3 letras) e ICAO (4 letras).
				</p>
				<p>
					<strong>Principales aeropuertos:</strong>
				</p>
				<ul class="list-disc list-inside ml-4 space-y-1">
					<li><strong>MEX (MMMX):</strong> Aeropuerto Internacional de la Ciudad de México</li>
					<li><strong>GDL (MMGL):</strong> Aeropuerto Internacional de Guadalajara</li>
					<li><strong>CUN (MMUN):</strong> Aeropuerto Internacional de Cancún</li>
					<li><strong>MTY (MMMY):</strong> Aeropuerto Internacional de Monterrey</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Servicio de Administración Tributaria (SAT)
				</p>
				<p>
					<strong>Uso:</strong> Campo obligatorio cuando la modalidad de transporte es aérea en el
					Complemento Carta Porte 3.0.
				</p>
			</div>
		</div>
	{/if}
</div>
