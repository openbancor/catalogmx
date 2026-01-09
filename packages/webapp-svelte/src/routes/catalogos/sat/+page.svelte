<script lang="ts">
	import { base } from '$app/paths';
	import { ChevronRight, FileText, CreditCard, Building2, Receipt, Truck, Globe, Percent } from 'lucide-svelte';

	const catalogs = [
		{
			category: 'CFDI 4.0',
			items: [
				{ title: 'Productos y Servicios', description: '52,000+ claves de productos y servicios', href: `${base}/catalogos/sat/cfdi`, icon: FileText },
				{ title: 'Claves de Unidad', description: '2,800+ unidades de medida', href: `${base}/catalogos/sat/unidades`, icon: FileText },
				{ title: 'Regímenes Fiscales', description: '25 tipos de régimen', href: `${base}/catalogos/sat/regimen-fiscal`, icon: Building2 },
				{ title: 'Uso de CFDI', description: '22 claves de uso', href: `${base}/catalogos/sat/uso-cfdi`, icon: Receipt },
				{ title: 'Formas de Pago', description: '18 métodos de pago', href: `${base}/catalogos/sat/forma-pago`, icon: CreditCard },
				{ title: 'Métodos de Pago', description: 'PUE, PPD', href: `${base}/catalogos/sat/metodo-pago`, icon: CreditCard },
				{ title: 'Monedas', description: '180+ divisas', href: `${base}/catalogos/sat/moneda`, icon: Globe },
				{ title: 'Países', description: '250 países', href: `${base}/catalogos/sat/pais`, icon: Globe },
				{ title: 'Tipos de Comprobante', description: '6 tipos', href: `${base}/catalogos/sat/tipo-comprobante`, icon: FileText },
			]
		},
		{
			category: 'Nómina 1.2',
			items: [
				{ title: 'Catálogos de Nómina', description: 'Todos los catálogos', href: `${base}/catalogos/sat/nomina`, icon: FileText },
				{ title: 'Bancos para Nómina', description: '100+ instituciones', href: `${base}/catalogos/sat/nomina/banco`, icon: Building2 },
				{ title: 'Tipos de Contrato', description: '10 tipos', href: `${base}/catalogos/sat/nomina/tipo-contrato`, icon: FileText },
				{ title: 'Tipos de Régimen', description: '14 regímenes', href: `${base}/catalogos/sat/nomina/tipo-regimen`, icon: Building2 },
				{ title: 'Periodicidad', description: '10 periodos', href: `${base}/catalogos/sat/nomina/periodicidad`, icon: FileText },
				{ title: 'Tipos de Jornada', description: '6 tipos', href: `${base}/catalogos/sat/nomina/tipo-jornada`, icon: FileText },
				{ title: 'Riesgo de Puesto', description: '5 clases', href: `${base}/catalogos/sat/nomina/riesgo-puesto`, icon: FileText },
			]
		},
		{
			category: 'Impuestos',
			items: [
				{ title: 'Catálogos de Impuestos', description: 'ISR, IVA, IEPS', href: `${base}/catalogos/sat/impuestos`, icon: Percent },
				{ title: 'Tablas ISR', description: 'Tablas mensuales y anuales', href: `${base}/catalogos/sat/impuestos/isr-tablas`, icon: Percent },
				{ title: 'Tasas IVA', description: 'Tasas por tipo de operación', href: `${base}/catalogos/sat/impuestos/iva-tasas`, icon: Percent },
			]
		},
		{
			category: 'Comercio Exterior',
			items: [
				{ title: 'Catálogos CCE', description: 'Comercio exterior', href: `${base}/catalogos/sat/comercio-exterior`, icon: Globe },
				{ title: 'Incoterms', description: 'Términos internacionales', href: `${base}/catalogos/sat/comercio-exterior/incoterms`, icon: Globe },
				{ title: 'Claves de Pedimento', description: 'Tipos de operación', href: `${base}/catalogos/sat/comercio-exterior/claves-pedimento`, icon: FileText },
			]
		},
		{
			category: 'Carta Porte',
			items: [
				{ title: 'Catálogos Carta Porte', description: 'Complemento de traslado', href: `${base}/catalogos/sat/carta-porte`, icon: Truck },
				{ title: 'Aeropuertos', description: 'Códigos IATA', href: `${base}/catalogos/sat/carta-porte/aeropuertos`, icon: Truck },
				{ title: 'Carreteras', description: 'Tramos federales', href: `${base}/catalogos/sat/carta-porte/carreteras`, icon: Truck },
			]
		}
	];
</script>

<svelte:head>
	<title>Catálogos SAT - catalogmx</title>
	<meta name="description" content="Catálogos oficiales del SAT para CFDI 4.0, Nómina, Comercio Exterior y Carta Porte" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">SAT</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg">
				<FileText class="h-6 w-6 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogos del SAT
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogos oficiales del Servicio de Administración Tributaria para facturación electrónica
				</p>
			</div>
		</div>
	</div>

	<!-- Catalog sections -->
	<div class="space-y-10">
		{#each catalogs as section}
			<section>
				<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
					{section.category}
				</h2>
				<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
					{#each section.items as item}
						<a
							href={item.href}
							class="card p-4 hover:border-brand-300 dark:hover:border-brand-600 transition-colors group"
						>
							<div class="flex items-start gap-3">
								<div class="bg-red-100 dark:bg-red-900/30 p-2 rounded-lg group-hover:bg-red-200 dark:group-hover:bg-red-800/40 transition-colors">
									<svelte:component this={item.icon} class="h-4 w-4 text-red-600 dark:text-red-400" />
								</div>
								<div>
									<h3 class="font-medium text-slate-900 dark:text-white group-hover:text-brand-500">
										{item.title}
									</h3>
									<p class="text-sm text-slate-500 dark:text-slate-400 mt-1">
										{item.description}
									</p>
								</div>
							</div>
						</a>
					{/each}
				</div>
			</section>
		{/each}
	</div>

	<!-- Info -->
	<div class="mt-10 card p-6">
		<h2 class="font-semibold text-slate-900 dark:text-white mb-2">Sobre los catálogos del SAT</h2>
		<p class="text-sm text-slate-600 dark:text-slate-300">
			Estos catálogos son publicados por el Servicio de Administración Tributaria y son obligatorios
			para la emisión de Comprobantes Fiscales Digitales por Internet (CFDI). Se actualizan periódicamente
			según las disposiciones fiscales vigentes.
		</p>
	</div>
</div>