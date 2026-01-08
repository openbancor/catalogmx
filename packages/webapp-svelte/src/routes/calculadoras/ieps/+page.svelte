<script lang="ts">
	import { Calculator, Info, Wine, Cigarette, Fuel, Droplet, Cookie } from 'lucide-svelte';
	import type { ComponentType } from 'svelte';

	// TypeScript interfaces
	interface Subcategoria {
		id: string;
		label: string;
		tasa: number;
		tipo: string;
		cuotaFija?: number;
		unidad?: string;
	}

	interface Categoria {
		id: string;
		label: string;
		icon: ComponentType;
		subcategorias: Subcategoria[];
		descripcion: string;
		unidad: string;
	}

	// IEPS Categories and rates
	const categorias: Categoria[] = [
		{
			id: 'bebidas_alcoholicas',
			label: 'Bebidas Alcohólicas',
			icon: Wine,
			subcategorias: [
				{ id: 'cerveza', label: 'Cerveza y bebidas hasta 14°', tasa: 26.5, tipo: 'ad_valorem' },
				{ id: 'bebidas_14_20', label: 'Bebidas de 14° a 20° GL', tasa: 30.0, tipo: 'ad_valorem' },
				{ id: 'bebidas_mas_20', label: 'Bebidas mayores a 20° GL', tasa: 53.0, tipo: 'ad_valorem' }
			],
			descripcion: 'Tasa según contenido de alcohol (grados Gay-Lussac)',
			unidad: 'valor'
		},
		{
			id: 'tabacos',
			label: 'Tabacos',
			icon: Cigarette,
			subcategorias: [
				{ id: 'cigarros', label: 'Cigarros', tasa: 160.0, tipo: 'ad_valorem', cuotaFija: 0.508 },
				{ id: 'puros', label: 'Puros y otros tabacos', tasa: 160.0, tipo: 'ad_valorem' }
			],
			descripcion: 'Tasa ad-valorem más cuota fija por cigarro',
			unidad: 'valor_y_cantidad'
		},
		{
			id: 'combustibles',
			label: 'Combustibles',
			icon: Fuel,
			subcategorias: [
				{ id: 'gasolina_menor_92', label: 'Gasolina < 92 octanos', tasa: 5.117, tipo: 'cuota_fija', unidad: 'litro' },
				{ id: 'gasolina_mayor_92', label: 'Gasolina ≥ 92 octanos', tasa: 4.579, tipo: 'cuota_fija', unidad: 'litro' },
				{ id: 'diesel', label: 'Diesel', tasa: 5.563, tipo: 'cuota_fija', unidad: 'litro' }
			],
			descripcion: 'Cuota fija por litro (actualizada 2025)',
			unidad: 'cantidad'
		},
		{
			id: 'bebidas_azucaradas',
			label: 'Bebidas Azucaradas',
			icon: Droplet,
			subcategorias: [
				{ id: 'bebidas_con_azucar', label: 'Bebidas saborizadas', tasa: 1.0, tipo: 'cuota_fija', unidad: 'litro' },
				{ id: 'concentrados', label: 'Concentrados y jarabes', tasa: 1.0, tipo: 'cuota_fija', unidad: 'litro' }
			],
			descripcion: 'Cuota de $1 por litro',
			unidad: 'cantidad'
		},
		{
			id: 'alimentos_alta_densidad',
			label: 'Alimentos Alta Densidad',
			icon: Cookie,
			subcategorias: [
				{ id: 'alimentos_chatarra', label: 'Botanas, dulces, chocolates', tasa: 8.0, tipo: 'ad_valorem' }
			],
			descripcion: 'Productos ≥ 275 kcal/100g',
			unidad: 'valor'
		}
	];

	// State
	let categoriaSeleccionada = $state<string>('bebidas_alcoholicas');
	let subcategoriaSeleccionada = $state<string>('cerveza');
	let valor = $state<number>(1000);
	let cantidad = $state<number>(20);

	interface CalculationResult {
		base: number;
		tasa: number;
		ieps: number;
		total: number;
		tipo: string;
		unidad?: string;
		cantidad?: number;
		desglose?: {
			adValorem?: number;
			cuotaFija?: number;
		};
	}

	let resultado = $state<CalculationResult | null>(null);

	// Derived values
	const categoriaActual = $derived(
		categorias.find(c => c.id === categoriaSeleccionada) || categorias[0]
	);

	const subcategoriaActual = $derived(
		categoriaActual.subcategorias.find(s => s.id === subcategoriaSeleccionada) || categoriaActual.subcategorias[0]
	);

	const IconoCategoria = $derived(categoriaActual.icon);

	const requiereValor = $derived(
		categoriaActual.unidad === 'valor' || categoriaActual.unidad === 'valor_y_cantidad'
	);

	const requiereCantidad = $derived(
		categoriaActual.unidad === 'cantidad' || categoriaActual.unidad === 'valor_y_cantidad'
	);

	function calculateIEPS() {
		if (!subcategoriaActual) {
			resultado = null;
			return;
		}

		const { tasa, tipo, cuotaFija } = subcategoriaActual;

		if (tipo === 'ad_valorem') {
			// Cigarros: ad-valorem + cuota fija
			if (subcategoriaActual.id === 'cigarros' && cuotaFija) {
				const iepsAdValorem = (valor * tasa) / 100;
				const iepsCuotaFija = cantidad * cuotaFija;
				const iepsTotal = iepsAdValorem + iepsCuotaFija;

				resultado = {
					base: valor,
					tasa,
					ieps: iepsTotal,
					total: valor + iepsTotal,
					tipo: 'ad_valorem_cuota',
					cantidad,
					desglose: {
						adValorem: iepsAdValorem,
						cuotaFija: iepsCuotaFija
					}
				};
			} else {
				// Ad-valorem simple
				const ieps = (valor * tasa) / 100;
				resultado = {
					base: valor,
					tasa,
					ieps,
					total: valor + ieps,
					tipo: 'ad_valorem'
				};
			}
		} else if (tipo === 'cuota_fija') {
			// Cuota fija por unidad
			const ieps = cantidad * tasa;
			resultado = {
				base: cantidad,
				tasa,
				ieps,
				total: ieps,
				tipo: 'cuota_fija',
				unidad: subcategoriaActual.unidad,
				cantidad
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

	function formatNumber(value: number): string {
		return new Intl.NumberFormat('es-MX', {
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		}).format(value);
	}

	// Update subcategoria when categoria changes
	$effect(() => {
		const cat = categorias.find(c => c.id === categoriaSeleccionada);
		if (cat && cat.subcategorias.length > 0) {
			subcategoriaSeleccionada = cat.subcategorias[0].id;
		}
	});

	// Auto-calculate when inputs change
	$effect(() => {
		if ((requiereValor && valor > 0) || (requiereCantidad && cantidad > 0)) {
			calculateIEPS();
		}
	});
</script>

<svelte:head>
	<title>Calculadora IEPS - catalogmx</title>
	<meta name="description" content="Calcula el IEPS (Impuesto Especial sobre Producción y Servicios) en México. Bebidas alcohólicas, tabacos, combustibles, bebidas azucaradas y alimentos chatarra." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="/calculadoras" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Calculadoras
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">IEPS</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-purple-100 dark:bg-purple-900/30">
				<Wine class="h-8 w-8 text-purple-600 dark:text-purple-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Calculadora IEPS
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Impuesto Especial sobre Producción y Servicios
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
			<Info class="h-5 w-5 text-purple-600 dark:text-purple-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-purple-900 dark:text-purple-300">
				<p class="font-medium mb-1">IEPS en México</p>
				<p>Impuesto especial que aplica a bebidas alcohólicas, tabacos, combustibles, bebidas azucaradas y alimentos de alta densidad calórica. Las tasas varían según el producto.</p>
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
					<!-- Categoría -->
					<div>
						<label for="categoria" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Categoría de producto
						</label>
						<select
							id="categoria"
							bind:value={categoriaSeleccionada}
							class="input"
						>
							{#each categorias as cat}
								<option value={cat.id}>{cat.label}</option>
							{/each}
						</select>
						<p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
							{categoriaActual.descripcion}
						</p>
					</div>

					<!-- Subcategoría -->
					<div>
						<label for="subcategoria" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Tipo de producto
						</label>
						<select
							id="subcategoria"
							bind:value={subcategoriaSeleccionada}
							class="input"
						>
							{#each categoriaActual.subcategorias as subcat}
								<option value={subcat.id}>{subcat.label}</option>
							{/each}
						</select>
					</div>

					<!-- Valor (if required) -->
					{#if requiereValor}
						<div>
							<label for="valor" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Valor del producto
							</label>
							<div class="relative">
								<span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
								<input
									id="valor"
									type="number"
									bind:value={valor}
									min="0"
									step="0.01"
									class="input pl-8 tabular-nums"
									placeholder="1000.00"
								/>
							</div>
						</div>
					{/if}

					<!-- Cantidad (if required) -->
					{#if requiereCantidad}
						<div>
							<label for="cantidad" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Cantidad
								{#if subcategoriaActual.unidad}
									<span class="text-slate-500">({subcategoriaActual.unidad}s)</span>
								{:else if subcategoriaActual.id === 'cigarros'}
									<span class="text-slate-500">(número de cigarros)</span>
								{/if}
							</label>
							<input
								id="cantidad"
								type="number"
								bind:value={cantidad}
								min="0"
								step={subcategoriaActual.unidad === 'litro' ? '0.1' : '1'}
								class="input tabular-nums"
								placeholder="20"
							/>
						</div>
					{/if}

					<!-- Info adicional según categoría -->
					{#if categoriaSeleccionada === 'tabacos' && subcategoriaSeleccionada === 'cigarros'}
						<div class="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
							<p class="text-sm text-amber-800 dark:text-amber-300">
								<strong>Cigarros:</strong> IEPS = 160% del valor + $0.508 por cigarro
							</p>
						</div>
					{/if}

					{#if categoriaSeleccionada === 'alimentos_alta_densidad'}
						<div class="p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
							<p class="text-sm text-amber-800 dark:text-amber-300">
								<strong>Nota:</strong> Aplica a productos con ≥275 kcal por 100g (botanas, dulces, chocolates, etc.)
							</p>
						</div>
					{/if}
				</div>
			</div>

			<!-- Results -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<IconoCategoria class="h-5 w-5 text-purple-500" />
					Resultados
				</h2>

				{#if resultado}
					<div class="space-y-4">
						<!-- IEPS destacado -->
						<div class="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg border border-purple-200 dark:border-purple-800">
							<div class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">
								IEPS Total
							</div>
							<div class="text-3xl font-bold text-purple-900 dark:text-purple-100 tabular-nums">
								{formatCurrency(resultado.ieps)}
							</div>
						</div>

						<!-- Desglose -->
						<div class="space-y-3">
							<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2">
								Desglose
							</h3>

							<div class="space-y-2 text-sm">
								{#if resultado.tipo === 'ad_valorem' || resultado.tipo === 'ad_valorem_cuota'}
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Valor base</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.base)}
										</span>
									</div>

									{#if resultado.tipo === 'ad_valorem_cuota' && resultado.desglose}
										<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
											<span class="text-slate-600 dark:text-slate-400">IEPS ad-valorem ({resultado.tasa}%)</span>
											<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
												{formatCurrency(resultado.desglose.adValorem || 0)}
											</span>
										</div>

										<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
											<span class="text-slate-600 dark:text-slate-400">Cuota fija ({resultado.cantidad} cigarros × $0.508)</span>
											<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
												{formatCurrency(resultado.desglose.cuotaFija || 0)}
											</span>
										</div>
									{:else}
										<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
											<span class="text-slate-600 dark:text-slate-400">Tasa IEPS</span>
											<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
												{resultado.tasa}%
											</span>
										</div>
									{/if}
								{/if}

								{#if resultado.tipo === 'cuota_fija'}
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Cantidad</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatNumber(resultado.cantidad || 0)} {resultado.unidad}s
										</span>
									</div>

									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Cuota por {resultado.unidad}</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.tasa)}
										</span>
									</div>
								{/if}

								<div class="flex justify-between py-2 pt-3 border-t-2 border-purple-200 dark:border-purple-800">
									<span class="text-slate-700 dark:text-slate-300 font-semibold">IEPS Total</span>
									<span class="font-bold text-purple-600 dark:text-purple-400 tabular-nums">
										{formatCurrency(resultado.ieps)}
									</span>
								</div>

								{#if resultado.tipo !== 'cuota_fija'}
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400 font-medium">Precio total</span>
										<span class="font-semibold text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.total)}
										</span>
									</div>
								{/if}
							</div>
						</div>
					</div>
				{:else}
					<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
						<div class="text-center">
							<Calculator class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Ingresa los datos para calcular el IEPS</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info adicional por categoría -->
		<div class="mt-8 grid gap-4 sm:grid-cols-3">
			<div class="card p-5">
				<div class="flex items-center gap-2 mb-2">
					<Wine class="h-5 w-5 text-purple-600 dark:text-purple-400" />
					<h3 class="font-semibold text-slate-900 dark:text-white">
						Bebidas Alcohólicas
					</h3>
				</div>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					Cerveza 26.5%, vinos 14-20° 30%, destilados >20° 53%
				</p>
			</div>

			<div class="card p-5">
				<div class="flex items-center gap-2 mb-2">
					<Cigarette class="h-5 w-5 text-purple-600 dark:text-purple-400" />
					<h3 class="font-semibold text-slate-900 dark:text-white">
						Tabacos
					</h3>
				</div>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					160% + $0.508 por cigarro (cajetilla 20 cigarros ≈ $10.16 cuota)
				</p>
			</div>

			<div class="card p-5">
				<div class="flex items-center gap-2 mb-2">
					<Fuel class="h-5 w-5 text-purple-600 dark:text-purple-400" />
					<h3 class="font-semibold text-slate-900 dark:text-white">
						Combustibles
					</h3>
				</div>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					Gasolina ~$4.50-5.10/L, Diesel ~$5.56/L (2025)
				</p>
			</div>

			<div class="card p-5">
				<div class="flex items-center gap-2 mb-2">
					<Droplet class="h-5 w-5 text-purple-600 dark:text-purple-400" />
					<h3 class="font-semibold text-slate-900 dark:text-white">
						Bebidas Azucaradas
					</h3>
				</div>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					$1.00 por litro para bebidas saborizadas con azúcar añadida
				</p>
			</div>

			<div class="card p-5">
				<div class="flex items-center gap-2 mb-2">
					<Cookie class="h-5 w-5 text-purple-600 dark:text-purple-400" />
					<h3 class="font-semibold text-slate-900 dark:text-white">
						Alimentos Chatarra
					</h3>
				</div>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					8% para productos ≥275 kcal/100g (botanas, dulces, chocolates)
				</p>
			</div>

			<div class="card p-5">
				<h3 class="font-semibold text-slate-900 dark:text-white mb-2">
					Tipos de IEPS
				</h3>
				<p class="text-sm text-slate-600 dark:text-slate-400">
					Ad-valorem (%) o cuota fija ($/unidad) según producto
				</p>
			</div>
		</div>

		<!-- Nota legal -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Esta calculadora es informativa. Las tasas IEPS pueden variar y algunas cuotas se actualizan anualmente.
				Los combustibles tienen estímulos fiscales que reducen el IEPS efectivo. Consulta con un contador para casos específicos. Ley del IEPS, Arts. 2 y 2-A.
			</p>
		</div>
	</div>
</section>
