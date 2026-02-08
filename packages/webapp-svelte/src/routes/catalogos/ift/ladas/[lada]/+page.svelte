<script lang="ts">
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { ChevronRight, Phone, Search, AlertCircle, MapPin, RadioTower } from 'lucide-svelte';

	type KnownLadaData = {
		ciudad: string;
		estado: string;
		tipo: string;
		region: string;
	};

	type PageData = {
		lada: string;
		knownLadaData: KnownLadaData | null;
	};

	type LadaRow = {
		lada: string;
		ciudad: string;
		estado: string;
		tipo: string;
		region: string;
		cve_entidad: string;
		cve_municipio: string;
		estado_slug: string | null;
		municipio_slug: string | null;
	};

	const SITE_URL = 'https://catalogmx.openbancor.com';
	let { data }: { data: PageData } = $props();

	let rows = $state<LadaRow[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let ladaInput = $state('');

	function getCanonicalUrl(): string {
		return `${SITE_URL}/catalogos/ift/ladas/${data.lada}`;
	}

	function getHeadline(): string {
		const known = data.knownLadaData;
		if (!known) return `LADA ${data.lada}: clave de larga distancia en México`;
		return `LADA ${data.lada}: ${known.ciudad}, ${known.estado}`;
	}

	function getDescription(): string {
		const known = data.knownLadaData;
		if (!known) {
			return `Consulta información de la clave LADA ${data.lada}: ciudad, estado, región y tipo según datos del IFT.`;
		}
		return `La LADA ${data.lada} corresponde a ${known.ciudad}, ${known.estado}. Tipo ${known.tipo}, región ${known.region}. Datos oficiales del IFT.`;
	}

	function getJsonLd() {
		const first = rows[0];
		const place =
			first
				? {
						'@type': 'Place',
						name: first.ciudad,
						address: {
							'@type': 'PostalAddress',
							addressRegion: first.estado,
							addressCountry: 'MX'
						}
					}
				: undefined;

		return {
			'@context': 'https://schema.org',
			'@type': 'WebPage',
			name: getHeadline(),
			description: getDescription(),
			url: getCanonicalUrl(),
			mainEntity: place
		};
	}

	async function loadLadaData(): Promise<void> {
		const lada = data.lada;
		if (!/^\d{2,3}$/.test(lada)) {
			loading = false;
			error = 'La LADA debe tener 2 o 3 dígitos.';
			return;
		}

		try {
			loading = true;
			error = null;
			rows = await query<LadaRow>(
				`SELECT
					l.lada,
					l.ciudad,
					l.estado,
					l.tipo,
					l.region,
					l.cve_entidad,
					l.cve_municipio,
					e.nombre_slug as estado_slug,
					m.nombre_slug as municipio_slug
				FROM ift_codigos_lada l
				LEFT JOIN geo_estados e ON l.cve_entidad = e.cve_inegi
				LEFT JOIN geo_municipios m
					ON l.cve_entidad = m.cve_entidad
					AND l.cve_municipio = m.cve_municipio
				WHERE l.lada = ?
				ORDER BY l.ciudad`,
				[lada]
			);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
		} finally {
			loading = false;
		}
	}

	async function handleSubmit(event: SubmitEvent): Promise<void> {
		event.preventDefault();
		const target = ladaInput.trim();
		if (!/^\d{2,3}$/.test(target)) return;
		await goto(`${base}/catalogos/ift/ladas/${target}`);
	}

	onMount(() => {
		ladaInput = data.lada;
		loadLadaData();
	});
</script>

<svelte:head>
	<title>{getHeadline()} - catalogmx</title>
	<meta name="description" content={getDescription()} />
	<meta name="keywords" content={`lada ${data.lada}, clave lada ${data.lada}, prefijo telefonico mexico, ift`} />
	<meta name="robots" content="index, follow, max-image-preview:large" />
	<link rel="canonical" href={getCanonicalUrl()} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content={`${getHeadline()} - catalogmx`} />
	<meta property="og:description" content={getDescription()} />
	<meta property="og:url" content={getCanonicalUrl()} />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content={`${getHeadline()} - catalogmx`} />
	<meta name="twitter:description" content={getDescription()} />
	{@html `<script type="application/ld+json">${JSON.stringify(getJsonLd())}</script>`}
</svelte:head>

<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/ift" class="hover:text-brand-500">IFT</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/ift/ladas" class="hover:text-brand-500">LADAS</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">{data.lada}</span>
	</nav>

	<div class="mb-6">
		<h1 class="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-2">{getHeadline()}</h1>
		<p class="text-slate-600 dark:text-slate-300">
			Detalle de la clave LADA de México con ciudad, estado, región y tipo según catálogo oficial del IFT.
		</p>
	</div>

	<form class="mb-8" onsubmit={handleSubmit}>
		<label for="lada" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
			Buscar otra LADA
		</label>
		<div class="flex gap-2">
			<input
				id="lada"
				type="text"
				maxlength="3"
				bind:value={ladaInput}
				class="input font-mono"
				placeholder="55"
			/>
			<button type="submit" class="btn btn-primary whitespace-nowrap">
				<Search class="h-4 w-4 mr-1" /> Buscar
			</button>
		</div>
	</form>

	{#if loading}
		<div class="card p-6 text-slate-600 dark:text-slate-300">Cargando información de la LADA...</div>
	{:else if error}
		<div class="card p-6 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-200">
			<div class="flex items-start gap-2">
				<AlertCircle class="h-5 w-5 mt-0.5" />
				<p>{error}</p>
			</div>
		</div>
	{:else if rows.length === 0}
		<div class="card p-6">
			<p class="text-slate-700 dark:text-slate-200 font-medium mb-1">No encontramos registros para la LADA {data.lada}.</p>
			<p class="text-slate-600 dark:text-slate-300 text-sm">
				Verifica los dígitos o consulta el catálogo completo de LADAS.
			</p>
		</div>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each rows as row}
				<div class="card p-4">
					<div class="flex items-center gap-2 mb-2">
						<Phone class="h-4 w-4 text-brand-500" />
						<p class="font-semibold text-slate-900 dark:text-white font-mono">LADA {row.lada}</p>
					</div>
					<p class="text-sm text-slate-700 dark:text-slate-200 flex items-center gap-1">
						<MapPin class="h-3.5 w-3.5" /> {row.ciudad}, {row.estado}
					</p>
					<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Región: {row.region}</p>
					<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Tipo: {row.tipo}</p>
					{#if row.estado_slug && row.municipio_slug}
						<a
							href="{base}/mexico/{row.estado_slug}/{row.municipio_slug}/"
							class="text-xs text-brand-600 dark:text-brand-400 hover:underline mt-2 inline-flex items-center gap-1"
						>
							<RadioTower class="h-3 w-3" /> Ver municipio relacionado
						</a>
					{/if}
				</div>
			{/each}
		</div>
	{/if}

	<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
		<p class="text-xs text-slate-500 dark:text-slate-400">
			<strong>Nota:</strong> El código LADA identifica región geográfica de telefonía fija/móvil en México.
			Fuente de datos: Instituto Federal de Telecomunicaciones (IFT).
		</p>
	</div>
</div>
