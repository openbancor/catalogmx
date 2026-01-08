<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Ship, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface Incoterm {
		code: string;
		name: string;
		name_es: string;
		description: string;
		transport_mode: string;
		seller_responsibility: string;
		seller_pays_freight: boolean;
		seller_pays_insurance: boolean;
		risk_transfer_point: string;
		suitable_for: string[];
		notes?: string;
		seller_unloads?: boolean;
		seller_pays_import_duties?: boolean;
		seller_clears_import?: boolean;
		insurance_coverage?: string;
	}

	let data = $state<Incoterm[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const totalIncoterms = $derived(data.length);
	const maritimeOnly = $derived(data.filter(i => i.transport_mode === 'maritime').length);
	const anyMode = $derived(data.filter(i => i.transport_mode === 'any').length);

	const columns: ColumnDef<Incoterm, unknown>[] = [
		{
			accessorKey: 'code',
			header: 'Código',
			cell: ({ getValue }) => {
				const code = getValue() as string;
				return code;
			},
		},
		{
			accessorKey: 'name_es',
			header: 'Nombre',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'name',
			header: 'Nombre en Inglés',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'description',
			header: 'Descripción',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'transport_mode',
			header: 'Modo de Transporte',
			cell: ({ getValue }) => {
				const mode = getValue() as string;
				return mode === 'any' ? 'Cualquiera' : 'Marítimo';
			},
		},
		{
			accessorKey: 'seller_responsibility',
			header: 'Responsabilidad Vendedor',
			cell: ({ getValue }) => {
				const resp = getValue() as string;
				const labels: Record<string, string> = {
					minimal: 'Mínima',
					medium: 'Media',
					high: 'Alta',
					maximum: 'Máxima'
				};
				return labels[resp] || resp;
			},
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load incoterms data from SQLite
			const incoterms = await query<Incoterm>('SELECT * FROM sat_comercio_exterior_incoterms ORDER BY code');
			data = incoterms;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading incoterms data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Incoterms (SAT Comercio Exterior) - catalogmx</title>
	<meta name="description" content="Catálogo de Incoterms (términos internacionales de comercio) del SAT para comercio exterior." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat/comercio-exterior" class="hover:text-brand-500">Comercio Exterior</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Incoterms</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
				<Ship class="h-6 w-6 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogo de Incoterms
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Términos Internacionales de Comercio (International Commercial Terms) - Incoterms 2020
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-3 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total de Incoterms</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{totalIncoterms}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Cualquier Transporte</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{anyMode}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Solo Marítimo</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{maritimeOnly}
				{/if}
			</p>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catálogo desde SQLite...</span>
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
			searchPlaceholder="Buscar por código o nombre..."
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
					<strong>Incoterms 2020:</strong> Los Incoterms (International Commercial Terms) son términos estandarizados
					publicados por la Cámara de Comercio Internacional (ICC) que definen las responsabilidades de compradores
					y vendedores en transacciones internacionales. Establecen quién paga el transporte, el seguro, y en qué
					punto se transfiere el riesgo de la mercancía.
				</p>
				<p>
					<strong>Clasificación:</strong> Los Incoterms se dividen en dos grupos:
				</p>
				<ul class="list-disc list-inside ml-4 space-y-1">
					<li><strong>Cualquier modo de transporte:</strong> EXW, FCA, CPT, CIP, DAP, DPU, DDP (7 términos)</li>
					<li><strong>Solo transporte marítimo:</strong> FAS, FOB, CFR, CIF (4 términos)</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Cámara de Comercio Internacional (ICC) - Incoterms 2020
				</p>
				<p>
					<strong>Uso en México:</strong> Los Incoterms son obligatorios en el Complemento de Comercio Exterior
					del CFDI (versión 1.1) para especificar las condiciones de entrega de las mercancías.
				</p>
			</div>
		</div>
	{/if}
</div>
