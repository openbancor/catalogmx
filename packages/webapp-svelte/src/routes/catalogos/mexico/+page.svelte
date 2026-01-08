<script lang="ts">
	import { ChevronRight, Flag, DollarSign, Calendar, Car } from 'lucide-svelte';
</script>

<svelte:head>
	<title>México - Catálogos Nacionales - catalogmx</title>
	<meta name="description" content="Catálogos oficiales de México - UMA, salarios mínimos, hoy no circula y más." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">México</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<Flag class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogos Nacionales de México
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogos oficiales de instituciones gubernamentales mexicanas
				</p>
			</div>
		</div>
	</div>

	<!-- Catalog List -->
	<div class="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
		<a
			href="/catalogos/mexico/uma"
			class="card p-6 hover:shadow-lg transition-shadow"
		>
			<div class="flex items-start gap-4">
				<div class="bg-blue-100 dark:bg-blue-900/30 p-2 rounded">
					<DollarSign class="h-5 w-5 text-blue-600 dark:text-blue-400" />
				</div>
				<div class="flex-1">
					<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-1">
						UMA
					</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Unidad de Medida y Actualización - Valores históricos desde 2017
					</p>
				</div>
				<ChevronRight class="h-5 w-5 text-slate-400 flex-shrink-0" />
			</div>
		</a>

		<a
			href="/catalogos/mexico/salarios-minimos"
			class="card p-6 hover:shadow-lg transition-shadow"
		>
			<div class="flex items-start gap-4">
				<div class="bg-green-100 dark:bg-green-900/30 p-2 rounded">
					<DollarSign class="h-5 w-5 text-green-600 dark:text-green-400" />
				</div>
				<div class="flex-1">
					<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-1">
						Salarios Mínimos
					</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Salarios mínimos históricos por zona geográfica desde 2010
					</p>
				</div>
				<ChevronRight class="h-5 w-5 text-slate-400 flex-shrink-0" />
			</div>
		</a>

		<a
			href="/catalogos/mexico/hoy-no-circula"
			class="card p-6 hover:shadow-lg transition-shadow"
		>
			<div class="flex items-start gap-4">
				<div class="bg-orange-100 dark:bg-orange-900/30 p-2 rounded">
					<Car class="h-5 w-5 text-orange-600 dark:text-orange-400" />
				</div>
				<div class="flex-1">
					<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-1">
						Hoy No Circula
					</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Programa de restricción vehicular CDMX y Zona Metropolitana
					</p>
				</div>
				<ChevronRight class="h-5 w-5 text-slate-400 flex-shrink-0" />
			</div>
		</a>
	</div>

	<!-- Info section -->
	<div class="mt-8 card p-6">
		<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
			Acerca de estos catálogos
		</h2>
		<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
			<p>
				Los catálogos nacionales de México contienen información oficial publicada por instituciones
				gubernamentales federales y locales.
			</p>
			<p>
				<strong>UMA:</strong> Unidad de referencia económica que reemplazó al salario mínimo para cálculos
				de obligaciones fiscales, multas y créditos (INEGI).
			</p>
			<p>
				<strong>Salarios Mínimos:</strong> Remuneración mínima diaria que debe recibir un trabajador
				(CONASAMI - Comisión Nacional de los Salarios Mínimos).
			</p>
			<p>
				<strong>Hoy No Circula:</strong> Programa de restricción vehicular para mejorar la calidad del aire
				(CAMe - Comisión Ambiental de la Megalópolis).
			</p>
		</div>
	</div>
</div>
