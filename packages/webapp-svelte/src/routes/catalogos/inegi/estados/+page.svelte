<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, MapPin, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface Estado {
		code: string;
		name: string;
		abbreviation: string;
		clave_inegi: string;
		aliases?: string;
		region?: string;
	}

	interface EstadoWithRegion extends Estado {
		region: string;
	}

	// Regional classification based on INEGI's geographic divisions
	const regionMapping: Record<string, string> = {
		'01': 'Centro Norte', // Aguascalientes
		'02': 'Noroeste', // Baja California
		'03': 'Noroeste', // Baja California Sur
		'04': 'Sureste', // Campeche
		'05': 'Noreste', // Coahuila
		'06': 'Centro Occidente', // Colima
		'07': 'Sureste', // Chiapas
		'08': 'Norte', // Chihuahua
		'09': 'Centro', // Ciudad de Mexico
		'10': 'Norte', // Durango
		'11': 'Centro', // Guanajuato
		'12': 'Sur', // Guerrero
		'13': 'Centro', // Hidalgo
		'14': 'Centro Occidente', // Jalisco
		'15': 'Centro', // Estado de Mexico
		'16': 'Centro Occidente', // Michoacan
		'17': 'Centro', // Morelos
		'18': 'Centro Occidente', // Nayarit
		'19': 'Noreste', // Nuevo Leon
		'20': 'Sur', // Oaxaca
		'21': 'Centro', // Puebla
		'22': 'Centro', // Queretaro
		'23': 'Sureste', // Quintana Roo
		'24': 'Centro Norte', // San Luis Potosi
		'25': 'Noroeste', // Sinaloa
		'26': 'Noroeste', // Sonora
		'27': 'Sureste', // Tabasco
		'28': 'Noreste', // Tamaulipas
		'29': 'Centro', // Tlaxcala
		'30': 'Oriente', // Veracruz
		'31': 'Sureste', // Yucatan
		'32': 'Centro Norte', // Zacatecas
		'99': 'Internacional', // Nacido en el extranjero
	};

	let data = $state<EstadoWithRegion[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let selectedRegion = $state<string | null>(null);

	const columns: ColumnDef<EstadoWithRegion, unknown>[] = [
		{
			accessorKey: 'clave_inegi',
			header: 'Clave',
			cell: ({ getValue }) => getValue() as string,
		},
		{
			accessorKey: 'name',
			header: 'Nombre',
		},
		{
			accessorKey: 'abbreviation',
			header: 'Abreviatura',
		},
		{
			accessorKey: 'region',
			header: 'Region',
		},
	];

	const regions = $derived([...new Set(data.map(e => e.region))].sort());

	const filteredData = $derived(
		selectedRegion
			? data.filter(e => e.region === selectedRegion)
			: data
	);

	const regionCounts = $derived(
		regions.map(region => ({
			region,
			count: data.filter(e => e.region === region).length
		}))
	);

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load states data from SQLite
			const rawData = await query<Estado>('SELECT * FROM inegi_states ORDER BY clave_inegi');

			// Add region to each state
			data = rawData.map(estado => ({
				...estado,
				region: regionMapping[estado.clave_inegi] || 'Sin clasificar'
			}));

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading INEGI estados data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Estados de México (INEGI) - catalogmx</title>
	<meta name="description" content="Catalogo oficial de estados de Mexico segun INEGI. Incluye claves, abreviaturas y clasificacion regional." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/inegi" class="hover:text-brand-500">INEGI</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Estados</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-3 mb-2">
			<div class="bg-brand-100 dark:bg-brand-900/30 p-2 rounded-lg">
				<MapPin class="h-6 w-6 text-brand-600 dark:text-brand-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white">
					Estados de Mexico
				</h1>
				<p class="text-slate-600 dark:text-slate-300 mt-1">
					Catalogo oficial de entidades federativas segun INEGI con claves y clasificacion regional
				</p>
			</div>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando estados desde SQLite...</span>
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
		<div class="grid gap-4 sm:grid-cols-4 mb-8">
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total estados</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">{data.length - 1}</p>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">32 entidades federativas</p>
			</div>
			<div class="card p-4">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Regiones</p>
				<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">{regions.length - 1}</p>
				<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Clasificacion geografica</p>
			</div>
			<div class="card p-4 col-span-2">
				<p class="text-sm text-slate-500 dark:text-slate-400 mb-2">Filtrar por region</p>
				<select
					class="input w-full"
					bind:value={selectedRegion}
				>
					<option value={null}>Todas las regiones</option>
					{#each regions.filter(r => r !== 'Internacional') as region}
						<option value={region}>
							{region} ({regionCounts.find(rc => rc.region === region)?.count || 0})
						</option>
					{/each}
				</select>
			</div>
		</div>

		<!-- Region distribution -->
		<div class="card p-6 mb-8">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
				Distribucion por Region
			</h2>
			<div class="grid gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
				{#each regionCounts.filter(rc => rc.region !== 'Internacional') as { region, count }}
					<button
						class={`text-left p-3 rounded-lg border transition-colors ${
							selectedRegion === region
								? 'border-brand-500 bg-brand-50 dark:bg-brand-900/20'
								: 'border-slate-200 dark:border-slate-700 hover:border-brand-500 hover:bg-brand-50 dark:hover:bg-brand-900/20'
						}`}
						onclick={() => selectedRegion = selectedRegion === region ? null : region}
					>
						<p class="font-medium text-slate-900 dark:text-white">{region}</p>
						<p class="text-sm text-slate-500 dark:text-slate-400">{count} estado{count !== 1 ? 's' : ''}</p>
					</button>
				{/each}
			</div>
		</div>

		<!-- Data table -->
		<div class="card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
				{#if selectedRegion}
					Estados - Region {selectedRegion}
				{:else}
					Todos los Estados
				{/if}
			</h2>
			<DataTable
				data={filteredData}
				{columns}
				searchPlaceholder="Buscar por clave, nombre o abreviatura..."
				pageSize={33}
			/>
		</div>

		<!-- Additional info -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
			<p class="text-sm text-slate-600 dark:text-slate-400">
				<strong>Nota:</strong> La clasificacion regional se basa en las divisiones geograficas establecidas por el INEGI.
				Las claves INEGI son utilizadas en diversos sistemas oficiales como CURP, RFC, codigo postal, entre otros.
			</p>
		</div>
	{/if}
</div>
