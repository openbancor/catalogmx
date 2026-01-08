<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, Coins, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';

	interface Moneda {
		codigo_iso: string;
		numero_iso: string;
		moneda: string;
		pais: string;
		simbolo: string;
		decimales: number;
		moneda_nacional: boolean;
		tipo_cambio_banxico: boolean;
		activa: boolean;
	}

	interface MonedasData {
		metadata: {
			catalog: string;
			description: string;
			source: string;
			last_updated: string;
			notes: string;
		};
		monedas: Moneda[];
	}

	let data = $state<Moneda[]>([]);
	let metadata = $state<MonedasData['metadata'] | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let filterActive = $state<boolean | null>(null);
	let filterBanxico = $state<boolean | null>(null);

	const columns: ColumnDef<Moneda, unknown>[] = [
		{
			accessorKey: 'codigo_iso',
			header: 'Código ISO',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'moneda',
			header: 'Moneda',
		},
		{
			accessorKey: 'pais',
			header: 'País',
		},
		{
			accessorKey: 'simbolo',
			header: 'Símbolo',
			cell: ({ getValue }) => getValue() as string,
		},
	];

	const monedasActivas = $derived(data.filter(m => m.activa).length);
	const monedasConTipoCambio = $derived(data.filter(m => m.tipo_cambio_banxico).length);

	const filteredData = $derived(() => {
		let result = data;
		if (filterActive !== null) {
			result = result.filter(m => m.activa === filterActive);
		}
		if (filterBanxico !== null) {
			result = result.filter(m => m.tipo_cambio_banxico === filterBanxico);
		}
		return result;
	});

	async function loadData() {
		try {
			loading = true;
			error = null;

			const response = await fetch('/data/banxico/monedas_divisas.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const jsonData: MonedasData = await response.json();
			data = jsonData.monedas;
			metadata = jsonData.metadata;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading Banxico monedas data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Monedas y Divisas (Banxico) - catalogmx</title>
	<meta name="description" content="Catálogo de monedas y divisas internacionales utilizadas en operaciones cambiarias en México según Banxico." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/banxico" class="hover:text-brand-500">Banxico</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Monedas</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-3">
			<div class="bg-amber-100 dark:bg-amber-900/30 p-3 rounded-lg">
				<Coins class="h-6 w-6 text-amber-600 dark:text-amber-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Monedas y Divisas
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogo de monedas internacionales utilizadas en operaciones cambiarias
				</p>
			</div>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando monedas...</span>
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
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total monedas</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{data.length}
				</p>
			</div>
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Monedas activas</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{monedasActivas}
				</p>
			</div>
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Con tipo de cambio Banxico</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
					{monedasConTipoCambio}
				</p>
			</div>
		</div>

		<!-- Filters -->
		<div class="card p-6 mb-8">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Filtros</h2>
			<div class="grid sm:grid-cols-2 gap-4">
				<div>
					<label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
						Estado de la moneda
					</label>
					<select class="input w-full" bind:value={filterActive}>
						<option value={null}>Todas</option>
						<option value={true}>Solo activas</option>
						<option value={false}>Solo inactivas</option>
					</select>
				</div>
				<div>
					<label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
						Tipo de cambio Banxico
					</label>
					<select class="input w-full" bind:value={filterBanxico}>
						<option value={null}>Todas</option>
						<option value={true}>Con tipo de cambio</option>
						<option value={false}>Sin tipo de cambio</option>
					</select>
				</div>
			</div>
		</div>

		<!-- Data table -->
		<div class="card p-6 mb-8">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
				Catálogo de Monedas
			</h2>
			<DataTable
				data={filteredData()}
				{columns}
				searchPlaceholder="Buscar por código, moneda o país..."
				pageSize={50}
			/>
		</div>

		<!-- Detailed list -->
		<div class="space-y-4 mb-8">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white">
				Información detallada
			</h2>
			<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{#each filteredData() as moneda}
					<div class="card p-4">
						<div class="flex items-start justify-between mb-3">
							<div>
								<div class="text-2xl mb-1">{moneda.simbolo}</div>
								<div class="font-mono text-sm font-bold text-slate-700 dark:text-slate-300">
									{moneda.codigo_iso}
								</div>
							</div>
							<div class="flex gap-1">
								{#if moneda.activa}
									<span class="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-2 py-1 rounded">
										Activa
									</span>
								{/if}
								{#if moneda.moneda_nacional}
									<span class="text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">
										MXN
									</span>
								{/if}
							</div>
						</div>
						<h3 class="font-semibold text-slate-900 dark:text-white mb-1">
							{moneda.moneda}
						</h3>
						<p class="text-sm text-slate-600 dark:text-slate-400 mb-3">
							{moneda.pais}
						</p>
						<div class="text-xs text-slate-500 dark:text-slate-400 space-y-1">
							<div class="flex justify-between">
								<span>Número ISO:</span>
								<span class="font-mono">{moneda.numero_iso}</span>
							</div>
							<div class="flex justify-between">
								<span>Decimales:</span>
								<span>{moneda.decimales}</span>
							</div>
							<div class="flex justify-between">
								<span>Tipo cambio Banxico:</span>
								<span>{moneda.tipo_cambio_banxico ? 'Sí' : 'No'}</span>
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Info section -->
		<div class="card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de este catálogo
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>Códigos ISO 4217:</strong> Estándar internacional para códigos de monedas de 3 letras.
					Los primeros 2 caracteres corresponden al código del país (ISO 3166-1 alpha-2) y el tercero
					a la inicial de la moneda.
				</p>
				<p>
					<strong>Tipo de cambio Banxico:</strong> Banxico publica diariamente tipos de cambio oficiales
					para las principales divisas internacionales utilizadas en operaciones cambiarias en México.
				</p>
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
