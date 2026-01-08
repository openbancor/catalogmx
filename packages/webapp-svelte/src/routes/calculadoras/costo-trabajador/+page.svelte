<script lang="ts">
	import { Calculator, Info, Users, Wallet, TrendingDown } from 'lucide-svelte';
	import imssTablesData from '../../../../../shared-data/imss-tables.json';

	type ClaseRiesgo = 1 | 2 | 3 | 4 | 5;
	type Year = 2024 | 2025 | 2026;

	// State
	let salarioMensual = $state<number>(15000);
	let antiguedadAnios = $state<number>(1);
	let claseRiesgo = $state<ClaseRiesgo>(1);
	let year = $state<Year>(2025);
	let incluirPTU = $state<boolean>(true);
	let porcentajePTU = $state<number>(10);
	let incluirReserva = $state<boolean>(true);
	let estado = $state<string>('CDMX');
	let diasAguinaldo = $state<number>(15);

	// Estados con sus tasas de ISN
	const estados = [
		{ value: 'CDMX', label: 'CDMX', tasa: 3.0 },
		{ value: 'EDOMEX', label: 'Estado de México', tasa: 3.0 },
		{ value: 'JAL', label: 'Jalisco', tasa: 2.0 },
		{ value: 'NL', label: 'Nuevo León', tasa: 3.0 },
		{ value: 'QRO', label: 'Querétaro', tasa: 2.0 },
		{ value: 'GTO', label: 'Guanajuato', tasa: 2.5 },
		{ value: 'OTROS', label: 'Otros (promedio 2.5%)', tasa: 2.5 }
	];

	const clasesRiesgo = imssTablesData.riesgos_trabajo_clases.map(c => ({
		value: c.clase as ClaseRiesgo,
		label: `Clase ${c.clase}`,
		prima: c.prima
	}));

	const years = [2024, 2025, 2026] as const;

	// Tabla LFT 2023 de días de vacaciones
	function getDiasVacaciones(anios: number): number {
		if (anios <= 0) return 0;
		if (anios === 1) return 12;
		if (anios === 2) return 14;
		if (anios === 3) return 16;
		if (anios === 4) return 18;
		if (anios === 5) return 20;
		if (anios >= 6 && anios <= 10) return 22;
		if (anios >= 11 && anios <= 15) return 24;
		if (anios >= 16 && anios <= 20) return 26;
		if (anios >= 21 && anios <= 25) return 28;
		if (anios >= 26 && anios <= 30) return 30;
		return 32; // 31+ años
	}

	interface CostoResult {
		salarioMensual: number;
		salarioAnual: number;
		// IMSS
		imssPatron: number;
		imssTrabajador: number;
		// Infonavit
		infonavit: number;
		// ISN
		impuestoNomina: number;
		tasaISN: number;
		// Prestaciones
		aguinaldo: number;
		diasVacaciones: number;
		vacaciones: number;
		primaVacacional: number;
		ptu: number;
		// Reservas
		reservaIndemnizacion: number;
		reservaPrimaAntiguedad: number;
		// Totales
		costoMensual: number;
		costoAnual: number;
		factorCarga: number;
	}

	let resultado = $state<CostoResult | null>(null);

	function getUMA(year: Year): number {
		return imssTablesData.uma[year.toString() as '2024' | '2025' | '2026'].diaria;
	}

	function calculateCostoPatronal() {
		if (!salarioMensual || salarioMensual <= 0) {
			resultado = null;
			return;
		}

		const uma = getUMA(year);
		const salarioAnual = salarioMensual * 12;
		const salarioDiario = salarioMensual / 30;
		const cuotas = imssTablesData.cuotas_imss;
		const primaRiesgo = cuotas.riesgo_trabajo[`clase_${claseRiesgo}` as keyof typeof cuotas.riesgo_trabajo] as number;

		// === CUOTAS IMSS PATRÓN ===
		let imssPatron = 0;

		// Cuota fija sobre UMA
		imssPatron += uma * 30 * cuotas.enfermedad_maternidad.prestaciones_en_especie.patron;

		// Excedente 3 UMA
		if (salarioDiario > uma * 3) {
			const excedente = salarioDiario - (uma * 3);
			imssPatron += excedente * 30 * cuotas.enfermedad_maternidad.prestaciones_en_especie_excedente.patron;
		}

		// Prestaciones en dinero
		imssPatron += salarioMensual * cuotas.enfermedad_maternidad.prestaciones_en_dinero.patron;

		// Gastos médicos pensionados
		imssPatron += salarioMensual * cuotas.enfermedad_maternidad.gastos_medicos_pensionados.patron;

		// Invalidez y vida
		imssPatron += salarioMensual * cuotas.invalidez_vida.patron;

		// Retiro
		imssPatron += salarioMensual * cuotas.retiro_cesantia_vejez.retiro.patron;

		// Cesantía y vejez
		imssPatron += salarioMensual * cuotas.retiro_cesantia_vejez.cesantia_vejez.patron;

		// Guarderías
		imssPatron += salarioMensual * cuotas.guarderias_prestaciones_sociales.patron;

		// Riesgo de trabajo
		imssPatron += salarioMensual * primaRiesgo;

		// === CUOTAS IMSS TRABAJADOR ===
		let imssTrabajador = 0;

		// Excedente 3 UMA
		if (salarioDiario > uma * 3) {
			const excedente = salarioDiario - (uma * 3);
			imssTrabajador += excedente * 30 * cuotas.enfermedad_maternidad.prestaciones_en_especie_excedente.trabajador;
		}

		// Prestaciones en dinero
		imssTrabajador += salarioMensual * cuotas.enfermedad_maternidad.prestaciones_en_dinero.trabajador;

		// Gastos médicos pensionados
		imssTrabajador += salarioMensual * cuotas.enfermedad_maternidad.gastos_medicos_pensionados.trabajador;

		// Invalidez y vida
		imssTrabajador += salarioMensual * cuotas.invalidez_vida.trabajador;

		// Cesantía y vejez
		imssTrabajador += salarioMensual * cuotas.retiro_cesantia_vejez.cesantia_vejez.trabajador;

		// === INFONAVIT (5%) ===
		const infonavit = salarioMensual * 0.05;

		// === IMPUESTO SOBRE NÓMINA ===
		const estadoSeleccionado = estados.find(e => e.value === estado);
		const tasaISN = estadoSeleccionado ? estadoSeleccionado.tasa : 2.5;
		const impuestoNomina = salarioMensual * (tasaISN / 100);

		// === PRESTACIONES ===
		// Aguinaldo
		const aguinaldo = salarioDiario * diasAguinaldo;
		const aguinaldoMensual = aguinaldo / 12;

		// Vacaciones
		const diasVacaciones = getDiasVacaciones(antiguedadAnios);
		const vacaciones = salarioDiario * diasVacaciones;
		const vacacionesMensual = vacaciones / 12;

		// Prima vacacional (25% sobre vacaciones)
		const primaVacacional = vacaciones * 0.25;
		const primaVacacionalMensual = primaVacacional / 12;

		// PTU
		const ptu = incluirPTU ? (salarioAnual * porcentajePTU / 100) : 0;
		const ptuMensual = ptu / 12;

		// === RESERVAS (si aplica) ===
		let reservaIndemnizacion = 0;
		let reservaPrimaAntiguedad = 0;

		if (incluirReserva) {
			// Reserva indemnización: 3 meses de salario / 12 para provisión mensual
			reservaIndemnizacion = (salarioMensual * 3) / 12;

			// Prima de antigüedad: 12 días por año, tope 2 salarios mínimos
			const salarioMinimo = imssTablesData.salario_minimo[year.toString() as '2024' | '2025' | '2026'].general;
			const tope2SM = salarioMinimo * 2;
			const salarioPrimaAntiguedad = Math.min(salarioDiario, tope2SM);
			reservaPrimaAntiguedad = (salarioPrimaAntiguedad * 12 * antiguedadAnios) / 12 / antiguedadAnios || 0;
			// Simplificado: 12 días al año / 12 meses
			reservaPrimaAntiguedad = salarioPrimaAntiguedad * 12 / 12;
		}

		// === TOTALES ===
		const costoMensual = salarioMensual
			+ imssPatron
			+ infonavit
			+ impuestoNomina
			+ aguinaldoMensual
			+ vacacionesMensual
			+ primaVacacionalMensual
			+ ptuMensual
			+ reservaIndemnizacion
			+ reservaPrimaAntiguedad;

		const costoAnual = costoMensual * 12;
		const factorCarga = costoMensual / salarioMensual;

		resultado = {
			salarioMensual,
			salarioAnual,
			imssPatron,
			imssTrabajador,
			infonavit,
			impuestoNomina,
			tasaISN,
			aguinaldo,
			diasVacaciones,
			vacaciones,
			primaVacacional,
			ptu,
			reservaIndemnizacion,
			reservaPrimaAntiguedad,
			costoMensual,
			costoAnual,
			factorCarga
		};
	}

	function formatCurrency(value: number): string {
		return new Intl.NumberFormat('es-MX', {
			style: 'currency',
			currency: 'MXN',
			minimumFractionDigits: 2,
			maximumFractionDigits: 2
		}).format(value);
	}

	function formatPercent(value: number): string {
		return new Intl.NumberFormat('es-MX', {
			style: 'percent',
			minimumFractionDigits: 1,
			maximumFractionDigits: 1
		}).format(value);
	}

	// Auto-calculate when inputs change
	$effect(() => {
		calculateCostoPatronal();
	});
</script>

<svelte:head>
	<title>Costo Total del Trabajador - catalogmx</title>
	<meta name="description" content="Calcula el costo total de un trabajador para el empleador: IMSS, Infonavit, ISN, aguinaldo, vacaciones, prima vacacional, PTU y reservas." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="/calculadoras" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Calculadoras
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">Costo Total del Trabajador</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-orange-100 dark:bg-orange-900/30">
				<Users class="h-8 w-8 text-orange-600 dark:text-orange-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Costo Total del Trabajador
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Calcula el costo real para el empleador incluyendo prestaciones y cargas sociales
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800">
			<Info class="h-5 w-5 text-orange-600 dark:text-orange-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-orange-900 dark:text-orange-300">
				<p class="font-medium mb-1">Factor de carga laboral</p>
				<p>El costo real de un trabajador es significativamente mayor al salario nominal. Esta calculadora incluye IMSS, Infonavit, ISN, prestaciones de ley y reservas.</p>
			</div>
		</div>
	</div>
</section>

<!-- Calculator -->
<section class="py-8">
	<div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 lg:grid-cols-5">
			<!-- Input Form -->
			<div class="lg:col-span-2 card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<Calculator class="h-5 w-5 text-brand-500" />
					Datos del trabajador
				</h2>

				<div class="space-y-5">
					<!-- Salario mensual -->
					<div>
						<label for="salarioMensual" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Salario mensual bruto
						</label>
						<div class="relative">
							<span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
							<input
								id="salarioMensual"
								type="number"
								bind:value={salarioMensual}
								min="0"
								step="100"
								class="input pl-8 tabular-nums"
								placeholder="15000"
							/>
						</div>
					</div>

					<!-- Antigüedad -->
					<div>
						<label for="antiguedad" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Antigüedad (años)
						</label>
						<input
							id="antiguedad"
							type="number"
							bind:value={antiguedadAnios}
							min="1"
							max="50"
							class="input tabular-nums"
						/>
						<p class="text-xs text-slate-500 mt-1">
							Días de vacaciones: {getDiasVacaciones(antiguedadAnios)} días (LFT 2023)
						</p>
					</div>

					<div class="grid grid-cols-2 gap-4">
						<!-- Año -->
						<div>
							<label for="year" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Año
							</label>
							<select id="year" bind:value={year} class="input">
								{#each years as y}
									<option value={y}>{y}</option>
								{/each}
							</select>
						</div>

						<!-- Clase de riesgo -->
						<div>
							<label for="claseRiesgo" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Clase riesgo
							</label>
							<select id="claseRiesgo" bind:value={claseRiesgo} class="input">
								{#each clasesRiesgo as clase}
									<option value={clase.value}>{clase.label}</option>
								{/each}
							</select>
						</div>
					</div>

					<!-- Estado -->
					<div>
						<label for="estado" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Estado (ISN)
						</label>
						<select id="estado" bind:value={estado} class="input">
							{#each estados as e}
								<option value={e.value}>{e.label} ({e.tasa}%)</option>
							{/each}
						</select>
					</div>

					<!-- Días de aguinaldo -->
					<div>
						<label for="diasAguinaldo" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Días de aguinaldo
						</label>
						<input
							id="diasAguinaldo"
							type="number"
							bind:value={diasAguinaldo}
							min="15"
							max="90"
							class="input tabular-nums"
						/>
						<p class="text-xs text-slate-500 mt-1">Mínimo LFT: 15 días</p>
					</div>

					<!-- PTU -->
					<div class="flex items-start gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<input
							id="ptu"
							type="checkbox"
							bind:checked={incluirPTU}
							class="mt-1 h-4 w-4 rounded border-slate-300 text-brand-500 focus:ring-brand-500"
						/>
						<div class="flex-1">
							<label for="ptu" class="text-sm text-slate-700 dark:text-slate-300 cursor-pointer">
								<span class="font-medium block mb-1">Incluir PTU (estimado)</span>
							</label>
							{#if incluirPTU}
								<div class="flex items-center gap-2 mt-2">
									<input
										type="number"
										bind:value={porcentajePTU}
										min="0"
										max="100"
										class="input w-20 text-sm tabular-nums"
									/>
									<span class="text-sm text-slate-500">% del salario anual</span>
								</div>
							{/if}
						</div>
					</div>

					<!-- Reserva -->
					<div class="flex items-start gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<input
							id="reserva"
							type="checkbox"
							bind:checked={incluirReserva}
							class="mt-1 h-4 w-4 rounded border-slate-300 text-brand-500 focus:ring-brand-500"
						/>
						<label for="reserva" class="text-sm text-slate-700 dark:text-slate-300 cursor-pointer">
							<span class="font-medium block mb-1">Incluir reservas de liquidación</span>
							<span class="text-slate-500 dark:text-slate-400">
								Indemnización (3 meses) y prima de antigüedad
							</span>
						</label>
					</div>
				</div>
			</div>

			<!-- Results -->
			<div class="lg:col-span-3 space-y-6">
				{#if resultado}
					<!-- Resumen principal -->
					<div class="card p-6">
						<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
							<Wallet class="h-5 w-5 text-orange-500" />
							Costo total del trabajador
						</h2>

						<div class="grid gap-4 sm:grid-cols-3">
							<div class="p-4 bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 rounded-lg border border-orange-200 dark:border-orange-800">
								<div class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">
									Costo mensual
								</div>
								<div class="text-2xl font-bold text-orange-900 dark:text-orange-100 tabular-nums">
									{formatCurrency(resultado.costoMensual)}
								</div>
							</div>
							<div class="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg border border-green-200 dark:border-green-800">
								<div class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">
									Costo anual
								</div>
								<div class="text-2xl font-bold text-green-900 dark:text-green-100 tabular-nums">
									{formatCurrency(resultado.costoAnual)}
								</div>
							</div>
							<div class="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg border border-blue-200 dark:border-blue-800">
								<div class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">
									Factor de carga
								</div>
								<div class="text-2xl font-bold text-blue-900 dark:text-blue-100 tabular-nums">
									{formatPercent(resultado.factorCarga - 1)}
								</div>
								<div class="text-xs text-blue-600 dark:text-blue-400">
									sobre el salario
								</div>
							</div>
						</div>
					</div>

					<!-- Desglose -->
					<div class="card p-6">
						<h3 class="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
							<TrendingDown class="h-5 w-5 text-slate-500" />
							Desglose mensual
						</h3>

						<div class="space-y-4">
							<!-- Salario base -->
							<div>
								<h4 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Salario</h4>
								<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
									<span class="text-slate-600 dark:text-slate-400">Salario mensual bruto</span>
									<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
										{formatCurrency(resultado.salarioMensual)}
									</span>
								</div>
							</div>

							<!-- Cargas sociales -->
							<div>
								<h4 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Cargas sociales</h4>
								<div class="space-y-1 text-sm">
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">IMSS Patrón</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.imssPatron)}
										</span>
									</div>
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Infonavit (5%)</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.infonavit)}
										</span>
									</div>
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">ISN ({resultado.tasaISN}%)</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.impuestoNomina)}
										</span>
									</div>
								</div>
							</div>

							<!-- Prestaciones -->
							<div>
								<h4 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Prestaciones (provisión mensual)</h4>
								<div class="space-y-1 text-sm">
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Aguinaldo ({diasAguinaldo} días)</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.aguinaldo / 12)}
										</span>
									</div>
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Vacaciones ({resultado.diasVacaciones} días)</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.vacaciones / 12)}
										</span>
									</div>
									<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
										<span class="text-slate-600 dark:text-slate-400">Prima vacacional (25%)</span>
										<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
											{formatCurrency(resultado.primaVacacional / 12)}
										</span>
									</div>
									{#if incluirPTU && resultado.ptu > 0}
										<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
											<span class="text-slate-600 dark:text-slate-400">PTU ({porcentajePTU}%)</span>
											<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
												{formatCurrency(resultado.ptu / 12)}
											</span>
										</div>
									{/if}
								</div>
							</div>

							{#if incluirReserva}
								<!-- Reservas -->
								<div>
									<h4 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">Reservas de liquidación</h4>
									<div class="space-y-1 text-sm">
										<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
											<span class="text-slate-600 dark:text-slate-400">Indemnización (3 meses)</span>
											<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
												{formatCurrency(resultado.reservaIndemnizacion)}
											</span>
										</div>
										<div class="flex justify-between py-2 border-b border-slate-100 dark:border-slate-800">
											<span class="text-slate-600 dark:text-slate-400">Prima antigüedad</span>
											<span class="font-medium text-slate-900 dark:text-slate-100 tabular-nums">
												{formatCurrency(resultado.reservaPrimaAntiguedad)}
											</span>
										</div>
									</div>
								</div>
							{/if}

							<!-- Total -->
							<div class="pt-4 border-t-2 border-slate-200 dark:border-slate-700">
								<div class="flex justify-between items-center">
									<span class="font-bold text-slate-900 dark:text-white">
										COSTO TOTAL MENSUAL
									</span>
									<span class="text-2xl font-bold text-orange-600 dark:text-orange-400 tabular-nums">
										{formatCurrency(resultado.costoMensual)}
									</span>
								</div>
							</div>
						</div>
					</div>

					<!-- Info descuento trabajador -->
					<div class="card p-6 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
						<h3 class="text-lg font-bold text-blue-900 dark:text-blue-100 mb-4">
							Referencia: Descuentos al trabajador
						</h3>
						<p class="text-sm text-blue-800 dark:text-blue-300 mb-3">
							Estos montos se descuentan del salario del trabajador (no son costo patronal adicional):
						</p>
						<div class="flex justify-between py-2 text-sm">
							<span class="text-blue-700 dark:text-blue-400">IMSS Trabajador</span>
							<span class="font-medium text-blue-900 dark:text-blue-100 tabular-nums">
								{formatCurrency(resultado.imssTrabajador)}
							</span>
						</div>
					</div>
				{:else}
					<div class="card p-6">
						<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
							<div class="text-center">
								<Calculator class="h-12 w-12 mx-auto mb-3 opacity-50" />
								<p class="text-sm">Ingresa un salario para calcular el costo total</p>
							</div>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Nota legal -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Esta calculadora es informativa y proporciona estimaciones basadas en la LFT, LSS y disposiciones fiscales vigentes.
				Los costos reales pueden variar según situaciones específicas de cada empresa y trabajador.
				Los días de vacaciones corresponden a la reforma LFT 2023. Consulta con un especialista para cálculos precisos.
			</p>
		</div>
	</div>
</section>
