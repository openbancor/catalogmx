<script lang="ts">
	import { ChevronRight, Mail, MapPin } from 'lucide-svelte';
</script>

<svelte:head>
	<title>SEPOMEX - Servicio Postal Mexicano - catalogmx</title>
	<meta name="description" content="Catálogos del Servicio Postal Mexicano (SEPOMEX) - Códigos postales de México." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">SEPOMEX</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
				<Mail class="h-6 w-6 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					SEPOMEX - Servicio Postal Mexicano
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogos oficiales del Servicio Postal Mexicano
				</p>
			</div>
		</div>
	</div>

	<!-- Catalog List -->
	<div class="grid gap-4 sm:grid-cols-1 md:grid-cols-2">
		<a
			href="/catalogos/sepomex/codigos-postales"
			class="card p-6 hover:shadow-lg transition-shadow"
		>
			<div class="flex items-start gap-4">
				<div class="bg-blue-100 dark:bg-blue-900/30 p-2 rounded">
					<MapPin class="h-5 w-5 text-blue-600 dark:text-blue-400" />
				</div>
				<div class="flex-1">
					<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-1">
						Códigos Postales
					</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Catálogo de códigos postales de México con información de asentamientos, municipios y estados
					</p>
				</div>
				<ChevronRight class="h-5 w-5 text-slate-400 flex-shrink-0" />
			</div>
		</a>
	</div>

	<!-- Info section -->
	<div class="mt-8 card p-6">
		<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
			Acerca de SEPOMEX
		</h2>
		<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
			<p>
				El <strong>Servicio Postal Mexicano (SEPOMEX)</strong> es el organismo público descentralizado encargado
				de prestar el servicio postal en México. Cuenta con el catálogo oficial de códigos postales del país.
			</p>
			<p>
				<strong>Código Postal:</strong> Identificador numérico de 5 dígitos que permite ubicar una localidad
				específica dentro del territorio nacional.
			</p>
			<p>
				<strong>Fuente:</strong> Servicio Postal Mexicano (SEPOMEX)
			</p>
		</div>
	</div>
</div>
