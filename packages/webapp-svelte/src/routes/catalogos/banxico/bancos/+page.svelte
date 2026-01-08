<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Building2, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';

	interface Bank {
		code: string;
		name: string;
		full_name: string;
		rfc: string | null;
		spei: boolean;
	}

	let data = $state<Bank[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const banksWithSPEI = $derived(data.filter(bank => bank.spei).length);
	const banksWithRFC = $derived(data.filter(bank => bank.rfc !== null).length);

	const columns: ColumnDef<Bank, unknown>[] = [
		{
			accessorKey: 'code',
			header: 'Clave SPEI',
			cell: ({ getValue }) => {
				const code = getValue() as string;
				return code;
			},
		},
		{
			accessorKey: 'full_name',
			header: 'Nombre',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'name',
			header: 'Nombre Corto',
			cell: ({ getValue }) => getValue() as string,
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load banks data from JSON
			const response = await fetch('/data/banxico/banks.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const banks = await response.json();
			data = banks;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading banks data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Bancos (Banxico) - catalogmx</title>
	<meta name="description" content="Catálogo de bancos e instituciones financieras registradas en Banxico con clave SPEI." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Bancos</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<Building2 class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Bancos e Instituciones Financieras
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogo de instituciones financieras participantes en el sistema SPEI de Banxico
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-3 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total instituciones</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{data.length.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Con SPEI activo</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{banksWithSPEI.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Con RFC</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{banksWithRFC.toLocaleString('es-MX')}
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
			searchPlaceholder="Buscar por clave, nombre o RFC..."
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
					<strong>SPEI</strong> (Sistema de Pagos Electrónicos Interbancarios) es el sistema de transferencias
					electrónicas de Banxico que opera 24/7/365. Cada institución participante tiene una clave única de 3 dígitos.
				</p>
				<p>
					<strong>Fuente:</strong> Banco de México (Banxico)
				</p>
				<p>
					<strong>Uso:</strong> Las claves SPEI se utilizan para generar CLABEs (Clave Bancaria Estandarizada)
					y para identificar instituciones en transferencias electrónicas.
				</p>
			</div>
		</div>
	{/if}
</div>
