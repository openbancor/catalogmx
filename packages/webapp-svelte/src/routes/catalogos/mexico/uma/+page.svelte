<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, DollarSign, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface UMA {
		año: number;
		vigencia_inicio: string;
		vigencia_fin: string;
		valor_diario: number;
		valor_mensual: number;
		valor_anual: number;
		moneda: string;
		publicacion_dof: string;
		incremento_porcentual: number | null;
		notas: string;
	}

	let data = $state<UMA[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const umaActual = $derived(data.length > 0 ? data[0] : null);
	const añosDisponibles = $derived(data.length);

	const columns: ColumnDef<UMA, unknown>[] = [
		{
			accessorKey: 'año',
			header: 'Ano',
			cell: ({ getValue }) => getValue() as number,
		},
		{
			accessorKey: 'valor_diario',
			header: 'Valor Diario',
			cell: ({ getValue }) => {
				const valor = getValue() as number;
				return `$${valor.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
			},
		},
		{
			accessorKey: 'valor_mensual',
			header: 'Valor Mensual',
			cell: ({ getValue }) => {
				const valor = getValue() as number;
				return `$${valor.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
			},
		},
		{
			accessorKey: 'valor_anual',
			header: 'Valor Anual',
			cell: ({ getValue }) => {
				const valor = getValue() as number;
				return `$${valor.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
			},
		},
		{
			accessorKey: 'incremento_porcentual',
			header: 'Incremento %',
			cell: ({ getValue }) => {
				const incremento = getValue() as number | null;
				return incremento !== null ? `${incremento.toFixed(2)}%` : 'N/A';
			},
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load UMA data from SQLite
			data = await query<UMA>('SELECT * FROM mexico_uma ORDER BY año DESC');

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading UMA data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>UMA - Unidad de Medida y Actualizacion - catalogmx</title>
	<meta name="description" content="Catalogo historico de valores de la Unidad de Medida y Actualizacion (UMA) en Mexico desde 2017." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/mexico" class="hover:text-brand-500">Mexico</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">UMA</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
				<DollarSign class="h-6 w-6 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					UMA - Unidad de Medida y Actualizacion
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Valores historicos de la UMA desde su creacion en 2017
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-4 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">UMA Diario Actual</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else if umaActual}
					${umaActual.valor_diario.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
				{:else}
					--
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">UMA Mensual Actual</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else if umaActual}
					${umaActual.valor_mensual.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
				{:else}
					--
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">UMA Anual Actual</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else if umaActual}
					${umaActual.valor_anual.toLocaleString('es-MX', { minimumFractionDigits: 2 })}
				{:else}
					--
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Anos disponibles</p>
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
			searchPlaceholder="Buscar por ano o valor..."
		/>
	{/if}

	<!-- Info section -->
	{#if !loading && !error}
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de la UMA
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					La <strong>Unidad de Medida y Actualizacion (UMA)</strong> es la referencia economica en pesos
					mexicanos para determinar la cuantia del pago de obligaciones y supuestos previstos en las leyes
					federales, de las entidades federativas y del Distrito Federal, asi como en las disposiciones
					juridicas que emanen de todas las anteriores.
				</p>
				<p>
					<strong>Vigencia:</strong> Desde el 27 de enero de 2016, la UMA sustituyo al salario minimo
					como unidad de cuenta, indice, base, medida o referencia para fines diversos a la remuneracion
					de los trabajadores.
				</p>
				<p>
					<strong>Actualizacion:</strong> El valor de la UMA se actualiza anualmente con base en la inflacion
					y se publica en el Diario Oficial de la Federacion (DOF) cada enero.
				</p>
				<p>
					<strong>Fuente:</strong> Instituto Nacional de Estadistica y Geografia (INEGI)
				</p>
				<p>
					<strong>Uso:</strong> Multas, creditos del INFONAVIT, pagos de derechos, impuestos,
					aportaciones de seguridad social, y otros conceptos establecidos en las leyes.
				</p>
			</div>
		</div>
	{/if}
</div>
