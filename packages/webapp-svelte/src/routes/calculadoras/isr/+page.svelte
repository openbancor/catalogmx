<script lang="ts">
	import { base } from '$app/paths';
	import { Info, Receipt } from 'lucide-svelte';
</script>

<svelte:head>
	<title>Estado de la calculadora ISR - catalogmx</title>
	<meta
		name="description"
		content="La calculadora ISR está temporalmente deshabilitada mientras se auditan sus fuentes fiscales."
	/>
</svelte:head>

<section
	data-testid="isr-audit-state"
	class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800"
>
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a
				href="{base}/calculadoras"
				class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500"
			>
				Calculadoras
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">ISR</span>
		</div>

		<div class="flex items-start gap-4 mb-6">
			<div class="p-3 rounded-lg bg-amber-100 dark:bg-amber-900/30">
				<Receipt class="h-8 w-8 text-amber-700 dark:text-amber-300" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Calculadora ISR
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Temporalmente no disponible
				</p>
			</div>
		</div>

		<div
			role="status"
			class="flex items-start gap-3 p-5 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800"
		>
			<Info class="h-5 w-5 text-amber-700 dark:text-amber-300 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-amber-950 dark:text-amber-200 space-y-2">
				<p class="font-medium">Las tablas ISR incluidas siguen pendientes de verificación documental.</p>
				<p>
					El cálculo público permanecerá deshabilitado hasta que cada ejercicio tenga fuente,
					vigencia y checksum verificados. No uses los datos históricos del paquete para determinar
					retenciones de nómina.
				</p>
				<a
					class="font-medium underline"
					href="https://github.com/openbancor/catalogmx/blob/master/packages/shared-data/fiscal-manifest.json"
				>
					Consultar el manifiesto fiscal
				</a>
			</div>
		</div>
	</div>
</section>
