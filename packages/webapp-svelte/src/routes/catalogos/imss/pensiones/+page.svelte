<script lang="ts">
	import { ChevronRight, TrendingUp, Calendar, DollarSign, Users } from 'lucide-svelte';

	const tabulador = {
		"2024": {
			pension_minima_garantizada: 2622.00,
			ayuda_asistencial: 1311.00,
			asignaciones_familiares: {
				esposa: 262.20,
				hijo_menor_16: 174.80,
				ascendiente: 174.80
			}
		},
		"2025": {
			pension_minima_garantizada: 2738.00,
			ayuda_asistencial: 1369.00,
			asignaciones_familiares: {
				esposa: 273.80,
				hijo_menor_16: 182.53,
				ascendiente: 182.53
			}
		},
		"2026": {
			pension_minima_garantizada: 2738.00,
			ayuda_asistencial: 1369.00,
			asignaciones_familiares: {
				esposa: 273.80,
				hijo_menor_16: 182.53,
				ascendiente: 182.53
			}
		}
	};

	function formatCurrency(value: number): string {
		return new Intl.NumberFormat('es-MX', {
			style: 'currency',
			currency: 'MXN'
		}).format(value);
	}
</script>

<svelte:head>
	<title>Tabulador de Pensiones IMSS - catalogmx</title>
	<meta name="description" content="Montos mínimos de pensiones del IMSS y asignaciones familiares 2024-2026" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/imss" class="hover:text-brand-500">IMSS</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Pensiones</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-teal-100 dark:bg-teal-900/30 p-3 rounded-lg">
				<TrendingUp class="h-6 w-6 text-teal-600 dark:text-teal-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Tabulador de Pensiones IMSS
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Montos mínimos de pensiones y asignaciones familiares por año
				</p>
			</div>
		</div>
	</div>

	<!-- Tabla por año -->
	<div class="grid gap-6 lg:grid-cols-3">
		{#each Object.entries(tabulador) as [year, data]}
			<div class="card p-6">
				<div class="flex items-center gap-3 mb-4">
					<Calendar class="h-5 w-5 text-teal-500" />
					<h2 class="text-xl font-bold text-slate-900 dark:text-white">{year}</h2>
				</div>

				<div class="space-y-4">
					<!-- Pensión mínima -->
					<div class="p-4 bg-teal-50 dark:bg-teal-900/20 rounded-lg">
						<div class="flex items-center gap-2 mb-2">
							<DollarSign class="h-4 w-4 text-teal-600 dark:text-teal-400" />
							<span class="text-sm font-medium text-teal-700 dark:text-teal-300">Pensión Mínima Garantizada</span>
						</div>
						<p class="text-2xl font-bold text-teal-600 dark:text-teal-400">
							{formatCurrency(data.pension_minima_garantizada)}
						</p>
						<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">mensual</p>
					</div>

					<!-- Ayuda asistencial -->
					<div class="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
						<span class="text-sm font-medium text-slate-700 dark:text-slate-300">Ayuda Asistencial</span>
						<p class="text-lg font-semibold text-slate-900 dark:text-white">
							{formatCurrency(data.ayuda_asistencial)}
						</p>
					</div>

					<!-- Asignaciones familiares -->
					<div class="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg">
						<div class="flex items-center gap-2 mb-3">
							<Users class="h-4 w-4 text-slate-500" />
							<span class="text-sm font-medium text-slate-700 dark:text-slate-300">Asignaciones Familiares</span>
						</div>
						<div class="space-y-2">
							<div class="flex justify-between">
								<span class="text-sm text-slate-600 dark:text-slate-400">Esposa</span>
								<span class="text-sm font-medium text-slate-900 dark:text-white">{formatCurrency(data.asignaciones_familiares.esposa)}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-sm text-slate-600 dark:text-slate-400">Hijo menor de 16</span>
								<span class="text-sm font-medium text-slate-900 dark:text-white">{formatCurrency(data.asignaciones_familiares.hijo_menor_16)}</span>
							</div>
							<div class="flex justify-between">
								<span class="text-sm text-slate-600 dark:text-slate-400">Ascendiente</span>
								<span class="text-sm font-medium text-slate-900 dark:text-white">{formatCurrency(data.asignaciones_familiares.ascendiente)}</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		{/each}
	</div>

	<!-- Nota -->
	<div class="mt-8 card p-6">
		<h3 class="font-semibold text-slate-900 dark:text-white mb-2">Sobre las pensiones mínimas</h3>
		<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
			<p>
				<strong>Pensión Mínima Garantizada:</strong> Monto mínimo mensual que recibe un pensionado
				que cumple con los requisitos de semanas cotizadas.
			</p>
			<p>
				<strong>Ayuda Asistencial:</strong> Prestación adicional para pensionados que requieren
				asistencia de terceros.
			</p>
			<p>
				<strong>Asignaciones Familiares:</strong> Montos adicionales por dependientes económicos
				del pensionado.
			</p>
		</div>
	</div>
</div>
