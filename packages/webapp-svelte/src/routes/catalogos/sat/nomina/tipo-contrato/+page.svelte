<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, FileText, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';

	interface ContractType {
		code: string;
		description: string;
	}

	let data = $state<ContractType[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const totalTypes = $derived(data.length);

	const columns: ColumnDef<ContractType, unknown>[] = [
		{
			accessorKey: 'code',
			header: 'Clave',
			cell: ({ getValue }) => {
				const code = getValue() as string;
				return code;
			},
		},
		{
			accessorKey: 'description',
			header: 'Descripción',
			cell: ({ getValue }) => getValue() as string,
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load contract types data from JSON
			const response = await fetch('/data/sat/nomina_1.2/tipo_contrato.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const types = await response.json();
			data = types;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading contract types data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Tipos de Contrato (SAT Nómina) - catalogmx</title>
	<meta name="description" content="Catálogo de tipos de contrato laboral del SAT para nómina electrónica." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/sat/nomina" class="hover:text-brand-500">Nómina</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Tipos de Contrato</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-lg">
				<FileText class="h-6 w-6 text-purple-600 dark:text-purple-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Tipos de Contrato
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Modalidades de contratación laboral según el SAT
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-2 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total de tipos</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{totalTypes.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Versión del catálogo</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				1.2
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
			searchPlaceholder="Buscar por clave o descripción..."
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
					<strong>Tipos de Contrato:</strong> Catálogo de las modalidades de contratación laboral
					establecidas por la Ley Federal del Trabajo y reconocidas por el SAT para efectos del
					Complemento de Nómina versión 1.2.
				</p>
				<p>
					<strong>Fuente:</strong> Servicio de Administración Tributaria (SAT)
				</p>
				<p>
					<strong>Uso:</strong> El tipo de contrato es un dato obligatorio en el CFDI de nómina
					que define la naturaleza de la relación laboral entre el empleador y el trabajador.
				</p>
			</div>
		</div>
	{/if}
</div>
