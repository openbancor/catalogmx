<script lang="ts">
	import { base } from '$app/paths';
	import { ChevronRight, FileText, Package, Ruler, CreditCard, Receipt, Globe, Building2, FileCode } from 'lucide-svelte';

	const catalogs = [
		{
			title: 'Productos y Servicios',
			description: '52,000+ claves de productos y servicios (c_ClaveProdServ)',
			href: `${base}/catalogos/sat/cfdi/productos-servicios`,
			icon: Package,
			count: '52,514'
		},
		{
			title: 'Claves de Unidad',
			description: '2,800+ unidades de medida (c_ClaveUnidad)',
			href: `${base}/catalogos/sat/unidades`,
			icon: Ruler,
			count: '2,856'
		},
		{
			title: 'Regimenes Fiscales',
			description: '25 tipos de regimen fiscal (c_RegimenFiscal)',
			href: `${base}/catalogos/sat/regimen-fiscal`,
			icon: Building2,
			count: '25'
		},
		{
			title: 'Uso de CFDI',
			description: '22 claves de uso de comprobante (c_UsoCFDI)',
			href: `${base}/catalogos/sat/uso-cfdi`,
			icon: Receipt,
			count: '22'
		},
		{
			title: 'Formas de Pago',
			description: '18 metodos de pago disponibles (c_FormaPago)',
			href: `${base}/catalogos/sat/forma-pago`,
			icon: CreditCard,
			count: '18'
		},
		{
			title: 'Metodos de Pago',
			description: 'PUE y PPD (c_MetodoPago)',
			href: `${base}/catalogos/sat/metodo-pago`,
			icon: CreditCard,
			count: '2'
		},
		{
			title: 'Monedas',
			description: '180+ divisas internacionales (c_Moneda)',
			href: `${base}/catalogos/sat/moneda`,
			icon: Globe,
			count: '180+'
		},
		{
			title: 'Paises',
			description: '250 paises (c_Pais)',
			href: `${base}/catalogos/sat/pais`,
			icon: Globe,
			count: '250'
		},
		{
			title: 'Tipos de Comprobante',
			description: '6 tipos de comprobante (c_TipoDeComprobante)',
			href: `${base}/catalogos/sat/tipo-comprobante`,
			icon: FileCode,
			count: '6'
		},
		{
			title: 'Impuesto',
			description: 'Tipos de impuesto (c_Impuesto)',
			href: `${base}/catalogos/sat/impuesto`,
			icon: FileText,
			count: '3'
		},
	];
</script>

<svelte:head>
	<title>Catalogos CFDI 4.0 - catalogmx</title>
	<meta name="description" content="Catalogos oficiales del SAT para CFDI 4.0: productos, unidades, regimenes fiscales, formas de pago y mas." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">CFDI 4.0</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg">
				<FileText class="h-6 w-6 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catalogos CFDI 4.0
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catalogos oficiales del SAT para la emision de Comprobantes Fiscales Digitales por Internet version 4.0
				</p>
			</div>
		</div>
	</div>

	<!-- Catalog grid -->
	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 mb-8">
		{#each catalogs as catalog}
			<a
				href={catalog.href}
				class="card p-5 hover:border-brand-300 dark:hover:border-brand-600 transition-colors group"
			>
				<div class="flex items-start gap-4">
					<div class="bg-red-100 dark:bg-red-900/30 p-2.5 rounded-lg group-hover:bg-red-200 dark:group-hover:bg-red-800/40 transition-colors">
						<svelte:component this={catalog.icon} class="h-5 w-5 text-red-600 dark:text-red-400" />
					</div>
					<div class="flex-1 min-w-0">
						<div class="flex items-start justify-between gap-2">
							<h3 class="font-semibold text-slate-900 dark:text-white group-hover:text-brand-500 transition-colors">
								{catalog.title}
							</h3>
							<span class="text-xs font-medium text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
								{catalog.count}
							</span>
						</div>
						<p class="text-sm text-slate-500 dark:text-slate-400 mt-1.5">
							{catalog.description}
						</p>
					</div>
				</div>
			</a>
		{/each}
	</div>

	<!-- Info box -->
	<div class="card p-6">
		<h2 class="font-semibold text-slate-900 dark:text-white mb-2">Sobre CFDI 4.0</h2>
		<p class="text-sm text-slate-600 dark:text-slate-300 mb-4">
			La version 4.0 del CFDI es obligatoria desde el 1 de enero de 2022. Incluye cambios importantes
			como la obligatoriedad del nombre y domicilio fiscal del receptor, el regimen fiscal y el codigo postal.
		</p>
		<div class="flex flex-wrap gap-2">
			<span class="px-2.5 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">
				Vigente
			</span>
			<span class="px-2.5 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
				Version 4.0
			</span>
			<span class="px-2.5 py-1 text-xs font-medium rounded-full bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300">
				Obligatorio desde 01/01/2022
			</span>
		</div>
	</div>
</div>
