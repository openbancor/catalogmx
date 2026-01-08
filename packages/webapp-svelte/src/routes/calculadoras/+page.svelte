<script lang="ts">
	import { Calculator, TrendingUp, Percent, DollarSign, Receipt } from 'lucide-svelte';

	const calculators = [
		{
			id: 'isr',
			name: 'ISR',
			description: 'Impuesto Sobre la Renta',
			longDescription: 'Calcula el ISR con las tarifas oficiales 2024-2026 y subsidio al empleo',
			href: '/calculadoras/isr',
			icon: Receipt,
			color: 'bg-red-500',
			features: [
				'Tarifas ISR 2024, 2025, 2026',
				'Subsidio al empleo',
				'Múltiples periodos (mensual, anual, quincenal, semanal)',
				'Cálculo de tasa efectiva'
			],
			status: 'available'
		},
		{
			id: 'resico',
			name: 'RESICO',
			description: 'Régimen Simplificado de Confianza',
			longDescription: 'Calcula impuestos bajo el Régimen Simplificado de Confianza',
			href: '/calculadoras/resico',
			icon: TrendingUp,
			color: 'bg-blue-500',
			features: [
				'Tarifas RESICO',
				'Cálculo simplificado',
				'Estimación anual',
				'Pagos provisionales'
			],
			status: 'coming-soon'
		},
		{
			id: 'iva',
			name: 'IVA',
			description: 'Impuesto al Valor Agregado',
			longDescription: 'Calcula IVA (16%), IVA retenido y IVA neto',
			href: '/calculadoras/iva',
			icon: Percent,
			color: 'bg-green-500',
			features: [
				'IVA 16% general',
				'IVA 0% exportación',
				'IVA retenido (2/3)',
				'Acreditamiento IVA'
			],
			status: 'coming-soon'
		},
		{
			id: 'tipo-cambio',
			name: 'Tipo de Cambio',
			description: 'Conversión USD/MXN histórica',
			longDescription: 'Convierte entre pesos mexicanos y dólares con tipos de cambio históricos',
			href: '/calculadoras/tipo-cambio',
			icon: DollarSign,
			color: 'bg-purple-500',
			features: [
				'Datos históricos Banxico',
				'Conversión USD ↔ MXN',
				'Tipos de cambio diarios',
				'Gráficas de tendencia'
			],
			status: 'coming-soon'
		}
	];

	function formatFeatures(features: string[]): string {
		return features.join(' • ');
	}
</script>

<svelte:head>
	<title>Calculadoras - catalogmx</title>
	<meta name="description" content="Calculadoras fiscales y financieras de México: ISR, RESICO, IVA, tipo de cambio. Basadas en datos oficiales." />
</svelte:head>

<!-- Hero -->
<section class="py-12 md:py-16 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="max-w-3xl">
			<div class="flex items-center gap-3 mb-4">
				<div class="p-3 rounded-lg bg-purple-100 dark:bg-purple-900/30">
					<Calculator class="h-8 w-8 text-purple-600 dark:text-purple-400" />
				</div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">
					Calculadoras
				</h1>
			</div>
			<p class="text-lg text-slate-600 dark:text-slate-300">
				Herramientas para calcular impuestos, conversiones de moneda y más.
				Todas basadas en datos oficiales y tarifas actualizadas.
			</p>
		</div>
	</div>
</section>

<!-- Calculators Grid -->
<section class="py-12">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 md:grid-cols-2">
			{#each calculators as calc}
				{@const Icon = calc.icon}
				<div class="card p-6 relative overflow-hidden">
					<!-- Status badge -->
					{#if calc.status === 'coming-soon'}
						<div class="absolute top-4 right-4">
							<span class="badge badge-warning">Próximamente</span>
						</div>
					{/if}

					<!-- Header -->
					<div class="flex items-start gap-4 mb-4">
						<div class="{calc.color} p-3 rounded-lg text-white">
							<Icon class="h-6 w-6" />
						</div>
						<div class="flex-1">
							<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-1">
								{calc.name}
							</h2>
							<p class="text-sm text-slate-600 dark:text-slate-400">
								{calc.description}
							</p>
						</div>
					</div>

					<!-- Description -->
					<p class="text-slate-700 dark:text-slate-300 mb-4">
						{calc.longDescription}
					</p>

					<!-- Features -->
					<div class="mb-6">
						<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
							Características:
						</h3>
						<ul class="space-y-1.5">
							{#each calc.features as feature}
								<li class="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
									<span class="text-brand-500 mt-0.5">✓</span>
									<span>{feature}</span>
								</li>
							{/each}
						</ul>
					</div>

					<!-- Action button -->
					{#if calc.status === 'available'}
						<a href={calc.href} class="btn btn-primary w-full">
							<Calculator class="h-4 w-4" />
							Abrir calculadora
						</a>
					{:else}
						<button class="btn btn-secondary w-full" disabled>
							Próximamente
						</button>
					{/if}
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- Info section -->
<section class="py-12 bg-slate-50 dark:bg-slate-800/50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="max-w-3xl mx-auto text-center">
			<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-4">
				Datos oficiales y actualizados
			</h2>
			<p class="text-slate-600 dark:text-slate-300 mb-6">
				Todas las calculadoras utilizan tarifas y datos oficiales de fuentes gubernamentales:
				SAT, Banxico, INEGI y SEPOMEX. Los cálculos son precisos y se actualizan regularmente.
			</p>
			<div class="flex flex-wrap justify-center gap-4 text-sm text-slate-500 dark:text-slate-400">
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-green-500"></span>
					Tarifas actualizadas 2026
				</span>
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-blue-500"></span>
					Datos oficiales verificados
				</span>
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-purple-500"></span>
					Cálculos precisos
				</span>
			</div>
		</div>
	</div>
</section>
