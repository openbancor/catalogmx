<script lang="ts">
	import { ChevronRight, Search, Ruler } from 'lucide-svelte';
	import { onMount } from 'svelte';

	interface Unidad {
		id: string;
		nombre: string;
		descripcion: string;
		simbolo: string;
		fechaDeInicioDeVigencia: string;
		fechaDeFinDeVigencia: string;
	}

	let unidades = $state<Unidad[]>([]);
	let searchQuery = $state('');
	let loading = $state(true);
	let displayLimit = $state(50);

	const filteredUnidades = $derived(
		searchQuery.trim()
			? unidades.filter(u =>
					u.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
					u.nombre.toLowerCase().includes(searchQuery.toLowerCase()) ||
					(u.simbolo && u.simbolo.toLowerCase().includes(searchQuery.toLowerCase()))
				)
			: unidades
	);

	const displayedUnidades = $derived(filteredUnidades.slice(0, displayLimit));

	onMount(async () => {
		try {
			const res = await fetch('/data/sat/cfdi_4.0/clave_unidad.json');
			unidades = await res.json();
		} catch (error) {
			console.error('Error loading unidades:', error);
		} finally {
			loading = false;
		}
	});

	function loadMore() {
		displayLimit += 50;
	}
</script>

<svelte:head>
	<title>Claves de Unidad SAT - catalogmx</title>
	<meta name="description" content="Catálogo de claves de unidad de medida del SAT para CFDI 4.0" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Claves de Unidad</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg">
				<Ruler class="h-6 w-6 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Claves de Unidad de Medida
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogo c_ClaveUnidad del SAT para CFDI 4.0 ({unidades.length.toLocaleString()} unidades)
				</p>
			</div>
		</div>
	</div>

	<!-- Search -->
	<div class="relative max-w-md mb-6">
		<Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
		<input
			type="search"
			placeholder="Buscar por clave, nombre o símbolo..."
			bind:value={searchQuery}
			class="input pl-11"
		/>
	</div>

	{#if loading}
		<div class="text-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-500 mx-auto"></div>
			<p class="mt-4 text-slate-500 dark:text-slate-400">Cargando unidades...</p>
		</div>
	{:else}
		<!-- Results count -->
		{#if searchQuery}
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-4">
				{filteredUnidades.length.toLocaleString()} resultado{filteredUnidades.length !== 1 ? 's' : ''}
			</p>
		{/if}

		<!-- Table -->
		<div class="card overflow-hidden">
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead class="bg-slate-50 dark:bg-slate-800">
						<tr>
							<th class="text-left py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Clave</th>
							<th class="text-left py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Nombre</th>
							<th class="text-left py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Símbolo</th>
							<th class="text-left py-3 px-4 font-medium text-slate-700 dark:text-slate-300">Vigencia</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-200 dark:divide-slate-700">
						{#each displayedUnidades as unidad}
							<tr class="hover:bg-slate-50 dark:hover:bg-slate-800/50">
								<td class="py-3 px-4 font-mono text-slate-900 dark:text-white">{unidad.id}</td>
								<td class="py-3 px-4 text-slate-700 dark:text-slate-300">{unidad.nombre}</td>
								<td class="py-3 px-4 text-slate-500 dark:text-slate-400">{unidad.simbolo || '-'}</td>
								<td class="py-3 px-4 text-slate-500 dark:text-slate-400 text-xs">
									{unidad.fechaDeInicioDeVigencia}
									{#if unidad.fechaDeFinDeVigencia}
										<span class="text-red-500"> - {unidad.fechaDeFinDeVigencia}</span>
									{/if}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>

		<!-- Load more -->
		{#if displayedUnidades.length < filteredUnidades.length}
			<div class="text-center mt-6">
				<button onclick={loadMore} class="btn-primary">
					Cargar más ({filteredUnidades.length - displayedUnidades.length} restantes)
				</button>
			</div>
		{/if}
	{/if}
</div>
