<script lang="ts">
	import { Database, CheckCircle, Calculator, ArrowRight, FileText, Building2, Sparkles, Shield, TrendingUp, DollarSign, Percent, Activity, Loader2 } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { base } from '$app/paths';
	import { queryOne } from '$lib/db';

	const SITE_URL = 'https://catalogmx.openbancor.com';
	const canonicalUrl = `${SITE_URL}/`;
	const packageLinks = [
		{ label: 'PyPI', href: 'https://pypi.org/project/catalogmx/' },
		{ label: 'npm', href: 'https://www.npmjs.com/package/catalogmx' },
		{ label: 'pub.dev', href: 'https://pub.dev/packages/catalogmx' }
	];
	const homeJsonLd = {
		'@context': 'https://schema.org',
		'@type': 'WebSite',
		name: 'catalogmx',
		url: SITE_URL,
		description: 'Catálogos oficiales de México y validadores de RFC, CURP, CLABE y NSS.',
		potentialAction: {
			'@type': 'SearchAction',
			target: `${SITE_URL}/catalogos`,
			'query-input': 'required name=query'
		}
	};

	// Live data state
	let udiData = $state<{ value: number; date: string } | null>(null);
	let exchangeData = $state<{ rate: number; date: string } | null>(null);
	let ratesData = $state<{ cetes28: number; tiie28: number; date: string } | null>(null);
	let loading = $state(true);

	interface UDIRecord { fecha: string; valor: number; }
	interface TipoCambioRecord { fecha: string; tipo_cambio: number; }
	interface TIIERecord { fecha: string; valor: number; }
	interface CETESRecord { fecha: string; valor: number; }

	// Load live data from SQLite on mount
	onMount(async () => {
		try {
			// Query SQLite for latest values
			const [latestUdi, latestTipoCambio, latestTiie, latestCetes] = await Promise.all([
				queryOne<UDIRecord>('SELECT fecha, valor FROM banxico_udis ORDER BY fecha DESC LIMIT 1'),
				queryOne<TipoCambioRecord>('SELECT fecha, tipo_cambio FROM banxico_tipo_cambio ORDER BY fecha DESC LIMIT 1'),
				queryOne<TIIERecord>('SELECT fecha, tasa as valor FROM banxico_tiie WHERE plazo = 28 ORDER BY fecha DESC LIMIT 1'),
				queryOne<CETESRecord>('SELECT fecha, tasa as valor FROM banxico_cetes WHERE plazo = 28 ORDER BY fecha DESC LIMIT 1')
			]);

			if (latestUdi) {
				udiData = { value: latestUdi.valor, date: latestUdi.fecha };
			}

			if (latestTipoCambio) {
				exchangeData = { rate: latestTipoCambio.tipo_cambio, date: latestTipoCambio.fecha };
			}

			if (latestTiie || latestCetes) {
				ratesData = {
					tiie28: latestTiie?.valor ?? 0,
					cetes28: latestCetes?.valor ?? 0,
					date: latestTiie?.fecha ?? latestCetes?.fecha ?? ''
				};
			}
		} catch (e) {
			console.error('Error loading live data from SQLite:', e);
		} finally {
			loading = false;
		}
	});

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr + 'T00:00:00');
		return date.toLocaleDateString('es-MX', { day: 'numeric', month: 'short', year: 'numeric' });
	}

	const catalogs = [
		{
			source: 'SAT',
			description: 'Servicio de Administración Tributaria',
			color: 'bg-red-500',
			items: [
				{ name: 'Productos y Servicios', count: 52000, href: `${base}/catalogos/sat/cfdi` },
				{ name: 'Regímenes Fiscales', count: 25, href: `${base}/catalogos/sat/regimen-fiscal` },
				{ name: 'Uso de CFDI', count: 22, href: `${base}/catalogos/sat/uso-cfdi` },
				{ name: 'Nómina', count: 50, href: `${base}/catalogos/sat/nomina` },
			]
		},
		{
			source: 'INEGI',
			description: 'Instituto Nacional de Estadística',
			color: 'bg-blue-500',
			items: [
				{ name: 'Estados', count: 32, href: `${base}/catalogos/inegi/estados` },
				{ name: 'Municipios', count: 2469, href: `${base}/catalogos/inegi/municipios` },
				{ name: 'SCIAN', count: 1800, href: `${base}/catalogos/inegi/scian` },
			]
		},
		{
			source: 'Banxico',
			description: 'Banco de México',
			color: 'bg-green-600',
			items: [
				{ name: 'Instituciones Bancarias', count: 150, href: `${base}/catalogos/banxico/bancos` },
				{ name: 'Códigos de Plaza', count: 900, href: `${base}/catalogos/banxico/plazas` },
				{ name: 'Monedas', count: 180, href: `${base}/catalogos/banxico/monedas` },
			]
		},
		{
			source: 'SEPOMEX',
			description: 'Servicio Postal Mexicano',
			color: 'bg-amber-500',
			items: [
				{ name: 'Códigos Postales', count: 145000, href: `${base}/catalogos/sepomex/codigos-postales` },
			]
		},
	];

	const validators = [
		{ name: 'RFC', description: 'Registro Federal de Contribuyentes', icon: FileText, href: `${base}/validadores/rfc` },
		{ name: 'CURP', description: 'Clave Única de Registro de Población', icon: FileText, href: `${base}/validadores/curp` },
		{ name: 'CLABE', description: 'Clave Bancaria Estandarizada', icon: Building2, href: `${base}/validadores/clabe` },
		{ name: 'NSS', description: 'Número de Seguro Social', icon: Shield, href: `${base}/validadores/nss` },
	];

	const generators = [
		{ name: 'RFC', description: 'Generar RFC con homoclave', icon: FileText, href: `${base}/generadores/rfc` },
		{ name: 'CURP', description: 'Generar CURP completa', icon: FileText, href: `${base}/generadores/curp` },
	];

	const calculators = [
		{ name: 'ISR', description: 'Impuesto Sobre la Renta', href: `${base}/calculadoras/isr` },
		{ name: 'RESICO', description: 'Régimen Simplificado', href: `${base}/calculadoras/resico` },
		{ name: 'IVA', description: 'Impuesto al Valor Agregado', href: `${base}/calculadoras/iva` },
		{ name: 'IEPS', description: 'Impuesto Especial', href: `${base}/calculadoras/ieps` },
		{ name: 'IMSS', description: 'Cuotas obrero-patronales', href: `${base}/calculadoras/imss` },
		{ name: 'Costo Trabajador', description: 'Costo total de nómina', href: `${base}/calculadoras/costo-trabajador` },
	];

	function formatCount(num: number): string {
		if (num >= 1000) {
			return (num / 1000).toFixed(num >= 10000 ? 0 : 1) + 'k';
		}
		return num.toString();
	}
</script>

<svelte:head>
	<title>catalogmx - Catálogos Oficiales de México</title>
	<meta name="description" content="Catálogos oficiales de México: SAT, INEGI, Banxico, SEPOMEX. Más de 470,000 registros. Validadores de RFC, CURP, CLABE. Calculadoras fiscales." />
	<meta name="robots" content="index, follow, max-image-preview:large" />
	<link rel="canonical" href={canonicalUrl} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="catalogmx - Catálogos Oficiales de México" />
	<meta property="og:description" content="Validadores de RFC, CURP, CLABE y NSS, más catálogos oficiales de SAT, INEGI, Banxico y SEPOMEX." />
	<meta property="og:url" content={canonicalUrl} />
	<meta property="og:site_name" content="catalogmx" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="catalogmx - Catálogos Oficiales de México" />
	<meta name="twitter:description" content="Validadores de RFC, CURP, CLABE y NSS con catálogos oficiales de México." />
	{@html `<script type="application/ld+json">${JSON.stringify(homeJsonLd)}</script>`}
</svelte:head>

<!-- Hero -->
<section class="py-12 md:py-20 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="max-w-3xl">
			<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">
				Catálogos Oficiales de México
			</h1>
			<p class="text-lg text-slate-600 dark:text-slate-300 mb-6">
				Más de <span class="font-semibold text-brand-500">470,000</span> registros de fuentes oficiales:
				SAT, INEGI, Banxico y SEPOMEX. Validadores, calculadoras y API para desarrolladores.
			</p>
			<div class="flex flex-wrap gap-3">
				<a href="{base}/catalogos" class="btn btn-primary">
					<Database class="h-4 w-4" />
					Explorar catálogos
				</a>
				<a href="{base}/validadores" class="btn btn-secondary">
					<CheckCircle class="h-4 w-4" />
					Validadores
				</a>
				<a href="{base}/validadores/clabe" class="btn btn-secondary">
					<Building2 class="h-4 w-4" />
					Validador CLABE
				</a>
				<a href="{base}/calculadoras" class="btn btn-secondary">
					<Calculator class="h-4 w-4" />
					Calculadoras
				</a>
			</div>
		</div>
	</div>
</section>

<!-- Live Data Section -->
<section class="py-8 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-6">
			<Activity class="h-5 w-5 text-green-600 dark:text-green-400" />
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white">Indicadores en Tiempo Real</h2>
			{#if !loading && (udiData || exchangeData || ratesData)}
				<span class="text-xs text-slate-500 dark:text-slate-400 ml-2">
					Actualización diaria desde Banxico
				</span>
			{/if}
		</div>

		{#if loading}
			<div class="flex items-center gap-3 text-slate-500 dark:text-slate-400">
				<Loader2 class="h-5 w-5 animate-spin" />
				<span>Cargando indicadores...</span>
			</div>
		{:else}
			<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
				<!-- UDI -->
				{#if udiData}
					<a href="{base}/catalogos/banxico/udis" class="card p-4 hover:border-green-300 dark:hover:border-green-700 transition-colors group">
						<div class="flex items-start justify-between">
							<div>
								<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">UDI</p>
								<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
									${udiData.value.toFixed(6)}
								</p>
								<p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
									{formatDate(udiData.date)}
								</p>
							</div>
							<div class="p-2 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 group-hover:bg-green-200 dark:group-hover:bg-green-900/50 transition-colors">
								<TrendingUp class="h-5 w-5" />
							</div>
						</div>
					</a>
				{/if}

				<!-- Exchange Rate -->
				{#if exchangeData}
					<a href="{base}/catalogos/banxico/tipo-cambio" class="card p-4 hover:border-blue-300 dark:hover:border-blue-700 transition-colors group">
						<div class="flex items-start justify-between">
							<div>
								<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Tipo de Cambio FIX</p>
								<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
									${exchangeData.rate.toFixed(4)}
								</p>
								<p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
									MXN/USD · {formatDate(exchangeData.date)}
								</p>
							</div>
							<div class="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 group-hover:bg-blue-200 dark:group-hover:bg-blue-900/50 transition-colors">
								<DollarSign class="h-5 w-5" />
							</div>
						</div>
					</a>
				{/if}

				<!-- CETES 28 -->
				{#if ratesData && ratesData.cetes28}
					<a href="{base}/catalogos/banxico/tasas" class="card p-4 hover:border-purple-300 dark:hover:border-purple-700 transition-colors group">
						<div class="flex items-start justify-between">
							<div>
								<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">CETES 28 días</p>
								<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
									{ratesData.cetes28.toFixed(2)}%
								</p>
								<p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
									Tasa anual · {formatDate(ratesData.date)}
								</p>
							</div>
							<div class="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 group-hover:bg-purple-200 dark:group-hover:bg-purple-900/50 transition-colors">
								<Percent class="h-5 w-5" />
							</div>
						</div>
					</a>
				{/if}

				<!-- TIIE 28 -->
				{#if ratesData && ratesData.tiie28}
					<a href="{base}/catalogos/banxico/tiie" class="card p-4 hover:border-amber-300 dark:hover:border-amber-700 transition-colors group">
						<div class="flex items-start justify-between">
							<div>
								<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">TIIE 28 días</p>
								<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
									{ratesData.tiie28.toFixed(4)}%
								</p>
								<p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
									Tasa anual · {formatDate(ratesData.date)}
								</p>
							</div>
							<div class="p-2 rounded-lg bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 group-hover:bg-amber-200 dark:group-hover:bg-amber-900/50 transition-colors">
								<Percent class="h-5 w-5" />
							</div>
						</div>
					</a>
				{/if}
			</div>
		{/if}
	</div>
</section>

<!-- Catalogs Grid -->
<section class="py-12">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-8 flex items-center gap-2">
			<Database class="h-6 w-6 text-brand-500" />
			Catálogos por Fuente
		</h2>

		<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
			{#each catalogs as catalog}
				<div class="card p-5">
					<div class="flex items-center gap-3 mb-4">
						<div class="{catalog.color} w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold text-sm">
							{catalog.source.slice(0, 2)}
						</div>
						<div>
							<h3 class="font-semibold text-slate-900 dark:text-white">{catalog.source}</h3>
							<p class="text-xs text-slate-500 dark:text-slate-400">{catalog.description}</p>
						</div>
					</div>

					<ul class="space-y-2">
						{#each catalog.items as item}
							<li>
								<a
									href={item.href}
									class="flex items-center justify-between py-1.5 px-2 -mx-2 rounded hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors group"
								>
									<span class="text-sm text-slate-700 dark:text-slate-300 group-hover:text-brand-500">
										{item.name}
									</span>
									<span class="text-xs text-slate-400 dark:text-slate-500 tabular-nums">
										{formatCount(item.count)}
									</span>
								</a>
							</li>
						{/each}
					</ul>

					<a
						href="{base}/catalogos/{catalog.source.toLowerCase()}"
						class="flex items-center gap-1 mt-4 text-sm text-brand-500 hover:text-brand-600 font-medium"
					>
						Ver todos
						<ArrowRight class="h-4 w-4" />
					</a>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- Validators -->
<section class="py-12 bg-slate-50 dark:bg-slate-800/50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-8 flex items-center gap-2">
			<CheckCircle class="h-6 w-6 text-green-500" />
			Validadores
		</h2>

		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
			{#each validators as validator}
				<a
					href={validator.href}
					class="card p-5 hover:border-brand-300 dark:hover:border-brand-700 transition-colors group"
				>
					<div class="flex items-start gap-3">
						<div class="p-2 rounded-lg bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400">
							<validator.icon class="h-5 w-5" />
						</div>
						<div>
							<h3 class="font-semibold text-slate-900 dark:text-white group-hover:text-brand-500">
								{validator.name}
							</h3>
							<p class="text-sm text-slate-500 dark:text-slate-400">
								{validator.description}
							</p>
						</div>
					</div>
				</a>
			{/each}
		</div>
	</div>
</section>

<!-- Generators -->
<section class="py-12">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-8 flex items-center gap-2">
			<Sparkles class="h-6 w-6 text-amber-500" />
			Generadores
		</h2>

		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
			{#each generators as gen}
				<a
					href={gen.href}
					class="card p-5 hover:border-brand-300 dark:hover:border-brand-700 transition-colors group"
				>
					<div class="flex items-start gap-3">
						<div class="p-2 rounded-lg bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400">
							<gen.icon class="h-5 w-5" />
						</div>
						<div>
							<h3 class="font-semibold text-slate-900 dark:text-white group-hover:text-brand-500">
								{gen.name}
							</h3>
							<p class="text-sm text-slate-500 dark:text-slate-400">
								{gen.description}
							</p>
						</div>
					</div>
				</a>
			{/each}
		</div>
	</div>
</section>

<!-- Calculators -->
<section class="py-12 bg-slate-50 dark:bg-slate-800/50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-8 flex items-center gap-2">
			<Calculator class="h-6 w-6 text-purple-500" />
			Calculadoras
		</h2>

		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each calculators as calc}
				<a
					href={calc.href}
					class="card p-5 hover:border-brand-300 dark:hover:border-brand-700 transition-colors group"
				>
					<h3 class="font-semibold text-slate-900 dark:text-white group-hover:text-brand-500 mb-1">
						{calc.name}
					</h3>
					<p class="text-sm text-slate-500 dark:text-slate-400">
						{calc.description}
					</p>
				</a>
			{/each}
		</div>
	</div>
</section>

<!-- Install CTA -->
<section class="py-12 bg-slate-900 dark:bg-slate-950">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="max-w-2xl">
			<h2 class="text-2xl font-bold text-white mb-4">
				Usa catalogmx en tu proyecto
			</h2>
			<p class="text-slate-300 mb-6">
				Librería disponible para Python, TypeScript y Dart. Sin dependencias externas, funciona offline.
			</p>

			<div class="space-y-3">
				<div class="bg-slate-800 rounded-lg p-4 font-mono text-sm">
					<span class="text-slate-400"># Python</span>
					<br />
					<span class="text-green-400">pip install</span> <span class="text-white">catalogmx</span>
				</div>
				<div class="bg-slate-800 rounded-lg p-4 font-mono text-sm">
					<span class="text-slate-400"># Node.js</span>
					<br />
					<span class="text-green-400">npm install</span> <span class="text-white">catalogmx</span>
				</div>
			</div>

			<div class="mt-6 flex flex-wrap gap-3">
				{#each packageLinks as pkg}
					<a
						href={pkg.href}
						target="_blank"
						rel="noopener noreferrer"
						class="inline-flex items-center rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:border-brand-400 hover:text-white transition-colors"
					>
						Ver paquete en {pkg.label}
					</a>
				{/each}
			</div>
		</div>
	</div>
</section>
