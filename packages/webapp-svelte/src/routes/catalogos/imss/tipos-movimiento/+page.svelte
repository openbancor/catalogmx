<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Activity, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '@tanstack/svelte-table';
	import { onMount } from 'svelte';

	interface TipoMovimiento {
		clave: string;
		descripcion: string;
		tipo: string;
	}

	let data = $state<TipoMovimiento[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const totalMovimientos = $derived(data.length);

	const columns: ColumnDef<TipoMovimiento, unknown>[] = [
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
			accessorKey: 'tipo',
			header: 'Tipo',
			cell: ({ getValue }) => {
				const tipo = getValue() as string;
				const colorMap: Record<string, string> = {
					'alta': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
					'baja': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
					'modificacion': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
					'reingreso': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400'
				};
				const colorClass = colorMap[tipo] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
				return `<span class="px-2 py-1 rounded-full text-xs font-medium ${colorClass}">${tipo}</span>`;
			},
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
			data = json.tipos_movimiento_afiliatorio || [];

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
	<title>Tipos de Movimiento Afiliatorio (IMSS) - catalogmx</title>
	<meta name="description" content="Catálogo de tipos de movimiento afiliatorio del IMSS para el Sistema Único de Autodeterminación (SUA)" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/imss" class="hover:text-brand-500">IMSS</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Tipos de Movimiento</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<Activity class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Tipos de Movimiento Afiliatorio
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Claves de movimientos para el Sistema Único de Autodeterminación (SUA)
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-2 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total de movimientos</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{totalMovimientos}
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
					<strong>Movimientos Afiliatoriос:</strong> Son las operaciones que los patrones deben reportar al IMSS
					a través del Sistema Único de Autodeterminación (SUA) para mantener actualizado el registro de sus trabajadores.
				</p>
				<p>
					<strong>Tipos principales:</strong>
				</p>
				<ul class="list-disc list-inside space-y-1 ml-4">
					<li><strong>Alta (08):</strong> Registro inicial de un trabajador ante el IMSS</li>
					<li><strong>Baja (02):</strong> Terminación de la relación laboral</li>
					<li><strong>Modificación (07):</strong> Cambio en el salario del trabajador</li>
					<li><strong>Reingreso (12):</strong> Reincorporación de un trabajador previamente dado de baja</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Instituto Mexicano del Seguro Social (IMSS)
				</p>
				<p>
					<strong>Uso:</strong> Estos códigos deben utilizarse al presentar movimientos afiliatoriOS en el SUA
					para que el IMSS actualice correctamente el registro patronal y calcule las cuotas correspondientes.
				</p>
			</div>
		</div>
	{/if}
</div>
