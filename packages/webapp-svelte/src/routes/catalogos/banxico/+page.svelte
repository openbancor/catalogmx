<script lang="ts">
import { base } from '$app/paths';
import { ChevronRight, Building2, MapPin, Coins, ArrowRight, DollarSign, TrendingUp, Percent } from 'lucide-svelte';

const SITE_URL = 'https://catalogmx.openbancor.com';
const canonicalUrl = `${SITE_URL}/catalogos/banxico`;
const banxicoJsonLd = {
	'@context': 'https://schema.org',
	'@type': 'CollectionPage',
	name: 'Catálogos Banxico',
	url: canonicalUrl,
	description:
		'Colección de catálogos del Banco de México: bancos, plazas, UDI, inflación, TIIE, CETES y tipo de cambio.',
	mainEntity: {
		'@type': 'ItemList',
		name: 'Catálogos financieros Banxico'
	}
};

	const catalogs = [
		{
			id: 'bancos',
			name: 'Instituciones Bancarias',
			description: 'Bancos y casas de bolsa con clave SPEI',
			icon: Building2,
			count: '90+',
			available: true,
		},
		{
			id: 'plazas',
			name: 'Códigos de Plaza',
			description: 'Plazas bancarias para generación de CLABE',
			icon: MapPin,
			count: '900+',
			available: true,
		},
		{
			id: 'monedas',
			name: 'Monedas y Divisas',
			description: 'Catálogo de monedas y divisas internacionales',
			icon: Coins,
			count: '50+',
			available: true,
		},
		{
			id: 'tipo-cambio',
			name: 'Tipo de Cambio USD/MXN',
			description: 'Histórico del tipo de cambio FIX',
			icon: DollarSign,
			count: '500+',
			available: true,
		},
		{
			id: 'udis',
			name: 'Valor de la UDI',
			description: 'Unidades de Inversión históricas',
			icon: TrendingUp,
			count: '500+',
			available: true,
		},
		{
			id: 'tiie',
			name: 'TIIE / CETES',
			description: 'Tasas de interés de referencia',
			icon: Percent,
			count: '200+',
			available: true,
		},
		{
			id: 'inflacion',
			name: 'Inflación (INPC)',
			description: 'Índice Nacional de Precios al Consumidor',
			icon: TrendingUp,
			count: '180+',
			available: true,
		},
	];
</script>

<svelte:head>
	<title>Catálogos Banxico: UDI, inflación, TIIE, CETES y más - catalogmx</title>
	<meta name="description" content="Explora catálogos oficiales de Banxico: bancos, códigos de plaza, UDI, inflación, TIIE, CETES, tipo de cambio y monedas." />
	<meta name="robots" content="index, follow, max-image-preview:large" />
	<link rel="canonical" href={canonicalUrl} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="Catálogos Banxico: UDI, inflación, TIIE, CETES y más - catalogmx" />
	<meta property="og:description" content="Datos financieros oficiales de Banxico para validación, análisis y cálculo en México." />
	<meta property="og:url" content={canonicalUrl} />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Catálogos Banxico - catalogmx" />
	<meta name="twitter:description" content="UDI, inflación, TIIE, CETES, tipo de cambio y catálogos bancarios de Banxico." />
	{@html `<script type="application/ld+json">${JSON.stringify(banxicoJsonLd)}</script>`}
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Banxico</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<Building2 class="h-8 w-8 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogos del Banco de México
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Datos oficiales del sistema financiero mexicano y estadísticas económicas
				</p>
			</div>
		</div>
	</div>

	<!-- Catalogs grid -->
	<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
		{#each catalogs as catalog}
			{@const Icon = catalog.icon}
			{#if catalog.available}
				<a
					href="{base}/catalogos/banxico/{catalog.id}"
					class="card p-6 hover:shadow-lg transition-shadow group"
				>
					<div class="flex items-start justify-between mb-4">
						<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
							<Icon class="h-6 w-6 text-green-600 dark:text-green-400" />
						</div>
						<span class="text-sm font-medium text-green-600 dark:text-green-400">
							{catalog.count}
						</span>
					</div>
					<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2 group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors">
						{catalog.name}
					</h3>
					<p class="text-sm text-slate-600 dark:text-slate-300 mb-4">
						{catalog.description}
					</p>
					<div class="flex items-center text-sm text-green-600 dark:text-green-400 font-medium">
						Ver catálogo
						<ArrowRight class="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform" />
					</div>
				</a>
			{:else}
				<div class="card p-6 opacity-50">
					<div class="flex items-start justify-between mb-4">
						<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
							<Icon class="h-6 w-6 text-green-600 dark:text-green-400" />
						</div>
						<span class="text-sm font-medium text-slate-400">
							{catalog.count}
						</span>
					</div>
					<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">
						{catalog.name}
					</h3>
					<p class="text-sm text-slate-600 dark:text-slate-300 mb-4">
						{catalog.description}
					</p>
					<div class="flex items-center text-sm text-slate-400 font-medium">
						Próximamente
					</div>
				</div>
			{/if}
		{/each}
	</div>

	<!-- Info section -->
	<div class="mt-12 card p-6">
		<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
			Acerca de Banxico
		</h2>
		<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
			<p>
				<strong>Banco de México (Banxico)</strong> es el banco central del país, responsable de emitir
				la moneda nacional, regular el sistema financiero y mantener la estabilidad de precios.
			</p>
			<p>
				Los catálogos incluyen información sobre instituciones financieras participantes en el
				<strong>Sistema de Pagos Electrónicos Interbancarios (SPEI)</strong>, códigos de plaza
				para la generación de CLABEs, y estadísticas económicas fundamentales.
			</p>
			<p>
				<strong>Fuente:</strong> Banco de México (<a
					href="https://www.banxico.org.mx"
					target="_blank"
					rel="noopener noreferrer"
					class="text-green-600 dark:text-green-400 hover:underline"
				>www.banxico.org.mx</a>)
			</p>
		</div>
	</div>
</div>
