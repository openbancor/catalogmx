<script lang="ts">
	import { ChevronRight, Shield, Heart, Pill, Baby, Hospital, Briefcase } from 'lucide-svelte';

	const seguros = [
		{
			id: 'riesgo_trabajo',
			nombre: 'Riesgos de Trabajo',
			descripcion: 'Cubre accidentes y enfermedades de trabajo',
			icon: Briefcase,
			beneficios: [
				'Asistencia médica',
				'Hospitalización',
				'Medicamentos',
				'Indemnizaciones por incapacidad',
				'Pensión por invalidez o muerte'
			],
			cuota_patron: 'Variable (0.5% a 15% según riesgo)',
			cuota_trabajador: '0%'
		},
		{
			id: 'enfermedad_maternidad',
			nombre: 'Enfermedad y Maternidad',
			descripcion: 'Atención médica y prestaciones en dinero',
			icon: Hospital,
			beneficios: [
				'Asistencia médica',
				'Subsidios por incapacidad',
				'Prestaciones de maternidad',
				'Ayudas de lactancia'
			],
			cuota_patron: '20.4% (cuota fija) + 1.1% (excedente 3 UMAs) + 0.7% (dinero) + 1.05% (pensionados)',
			cuota_trabajador: '0.4% (excedente) + 0.25% (dinero) + 0.375% (pensionados)'
		},
		{
			id: 'invalidez_vida',
			nombre: 'Invalidez y Vida',
			descripcion: 'Pensiones por invalidez o muerte del asegurado',
			icon: Heart,
			beneficios: [
				'Pensión por invalidez',
				'Pensión de viudez',
				'Pensión de orfandad',
				'Ayuda asistencial'
			],
			cuota_patron: '1.75%',
			cuota_trabajador: '0.625%'
		},
		{
			id: 'retiro',
			nombre: 'Retiro',
			descripcion: 'Aportaciones para el retiro (cuenta individual)',
			icon: Pill,
			beneficios: [
				'Ahorro para el retiro',
				'Cuenta individual AFORE'
			],
			cuota_patron: '2%',
			cuota_trabajador: '0%'
		},
		{
			id: 'cesantia_vejez',
			nombre: 'Cesantía en Edad Avanzada y Vejez',
			descripcion: 'Pensión al cumplir 60 o 65 años',
			icon: Shield,
			beneficios: [
				'Pensión por cesantía (60 años)',
				'Pensión por vejez (65 años)',
				'Asistencia médica'
			],
			cuota_patron: '3.15%',
			cuota_trabajador: '1.125%'
		},
		{
			id: 'guarderias',
			nombre: 'Guarderías y Prestaciones Sociales',
			descripcion: 'Servicio de guardería y prestaciones sociales',
			icon: Baby,
			beneficios: [
				'Guarderías para hijos de trabajadoras',
				'Prestaciones sociales',
				'Centros vacacionales'
			],
			cuota_patron: '1%',
			cuota_trabajador: '0%'
		}
	];
</script>

<svelte:head>
	<title>Seguros del IMSS - catalogmx</title>
	<meta name="description" content="Ramos de aseguramiento del IMSS: Riesgos de Trabajo, Enfermedad y Maternidad, Invalidez y Vida, Retiro, Cesantía y Vejez, Guarderías" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/imss" class="hover:text-brand-500">IMSS</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Seguros</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
			Seguros del IMSS
		</h1>
		<p class="text-slate-600 dark:text-slate-300">
			Ramos de aseguramiento y prestaciones del Instituto Mexicano del Seguro Social
		</p>
	</div>

	<!-- Seguros Grid -->
	<div class="space-y-6">
		{#each seguros as seguro}
			<div class="card p-6">
				<div class="flex items-start gap-4 mb-4">
					<div class="bg-teal-100 dark:bg-teal-900/30 p-3 rounded-lg">
						<svelte:component this={seguro.icon} class="h-6 w-6 text-teal-600 dark:text-teal-400" />
					</div>
					<div class="flex-1">
						<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-1">
							{seguro.nombre}
						</h2>
						<p class="text-slate-600 dark:text-slate-300">
							{seguro.descripcion}
						</p>
					</div>
				</div>

				<div class="grid md:grid-cols-2 gap-6">
					<!-- Beneficios -->
					<div>
						<h3 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Beneficios</h3>
						<ul class="space-y-1">
							{#each seguro.beneficios as beneficio}
								<li class="text-sm text-slate-600 dark:text-slate-400 flex items-start gap-2">
									<span class="text-teal-500 mt-1">•</span>
									{beneficio}
								</li>
							{/each}
						</ul>
					</div>

					<!-- Cuotas -->
					<div class="space-y-3">
						<div>
							<h3 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Cuota Patrón</h3>
							<p class="text-sm text-slate-600 dark:text-slate-400 font-mono bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
								{seguro.cuota_patron}
							</p>
						</div>
						<div>
							<h3 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Cuota Trabajador</h3>
							<p class="text-sm text-slate-600 dark:text-slate-400 font-mono bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
								{seguro.cuota_trabajador}
							</p>
						</div>
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Nota -->
	<div class="mt-8 card p-6 bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800">
		<h3 class="font-semibold text-amber-800 dark:text-amber-200 mb-2">Nota importante</h3>
		<p class="text-sm text-amber-700 dark:text-amber-300">
			Las cuotas pueden variar según el salario base de cotización, la clase de riesgo del patrón,
			y las reformas de ley vigentes. Consulte siempre la información oficial del IMSS.
		</p>
	</div>
</div>
