<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, UserX, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface TipoIncapacidad {
		clave: string;
		descripcion: string;
		dias_pago: string;
	}

	let data = $state<TipoIncapacidad[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	const totalTipos = $derived(data.length);

	const columns: ColumnDef<TipoIncapacidad, unknown>[] = [
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
			accessorKey: 'dias_pago',
			header: 'Dias de Pago',
			cell: ({ getValue }) => getValue() as string,
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load tipos de incapacidad from canonical IMSS JSON in SQLite
			const result = await query<{ payload: string }>(
				'SELECT payload FROM catalog_json WHERE path = ? LIMIT 1',
				['imss-catalogs.json']
			);
			if (result.length === 0) {
				throw new Error('No se encontro imss-catalogs.json en catalog_json');
			}
			const catalog = JSON.parse(result[0].payload) as {
				tipos_incapacidad?: TipoIncapacidad[];
			};
			data = Array.isArray(catalog.tipos_incapacidad) ? catalog.tipos_incapacidad : [];

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
	<title>Tipos de Incapacidad (IMSS) - catalogmx</title>
	<meta name="description" content="Catalogo de tipos de incapacidad y subsidios del IMSS" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/imss" class="hover:text-brand-500">IMSS</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Tipos de Incapacidad</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<UserX class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Tipos de Incapacidad
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Clasificacion de incapacidades y subsidios del IMSS
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
					<strong>Tipos de Incapacidad:</strong> El IMSS clasifica las incapacidades segun su origen,
					lo cual determina el porcentaje de pago del subsidio y los dias que se cubren.
				</p>
				<p>
					<strong>Clasificaciones:</strong>
				</p>
				<ul class="list-disc list-inside space-y-1 ml-4">
					<li><strong>Riesgo de trabajo (1):</strong> Accidentes o enfermedades laborales. Se paga 100% del salario desde el primer dia</li>
					<li><strong>Enfermedad general (2):</strong> Padecimientos no laborales. Se paga 60% del salario a partir del 4to dia</li>
					<li><strong>Maternidad (3):</strong> Descanso por embarazo. Se paga 100% del salario durante 84 dias (42 antes y 42 despues del parto)</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Instituto Mexicano del Seguro Social (IMSS)
				</p>
				<p>
					<strong>Uso:</strong> Los patrones deben especificar el tipo de incapacidad al tramitar
					certificados ante el IMSS y para el calculo correcto de subsidios en nomina.
				</p>
			</div>
		</div>
	{/if}
</div>
