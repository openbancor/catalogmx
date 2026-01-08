<script lang="ts">
	import { ChevronRight, Calendar, Clock, AlertCircle, CheckCircle } from 'lucide-svelte';

	const requisitos = [
		{
			id: 'pension_cesantia_vejez',
			titulo: 'Pensión por Cesantía o Vejez (Ley 97)',
			semanas: 1250,
			descripcion: 'Semanas mínimas para obtener pensión bajo la Ley del Seguro Social de 1997',
			detalles: [
				'Aplica para trabajadores inscritos a partir del 1 de julio de 1997',
				'Cesantía: 60 años de edad',
				'Vejez: 65 años de edad',
				'Se incrementará gradualmente hasta 1,500 semanas'
			],
			tipo: 'ley97'
		},
		{
			id: 'pension_vejez_ley_73',
			titulo: 'Pensión por Vejez (Ley 73)',
			semanas: 500,
			descripcion: 'Semanas mínimas para pensión bajo la Ley del Seguro Social de 1973',
			detalles: [
				'Aplica para trabajadores inscritos antes del 1 de julio de 1997',
				'Requisito de edad: 60 años (cesantía) o 65 años (vejez)',
				'El monto de la pensión depende del salario promedio de los últimos 5 años',
				'Puede ser más favorable que Ley 97 en algunos casos'
			],
			tipo: 'ley73'
		},
		{
			id: 'modalidad_40',
			titulo: 'Modalidad 40 (Continuación Voluntaria)',
			semanas: 52,
			descripcion: 'Semanas previas requeridas para inscribirse en Modalidad 40',
			detalles: [
				'Permite seguir cotizando después de dejar de trabajar',
				'Útil para incrementar semanas y salario promedio',
				'El asegurado paga la cuota completa (patrón + trabajador)',
				'Puede inscribirse hasta 5 años después de la baja'
			],
			tipo: 'modalidad40'
		}
	];
</script>

<svelte:head>
	<title>Semanas Cotizadas IMSS - catalogmx</title>
	<meta name="description" content="Requisitos de semanas cotizadas para pensiones del IMSS: Ley 73, Ley 97 y Modalidad 40" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/imss" class="hover:text-brand-500">IMSS</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Semanas Cotizadas</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-teal-100 dark:bg-teal-900/30 p-3 rounded-lg">
				<Calendar class="h-6 w-6 text-teal-600 dark:text-teal-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Semanas Cotizadas
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Requisitos de semanas cotizadas para acceder a pensiones del IMSS
				</p>
			</div>
		</div>
	</div>

	<!-- Requisitos -->
	<div class="space-y-6">
		{#each requisitos as req}
			<div class="card p-6">
				<div class="flex items-start justify-between mb-4">
					<div class="flex items-start gap-4">
						<div class="bg-teal-100 dark:bg-teal-900/30 p-3 rounded-lg">
							<Clock class="h-6 w-6 text-teal-600 dark:text-teal-400" />
						</div>
						<div>
							<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-1">
								{req.titulo}
							</h2>
							<p class="text-slate-600 dark:text-slate-300">
								{req.descripcion}
							</p>
						</div>
					</div>
					<div class="text-right">
						<div class="text-3xl font-bold text-teal-600 dark:text-teal-400">
							{req.semanas.toLocaleString()}
						</div>
						<div class="text-sm text-slate-500 dark:text-slate-400">semanas</div>
					</div>
				</div>

				<div class="bg-slate-50 dark:bg-slate-800 rounded-lg p-4">
					<h3 class="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">Detalles importantes</h3>
					<ul class="space-y-2">
						{#each req.detalles as detalle}
							<li class="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
								<CheckCircle class="h-4 w-4 text-teal-500 mt-0.5 flex-shrink-0" />
								{detalle}
							</li>
						{/each}
					</ul>
				</div>
			</div>
		{/each}
	</div>

	<!-- Comparativa -->
	<div class="mt-8 card p-6">
		<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">
			Comparativa Ley 73 vs Ley 97
		</h2>
		<div class="overflow-x-auto">
			<table class="w-full text-sm">
				<thead>
					<tr class="border-b border-slate-200 dark:border-slate-700">
						<th class="text-left py-2 px-3 font-medium text-slate-700 dark:text-slate-300">Aspecto</th>
						<th class="text-left py-2 px-3 font-medium text-slate-700 dark:text-slate-300">Ley 73</th>
						<th class="text-left py-2 px-3 font-medium text-slate-700 dark:text-slate-300">Ley 97</th>
					</tr>
				</thead>
				<tbody class="text-slate-600 dark:text-slate-400">
					<tr class="border-b border-slate-100 dark:border-slate-800">
						<td class="py-2 px-3">Semanas mínimas</td>
						<td class="py-2 px-3 font-medium">500</td>
						<td class="py-2 px-3 font-medium">1,250</td>
					</tr>
					<tr class="border-b border-slate-100 dark:border-slate-800">
						<td class="py-2 px-3">Tipo de pensión</td>
						<td class="py-2 px-3">Renta vitalicia o retiro programado</td>
						<td class="py-2 px-3">Cuenta individual (AFORE)</td>
					</tr>
					<tr class="border-b border-slate-100 dark:border-slate-800">
						<td class="py-2 px-3">Cálculo de pensión</td>
						<td class="py-2 px-3">Salario promedio últimos 5 años</td>
						<td class="py-2 px-3">Saldo acumulado en AFORE</td>
					</tr>
					<tr>
						<td class="py-2 px-3">Aplica a</td>
						<td class="py-2 px-3">Inscritos antes del 1/Jul/1997</td>
						<td class="py-2 px-3">Inscritos a partir del 1/Jul/1997</td>
					</tr>
				</tbody>
			</table>
		</div>
	</div>

	<!-- Nota -->
	<div class="mt-6 flex items-start gap-3 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
		<AlertCircle class="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
		<div class="text-sm text-amber-700 dark:text-amber-300">
			<strong>Importante:</strong> Los requisitos de semanas cotizadas pueden cambiar según
			las reformas de ley. Consulte siempre la información oficial del IMSS o de su AFORE.
		</div>
	</div>
</div>
