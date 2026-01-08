<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Coins, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '@tanstack/svelte-table';
	import { onMount } from 'svelte';

	interface Moneda {
		valor: string;
	}

	let data = $state<Moneda[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const columns: ColumnDef<Moneda, unknown>[] = [
		{
			accessorKey: 'valor',
			header: 'Código ISO',
			cell: ({ getValue }) => {
				const valor = getValue() as string;
				return valor;
			},
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			const response = await fetch('/data/sat/cfdi_4.0/c_Moneda.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const json = await response.json();
			data = json.data;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading moneda data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Moneda (SAT CFDI 4.0) - catalogmx</title>
	<meta name="description" content="Catálogo de monedas del SAT para CFDI 4.0." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Moneda</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg">
				<Coins class="h-6 w-6 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogo de Moneda
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Códigos ISO 4217 de monedas válidas para facturas electrónicas (CFDI 4.0)
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-2 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total monedas</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{data.length.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Versión CFDI</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white">
				4.0
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
			searchPlaceholder="Buscar código de moneda (MXN, USD, EUR...)..."
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
					<strong>Moneda</strong> es un elemento del CFDI que indica la moneda en la cual se expresa
					el comprobante, usando códigos ISO 4217.
				</p>
				<p>
					<strong>Monedas comunes:</strong>
				</p>
				<ul class="list-disc list-inside ml-4 space-y-1">
					<li><strong>MXN:</strong> Peso Mexicano</li>
					<li><strong>USD:</strong> Dólar Estadounidense</li>
					<li><strong>EUR:</strong> Euro</li>
					<li><strong>CAD:</strong> Dólar Canadiense</li>
					<li><strong>XXX:</strong> Sin moneda (operaciones que no involucran dinero)</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Servicio de Administración Tributaria (SAT) - ISO 4217
				</p>
				<p>
					<strong>Uso:</strong> Campo obligatorio en el CFDI 4.0 para especificar la moneda de la transacción.
					Si la moneda es diferente a MXN, se debe incluir el tipo de cambio.
				</p>
			</div>
		</div>
	{/if}
</div>
