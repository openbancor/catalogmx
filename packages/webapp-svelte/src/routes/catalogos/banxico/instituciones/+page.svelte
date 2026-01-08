<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Building, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';

	interface TipoInstitucion {
		codigo: string;
		tipo: string;
		descripcion: string;
		regulador: string;
		ley_aplicable: string;
		ejemplos?: string[];
	}

	interface InstitucionesData {
		metadata: {
			catalog: string;
			description: string;
			source: string;
			last_updated: string;
			notes: string;
		};
		tipos_institucion: TipoInstitucion[];
	}

	let data = $state<TipoInstitucion[]>([]);
	let metadata = $state<InstitucionesData['metadata'] | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let selectedRegulador = $state<string | null>(null);

	const columns: ColumnDef<TipoInstitucion, unknown>[] = [
		{
			accessorKey: 'codigo',
			header: 'Código',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'tipo',
			header: 'Tipo de Institución',
		},
		{
			accessorKey: 'regulador',
			header: 'Regulador',
		},
	];

	const reguladores = $derived([...new Set(data.map(i => i.regulador))].sort());

	const filteredData = $derived(
		selectedRegulador
			? data.filter(i => i.regulador === selectedRegulador)
			: data
	);

	const reguladorCounts = $derived(
		reguladores.map(regulador => ({
			regulador,
			count: data.filter(i => i.regulador === regulador).length
		}))
	);

	async function loadData() {
		try {
			loading = true;
			error = null;

			const response = await fetch('/data/banxico/instituciones_financieras.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const jsonData: InstitucionesData = await response.json();
			data = jsonData.tipos_institucion;
			metadata = jsonData.metadata;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading Banxico instituciones data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Instituciones Financieras (Banxico) - catalogmx</title>
	<meta name="description" content="Catálogo de tipos de instituciones del sistema financiero mexicano según Banxico." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Instituciones</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-3">
			<div class="bg-indigo-100 dark:bg-indigo-900/30 p-3 rounded-lg">
				<Building class="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Instituciones Financieras
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogo de tipos de instituciones del sistema financiero mexicano
				</p>
			</div>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando instituciones...</span>
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
		<!-- Stats -->
		<div class="grid gap-4 sm:grid-cols-3 mb-8">
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Tipos de institución</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{data.length}
				</p>
			</div>
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Reguladores</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{reguladores.length}
				</p>
			</div>
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-2">Filtrar por regulador</p>
				<select
					class="input w-full text-sm"
					bind:value={selectedRegulador}
				>
					<option value={null}>Todos los reguladores</option>
					{#each reguladorCounts as { regulador, count }}
						<option value={regulador}>
							{regulador} ({count})
						</option>
					{/each}
				</select>
			</div>
		</div>

		<!-- Data table -->
		<div class="card p-6 mb-8">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
				{#if selectedRegulador}
					Instituciones reguladas por {selectedRegulador}
				{:else}
					Todas las Instituciones
				{/if}
			</h2>
			<DataTable
				data={filteredData}
				{columns}
				searchPlaceholder="Buscar por código, tipo o regulador..."
				pageSize={20}
			/>
		</div>

		<!-- Detailed list -->
		<div class="space-y-4 mb-8">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white">
				Descripción detallada
			</h2>
			{#each filteredData as institucion}
				<div class="card p-6">
					<div class="flex items-start gap-3 mb-3">
						<div class="bg-indigo-100 dark:bg-indigo-900/30 px-3 py-1 rounded text-sm font-mono text-indigo-700 dark:text-indigo-300">
							{institucion.codigo}
						</div>
						<div class="flex-1">
							<h3 class="text-lg font-semibold text-slate-900 dark:text-white">
								{institucion.tipo}
							</h3>
						</div>
					</div>
					<p class="text-slate-600 dark:text-slate-300 mb-4">
						{institucion.descripcion}
					</p>
					<div class="grid sm:grid-cols-2 gap-4">
						<div>
							<p class="text-sm font-medium text-slate-700 dark:text-slate-300">Regulador</p>
							<p class="text-sm text-slate-600 dark:text-slate-400">{institucion.regulador}</p>
						</div>
						<div>
							<p class="text-sm font-medium text-slate-700 dark:text-slate-300">Ley aplicable</p>
							<p class="text-sm text-slate-600 dark:text-slate-400">{institucion.ley_aplicable}</p>
						</div>
					</div>
					{#if institucion.ejemplos && institucion.ejemplos.length > 0}
						<div class="mt-4">
							<p class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Ejemplos:</p>
							<div class="flex flex-wrap gap-2">
								{#each institucion.ejemplos as ejemplo}
									<span class="text-xs bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-1 rounded">
										{ejemplo}
									</span>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			{/each}
		</div>

		<!-- Info section -->
		<div class="card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de este catálogo
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>Sistema Financiero Mexicano:</strong> Conjunto de instituciones reguladas que
					facilitan la captación de recursos, otorgamiento de créditos, y servicios financieros.
				</p>
				<p>
					<strong>Principales reguladores:</strong>
				</p>
				<ul class="list-disc list-inside ml-4 space-y-1">
					<li><strong>CNBV</strong> - Comisión Nacional Bancaria y de Valores</li>
					<li><strong>CONSAR</strong> - Comisión Nacional del Sistema de Ahorro para el Retiro</li>
					<li><strong>CNSF</strong> - Comisión Nacional de Seguros y Fianzas</li>
					<li><strong>CONDUSEF</strong> - Comisión Nacional para la Protección y Defensa de los Usuarios de Servicios Financieros</li>
					<li><strong>Banxico</strong> - Banco de México</li>
				</ul>
				<p>
					<strong>Fuente:</strong> {metadata?.source || 'Banco de México (Banxico)'}
				</p>
				<p>
					<strong>Última actualización:</strong> {metadata?.last_updated || 'No disponible'}
				</p>
			</div>
		</div>
	{/if}
</div>
