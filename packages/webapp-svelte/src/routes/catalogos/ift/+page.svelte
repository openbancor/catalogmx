<script lang="ts">
	import { base } from '$app/paths';
	import { ChevronRight, Radio, Phone } from 'lucide-svelte';
</script>

<svelte:head>
	<title>IFT - Instituto Federal de Telecomunicaciones - catalogmx</title>
	<meta name="description" content="Catálogos del Instituto Federal de Telecomunicaciones (IFT) - Operadores móviles de México." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">IFT</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-lg">
				<Radio class="h-6 w-6 text-purple-600 dark:text-purple-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					IFT - Instituto Federal de Telecomunicaciones
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogos oficiales del Instituto Federal de Telecomunicaciones
				</p>
			</div>
		</div>
	</div>

	<!-- Catalog List -->
	<div class="grid gap-4 sm:grid-cols-1 md:grid-cols-2">
		<a
			href="{base}/catalogos/ift/operadores"
			class="card p-6 hover:shadow-lg transition-shadow"
		>
			<div class="flex items-start gap-4">
				<div class="bg-purple-100 dark:bg-purple-900/30 p-2 rounded">
					<Phone class="h-5 w-5 text-purple-600 dark:text-purple-400" />
				</div>
				<div class="flex-1">
					<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-1">
						Operadores Móviles
					</h3>
					<p class="text-sm text-slate-600 dark:text-slate-400">
						Catálogo de operadores de telefonía móvil en México (OMR y OMV)
					</p>
				</div>
				<ChevronRight class="h-5 w-5 text-slate-400 flex-shrink-0" />
			</div>
		</a>
	</div>

	<!-- Info section -->
	<div class="mt-8 card p-6">
		<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
			Acerca del IFT
		</h2>
		<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
			<p>
				El <strong>Instituto Federal de Telecomunicaciones (IFT)</strong> es el órgano autónomo encargado
				de regular y promover la competencia en los sectores de telecomunicaciones y radiodifusión en México.
			</p>
			<p>
				<strong>OMR:</strong> Operador Móvil de Red - Opera su propia infraestructura de telecomunicaciones.
			</p>
			<p>
				<strong>OMV:</strong> Operador Móvil Virtual - Utiliza infraestructura de terceros para ofrecer servicios.
			</p>
			<p>
				<strong>Fuente:</strong> Instituto Federal de Telecomunicaciones (IFT)
			</p>
		</div>
	</div>
</div>