<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Building, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { query, queryOne } from '$lib/db';

	interface TipoInstitucion {
		codigo: string;
		tipo: string;
		descripcion: string;
		regulador: string;
		ley_aplicable: string;
		ejemplos: string | null;
	}

	let data = $state<TipoInstitucion[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let selectedRegulador = $state<string | null>(null);
	let totalRecords = $state(0);

	const columns: ColumnDef<TipoInstitucion, unknown>[] = [
		{
			accessorKey: 'codigo',
			header: 'Codigo',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'tipo',
			header: 'Tipo de Institucion',
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

			const countResult = await queryOne<{ cnt: number }>('SELECT COUNT(*) as cnt FROM banxico_instituciones_financieras');
			totalRecords = countResult?.cnt ?? 0;

			const results = await query<TipoInstitucion>(
				'SELECT codigo, tipo, descripcion, regulador, ley_aplicable, ejemplos FROM banxico_instituciones_financieras ORDER BY codigo'
			);
			data = results;
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

	function parseEjemplos(ejemplos: string | null): string[] {
		if (!ejemplos) return [];
		try {
			return JSON.parse(ejemplos);
		} catch {
			return ejemplos.split(',').map(s => s.trim());
		}
	}
</script>

<svelte:head>
	<title>Instituciones Financieras (Banxico) - catalogmx</title>
	<meta name="description" content="Catalogo de tipos de instituciones del sistema financiero mexicano segun Banxico." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
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
					Catalogo de tipos de instituciones del sistema financiero mexicano
				</p>
			</div>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando desde SQLite...</span>
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
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Tipos de institucion</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{totalRecords}
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
				searchPlaceholder="Buscar por codigo, tipo o regulador..."
				pageSize={20}
			/>
		</div>

		<!-- Detailed list -->
		<div class="space-y-4 mb-8">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white">
				Descripcion detallada
			</h2>
			{#each filteredData as institucion}
				{@const ejemplos = parseEjemplos(institucion.ejemplos)}
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
					{#if ejemplos.length > 0}
						<div class="mt-4">
							<p class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Ejemplos:</p>
							<div class="flex flex-wrap gap-2">
								{#each ejemplos as ejemplo}
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
				Acerca de este catalogo
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>Sistema Financiero Mexicano:</strong> Conjunto de instituciones reguladas que
					facilitan la captacion de recursos, otorgamiento de creditos, y servicios financieros.
				</p>
				<p>
					<strong>Principales reguladores:</strong>
				</p>
				<ul class="list-disc list-inside ml-4 space-y-1">
					<li><strong>CNBV</strong> - Comision Nacional Bancaria y de Valores</li>
					<li><strong>CONSAR</strong> - Comision Nacional del Sistema de Ahorro para el Retiro</li>
					<li><strong>CNSF</strong> - Comision Nacional de Seguros y Fianzas</li>
					<li><strong>CONDUSEF</strong> - Comision Nacional para la Proteccion y Defensa de los Usuarios de Servicios Financieros</li>
					<li><strong>Banxico</strong> - Banco de Mexico</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Banco de Mexico (Banxico)
				</p>
			</div>
		</div>
	{/if}
</div>
