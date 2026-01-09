<script lang="ts">
	import { base } from '$app/paths';
	import { ChevronRight, Calculator, FileText, TrendingUp, Percent, Receipt } from 'lucide-svelte';

	const catalogs = [
		{
			id: 'isr-tablas',
			title: 'Tablas de ISR',
			description: 'Tablas históricas del Impuesto Sobre la Renta (mensuales)',
			icon: Calculator,
			count: '24 años (2002-2025)',
			color: 'blue'
		},
		{
			id: 'iva-tasas',
			title: 'Tasas de IVA',
			description: 'Tasas históricas del Impuesto al Valor Agregado',
			icon: Percent,
			count: '7 tasas históricas',
			color: 'green'
		},
		{
			id: 'ieps-tasas',
			title: 'Tasas de IEPS',
			description: 'Impuesto Especial sobre Producción y Servicios',
			icon: TrendingUp,
			count: '7 categorías',
			color: 'orange'
		},
		{
			id: 'retenciones',
			title: 'Retenciones',
			description: 'Tasas de retención de ISR e IVA',
			icon: Receipt,
			count: 'ISR + IVA',
			color: 'purple'
		},
		{
			id: 'impuestos-locales',
			title: 'Impuestos Locales',
			description: 'Impuestos estatales y municipales',
			icon: FileText,
			count: '32 estados',
			color: 'red'
		}
	];

	const colorClasses = {
		blue: {
			bg: 'bg-blue-100 dark:bg-blue-900/30',
			icon: 'text-blue-600 dark:text-blue-400',
			badge: 'bg-blue-50 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300'
		},
		green: {
			bg: 'bg-green-100 dark:bg-green-900/30',
			icon: 'text-green-600 dark:text-green-400',
			badge: 'bg-green-50 dark:bg-green-900/50 text-green-700 dark:text-green-300'
		},
		orange: {
			bg: 'bg-orange-100 dark:bg-orange-900/30',
			icon: 'text-orange-600 dark:text-orange-400',
			badge: 'bg-orange-50 dark:bg-orange-900/50 text-orange-700 dark:text-orange-300'
		},
		purple: {
			bg: 'bg-purple-100 dark:bg-purple-900/30',
			icon: 'text-purple-600 dark:text-purple-400',
			badge: 'bg-purple-50 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300'
		},
		red: {
			bg: 'bg-red-100 dark:bg-red-900/30',
			icon: 'text-red-600 dark:text-red-400',
			badge: 'bg-red-50 dark:bg-red-900/50 text-red-700 dark:text-red-300'
		}
	};
</script>

<svelte:head>
	<title>Impuestos SAT - catalogmx</title>
	<meta name="description" content="Catálogos de impuestos del SAT: ISR, IVA, IEPS, retenciones e impuestos locales." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Impuestos</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg">
				<Calculator class="h-6 w-6 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogos de Impuestos SAT
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Tablas y tasas de impuestos federales y locales en México
				</p>
			</div>
		</div>
	</div>

	<!-- Catalogs Grid -->
	<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
		{#each catalogs as catalog}
			<a
				href="{base}/catalogos/sat/impuestos/{catalog.id}"
				class="card p-6 hover:shadow-lg transition-shadow group"
			>
				<div class="flex items-start gap-4 mb-4">
					<div class="{colorClasses[catalog.color].bg} p-3 rounded-lg">
						<svelte:component this={catalog.icon} class="h-6 w-6 {colorClasses[catalog.color].icon}" />
					</div>
					<div class="flex-1">
						<h3 class="font-semibold text-slate-900 dark:text-white mb-1 group-hover:text-brand-500 transition-colors">
							{catalog.title}
						</h3>
						<p class="text-sm text-slate-600 dark:text-slate-400">
							{catalog.description}
						</p>
					</div>
				</div>
				<div class="{colorClasses[catalog.color].badge} px-3 py-1 rounded-full text-sm font-medium inline-block">
					{catalog.count}
				</div>
			</a>
		{/each}
	</div>

	<!-- Info Section -->
	<div class="mt-8 card p-6">
		<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
			Acerca de los catálogos de impuestos
		</h2>
		<div class="space-y-3 text-sm text-slate-600 dark:text-slate-300">
			<p>
				<strong>ISR (Impuesto Sobre la Renta):</strong> Tablas de tarifas mensuales desde 2002,
				con tramos de ingresos, cuotas fijas y tasas sobre el excedente. Incluye el subsidio al empleo.
			</p>
			<p>
				<strong>IVA (Impuesto al Valor Agregado):</strong> Tasas históricas desde 1983,
				incluyendo tasa general (16%), fronteriza (8%), tasa cero y exenciones.
			</p>
			<p>
				<strong>IEPS (Impuesto Especial sobre Producción y Servicios):</strong> Tasas aplicables
				a bebidas alcohólicas, tabacos, combustibles, bebidas azucaradas y alimentos de alta densidad calórica.
			</p>
			<p>
				<strong>Retenciones:</strong> Tasas de retención de ISR e IVA por conceptos como
				honorarios (10%), arrendamiento (10%), servicios profesionales (2/3 del IVA), y más.
			</p>
			<p>
				<strong>Impuestos Locales:</strong> Impuestos estatales como nómina (2-3%),
				hospedaje (2-5%), tenencia vehicular y otros tributos municipales.
			</p>
		</div>
	</div>
</div>