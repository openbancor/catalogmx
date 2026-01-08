<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, FileText, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '@tanstack/svelte-table';
	import { onMount } from 'svelte';

	interface RegimenFiscal {
		valor: string;
	}

	let data = $state<RegimenFiscal[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const columns: ColumnDef<RegimenFiscal, unknown>[] = [
		{
			accessorKey: 'valor',
			header: 'Clave',
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

			const response = await fetch('/data/sat/cfdi_4.0/c_RegimenFiscal.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const json = await response.json();
			data = json.data;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading regimen fiscal data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Régimen Fiscal (SAT CFDI 4.0) - catalogmx</title>
	<meta name="description" content="Catálogo de regímenes fiscales del SAT para CFDI 4.0." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Régimen Fiscal</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg">
				<FileText class="h-6 w-6 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogo de Régimen Fiscal
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Regímenes fiscales válidos para facturas electrónicas (CFDI 4.0)
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-2 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total regímenes fiscales</p>
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
			searchPlaceholder="Buscar por clave..."
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
					<strong>Régimen Fiscal</strong> es un elemento del CFDI que indica el régimen tributario
					bajo el cual está dado de alta el contribuyente ante el SAT.
				</p>
				<p>
					<strong>Ejemplos comunes:</strong>
				</p>
				<ul class="list-disc list-inside ml-4 space-y-1">
					<li><strong>601:</strong> General de Ley Personas Morales</li>
					<li><strong>605:</strong> Sueldos y Salarios e Ingresos Asimilados a Salarios</li>
					<li><strong>612:</strong> Personas Físicas con Actividades Empresariales y Profesionales</li>
					<li><strong>626:</strong> Régimen Simplificado de Confianza</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Servicio de Administración Tributaria (SAT)
				</p>
				<p>
					<strong>Uso:</strong> Campo obligatorio en el CFDI 4.0 para identificar el régimen fiscal del emisor y receptor.
				</p>
			</div>
		</div>
	{/if}
</div>
