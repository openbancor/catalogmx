<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Phone, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';

	interface Operador {
		nombre_comercial: string;
		razon_social: string;
		tipo: string;
		red_anfitriona?: string;
		grupo_empresarial?: string;
		tecnologias: string[];
		cobertura: string;
		servicios: string[];
		market_share_aprox: number;
		fecha_inicio_operaciones: string;
		activo: boolean;
		notas?: string;
	}

	let data = $state<Operador[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const operadoresActivos = $derived(data.filter(op => op.activo).length);
	const omrActivos = $derived(data.filter(op => op.activo && op.tipo === 'OMR').length);
	const omvActivos = $derived(data.filter(op => op.activo && op.tipo === 'OMV').length);

	const columns: ColumnDef<Operador, unknown>[] = [
		{
			accessorKey: 'nombre_comercial',
			header: 'Nombre Comercial',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'tipo',
			header: 'Tipo',
			cell: ({ getValue }) => {
				const tipo = getValue() as string;
				return tipo;
			},
		},
		{
			accessorKey: 'tecnologias',
			header: 'Tecnologías',
			cell: ({ getValue }) => {
				const tecnologias = getValue() as string[];
				return tecnologias.join(', ');
			},
		},
		{
			accessorKey: 'market_share_aprox',
			header: 'Market Share',
			cell: ({ getValue }) => {
				const share = getValue() as number;
				return `${share.toFixed(1)}%`;
			},
		},
		{
			accessorKey: 'activo',
			header: 'Estado',
			cell: ({ getValue }) => {
				const activo = getValue() as boolean;
				return activo ? 'Activo' : 'Inactivo';
			},
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load operators data from JSON
			const response = await fetch('/data/ift/operadores_moviles.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const jsonData = await response.json();
			data = jsonData.operadores || [];

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading operators data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Operadores Móviles - IFT - catalogmx</title>
	<meta name="description" content="Catálogo de operadores de telefonía móvil en México (OMR y OMV)." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/ift" class="hover:text-brand-500">IFT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Operadores Móviles</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-lg">
				<Phone class="h-6 w-6 text-purple-600 dark:text-purple-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Operadores de Telefonía Móvil
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogo de operadores móviles de red (OMR) y virtuales (OMV) en México
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-4 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total operadores</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{data.length.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Operadores activos</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{operadoresActivos.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">OMR activos</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{omrActivos.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">OMV activos</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{omvActivos.toLocaleString('es-MX')}
				{/if}
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
			searchPlaceholder="Buscar por nombre, tipo o tecnología..."
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
					<strong>OMR (Operador Móvil de Red):</strong> Opera su propia infraestructura de telecomunicaciones
					y tiene licencia para usar el espectro radioeléctrico.
				</p>
				<p>
					<strong>OMV (Operador Móvil Virtual):</strong> Utiliza infraestructura de terceros (OMR o red compartida)
					para ofrecer servicios de telefonía móvil sin poseer espectro propio.
				</p>
				<p>
					<strong>Fuente:</strong> Instituto Federal de Telecomunicaciones (IFT)
				</p>
				<p>
					<strong>Uso:</strong> Este catálogo permite identificar todos los operadores móviles autorizados en México,
					su tipo de operación, tecnologías soportadas y participación de mercado.
				</p>
			</div>
		</div>
	{/if}
</div>
