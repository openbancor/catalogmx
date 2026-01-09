<script lang="ts">
	import { base } from '$app/paths';
	import { ChevronRight, MapPin, Building, Map, Layers } from 'lucide-svelte';

	const catalogs = [
		{
			id: 'estados',
			name: 'Estados de Mexico',
			description: 'Catalogo oficial de entidades federativas con claves INEGI y clasificacion regional',
			count: 32,
			icon: MapPin,
			href: `${base}/catalogos/inegi/estados`
		},
		{
			id: 'municipios',
			name: 'Municipios',
			description: 'Catalogo de municipios y alcaldias de Mexico',
			count: 2469,
			icon: Building,
			href: `${base}/catalogos/inegi/municipios`,
			disabled: true
		},
		{
			id: 'localidades',
			name: 'Localidades',
			description: 'Catalogo de poblaciones y colonias',
			count: 304000,
			icon: Map,
			href: `${base}/catalogos/inegi/localidades`,
			disabled: true
		},
		{
			id: 'scian',
			name: 'SCIAN',
			description: 'Sistema de Clasificacion Industrial de America del Norte',
			count: 1800,
			icon: Layers,
			href: `${base}/catalogos/inegi/scian`,
			disabled: true
		}
	];

	function formatCount(num: number): string {
		if (num >= 1000) {
			return (num / 1000).toFixed(num >= 10000 ? 0 : 1) + 'k';
		}
		return num.toString();
	}
</script>

<svelte:head>
	<title>Catalogos INEGI - catalogmx</title>
	<meta name="description" content="Catalogos oficiales del Instituto Nacional de Estadistica y Geografia (INEGI) de Mexico." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">INEGI</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
			Catalogos INEGI
		</h1>
		<p class="text-slate-600 dark:text-slate-300">
			Instituto Nacional de Estadistica y Geografia
		</p>
	</div>

	<!-- Catalogs grid -->
	<div class="grid gap-6 md:grid-cols-2">
		{#each catalogs as catalog}
			{@const Icon = catalog.icon}
			{#if catalog.disabled}
				<div class="card p-6 opacity-50 cursor-not-allowed">
					<div class="flex items-start gap-4">
						<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
							<Icon class="h-6 w-6 text-blue-600 dark:text-blue-400" />
						</div>
						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-2 mb-1">
								<h3 class="font-semibold text-slate-900 dark:text-white">
									{catalog.name}
								</h3>
								<span class="badge badge-secondary text-xs">
									Proximamente
								</span>
								<span class="text-xs text-slate-400 dark:text-slate-500 tabular-nums">
									{formatCount(catalog.count)}
								</span>
							</div>
							<p class="text-sm text-slate-500 dark:text-slate-400">
								{catalog.description}
							</p>
						</div>
					</div>
				</div>
			{:else}
				<a
					href={catalog.href}
					class="card p-6 hover:border-brand-300 dark:hover:border-brand-600 transition-colors group"
				>
					<div class="flex items-start gap-4">
						<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
							<Icon class="h-6 w-6 text-blue-600 dark:text-blue-400" />
						</div>
						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-2 mb-1">
								<h3 class="font-semibold text-slate-900 dark:text-white group-hover:text-brand-500">
									{catalog.name}
								</h3>
								<span class="text-xs text-slate-400 dark:text-slate-500 tabular-nums bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
									{formatCount(catalog.count)}
								</span>
							</div>
							<p class="text-sm text-slate-500 dark:text-slate-400">
								{catalog.description}
							</p>
						</div>
					</div>
				</a>
			{/if}
		{/each}
	</div>

	<!-- Info section -->
	<div class="mt-12 p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
		<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">
			Acerca del INEGI
		</h2>
		<p class="text-sm text-slate-600 dark:text-slate-400">
			El Instituto Nacional de Estadistica y Geografia (INEGI) es el organismo publico autonomo responsable
			de normar y coordinar el Sistema Nacional de Informacion Estadistica y Geografica en Mexico. Los catalogos
			de INEGI son utilizados como estandares en diversos sistemas oficiales y de gobierno.
		</p>
	</div>
</div>