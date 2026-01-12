<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Receipt, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface FormaPago {
		code: string;
		description: string;
	}

	let data = $state<FormaPago[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const columns: ColumnDef<FormaPago, unknown>[] = [
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
			header: 'Descripcion',
			cell: ({ getValue }) => getValue() as string,
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load forma pago data from SQLite
			const result = await query<FormaPago>('SELECT * FROM sat_cfdi_4_0_forma_pago ORDER BY code');
			data = result;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading forma pago data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Forma de Pago (SAT CFDI 4.0) - catalogmx</title>
	<meta name="description" content="Catalogo de formas de pago del SAT para CFDI 4.0." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Forma de Pago</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg">
				<Receipt class="h-6 w-6 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catalogo de Forma de Pago
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Formas de pago validas para facturas electronicas (CFDI 4.0)
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-2 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total formas de pago</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{data.length.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Version CFDI</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white">
				4.0
			</p>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catalogo desde SQLite...</span>
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
			searchPlaceholder="Buscar por clave o descripcion..."
		/>
	{/if}

	<!-- Info section -->
	{#if !loading && !error}
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de este catalogo
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>Forma de Pago</strong> es un elemento del CFDI que especifica el medio por el cual
					se realiza o realizara el pago de la operacion (efectivo, transferencia, tarjeta, etc.).
				</p>
				<p>
					<strong>Fuente:</strong> Servicio de Administracion Tributaria (SAT)
				</p>
				<p>
					<strong>Uso:</strong> Campo obligatorio en el CFDI 4.0 cuando el Metodo de Pago es "PUE" (Pago en una sola exhibicion).
				</p>
			</div>
		</div>
	{/if}
</div>
