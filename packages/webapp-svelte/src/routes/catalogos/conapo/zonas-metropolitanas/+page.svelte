<script lang="ts">
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { Search, MapPinned, Building2, Users } from 'lucide-svelte';

	interface ZonaMetropolitana {
		zm_id: string;
		nombre: string;
		nombre_slug: string;
		tipo: string;
		num_municipios: number;
	}

	let zonas = $state<ZonaMetropolitana[]>([]);
	let loading = $state(true);
	let searchQuery = $state('');
	let filterTipo = $state<string>('all');

	const filteredZonas = $derived(() => {
		let result = zonas;

		if (filterTipo !== 'all') {
			result = result.filter(z => z.tipo === filterTipo);
		}

		if (searchQuery.trim()) {
			const q = searchQuery.toLowerCase();
			result = result.filter(z =>
				z.nombre.toLowerCase().includes(q) ||
				z.zm_id.toLowerCase().includes(q)
			);
		}

		return result;
	});

	const tipos = $derived(() => {
		const uniqueTipos = [...new Set(zonas.map(z => z.tipo))];
		return uniqueTipos.sort();
	});

	const stats = $derived(() => ({
		total: zonas.length,
		zonasMetropolitanas: zonas.filter(z => z.tipo === 'Zona metropolitana').length,
		metropolisMunicipales: zonas.filter(z => z.tipo === 'Metrópoli municipal').length,
		totalMunicipios: zonas.reduce((sum, z) => sum + z.num_municipios, 0)
	}));

	onMount(async () => {
		try {
			const data = await query<ZonaMetropolitana>(
				`SELECT zm_id, nombre, nombre_slug, tipo, num_municipios
				 FROM geo_zonas_metropolitanas
				 ORDER BY nombre`
			);
			zonas = data;
		} catch (error) {
			console.error('Error loading zonas metropolitanas:', error);
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>Zonas Metropolitanas - CONAPO - catalogmx</title>
	<meta name="description" content="Catálogo de las 92 zonas metropolitanas de México definidas por CONAPO 2020." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="mb-8">
		<h1 class="text-3xl font-bold text-slate-900 dark:text-white mb-2 flex items-center gap-3">
			<Building2 class="h-8 w-8 text-indigo-500" />
			Zonas Metropolitanas
		</h1>
		<p class="text-slate-600 dark:text-slate-300">
			Sistema Urbano Nacional - CONAPO 2020
		</p>
	</div>

	{#if loading}
		<div class="flex items-center justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500"></div>
		</div>
	{:else}
		<!-- Stats -->
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
			<div class="card p-4 text-center">
				<div class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">{stats().total}</div>
				<div class="text-sm text-slate-600 dark:text-slate-400">Total</div>
			</div>
			<div class="card p-4 text-center">
				<div class="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats().zonasMetropolitanas}</div>
				<div class="text-sm text-slate-600 dark:text-slate-400">Zonas Metropolitanas</div>
			</div>
			<div class="card p-4 text-center">
				<div class="text-2xl font-bold text-green-600 dark:text-green-400">{stats().metropolisMunicipales}</div>
				<div class="text-sm text-slate-600 dark:text-slate-400">Metrópolis Municipales</div>
			</div>
			<div class="card p-4 text-center">
				<div class="text-2xl font-bold text-amber-600 dark:text-amber-400">{stats().totalMunicipios}</div>
				<div class="text-sm text-slate-600 dark:text-slate-400">Municipios</div>
			</div>
		</div>

		<!-- Filters -->
		<div class="flex flex-col sm:flex-row gap-4 mb-6">
			<div class="relative flex-1 max-w-md">
				<Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
				<input
					type="search"
					placeholder="Buscar zona metropolitana..."
					class="input pl-10 w-full"
					bind:value={searchQuery}
				/>
			</div>
			<select class="input w-auto" bind:value={filterTipo}>
				<option value="all">Todos los tipos</option>
				{#each tipos() as tipo}
					<option value={tipo}>{tipo}</option>
				{/each}
			</select>
		</div>

		<!-- Results count -->
		<div class="text-sm text-slate-600 dark:text-slate-400 mb-4">
			Mostrando {filteredZonas().length} de {zonas.length} zonas
		</div>

		<!-- Grid -->
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
			{#each filteredZonas() as zona}
				<div class="card p-4 hover:border-indigo-300 dark:hover:border-indigo-700 transition-colors">
					<div class="flex items-start justify-between">
						<div>
							<h3 class="font-semibold text-slate-900 dark:text-white">
								{zona.nombre}
							</h3>
							<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
								{zona.zm_id}
							</p>
						</div>
						<span class="text-xs px-2 py-1 rounded-full {zona.tipo === 'Zona metropolitana' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'}">
							{zona.tipo === 'Zona metropolitana' ? 'ZM' : 'MM'}
						</span>
					</div>
					<div class="flex items-center gap-4 mt-3 text-xs text-slate-500 dark:text-slate-400">
						<span class="flex items-center gap-1">
							<MapPinned class="h-3 w-3" />
							{zona.num_municipios} municipio{zona.num_municipios !== 1 ? 's' : ''}
						</span>
					</div>
				</div>
			{/each}
		</div>

		{#if filteredZonas().length === 0}
			<div class="text-center py-12 text-slate-500 dark:text-slate-400">
				No se encontraron zonas metropolitanas
			</div>
		{/if}
	{/if}
</div>
