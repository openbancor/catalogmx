<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, DollarSign, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface SalarioMinimo {
		fecha: string;
		zona_frontera_norte: number | null;
		resto_pais: number | null;
		zona_general: number | null;
		zona_a: number | null;
		zona_b: number | null;
	}

	let data = $state<SalarioMinimo[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const salarioActual = $derived(data.length > 0 ? data[0] : null);
	const añosDisponibles = $derived(data.length);

	const columns: ColumnDef<SalarioMinimo, unknown>[] = [
		{
			accessorKey: 'fecha',
			header: 'Fecha',
			cell: ({ getValue }) => {
				const fecha = getValue() as string;
				return fecha;
			},
		},
		{
			id: 'salario_principal',
			header: 'Salario Diario',
			cell: ({ row }) => {
				const salario = row.original;
				if (salario.zona_frontera_norte !== null) {
					const frontera = salario.zona_frontera_norte.toLocaleString('es-MX', { minimumFractionDigits: 2 });
					const resto = salario.resto_pais?.toLocaleString('es-MX', { minimumFractionDigits: 2 }) || 'N/A';
					return `Frontera: $${frontera} / Resto: $${resto}`;
				} else if (salario.zona_general !== null) {
					return `$${salario.zona_general.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
				} else if (salario.zona_a !== null) {
					const zonaA = salario.zona_a.toLocaleString('es-MX', { minimumFractionDigits: 2 });
					const zonaB = salario.zona_b?.toLocaleString('es-MX', { minimumFractionDigits: 2 }) || 'N/A';
					return `Zona A: $${zonaA} / B: $${zonaB}`;
				}
				return 'N/A';
			},
		},
		{
			accessorKey: 'zona_frontera_norte',
			header: 'Frontera Norte',
			cell: ({ getValue }) => {
				const valor = getValue() as number | null;
				return valor !== null ? `$${valor.toLocaleString('es-MX', { minimumFractionDigits: 2 })}` : 'N/A';
			},
		},
		{
			accessorKey: 'resto_pais',
			header: 'Resto del Pais',
			cell: ({ getValue }) => {
				const valor = getValue() as number | null;
				return valor !== null ? `$${valor.toLocaleString('es-MX', { minimumFractionDigits: 2 })}` : 'N/A';
			},
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load salarios minimos data from SQLite (banxico_salarios_minimos from dynamic data)
			data = await query<SalarioMinimo>('SELECT * FROM banxico_salarios_minimos ORDER BY fecha DESC');

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
	<title>Salarios Minimos - Mexico - catalogmx</title>
	<meta name="description" content="Catalogo historico de salarios minimos en Mexico desde 2010 por zona geografica." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/mexico" class="hover:text-brand-500">Mexico</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Salarios Minimos</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<DollarSign class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Salarios Minimos en Mexico
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Historico de salarios minimos por zona geografica
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-3 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Frontera Norte (Actual)</p>
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
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Resto del Pais (Actual)</p>
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
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Registros disponibles</p>
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
			searchPlaceholder="Buscar por fecha o valor..."
		/>
	{/if}

	<!-- Info section -->
	{#if !loading && !error}
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de los salarios minimos
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					El <strong>salario minimo</strong> es la remuneracion minima diaria que debe recibir en efectivo
					un trabajador por los servicios prestados en una jornada de trabajo.
				</p>
				<p>
					<strong>Zona Frontera Norte (desde 2019):</strong> Municipios fronterizos con Estados Unidos que tienen
					un salario minimo mas alto debido al mayor costo de vida.
				</p>
				<p>
					<strong>Resto del Pais:</strong> Salario minimo aplicable al resto del territorio nacional.
				</p>
				<p>
					<strong>Zonas A y B (2010-2015):</strong> Antes de 2015, Mexico se dividia en dos zonas geograficas
					con diferentes salarios minimos.
				</p>
				<p>
					<strong>Fuente:</strong> Comision Nacional de los Salarios Minimos (CONASAMI) / Banco de Mexico
				</p>
				<p>
					<strong>Uso:</strong> Base para calcular remuneraciones, prestaciones laborales, y determinar
					el cumplimiento de obligaciones patronales.
				</p>
			</div>
		</div>
	{/if}
</div>
