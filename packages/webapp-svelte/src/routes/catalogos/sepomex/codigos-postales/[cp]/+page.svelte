<script lang="ts">
	import { base } from '$app/paths';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { ChevronRight, MapPin, Search, AlertCircle } from 'lucide-svelte';

	type KnownPostalData = {
		asentamientoPrincipal: string;
		municipio: string;
		estado: string;
		ciudad: string;
		zona: string;
	};

	type PageData = {
		cp: string;
		knownPostalData: KnownPostalData | null;
	};

	type CodigoPostalRow = {
		cp: string;
		asentamiento: string;
		tipo_asentamiento: string;
		municipio: string;
		estado: string;
		ciudad: string;
		zona: string;
	};

	const SITE_URL = 'https://catalogmx.openbancor.com';
	let { data }: { data: PageData } = $props();

	let rows = $state<CodigoPostalRow[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let cpInput = $state('');

	function getCanonicalUrl(): string {
		return `${SITE_URL}/catalogos/sepomex/codigos-postales/${data.cp}`;
	}

	function getHeadline(): string {
		const known = data.knownPostalData;
		if (!known) return `Código Postal ${data.cp} en México`;
		return `Código Postal ${data.cp}: ${known.asentamientoPrincipal}, ${known.municipio}, ${known.estado}`;
	}

	function getDescription(): string {
		const known = data.knownPostalData;
		if (!known) {
			return `Consulta información oficial del código postal ${data.cp}: asentamientos, municipio, estado y zona con datos de SEPOMEX.`;
		}
		return `Consulta el código postal ${data.cp} de ${known.asentamientoPrincipal} (${known.municipio}, ${known.estado}): colonias, municipio, estado y zona en SEPOMEX.`;
	}

	function getJsonLd() {
		const known = data.knownPostalData;
		const mainEntity = known
			? {
				'@type': 'PostalAddress',
				postalCode: data.cp,
				addressLocality: known.municipio,
				addressRegion: known.estado,
				streetAddress: known.asentamientoPrincipal,
				addressCountry: 'MX'
			}
			: {
				'@type': 'PostalAddress',
				postalCode: data.cp,
				addressCountry: 'MX'
			};

		return {
			'@context': 'https://schema.org',
			'@type': 'WebPage',
			name: getHeadline(),
			description: getDescription(),
			url: getCanonicalUrl(),
			mainEntity
		};
	}

	async function loadPostalCodeData(): Promise<void> {
		const cp = data.cp;
		if (!/^\d{5}$/.test(cp)) {
			loading = false;
			error = 'El código postal debe tener 5 dígitos.';
			return;
		}

		try {
			loading = true;
			error = null;
			rows = await query<CodigoPostalRow>(
				`SELECT cp, asentamiento, tipo_asentamiento, municipio, estado, ciudad, zona
				 FROM codigos_postales
				 WHERE cp = ?
				 ORDER BY asentamiento`,
				[cp]
			);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading postal code detail:', e);
		} finally {
			loading = false;
		}
	}

	async function handleSubmit(event: SubmitEvent): Promise<void> {
		event.preventDefault();
		const target = cpInput.trim();
		if (!/^\d{5}$/.test(target)) {
			return;
		}
		await goto(`${base}/catalogos/sepomex/codigos-postales/${target}`);
	}

	onMount(() => {
		cpInput = data.cp;
		loadPostalCodeData();
	});
</script>

<svelte:head>
	<title>{getHeadline()} - catalogmx</title>
	<meta name="description" content={getDescription()} />
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
		<a href="{base}/catalogos/sepomex" class="hover:text-brand-500">SEPOMEX</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sepomex/codigos-postales" class="hover:text-brand-500">Códigos Postales</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">{data.cp}</span>
	</nav>

	<div class="mb-6">
		<h1 class="text-2xl md:text-3xl font-bold text-slate-900 dark:text-white mb-2">{getHeadline()}</h1>
		<p class="text-slate-600 dark:text-slate-300">
			Ficha del código postal con datos oficiales de SEPOMEX para búsquedas por colonia, municipio y estado.
		</p>
	</div>

	<form class="mb-8" onsubmit={handleSubmit}>
		<label for="cp" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
			Buscar otro código postal
		</label>
		<div class="flex gap-2">
			<input
				id="cp"
				type="text"
				maxlength="5"
				bind:value={cpInput}
				class="input font-mono"
				placeholder="03650"
			/>
			<button type="submit" class="btn btn-primary whitespace-nowrap">
				<Search class="h-4 w-4 mr-1" /> Buscar
			</button>
		</div>
	</form>

	{#if loading}
		<div class="card p-6 text-slate-600 dark:text-slate-300">Cargando información del código postal...</div>
	{:else if error}
		<div class="card p-6 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-200">
			<div class="flex items-start gap-2">
				<AlertCircle class="h-5 w-5 mt-0.5" />
				<p>{error}</p>
			</div>
		</div>
	{:else if rows.length === 0}
		<div class="card p-6">
			<p class="text-slate-700 dark:text-slate-200 font-medium mb-1">No encontramos registros para el CP {data.cp}.</p>
			<p class="text-slate-600 dark:text-slate-300 text-sm">
				Verifica los 5 dígitos o consulta el catálogo completo de códigos postales.
			</p>
		</div>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each rows as row}
				<div class="card p-4">
					<div class="flex items-center gap-2 mb-2">
						<MapPin class="h-4 w-4 text-brand-500" />
						<p class="font-semibold text-slate-900 dark:text-white">{row.asentamiento}</p>
					</div>
					<p class="text-sm text-slate-600 dark:text-slate-300">{row.tipo_asentamiento}</p>
					<p class="text-sm text-slate-600 dark:text-slate-300">{row.municipio}, {row.estado}</p>
					<p class="text-xs text-slate-500 dark:text-slate-400 mt-2">Zona: {row.zona || 'N/D'}</p>
				</div>
			{/each}
		</div>
	{/if}
</div>
