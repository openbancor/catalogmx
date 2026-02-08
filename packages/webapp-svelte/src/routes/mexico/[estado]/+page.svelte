<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { query, queryOne } from '$lib/db';
	import { base } from '$app/paths';
	const SITE_URL = 'https://catalogmx.openbancor.com';

	type Estado = {
		cve_inegi: string;
		nombre: string;
		nombre_slug: string;
		abreviatura: string;
		codigo_rfc: string;
	};

	type Municipio = {
		cve_inegi: string;
		cve_municipio: string;
		nombre: string;
		nombre_slug: string;
		poblacion_total: number;
		cabecera: string;
		zm_nombre?: string;
		zm_slug?: string;
	};

	let estado: Estado | null = null;
	let municipios: Municipio[] = [];
	let loading = true;
	let error = '';
	let totalPoblacion = 0;
	let searchTerm = '';

	$: estadoSlug = $page.params.estado ?? '';

	function slugToName(slug: string): string {
		return decodeURIComponent(slug)
			.replace(/-/g, ' ')
			.replace(/\b\w/g, (c) => c.toUpperCase());
	}

	function getEstadoName(): string {
		return estado?.nombre ?? slugToName(estadoSlug);
	}

	function getCanonicalUrl(): string {
		return `${SITE_URL}/mexico/${estadoSlug}`;
	}

	function getDescription(): string {
		return estado
			? `Municipios de ${estado.nombre}: ${municipios.length} municipios, poblacion ${formatNumber(totalPoblacion)}. Datos de INEGI y CONAPO.`
			: `Municipios y datos demograficos del estado ${getEstadoName()} en Mexico.`;
	}

	function getJsonLd() {
		return {
			'@context': 'https://schema.org',
			'@type': 'AdministrativeArea',
			name: getEstadoName(),
			url: getCanonicalUrl(),
			description: getDescription()
		};
	}

	$: filteredMunicipios = searchTerm
		? municipios.filter(m =>
				m.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
				(m.cabecera && m.cabecera.toLowerCase().includes(searchTerm.toLowerCase()))
		  )
		: municipios;

	onMount(async () => {
		try {
			// Get state info
			estado = await queryOne<Estado>(
				'SELECT * FROM geo_estados WHERE nombre_slug = ?',
				[estadoSlug]
			);

			if (!estado) {
				error = 'Estado no encontrado';
				loading = false;
				return;
			}

			// Get municipalities with ZM info
			try {
				municipios = await query<Municipio>(
					`
					SELECT
						m.cve_inegi,
						m.cve_municipio,
						m.nombre,
						m.nombre_slug,
						m.poblacion_total,
						m.cabecera,
						zm.nombre as zm_nombre,
						zm.nombre_slug as zm_slug
					FROM geo_municipios m
					LEFT JOIN geo_municipio_zm mzm ON m.cve_inegi = mzm.cve_inegi
					LEFT JOIN geo_zonas_metropolitanas zm ON mzm.zm_id = zm.zm_id
					WHERE m.cve_entidad = ?
					ORDER BY m.nombre
					`,
					[estado.cve_inegi]
				);
			} catch {
				// Fallback without ZM info
				municipios = await query<Municipio>(
					`
					SELECT
						cve_inegi,
						cve_municipio,
						nombre,
						nombre_slug,
						poblacion_total,
						cabecera
					FROM geo_municipios
					WHERE cve_entidad = ?
					ORDER BY nombre
					`,
					[estado.cve_inegi]
				);
			}

			totalPoblacion = municipios.reduce((sum, m) => sum + (m.poblacion_total || 0), 0);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading estado:', e);
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
	<title>{getEstadoName()} - Municipios de Mexico | catalogmx</title>
	<meta name="description" content={getDescription()} />
	<meta name="keywords" content={`municipios de ${getEstadoName()}, ${getEstadoName()} poblacion, estado ${getEstadoName()} mexico`} />
	<meta name="robots" content="index, follow, max-image-preview:large" />
	<link rel="canonical" href={getCanonicalUrl()} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content={`${getEstadoName()} - Municipios de Mexico | catalogmx`} />
	<meta property="og:description" content={getDescription()} />
	<meta property="og:url" content={getCanonicalUrl()} />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content={`${getEstadoName()} - catalogmx`} />
	<meta name="twitter:description" content={getDescription()} />
	{@html `<script type="application/ld+json">${JSON.stringify(getJsonLd())}</script>`}
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<!-- Breadcrumb -->
	<nav class="text-sm mb-6">
		<ol class="flex items-center space-x-2">
			<li><a href="/" class="text-blue-600 hover:underline">Inicio</a></li>
			<li class="text-gray-400">/</li>
			<li><a href="{base}/mexico/" class="text-blue-600 hover:underline">Mexico</a></li>
			<li class="text-gray-400">/</li>
			<li class="text-gray-600">{estado?.nombre || 'Estado'}</li>
		</ol>
	</nav>

	{#if loading}
		<div class="flex justify-center py-12">
			<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
		</div>
	{:else if error}
		<div class="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
			{error}
		</div>
	{:else if estado}
		<div class="flex items-start justify-between mb-6">
			<div>
				<h1 class="text-3xl font-bold">{estado.nombre}</h1>
				<div class="flex items-center gap-3 mt-1 text-sm text-gray-500">
					<span class="font-mono bg-gray-100 px-2 py-0.5 rounded">{estado.abreviatura}</span>
					<span>Clave INEGI: <span class="font-mono">{estado.cve_inegi}</span></span>
					<span>RFC: <span class="font-mono">{estado.codigo_rfc}</span></span>
				</div>
			</div>
		</div>

		<!-- Summary Stats -->
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
			<div class="bg-blue-50 rounded-lg p-4">
				<div class="text-2xl font-bold text-blue-700">{municipios.length}</div>
				<div class="text-sm text-blue-600">Municipios</div>
			</div>
			<div class="bg-green-50 rounded-lg p-4">
				<div class="text-2xl font-bold text-green-700">{formatNumber(totalPoblacion)}</div>
				<div class="text-sm text-green-600">Poblacion Total</div>
			</div>
			<div class="bg-purple-50 rounded-lg p-4">
				<div class="text-2xl font-bold text-purple-700">
					{municipios.filter(m => m.zm_nombre).length}
				</div>
				<div class="text-sm text-purple-600">En Zonas Metropolitanas</div>
			</div>
		</div>

		<!-- Search -->
		<div class="mb-6">
			<input
				type="text"
				bind:value={searchTerm}
				placeholder="Buscar municipio..."
				class="w-full md:w-96 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
			/>
		</div>

		<!-- Municipalities Table -->
		<div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
			<table class="min-w-full divide-y divide-gray-200">
				<thead class="bg-gray-50">
					<tr>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Clave</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Municipio</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cabecera</th>
						<th class="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Poblacion</th>
						<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Zona Metro</th>
					</tr>
				</thead>
				<tbody class="bg-white divide-y divide-gray-200">
					{#each filteredMunicipios as municipio}
						<tr class="hover:bg-gray-50">
							<td class="px-4 py-3 text-sm font-mono text-gray-500">{municipio.cve_inegi}</td>
							<td class="px-4 py-3">
								<a
									href="{base}/mexico/{estadoSlug}/{municipio.nombre_slug}/"
									class="text-blue-600 hover:underline font-medium"
								>
									{municipio.nombre}
								</a>
							</td>
							<td class="px-4 py-3 text-sm text-gray-600">{municipio.cabecera || '-'}</td>
							<td class="px-4 py-3 text-sm text-right font-mono">{formatNumber(municipio.poblacion_total)}</td>
							<td class="px-4 py-3 text-sm">
								{#if municipio.zm_nombre}
									<a
										href="{base}/catalogos/conapo/zonas-metropolitanas"
										class="text-purple-600 hover:underline"
									>
										{municipio.zm_nombre}
									</a>
								{:else}
									<span class="text-gray-400">-</span>
								{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		{#if filteredMunicipios.length === 0 && searchTerm}
			<div class="text-center py-8 text-gray-500">
				No se encontraron municipios que coincidan con "{searchTerm}"
			</div>
		{/if}
	{/if}
</div>
