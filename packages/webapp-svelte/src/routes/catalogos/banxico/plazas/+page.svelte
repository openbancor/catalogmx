<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, MapPin, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '@tanstack/svelte-table';
	import { onMount } from 'svelte';

	interface Plaza {
		codigo: string;
		plaza: string;
		estado: string;
		cve_entidad: string;
	}

	interface PlazasData {
		metadata: {
			catalog: string;
			description: string;
			source: string;
			last_updated: string;
			total_codes: number;
			total_plazas: number;
			notes: string;
		};
		plazas: Plaza[];
	}

	let data = $state<Plaza[]>([]);
	let metadata = $state<PlazasData['metadata'] | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let selectedEstado = $state<string | null>(null);

	const columns: ColumnDef<Plaza, unknown>[] = [
		{
			accessorKey: 'codigo',
			header: 'Código',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'plaza',
			header: 'Plaza',
		},
		{
			accessorKey: 'estado',
			header: 'Estado',
		},
		{
			accessorKey: 'cve_entidad',
			header: 'Cve Estado',
		},
	];

	const estados = $derived([...new Set(data.map(p => p.estado))].sort());

	const filteredData = $derived(
		selectedEstado
			? data.filter(p => p.estado === selectedEstado)
			: data
	);

	const estadoCounts = $derived(
		estados.map(estado => ({
			estado,
			count: data.filter(p => p.estado === estado).length
		}))
	);

	async function loadData() {
		try {
			loading = true;
			error = null;

			const response = await fetch('/data/banxico/codigos_plaza.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const jsonData: PlazasData = await response.json();
			data = jsonData.plazas;
			metadata = jsonData.metadata;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading Banxico plazas data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Códigos de Plaza (Banxico) - catalogmx</title>
	<meta name="description" content="Catálogo de códigos de plaza para el sistema CLABE (Clave Bancaria Estandarizada) de Banxico." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Plazas</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-3">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<MapPin class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Códigos de Plaza Bancaria
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Códigos de plaza utilizados en el sistema CLABE de Banxico
				</p>
			</div>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando plazas...</span>
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
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total códigos</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{metadata?.total_codes?.toLocaleString('es-MX') || data.length.toLocaleString('es-MX')}
				</p>
			</div>
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Plazas únicas</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{metadata?.total_plazas?.toLocaleString('es-MX') || [...new Set(data.map(p => p.plaza))].length.toLocaleString('es-MX')}
				</p>
			</div>
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-2">Filtrar por estado</p>
				<select
					class="input w-full text-sm"
					bind:value={selectedEstado}
				>
					<option value={null}>Todos los estados</option>
					{#each estadoCounts as { estado, count }}
						<option value={estado}>
							{estado} ({count})
						</option>
					{/each}
				</select>
			</div>
		</div>

		<!-- Data table -->
		<div class="card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
				{#if selectedEstado}
					Plazas de {selectedEstado}
				{:else}
					Todas las Plazas
				{/if}
			</h2>
			<DataTable
				data={filteredData}
				{columns}
				searchPlaceholder="Buscar por código, plaza o estado..."
				pageSize={50}
			/>
		</div>

		<!-- Info section -->
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de este catálogo
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>Código de Plaza:</strong> Identificador de 3 dígitos que se utiliza en las CLABEs
					(Clave Bancaria Estandarizada) para indicar la ubicación geográfica de la sucursal bancaria.
				</p>
				<p>
					<strong>Estructura CLABE:</strong> Una CLABE completa tiene 18 dígitos:
					3 dígitos de banco + 3 dígitos de plaza + 11 dígitos de cuenta + 1 dígito verificador.
				</p>
				{#if metadata?.notes}
					<p>
						<strong>Nota:</strong> {metadata.notes}
					</p>
				{/if}
				<p>
					<strong>Fuente:</strong> {metadata?.source || 'Banco de México (BANXICO)'}
				</p>
				<p>
					<strong>Última actualización:</strong> {metadata?.last_updated || 'No disponible'}
				</p>
			</div>
		</div>
	{/if}
</div>
