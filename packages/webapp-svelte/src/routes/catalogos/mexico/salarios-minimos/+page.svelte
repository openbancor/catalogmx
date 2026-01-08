<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, DollarSign, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '@tanstack/svelte-table';
	import { onMount } from 'svelte';

	interface SalarioMinimo {
		año: number;
		vigencia_inicio: string;
		zona_frontera_norte?: number;
		resto_pais?: number;
		zona_general?: number;
		zona_a?: number;
		zona_b?: number;
		moneda: string;
		periodo: string;
		notas: string;
	}

	let data = $state<SalarioMinimo[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const salarioActual = $derived(data.length > 0 ? data[0] : null);
	const añosDisponibles = $derived(data.length);

	const columns: ColumnDef<SalarioMinimo, unknown>[] = [
		{
			accessorKey: 'año',
			header: 'Año',
			cell: ({ getValue }) => getValue() as number,
		},
		{
			accessorKey: 'vigencia_inicio',
			header: 'Vigencia',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			id: 'salario_principal',
			header: 'Salario Diario',
			cell: ({ row }) => {
				const salario = row.original;
				if (salario.zona_frontera_norte !== undefined) {
					return `Frontera: $${salario.zona_frontera_norte.toLocaleString('es-MX', { minimumFractionDigits: 2 })} / Resto: $${salario.resto_pais?.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
				} else if (salario.zona_general !== undefined) {
					return `$${salario.zona_general.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
				} else if (salario.zona_a !== undefined) {
					return `Zona A: $${salario.zona_a.toLocaleString('es-MX', { minimumFractionDigits: 2 })} / B: $${salario.zona_b?.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
				}
				return 'N/A';
			},
		},
		{
			accessorKey: 'notas',
			header: 'Notas',
			cell: ({ getValue }) => getValue() as string,
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load salarios minimos data from JSON
			const response = await fetch('/data/mexico/salarios_minimos.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const salariosData = await response.json();
			data = salariosData;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading salarios minimos data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Salarios Mínimos - México - catalogmx</title>
	<meta name="description" content="Catálogo histórico de salarios mínimos en México desde 2010 por zona geográfica." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/mexico" class="hover:text-brand-500">México</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Salarios Mínimos</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<DollarSign class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Salarios Mínimos en México
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Histórico de salarios mínimos por zona geográfica desde 2010
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-3 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Frontera Norte (2025)</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else if salarioActual && salarioActual.zona_frontera_norte}
					${salarioActual.zona_frontera_norte.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
				{:else}
					--
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Resto del País (2025)</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else if salarioActual && salarioActual.resto_pais}
					${salarioActual.resto_pais.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
				{:else}
					--
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Años disponibles</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{añosDisponibles.toLocaleString('es-MX')}
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
			searchPlaceholder="Buscar por año o valor..."
		/>
	{/if}

	<!-- Info section -->
	{#if !loading && !error}
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de los salarios mínimos
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					El <strong>salario mínimo</strong> es la remuneración mínima diaria que debe recibir en efectivo
					un trabajador por los servicios prestados en una jornada de trabajo.
				</p>
				<p>
					<strong>Zona Frontera Norte (desde 2019):</strong> Municipios fronterizos con Estados Unidos que tienen
					un salario mínimo más alto debido al mayor costo de vida.
				</p>
				<p>
					<strong>Resto del País:</strong> Salario mínimo aplicable al resto del territorio nacional.
				</p>
				<p>
					<strong>Zonas A y B (2010-2015):</strong> Antes de 2015, México se dividía en dos zonas geográficas
					con diferentes salarios mínimos.
				</p>
				<p>
					<strong>Fuente:</strong> Comisión Nacional de los Salarios Mínimos (CONASAMI)
				</p>
				<p>
					<strong>Uso:</strong> Base para calcular remuneraciones, prestaciones laborales, y determinar
					el cumplimiento de obligaciones patronales.
				</p>
			</div>
		</div>
	{/if}
</div>
