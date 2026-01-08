<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Calendar, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface PaymentPeriodicity {
		code: string;
		descripcion: string;
		days: number;
	}

	let data = $state<PaymentPeriodicity[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const totalTypes = $derived(data.length);
	const periodicTypesCount = $derived(data.filter(p => p.days > 0).length);

	const columns: ColumnDef<PaymentPeriodicity, unknown>[] = [
		{
			accessorKey: 'code',
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
			accessorKey: 'days',
			header: 'Días',
			cell: ({ getValue }) => {
				const days = getValue() as number;
				return days > 0 ? days.toString() : 'Variable';
			},
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load payment periodicity data from SQLite
			const types = await query<PaymentPeriodicity>('SELECT * FROM sat_nomina_1_2_periodicidad_pago ORDER BY code');
			data = types;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading payment periodicity data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Periodicidad de Pago (SAT Nómina) - catalogmx</title>
	<meta name="description" content="Catálogo de periodicidad de pago de nómina del SAT para nómina electrónica." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat/nomina" class="hover:text-brand-500">Nómina</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Periodicidad de Pago</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<Calendar class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Periodicidad de Pago
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Frecuencias de pago de nómina reconocidas por el SAT
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-3 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total de opciones</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{totalTypes.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Periodicidades fijas</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{periodicTypesCount.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Versión del catálogo</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				1.2
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
					<strong>Periodicidad de Pago:</strong> Catálogo de las frecuencias con las que se realiza
					el pago de nómina a los trabajadores. Este catálogo incluye periodicidades fijas (diario,
					semanal, quincenal, mensual, etc.) y variables (unidad de obra, comisión, precio alzado).
				</p>
				<p>
					<strong>Periodicidades Fijas:</strong> Las periodicidades con días específicos representan
					esquemas de pago recurrentes basados en tiempo (ej: semanal = 7 días, quincenal = 15 días).
				</p>
				<p>
					<strong>Periodicidades Variables:</strong> Las opciones con días = 0 representan esquemas
					de pago basados en resultados o sin periodicidad fija.
				</p>
				<p>
					<strong>Fuente:</strong> Servicio de Administración Tributaria (SAT)
				</p>
				<p>
					<strong>Uso:</strong> La periodicidad de pago es obligatoria en el CFDI de nómina y
					determina la frecuencia con la que el empleado recibe su remuneración.
				</p>
			</div>
		</div>
	{/if}
</div>
