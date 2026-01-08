<script lang="ts">
	import { ChevronRight, Building2, Shield, Landmark, Briefcase, CreditCard } from 'lucide-svelte';

	const catalogs = [
		{
			title: 'Sectores Financieros',
			description: 'Clasificación de sectores regulados por la CNBV',
			href: '/catalogos/cnbv/sectores',
			icon: Building2,
			count: '15 sectores'
		}
	];
</script>

<svelte:head>
	<title>Catálogos CNBV - catalogmx</title>
	<meta name="description" content="Catálogos oficiales de la Comisión Nacional Bancaria y de Valores" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">CNBV</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-lg">
				<Landmark class="h-6 w-6 text-purple-600 dark:text-purple-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogos de la CNBV
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogos de la Comisión Nacional Bancaria y de Valores
				</p>
			</div>
		</div>
	</div>

	<!-- Catalog Grid -->
	<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
		{#each catalogs as catalog}
			<a
				href={catalog.href}
				class="card p-6 hover:shadow-lg transition-shadow duration-200 group"
			>
				<div class="flex items-start gap-4 mb-4">
					<div class="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-lg group-hover:bg-purple-200 dark:group-hover:bg-purple-800/40 transition-colors">
						<svelte:component this={catalog.icon} class="h-5 w-5 text-purple-600 dark:text-purple-400" />
					</div>
					<div class="flex-1">
						<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-2 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
							{catalog.title}
						</h2>
						<p class="text-sm text-slate-600 dark:text-slate-300">
							{catalog.description}
						</p>
					</div>
				</div>
				{#if catalog.count}
					<div class="text-xs text-slate-500 dark:text-slate-400 mt-2">
						{catalog.count}
					</div>
				{/if}
			</a>
		{/each}
	</div>

	<!-- Info section -->
	<div class="mt-8 card p-6">
		<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
			Acerca de la CNBV
		</h2>
		<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
			<p>
				La <strong>Comisión Nacional Bancaria y de Valores (CNBV)</strong> es el organismo encargado
				de supervisar y regular las entidades integrantes del sistema financiero mexicano.
			</p>
			<p>
				Los sectores regulados incluyen banca múltiple, banca de desarrollo, casas de bolsa,
				sociedades financieras, aseguradoras, y entidades fintech.
			</p>
		</div>
	</div>
</div>
