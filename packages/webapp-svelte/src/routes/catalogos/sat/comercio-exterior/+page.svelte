<script lang="ts">
	import { base } from '$app/paths';
	import { ChevronRight, Globe, Ship, DollarSign, MapPin, FileText, AlertCircle, Package, Plane } from 'lucide-svelte';

	interface Catalog {
		title: string;
		description: string;
		href: string;
		icon: typeof FileText;
		count?: string;
	}

	const catalogs: Catalog[] = [
		{
			title: 'Incoterms',
			description: 'Términos internacionales de comercio (ICC)',
			href: `${base}/catalogos/sat/comercio-exterior/incoterms`,
			icon: Ship,
			count: '11 términos'
		},
		{
			title: 'Claves de Pedimento',
			description: 'Tipos de operaciones aduaneras',
			href: `${base}/catalogos/sat/comercio-exterior/claves-pedimento`,
			icon: FileText,
			count: '40+ claves'
		},
		{
			title: 'Estados USA/Canadá',
			description: 'Subdivisiones de Estados Unidos y Canadá',
			href: `${base}/catalogos/sat/comercio-exterior/estados-usa-canada`,
			icon: MapPin,
			count: '60+ estados'
		},
		{
			title: 'Monedas',
			description: 'Códigos ISO 4217 de monedas',
			href: `${base}/catalogos/sat/comercio-exterior/monedas`,
			icon: DollarSign,
			count: '150+ monedas'
		},
		{
			title: 'Países',
			description: 'Códigos ISO 3166 de países',
			href: `${base}/catalogos/sat/comercio-exterior/paises`,
			icon: Globe,
			count: '240+ países'
		},
		{
			title: 'Motivos de Traslado',
			description: 'Razones para traslado de mercancías',
			href: `${base}/catalogos/sat/comercio-exterior/motivos-traslado`,
			icon: Plane,
			count: '6 motivos'
		},
		{
			title: 'Registro de Identificación Tributaria',
			description: 'Tipos de identificación fiscal por país',
			href: `${base}/catalogos/sat/comercio-exterior/registro-ident-trib`,
			icon: AlertCircle,
			count: '16 tipos'
		},
		{
			title: 'Unidades de Aduana',
			description: 'Unidades de medida para comercio exterior',
			href: `${base}/catalogos/sat/comercio-exterior/unidades-aduana`,
			icon: Package,
			count: '20 unidades'
		}
	];
</script>

<svelte:head>
	<title>Catálogos SAT Comercio Exterior - catalogmx</title>
	<meta name="description" content="Catálogos oficiales del SAT para operaciones de comercio exterior e importación/exportación" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Comercio Exterior</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
				<Ship class="h-6 w-6 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogos SAT para Comercio Exterior
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogos oficiales del SAT para operaciones de importación, exportación y comercio internacional
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
					<div class="bg-brand-100 dark:bg-brand-900/30 p-3 rounded-lg group-hover:bg-brand-200 dark:group-hover:bg-brand-800/40 transition-colors">
						<svelte:component this={catalog.icon} class="h-5 w-5 text-brand-600 dark:text-brand-400" />
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
			Acerca de estos catálogos
		</h2>
		<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
			<p>
				<strong>Comercio Exterior:</strong> Estos catálogos son utilizados para operaciones de comercio internacional,
				incluyendo importaciones, exportaciones, y el Complemento de Comercio Exterior del CFDI versión 1.1.
			</p>
			<p>
				<strong>Fuente:</strong> Servicio de Administración Tributaria (SAT)
			</p>
			<p>
				<strong>Uso:</strong> Estos catálogos son fundamentales para la correcta emisión de
				CFDIs con Complemento de Comercio Exterior y el cumplimiento de obligaciones aduaneras en México.
			</p>
		</div>
	</div>
</div>