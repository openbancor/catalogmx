<script lang="ts">
	import { Database, CheckCircle, Calculator, ArrowRight, FileText, MapPin, Building2, Mail } from 'lucide-svelte';

	const catalogs = [
		{
			source: 'SAT',
			description: 'Servicio de Administración Tributaria',
			color: 'bg-red-500',
			items: [
				{ name: 'Productos y Servicios', count: 52000, href: '/catalogos/sat/cfdi' },
				{ name: 'Claves de Unidad', count: 2800, href: '/catalogos/sat/unidades' },
				{ name: 'Regímenes Fiscales', count: 25, href: '/catalogos/sat/regimen' },
				{ name: 'Uso de CFDI', count: 22, href: '/catalogos/sat/uso-cfdi' },
			]
		},
		{
			source: 'INEGI',
			description: 'Instituto Nacional de Estadística',
			color: 'bg-blue-500',
			items: [
				{ name: 'Estados', count: 32, href: '/catalogos/inegi/estados' },
				{ name: 'Municipios', count: 2469, href: '/catalogos/inegi/municipios' },
				{ name: 'Localidades', count: 304000, href: '/catalogos/inegi/localidades' },
				{ name: 'SCIAN', count: 1800, href: '/catalogos/inegi/scian' },
			]
		},
		{
			source: 'Banxico',
			description: 'Banco de México',
			color: 'bg-green-600',
			items: [
				{ name: 'Instituciones Bancarias', count: 150, href: '/catalogos/banxico/bancos' },
				{ name: 'Códigos de Plaza', count: 900, href: '/catalogos/banxico/plazas' },
				{ name: 'Tipo de Cambio', count: 10000, href: '/catalogos/banxico/tipo-cambio' },
				{ name: 'UDIs', count: 12000, href: '/catalogos/banxico/udis' },
			]
		},
		{
			source: 'SEPOMEX',
			description: 'Servicio Postal Mexicano',
			color: 'bg-amber-500',
			items: [
				{ name: 'Códigos Postales', count: 145000, href: '/catalogos/sepomex/cp' },
			]
		},
	];

	const validators = [
		{ name: 'RFC', description: 'Registro Federal de Contribuyentes', icon: FileText, href: '/validadores/rfc' },
		{ name: 'CURP', description: 'Clave Única de Registro de Población', icon: FileText, href: '/validadores/curp' },
		{ name: 'CLABE', description: 'Clave Bancaria Estandarizada', icon: Building2, href: '/validadores/clabe' },
		{ name: 'NSS', description: 'Número de Seguro Social', icon: FileText, href: '/validadores/nss' },
	];

	const calculators = [
		{ name: 'ISR', description: 'Impuesto Sobre la Renta', href: '/calculadoras/isr' },
		{ name: 'IVA', description: 'Impuesto al Valor Agregado', href: '/calculadoras/iva' },
		{ name: 'Tipo de Cambio', description: 'USD/MXN histórico', href: '/calculadoras/tipo-cambio' },
		{ name: 'UDI', description: 'Conversión UDI ↔ MXN', href: '/calculadoras/udi' },
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
				<a href="/catalogos" class="btn btn-primary">
					<Database class="h-4 w-4" />
					Explorar catálogos
				</a>
				<a href="/api" class="btn btn-secondary">
					Ver documentación API
				</a>
			</div>
		</div>
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
						href="/catalogos/{catalog.source.toLowerCase()}"
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
							<svelte:component this={validator.icon} class="h-5 w-5" />
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

<!-- Calculators -->
<section class="py-12">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-8 flex items-center gap-2">
			<Calculator class="h-6 w-6 text-purple-500" />
			Calculadoras
		</h2>

		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
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
		</div>
	</div>
</section>
