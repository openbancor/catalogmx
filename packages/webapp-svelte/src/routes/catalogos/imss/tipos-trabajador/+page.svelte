<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Users, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '@tanstack/svelte-table';
	import { onMount } from 'svelte';

	interface TipoTrabajador {
		clave: string;
		descripcion: string;
		caracteristicas: string;
	}

	let data = $state<TipoTrabajador[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const totalTipos = $derived(data.length);

	const columns: ColumnDef<TipoTrabajador, unknown>[] = [
		{
			accessorKey: 'clave',
			header: 'Clave',
			cell: ({ getValue }) => {
				const code = getValue() as string;
				return code;
			},
		},
		{
			accessorKey: 'descripcion',
			header: 'Descripción',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'caracteristicas',
			header: 'Características',
			cell: ({ getValue }) => getValue() as string,
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			const response = await fetch('/data/imss/imss-catalogs.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const json = await response.json();
			data = json.tipos_trabajador || [];

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading IMSS data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Tipos de Trabajador (IMSS) - catalogmx</title>
	<meta name="description" content="Catálogo de tipos de trabajador del IMSS según su régimen laboral" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/imss" class="hover:text-brand-500">IMSS</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Tipos de Trabajador</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<Users class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Tipos de Trabajador
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Clasificación de trabajadores según su régimen laboral en el IMSS
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
					{totalTipos}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Vigencia</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				2024-2026
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
					<strong>Tipos de Trabajador:</strong> El IMSS clasifica a los trabajadores según la naturaleza
					y duración de su relación laboral, lo cual determina sus derechos y las obligaciones del patrón.
				</p>
				<p>
					<strong>Clasificaciones principales:</strong>
				</p>
				<ul class="list-disc list-inside space-y-1 ml-4">
					<li><strong>Permanente (1):</strong> Trabajadores con contrato por tiempo indeterminado</li>
					<li><strong>Eventual Ciudad (2):</strong> Trabajadores urbanos con contrato temporal</li>
					<li><strong>Eventual del Campo (3):</strong> Trabajadores agrícolas con contrato temporal</li>
					<li><strong>Trabajador del hogar (4):</strong> Empleados domésticos</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Instituto Mexicano del Seguro Social (IMSS)
				</p>
				<p>
					<strong>Uso:</strong> Esta clasificación debe especificarse al dar de alta a un trabajador
					en el SUA y determina el tipo de prestaciones y el cálculo de cuotas obrero-patronales.
				</p>
			</div>
		</div>
	{/if}
</div>
