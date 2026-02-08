<script lang="ts">
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';
	const SITE_URL = 'https://catalogmx.openbancor.com';
	const canonicalUrl = `${SITE_URL}/mexico`;
	const mexicoJsonLd = {
		'@context': 'https://schema.org',
		'@type': 'CollectionPage',
		name: 'Estados de Mexico',
		url: canonicalUrl,
		description:
			'Explora los estados y municipios de Mexico con datos demograficos y enlaces a codigos postales.'
	};

	type Estado = {
		cve_inegi: string;
		nombre: string;
		nombre_slug: string;
		abreviatura: string;
		num_municipios: number;
		poblacion_total: number;
	};

	let estados: Estado[] = [];
	let loading = true;
	let error = '';
	let totalPoblacion = 0;
	let totalMunicipios = 0;

	onMount(async () => {
		try {
			// Try using the view first, fallback to join query
			try {
				estados = await query<Estado>(`
					SELECT * FROM v_estado_stats
					ORDER BY nombre
				`);
			} catch {
				// Fallback: manual join if view doesn't exist
				estados = await query<Estado>(`
					SELECT
						e.cve_inegi,
						e.nombre,
						e.nombre_slug,
						e.abreviatura,
						COUNT(m.cve_inegi) as num_municipios,
						COALESCE(SUM(m.poblacion_total), 0) as poblacion_total
					FROM geo_estados e
					LEFT JOIN geo_municipios m ON e.cve_inegi = m.cve_entidad
					GROUP BY e.cve_inegi
					ORDER BY e.nombre
				`);
			}

			totalPoblacion = estados.reduce((sum, e) => sum + (e.poblacion_total || 0), 0);
			totalMunicipios = estados.reduce((sum, e) => sum + (e.num_municipios || 0), 0);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading states';
			console.error('Error loading estados:', e);
		} finally {
			loading = false;
		}
	});

	function formatNumber(n: number | null | undefined): string {
		if (n == null) return '-';
		return n.toLocaleString('es-MX');
	}
</script>

<svelte:head>
	<title>Estados de México | catalogmx</title>
	<meta name="description" content="Explora los 32 estados de Mexico: poblacion, municipios, zonas metropolitanas, codigos postales y mas." />
	<meta name="keywords" content="estados de mexico, municipios de mexico, poblacion por estado, INEGI, codigos postales mexico" />
	<meta name="robots" content="index, follow, max-image-preview:large" />
	<link rel="canonical" href={canonicalUrl} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="Estados de Mexico - catalogmx" />
	<meta property="og:description" content="Consulta los 32 estados de Mexico con poblacion y municipios." />
	<meta property="og:url" content={canonicalUrl} />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Estados de Mexico - catalogmx" />
	<meta name="twitter:description" content="Datos de estados y municipios de Mexico con fuente oficial." />
	{@html `<script type="application/ld+json">${JSON.stringify(mexicoJsonLd)}</script>`}
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<!-- Breadcrumb -->
	<nav class="text-sm mb-6">
		<ol class="flex items-center space-x-2">
			<li><a href="/" class="text-blue-600 hover:underline">Inicio</a></li>
			<li class="text-gray-400">/</li>
			<li class="text-gray-600">Mexico</li>
		</ol>
	</nav>

	<h1 class="text-3xl font-bold mb-2">Estados de Mexico</h1>
	<p class="text-gray-600 mb-6">
		Explora los 32 estados de la Republica Mexicana con datos de poblacion, municipios y zonas metropolitanas.
	</p>

	{#if loading}
		<div class="flex justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
			{error}
		</div>
	{:else}
		<!-- Summary Stats -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
			<div class="bg-blue-50 rounded-lg p-4">
				<div class="text-2xl font-bold text-blue-700">{estados.length}</div>
				<div class="text-sm text-blue-600">Estados</div>
			</div>
			<div class="bg-green-50 rounded-lg p-4">
				<div class="text-2xl font-bold text-green-700">{formatNumber(totalMunicipios)}</div>
				<div class="text-sm text-green-600">Municipios</div>
			</div>
			<div class="bg-purple-50 rounded-lg p-4">
				<div class="text-2xl font-bold text-purple-700">{formatNumber(totalPoblacion)}</div>
				<div class="text-sm text-purple-600">Poblacion Total</div>
			</div>
		</div>

		<!-- States Grid -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
			{#each estados as estado}
				<a
					href="{base}/mexico/{estado.nombre_slug}/"
					class="block bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-400 hover:shadow-md transition-all"
				>
					<div class="flex items-start justify-between">
						<div>
							<h2 class="font-semibold text-lg text-gray-900">{estado.nombre}</h2>
							<span class="text-xs text-gray-400 font-mono">{estado.abreviatura}</span>
						</div>
						<span class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded font-mono">
							{estado.cve_inegi}
						</span>
					</div>
					<div class="mt-3 grid grid-cols-2 gap-2 text-sm">
						<div>
							<span class="text-gray-500">Municipios:</span>
							<span class="font-medium">{estado.num_municipios}</span>
						</div>
						<div>
							<span class="text-gray-500">Poblacion:</span>
							<span class="font-medium">{formatNumber(estado.poblacion_total)}</span>
						</div>
					</div>
				</a>
			{/each}
		</div>

		<div class="mt-8 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/40 p-4 text-xs text-slate-600 dark:text-slate-300">
			<strong>Relacionados:</strong>
			<a href="{base}/catalogos/sepomex/codigos-postales" class="text-brand-600 dark:text-brand-400 hover:underline">
				codigos postales
			</a>,
			<a href="{base}/catalogos/inegi/localidades" class="text-brand-600 dark:text-brand-400 hover:underline">
				localidades INEGI
			</a>
			y
			<a href="{base}/catalogos/ift/ladas" class="text-brand-600 dark:text-brand-400 hover:underline">
				codigos LADA
			</a>.
		</div>
	{/if}
</div>
