<script lang="ts">
	import { Calculator, Info, Percent } from 'lucide-svelte';

	// IVA rates
	const IVA_TASA_GENERAL = 16;
	const IVA_TASA_CERO = 0;
	const IVA_RETENCION_FACTOR = 2 / 3; // Retención del 2/3 del IVA

	// State
	let monto = $state<number>(10000);
	let tipoCalculo = $state<'agregar' | 'desglosar' | 'retencion'>('agregar');
	let tasa = $state<number>(16);

	interface CalculationResult {
		subtotal: number;
		iva: number;
		total: number;
		ivaRetenido?: number;
		ivaNeto?: number;
	}

	let resultado = $state<CalculationResult | null>(null);

	const tiposCalculo = [
		{ value: 'agregar', label: 'Agregar IVA al monto' },
		{ value: 'desglosar', label: 'Desglosar IVA del total' },
		{ value: 'retencion', label: 'Calcular retención IVA' }
	] as const;

	const tasasIVA = [
		{ value: 16, label: '16% (General)' },
		{ value: 0, label: '0% (Exportación / Exento)' },
		{ value: 8, label: '8% (Zona Fronteriza)' }
	];

	function calculateIVA() {
		if (!monto || monto <= 0) {
			resultado = null;
			return;
		}

		if (tipoCalculo === 'agregar') {
			const iva = (monto * tasa) / 100;
			resultado = {
				subtotal: monto,
				iva,
				total: monto + iva
			};
		} else if (tipoCalculo === 'desglosar') {
			const subtotal = monto / (1 + tasa / 100);
			const iva = monto - subtotal;
			resultado = {
				subtotal,
				iva,
				total: monto
			};
		} else if (tipoCalculo === 'retencion') {
			const iva = (monto * tasa) / 100;
			const ivaRetenido = iva * IVA_RETENCION_FACTOR;
			const ivaNeto = iva - ivaRetenido;
			resultado = {
				subtotal: monto,
				iva,
				total: monto + iva,
				ivaRetenido,
				ivaNeto
			};
		}
	}

	function formatCurrency(value: number): string {
		return new Intl.NumberFormat('es-MX', {
			style: 'currency',
			currency: 'MXN',
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		}).format(value);
	}

	// Auto-calculate when inputs change
	$effect(() => {
		if (monto > 0) {
			calculateIVA();
		}
	});
</script>

<svelte:head>
	<title>Calculadora IVA - catalogmx</title>
	<meta name="description" content="Calcula el IVA (Impuesto al Valor Agregado) en México. Agregar, desglosar o calcular retención del IVA al 16%, 8% o 0%." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="/calculadoras" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Calculadoras
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">IVA</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-green-100 dark:bg-green-900/30">
				<Percent class="h-8 w-8 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Calculadora IVA
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Impuesto al Valor Agregado en México
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
			<Info class="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-green-900 dark:text-green-300">
				<p class="font-medium mb-1">IVA en México</p>
				<p>Tasa general 16%, tasa 0% para exportaciones y alimentos básicos. Zona fronteriza puede aplicar 8%.</p>
			</div>
		</div>
	</div>
</section>

<!-- Calculator -->
<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Input Form -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<Calculator class="h-5 w-5 text-brand-500" />
					Datos de entrada
				</h2>

				<div class="space-y-5">
					<!-- Tipo de cálculo -->
					<div>
						<label for="tipoCalculo" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Tipo de cálculo
						</label>
						<select
							id="tipoCalculo"
							bind:value={tipoCalculo}
							class="input"
						>
							{#each tiposCalculo as t}
								<option value={t.value}>{t.label}</option>
							{/each}
						</select>
					</div>

					<!-- Monto -->
					<div>
						<label for="monto" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							{tipoCalculo === 'desglosar' ? 'Total (con IVA incluido)' : 'Subtotal (sin IVA)'}
						</label>
						<div class="relative">
							<span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
							<input
								id="monto"
								type="number"
								bind:value={monto}
								min="0"
								step="0.01"
								class="input pl-8 tabular-nums"
								placeholder="10000.00"
							/>
						</div>
					</div>

					<!-- Tasa IVA -->
					<div>
						<label for="tasa" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Tasa IVA
						</label>
						<select
							id="tasa"
							bind:value={tasa}
							class="input"
						>
							{#each tasasIVA as t}
								<option value={t.value}>{t.label}</option>
							{/each}
						</select>
					</div>

					{#if tipoCalculo === 'retencion'}
						<div class="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
							<p class="text-sm text-amber-800 dark:text-amber-300">
								<strong>Retención IVA:</strong> Aplica cuando el cliente es persona moral y el proveedor es persona física. Se retiene 2/3 del IVA.
							</p>
						</div>
					{/if}
				</div>
			</div>

			<!-- Results -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<Percent class="h-5 w-5 text-green-500" />
					Resultados
				</h2>

				{#if resultado}
					<div class="space-y-4">
						<!-- Total destacado -->
						<div class="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg border border-green-200 dark:border-green-800">
							<div class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">
								Total {tipoCalculo === 'retencion' ? '(sin retención)' : ''}
							</div>
							<div class="text-3xl font-bold text-green-900 dark:text-green-100 tabular-nums">
								{formatCurrency(resultado.total)}
							</div>
						</div>

						<!-- Desglose -->
						<div class="space-y-3">
							<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2">
								Desglose
							</h3>

							<div class="space-y-2 text-sm">
								<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
									<span class="text-slate-600 dark:text-slate-400">Subtotal</span>
									<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.subtotal)}
									</span>
								</div>

								<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
									<span class="text-slate-600 dark:text-slate-400">IVA ({tasa}%)</span>
									<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.iva)}
									</span>
								</div>

								{#if tipoCalculo === 'retencion' && resultado.ivaRetenido !== undefined}
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-amber-600 dark:text-amber-400">IVA retenido (2/3)</span>
										<span class="font-medium text-amber-600 dark:text-amber-400 tabular-nums">
											- {formatCurrency(resultado.ivaRetenido)}
										</span>
									</div>

									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">IVA neto a trasladar</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.ivaNeto || 0)}
										</span>
									</div>
								{/if}

								<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
									<span class="text-slate-600 dark:text-slate-400 font-medium">Total</span>
									<span class="font-semibold text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.total)}
									</span>
								</div>
							</div>
						</div>

						{#if tipoCalculo === 'retencion' && resultado.ivaRetenido !== undefined}
							<div class="pt-3 border-t-2 border-slate-200 dark:border-slate-700">
								<div class="flex justify-between items-center">
									<span class="text-sm font-medium text-slate-700 dark:text-slate-300">
										Total a cobrar (con retención)
									</span>
									<span class="text-xl font-bold text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.subtotal + (resultado.ivaNeto || 0))}
									</span>
								</div>
							</div>
						{/if}
					</div>
				{:else}
					<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
						<div class="text-center">
							<Calculator class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Ingresa un monto para calcular el IVA</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info adicional -->
		<div class="mt-8 grid gap-4 sm:grid-cols-3">
			<div class="card p-5">
				<h3 class="font-semibold text-slate-900 dark:text-white mb-2">
					IVA 16%
				</h3>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					Tasa general para la mayoría de bienes y servicios en México.
				</p>
			</div>

			<div class="card p-5">
				<h3 class="font-semibold text-slate-900 dark:text-white mb-2">
					IVA 0%
				</h3>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					Exportaciones, alimentos básicos, medicinas, libros y revistas.
				</p>
			</div>

			<div class="card p-5">
				<h3 class="font-semibold text-slate-900 dark:text-white mb-2">
					Retención 2/3
				</h3>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					Personas morales retienen 2/3 del IVA a personas físicas (Art. 1-A LIVA).
				</p>
			</div>
		</div>

		<!-- Nota legal -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Esta calculadora es informativa. La tasa de IVA aplicable puede variar según el tipo de bien o servicio.
				Consulta con un contador para casos específicos. Ley del IVA, Art. 1.
			</p>
		</div>
	</div>
</section>
