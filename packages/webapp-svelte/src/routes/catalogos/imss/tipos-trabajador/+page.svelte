<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Users, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

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
			header: 'Descripcion',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'caracteristicas',
			header: 'Caracteristicas',
			cell: ({ getValue }) => getValue() as string,
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load tipos de trabajador from canonical IMSS JSON in SQLite
			const result = await query<{ payload: string }>(
				'SELECT payload FROM catalog_json WHERE path = ? LIMIT 1',
				['imss-catalogs.json']
			);
			if (result.length === 0) {
				throw new Error('No se encontro imss-catalogs.json en catalog_json');
			}
			const catalog = JSON.parse(result[0].payload) as {
				tipos_trabajador?: TipoTrabajador[];
			};
			data = Array.isArray(catalog.tipos_trabajador) ? catalog.tipos_trabajador : [];

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
	<meta name="description" content="Catalogo de tipos de trabajador del IMSS segun su regimen laboral" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/imss" class="hover:text-brand-500">IMSS</a>
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
					Clasificacion de trabajadores segun su regimen laboral en el IMSS
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
					<strong>Tipos de Trabajador:</strong> El IMSS clasifica a los trabajadores segun la naturaleza
					y duracion de su relacion laboral, lo cual determina sus derechos y las obligaciones del patron.
				</p>
				<p>
					<strong>Clasificaciones principales:</strong>
				</p>
				<ul class="list-disc list-inside space-y-1 ml-4">
					<li><strong>Permanente (1):</strong> Trabajadores con contrato por tiempo indeterminado</li>
					<li><strong>Eventual Ciudad (2):</strong> Trabajadores urbanos con contrato temporal</li>
					<li><strong>Eventual del Campo (3):</strong> Trabajadores agricolas con contrato temporal</li>
					<li><strong>Trabajador del hogar (4):</strong> Empleados domesticos</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Instituto Mexicano del Seguro Social (IMSS)
				</p>
				<p>
					<strong>Uso:</strong> Esta clasificacion debe especificarse al dar de alta a un trabajador
					en el SUA y determina el tipo de prestaciones y el calculo de cuotas obrero-patronales.
				</p>
			</div>
		</div>
	{/if}
</div>
