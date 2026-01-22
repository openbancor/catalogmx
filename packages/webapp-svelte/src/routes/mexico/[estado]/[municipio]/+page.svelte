<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { query, queryOne } from '$lib/db';

	type Municipio = {
		cve_inegi: string;
		cve_entidad: string;
		cve_municipio: string;
		nombre: string;
		nombre_slug: string;
		estado: string;
		estado_slug: string;
		poblacion_total: number;
		poblacion_masculina: number;
		poblacion_femenina: number;
		viviendas_habitadas: number;
		cabecera: string;
		zm_id?: string;
		zm_nombre?: string;
		zm_slug?: string;
		zm_tipo?: string;
		es_central?: number;
		es_exterior?: number;
	};

	type CodigoPostal = {
		cp: string;
		asentamiento: string;
		tipo_asentamiento: string;
	};

	let municipio: Municipio | null = null;
	let codigosPostales: CodigoPostal[] = [];
	let loading = true;
	let error = '';

	$: estadoSlug = $page.params.estado;
	$: municipioSlug = $page.params.municipio;

	onMount(async () => {
		try {
			// Get municipality with ZM info
			try {
				municipio = await queryOne<Municipio>(`
					SELECT
						m.*,
						zm.zm_id,
						zm.nombre as zm_nombre,
						zm.nombre_slug as zm_slug,
						zm.tipo as zm_tipo,
						mzm.es_central,
						mzm.es_exterior
					FROM geo_municipios m
					LEFT JOIN geo_municipio_zm mzm ON m.cve_inegi = mzm.cve_inegi
					LEFT JOIN geo_zonas_metropolitanas zm ON mzm.zm_id = zm.zm_id
					WHERE m.estado_slug = '${estadoSlug}' AND m.nombre_slug = '${municipioSlug}'
				`);
			} catch {
				// Fallback without ZM
				municipio = await queryOne<Municipio>(`
					SELECT *
					FROM geo_municipios
					WHERE estado_slug = '${estadoSlug}' AND nombre_slug = '${municipioSlug}'
				`);
			}

			if (!municipio) {
				error = 'Municipio no encontrado';
				loading = false;
				return;
			}

			// Get postal codes for this municipality (if available)
			try {
				codigosPostales = await query<CodigoPostal>(`
					SELECT DISTINCT cp, asentamiento, tipo_asentamiento
					FROM codigos_postales
					WHERE LOWER(municipio) = LOWER('${municipio.nombre}')
					AND LOWER(estado) LIKE '%${municipio.estado.toLowerCase().substring(0, 10)}%'
					ORDER BY cp, asentamiento
					LIMIT 50
				`);
			} catch {
				// Postal codes not available
				codigosPostales = [];
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading municipio:', e);
		} finally {
			loading = false;
		}
	});

	function formatNumber(n: number | null | undefined): string {
		if (n == null) return '-';
		return n.toLocaleString('es-MX');
	}

	function calcPercentage(part: number, total: number): string {
		if (!total) return '0';
		return ((part / total) * 100).toFixed(1);
	}
</script>

<svelte:head>
	{#if municipio}
		<title>{municipio.nombre}, {municipio.estado} - Municipios de Mexico | catalogmx</title>
		<meta name="description" content="Datos de {municipio.nombre}, {municipio.estado}: poblacion {formatNumber(municipio.poblacion_total)}, {codigosPostales.length > 0 ? codigosPostales.length + ' colonias' : ''}. Datos oficiales de INEGI." />
	{:else}
		<title>Municipio | catalogmx</title>
	{/if}
</svelte:head>

<div class="container mx-auto px-4 py-8">
	<!-- Breadcrumb -->
	<nav class="text-sm mb-6">
		<ol class="flex items-center space-x-2 flex-wrap">
			<li><a href="/" class="text-blue-600 hover:underline">Inicio</a></li>
			<li class="text-gray-400">/</li>
			<li><a href="/mexico/" class="text-blue-600 hover:underline">Mexico</a></li>
			<li class="text-gray-400">/</li>
			{#if municipio}
				<li><a href="/mexico/{municipio.estado_slug}/" class="text-blue-600 hover:underline">{municipio.estado}</a></li>
				<li class="text-gray-400">/</li>
				<li class="text-gray-600">{municipio.nombre}</li>
			{/if}
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
	{:else if municipio}
		<div class="mb-6">
			<h1 class="text-3xl font-bold">{municipio.nombre}</h1>
			<p class="text-lg text-gray-600 mt-1">{municipio.estado}</p>
			<div class="flex items-center gap-3 mt-2 text-sm text-gray-500">
				<span>Clave INEGI: <span class="font-mono bg-gray-100 px-2 py-0.5 rounded">{municipio.cve_inegi}</span></span>
				{#if municipio.cabecera}
					<span>Cabecera: <span class="font-medium">{municipio.cabecera}</span></span>
				{/if}
			</div>
		</div>

		<!-- Zona Metropolitana Badge -->
		{#if municipio.zm_nombre}
			<div class="mb-6 bg-purple-50 border border-purple-200 rounded-lg p-4">
				<div class="flex items-center gap-2">
					<span class="text-purple-700 font-medium">Zona Metropolitana:</span>
					<a href="/zonas-metropolitanas/{municipio.zm_slug}/" class="text-purple-600 hover:underline font-semibold">
						{municipio.zm_nombre}
					</a>
					<span class="text-sm text-purple-500">({municipio.zm_tipo})</span>
				</div>
				<div class="text-sm text-purple-600 mt-1">
					{#if municipio.es_central}
						<span class="bg-purple-200 px-2 py-0.5 rounded text-xs">Municipio Central</span>
					{:else if municipio.es_exterior}
						<span class="bg-purple-100 px-2 py-0.5 rounded text-xs">Municipio Exterior</span>
					{/if}
				</div>
			</div>
		{/if}

		<!-- Population Stats -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
			<div class="bg-blue-50 rounded-lg p-4">
				<div class="text-2xl font-bold text-blue-700">{formatNumber(municipio.poblacion_total)}</div>
				<div class="text-sm text-blue-600">Poblacion Total</div>
			</div>
			<div class="bg-cyan-50 rounded-lg p-4">
				<div class="text-2xl font-bold text-cyan-700">{formatNumber(municipio.poblacion_masculina)}</div>
				<div class="text-sm text-cyan-600">
					Hombres ({calcPercentage(municipio.poblacion_masculina, municipio.poblacion_total)}%)
				</div>
			</div>
			<div class="bg-pink-50 rounded-lg p-4">
				<div class="text-2xl font-bold text-pink-700">{formatNumber(municipio.poblacion_femenina)}</div>
				<div class="text-sm text-pink-600">
					Mujeres ({calcPercentage(municipio.poblacion_femenina, municipio.poblacion_total)}%)
				</div>
			</div>
			<div class="bg-green-50 rounded-lg p-4">
				<div class="text-2xl font-bold text-green-700">{formatNumber(municipio.viviendas_habitadas)}</div>
				<div class="text-sm text-green-600">Viviendas Habitadas</div>
			</div>
		</div>

		<!-- Postal Codes Section -->
		{#if codigosPostales.length > 0}
			<div class="mb-8">
				<h2 class="text-xl font-semibold mb-4">Codigos Postales y Colonias</h2>
				<div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
					<table class="min-w-full divide-y divide-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">CP</th>
								<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Colonia/Asentamiento</th>
								<th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200">
							{#each codigosPostales as cp}
								<tr class="hover:bg-gray-50">
									<td class="px-4 py-2 font-mono text-sm">
										<a href="/codigo-postal/{cp.cp}/" class="text-blue-600 hover:underline">{cp.cp}</a>
									</td>
									<td class="px-4 py-2 text-sm">{cp.asentamiento}</td>
									<td class="px-4 py-2 text-sm text-gray-500">{cp.tipo_asentamiento}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
				{#if codigosPostales.length >= 50}
					<p class="text-sm text-gray-500 mt-2">Mostrando primeros 50 resultados.</p>
				{/if}
			</div>
		{/if}

		<!-- Quick Links -->
		<div class="border-t pt-6">
			<h2 class="text-lg font-semibold mb-3">Enlaces Relacionados</h2>
			<div class="flex flex-wrap gap-2">
				<a
					href="/catalogos/sepomex/codigos-postales/?estado={encodeURIComponent(municipio.estado)}&municipio={encodeURIComponent(municipio.nombre)}"
					class="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-lg text-gray-700"
				>
					Ver todos los codigos postales
				</a>
				<a
					href="/catalogos/inegi/localidades/?estado={encodeURIComponent(municipio.estado)}&municipio={encodeURIComponent(municipio.nombre)}"
					class="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded-lg text-gray-700"
				>
					Ver localidades
				</a>
			</div>
		</div>
	{/if}
</div>
