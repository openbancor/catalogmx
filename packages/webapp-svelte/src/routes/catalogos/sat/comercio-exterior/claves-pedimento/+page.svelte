<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, FileText, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';

	interface ClavePedimento {
		clave: string;
		descripcion: string;
		regimen: string;
		tipo_operacion: string;
		requiere_certificado_origen?: boolean;
		notes?: string;
	}

	let data = $state<ClavePedimento[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const totalClaves = $derived(data.length);
	const exportacion = $derived(data.filter(c => c.regimen === 'exportacion').length);
	const importacion = $derived(data.filter(c => c.regimen === 'importacion').length);
	const transito = $derived(data.filter(c => c.regimen === 'transito').length);

	const columns: ColumnDef<ClavePedimento, unknown>[] = [
		{
			accessorKey: 'clave',
			header: 'Clave',
			cell: ({ getValue }) => {
				const clave = getValue() as string;
				return clave;
			},
		},
		{
			accessorKey: 'descripcion',
			header: 'Descripción',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'regimen',
			header: 'Régimen',
			cell: ({ getValue }) => {
				const regimen = getValue() as string;
				const labels: Record<string, string> = {
					exportacion: 'Exportación',
					importacion: 'Importación',
					retorno: 'Retorno',
					transito: 'Tránsito',
					traslado: 'Traslado',
					deposito_fiscal: 'Depósito Fiscal',
					immex: 'IMMEX',
					automotriz: 'Automotriz',
					zona_franca: 'Zona Franca',
					recinto_fiscalizado: 'Recinto Fiscalizado',
					elaboracion: 'Elaboración'
				};
				return labels[regimen] || regimen;
			},
		},
		{
			accessorKey: 'tipo_operacion',
			header: 'Tipo de Operación',
			cell: ({ getValue }) => {
				const tipo = getValue() as string;
				const labels: Record<string, string> = {
					definitiva: 'Definitiva',
					temporal: 'Temporal',
					retorno_exportacion: 'Retorno de Exportación',
					retorno_importacion: 'Retorno de Importación',
					interno: 'Interno',
					internacional_ingreso: 'Internacional (Ingreso)',
					internacional_salida: 'Internacional (Salida)',
					introduccion: 'Introducción',
					extraccion: 'Extracción',
					importacion: 'Importación',
					exportacion: 'Exportación',
					retorno: 'Retorno',
					deposito: 'Depósito',
					envio: 'Envío'
				};
				return labels[tipo] || tipo;
			},
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load claves pedimento data from JSON
			const response = await fetch('/data/sat/comercio_exterior/claves_pedimento.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const claves = await response.json();
			data = claves;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading claves pedimento data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Claves de Pedimento (SAT Comercio Exterior) - catalogmx</title>
	<meta name="description" content="Catálogo de claves de pedimento del SAT para operaciones aduaneras de comercio exterior." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/sat/comercio-exterior" class="hover:text-brand-500">Comercio Exterior</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Claves de Pedimento</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
				<FileText class="h-6 w-6 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogo de Claves de Pedimento
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Tipos de operaciones aduaneras y regímenes de comercio exterior
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-4 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total de Claves</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{totalClaves}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Exportación</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{exportacion}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Importación</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{importacion}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Tránsito</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{transito}
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
			searchPlaceholder="Buscar por clave, descripción o régimen..."
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
					<strong>Claves de Pedimento:</strong> Las claves de pedimento son códigos que identifican el tipo de
					operación aduanera que se está realizando. Cada clave especifica el régimen aduanero (exportación,
					importación, tránsito, etc.) y el tipo de operación (definitiva, temporal, retorno, etc.).
				</p>
				<p>
					<strong>Principales regímenes:</strong>
				</p>
				<ul class="list-disc list-inside ml-4 space-y-1">
					<li><strong>Exportación:</strong> Salida de mercancías del territorio nacional</li>
					<li><strong>Importación:</strong> Entrada de mercancías al territorio nacional</li>
					<li><strong>Tránsito:</strong> Paso de mercancías por territorio nacional</li>
					<li><strong>IMMEX:</strong> Industria Manufacturera, Maquiladora y de Servicios de Exportación</li>
					<li><strong>Depósito Fiscal:</strong> Almacenamiento de mercancías extranjeras</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Servicio de Administración Tributaria (SAT) / Ley Aduanera
				</p>
				<p>
					<strong>Uso:</strong> Las claves de pedimento son obligatorias en todos los pedimentos aduanales
					y se utilizan en el Complemento de Comercio Exterior del CFDI.
				</p>
			</div>
		</div>
	{/if}
</div>
