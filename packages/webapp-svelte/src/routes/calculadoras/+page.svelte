<script lang="ts">
	import { base } from '$app/paths';
	import { Calculator, TrendingUp, Percent, DollarSign, Receipt, Shield, Users, CreditCard } from 'lucide-svelte';

	const calculators = [
		{
			id: 'isr',
			name: 'ISR',
			description: 'Impuesto Sobre la Renta',
			longDescription: 'Calcula el ISR con las tarifas oficiales 2024-2026 y subsidio al empleo',
			href: `${base}/calculadoras/isr`,
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
			longDescription: 'Calcula impuestos bajo el Régimen Simplificado de Confianza para personas físicas',
			href: `${base}/calculadoras/resico`,
			icon: TrendingUp,
			color: 'bg-blue-500',
			features: [
				'Tasas RESICO 1% a 2.5%',
				'Verificación de elegibilidad',
				'Límite $3.5M anuales',
				'Comparación mensual/anual'
			],
			status: 'available'
		},
		{
			id: 'iva',
			name: 'IVA',
			description: 'Impuesto al Valor Agregado',
			longDescription: 'Calcula IVA (16%), IVA retenido y desglose de impuestos',
			href: `${base}/calculadoras/iva`,
			icon: Percent,
			color: 'bg-green-500',
			features: [
				'IVA 16% general',
				'IVA 0% exportación',
				'IVA 8% zona fronteriza',
				'Retención 2/3 IVA'
			],
			status: 'available'
		},
		{
			id: 'ieps',
			name: 'IEPS',
			description: 'Impuesto Especial',
			longDescription: 'Calcula IEPS ad-valorem, cuotas fijas y tasas por categoría',
			href: `${base}/calculadoras/ieps`,
			icon: Percent,
			color: 'bg-amber-500',
			features: [
				'IEPS ad-valorem',
				'Cuotas fijas',
				'Bebidas alcohólicas',
				'Cigarros y tabacos'
			],
			status: 'available'
		},
		{
			id: 'imss',
			name: 'IMSS',
			description: 'Cuotas de Seguro Social',
			longDescription: 'Calcula cuotas IMSS obrero-patronales y Modalidad 40',
			href: `${base}/calculadoras/imss`,
			icon: Shield,
			color: 'bg-teal-500',
			features: [
				'Cuotas obrero-patronales',
				'Modalidad 40 (voluntaria)',
				'5 clases de riesgo de trabajo'
			],
			status: 'available'
		},
		{
			id: 'costo-trabajador',
			name: 'Costo Total Trabajador',
			description: 'Costo real para el empleador',
			longDescription: 'Calcula el costo total de un trabajador incluyendo prestaciones y cargas sociales',
			href: `${base}/calculadoras/costo-trabajador`,
			icon: Users,
			color: 'bg-orange-500',
			features: [
				'IMSS, Infonavit, ISN',
				'Aguinaldo, vacaciones, prima vacacional',
				'PTU estimado',
				'Reservas de liquidación'
			],
			status: 'available'
		},
		{
			id: 'informacion-clabe',
			name: 'Información CLABE',
			description: 'Decodifica banco y plaza',
			longDescription: 'Pega una CLABE y obtén información de banco, plaza, cuenta y validez del dígito de control',
			href: `${base}/calculadoras/informacion-clabe`,
			icon: CreditCard,
			color: 'bg-emerald-500',
			features: [
				'Identifica banco por código',
				'Decodifica plaza/sucursal',
				'Valida dígito de control',
				'Desglose completo de CLABE'
			],
			status: 'available'
		},
		{
			id: 'tipo-cambio',
			name: 'Dólar FIX',
			description: 'Conversión USD/MXN Banxico',
			longDescription: 'Convierte entre pesos mexicanos y dólares con histórico del tipo de cambio FIX de Banxico',
			href: `${base}/calculadoras/tipo-cambio`,
			icon: DollarSign,
			color: 'bg-purple-500',
			features: [
				'Datos históricos Banxico',
				'Conversión USD ↔ MXN',
				'Tipos de cambio diarios',
				'Comparación entre fechas'
			],
			status: 'available'
		},
		{
			id: 'udi',
			name: 'UDI',
			description: 'Unidades de Inversión',
			longDescription: 'Convierte entre UDIs y pesos mexicanos, calcula rendimientos indexados a inflación',
			href: `${base}/calculadoras/udi`,
			icon: TrendingUp,
			color: 'bg-blue-500',
			features: [
				'Conversión UDI ↔ MXN',
				'Valores históricos',
				'Cálculo de rendimientos',
				'Datos diarios Banxico'
			],
			status: 'available'
		},
		{
			id: 'tasas-interes',
			name: 'CETES/TIIE',
			description: 'Tasas de Interés',
			longDescription: 'Calcula intereses con histórico CETES 28 y TIIE 28 de Banxico, compara rendimientos',
			href: `${base}/calculadoras/tasas-interes`,
			icon: Percent,
			color: 'bg-emerald-500',
			features: [
				'CETES 28 días',
				'TIIE 28 días',
				'Comparación de tasas',
				'Cálculo de intereses'
			],
			status: 'available'
		}
	];
</script>

<svelte:head>
	<title>Calculadoras - catalogmx</title>
	<meta name="description" content="Calculadoras de México: ISR, RESICO, IVA, IMSS, costo laboral, UDI, dólar FIX Banxico e información de CLABE." />
	<meta name="keywords" content="calculadora ISR, calculadora IMSS, dólar FIX Banxico, información de CLABE, decodificar CLABE" />
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
				Herramientas para calcular impuestos, cuotas de seguridad social, costos laborales y más.
				Todas basadas en datos oficiales y tarifas actualizadas 2024-2026.
			</p>
		</div>
	</div>
</section>

<!-- Calculators Grid -->
<section class="py-12">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each calculators as calc}
				{@const Icon = calc.icon}
				<div class="card p-6 relative overflow-hidden flex flex-col">
					<!-- Status badge -->
					{#if calc.status === 'coming-soon'}
						<div class="absolute top-4 right-4">
							<span class="badge badge-warning">Próximamente</span>
						</div>
					{/if}

					<!-- Header -->
					<div class="flex items-start gap-4 mb-4">
						<div class="{calc.color} p-3 rounded-lg text-white flex-shrink-0">
							<Icon class="h-6 w-6" />
						</div>
						<div class="flex-1 min-w-0">
							<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-1 truncate">
								{calc.name}
							</h2>
							<p class="text-sm text-slate-600 dark:text-slate-400">
								{calc.description}
							</p>
						</div>
					</div>

					<!-- Description -->
					<p class="text-slate-700 dark:text-slate-300 mb-4 text-sm">
						{calc.longDescription}
					</p>

					<!-- Features -->
					<div class="mb-6 flex-1">
						<ul class="space-y-1.5">
							{#each calc.features as feature}
								<li class="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
									<span class="text-brand-500 mt-0.5 flex-shrink-0">✓</span>
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
				SAT, IMSS, INFONAVIT, Banxico e INEGI. Los cálculos son precisos y se actualizan regularmente.
			</p>
			<div class="flex flex-wrap justify-center gap-4 text-sm text-slate-500 dark:text-slate-400">
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-green-500"></span>
					Tarifas actualizadas 2026
				</span>
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-blue-500"></span>
					UMA y salarios mínimos vigentes
				</span>
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-purple-500"></span>
					LFT 2023 (vacaciones)
				</span>
			</div>
		</div>
	</div>
</section>
