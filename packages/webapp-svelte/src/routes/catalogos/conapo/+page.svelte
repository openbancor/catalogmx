<script lang="ts">
	import { base } from '$app/paths';
	import { MapPinned, Users, Building2 } from 'lucide-svelte';
</script>

<svelte:head>
	<title>CONAPO - catalogmx</title>
	<meta name="description" content="Catálogos del Consejo Nacional de Población: zonas metropolitanas, sistema urbano nacional." />
</svelte:head>

<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<div class="mb-8">
		<h1 class="text-3xl font-bold text-slate-900 dark:text-white mb-2">
			CONAPO
		</h1>
		<p class="text-slate-600 dark:text-slate-300">
			Consejo Nacional de Población - Catálogos demográficos y urbanos de México
		</p>
	</div>

	<div class="grid gap-4 md:grid-cols-2">
		<a
			href="{base}/catalogos/conapo/zonas-metropolitanas"
			class="card p-6 hover:border-brand-500 transition-colors group"
		>
			<div class="flex items-start gap-4">
				<div class="p-3 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400">
					<Building2 class="h-6 w-6" />
				</div>
				<div class="flex-1">
					<h2 class="text-lg font-semibold text-slate-900 dark:text-white group-hover:text-brand-500">
						Zonas Metropolitanas
					</h2>
					<p class="text-sm text-slate-600 dark:text-slate-400 mt-1">
						92 zonas metropolitanas y metrópolis municipales definidas por CONAPO 2020
					</p>
					<div class="flex items-center gap-4 mt-3 text-xs text-slate-500">
						<span class="flex items-center gap-1">
							<MapPinned class="h-3 w-3" />
							92 zonas
						</span>
						<span class="flex items-center gap-1">
							<Users class="h-3 w-3" />
							421 municipios
						</span>
					</div>
				</div>
			</div>
		</a>
	</div>
</div>
