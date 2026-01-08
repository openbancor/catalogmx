<script lang="ts">
	import { ChevronRight, Car, Loader2, AlertCircle } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface Restriccion {
		dia: string;
		terminacion_placa: string[];
		engomado: string[];
		horario_restriccion: string;
		aplica_sabados: boolean;
		aplica_contingencia?: boolean;
		notas?: string;
	}

	interface Holograma {
		holograma: string;
		exento: boolean;
		descripcion: string;
		restriccion_sabatina: boolean;
		dias_adicionales?: string;
		notas?: string;
	}

	// Static data for Hoy No Circula rules (rarely change)
	const restriccionesPorDia: Restriccion[] = [
		{ dia: "lunes", terminacion_placa: ["5", "6"], engomado: ["amarillo"], horario_restriccion: "05:00-22:00", aplica_sabados: false },
		{ dia: "martes", terminacion_placa: ["7", "8"], engomado: ["rosa"], horario_restriccion: "05:00-22:00", aplica_sabados: false },
		{ dia: "miercoles", terminacion_placa: ["3", "4"], engomado: ["rojo"], horario_restriccion: "05:00-22:00", aplica_sabados: false },
		{ dia: "jueves", terminacion_placa: ["1", "2"], engomado: ["azul"], horario_restriccion: "05:00-22:00", aplica_sabados: false },
		{ dia: "viernes", terminacion_placa: ["9", "0"], engomado: ["verde"], horario_restriccion: "05:00-22:00", aplica_sabados: false },
		{ dia: "sabado", terminacion_placa: [], engomado: [], horario_restriccion: "05:00-22:00", aplica_sabados: false, aplica_contingencia: true, notas: "Solo aplica en contingencia ambiental o para vehiculos sin verificacion" }
	];

	const exencionesPorHolograma: Holograma[] = [
		{ holograma: "00", exento: true, descripcion: "Cero emisiones - Vehiculos electricos e hibridos", restriccion_sabatina: false },
		{ holograma: "0", exento: true, descripcion: "Emisiones muy bajas", restriccion_sabatina: false },
		{ holograma: "1", exento: false, descripcion: "Emisiones bajas - Circula todos los dias excepto el dia de su engomado", restriccion_sabatina: false },
		{ holograma: "2", exento: false, descripcion: "Emisiones altas - No circula dos dias por semana", restriccion_sabatina: true, dias_adicionales: "Un sabado al mes segun terminacion de placa", notas: "Consultar calendario mensual para sabados" }
	];

	const tiposVehiculosExentos: string[] = [
		"Vehiculos electricos e hibridos con holograma 00",
		"Vehiculos con holograma 0",
		"Motocicletas",
		"Vehiculos de emergencia y seguridad publica",
		"Transporte publico concesionado",
		"Vehiculos de personas con discapacidad (con placas y credencial)",
		"Vehiculos con matricula de auto antiguo o clasico"
	];

	const zonasAplicacion: string[] = [
		"Ciudad de Mexico (todas las alcaldias)",
		"Estado de Mexico - 18 municipios de la ZMVM",
		"Hidalgo - Municipios conurbados",
		"Morelos - Municipios conurbados",
		"Puebla - Municipios conurbados",
		"Tlaxcala - Municipios conurbados"
	];

	let municipiosEdomex = $state<string[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let searchTerm = $state('');

	const metadata = {
		programa: "Hoy No Circula",
		jurisdiccion: "Ciudad de Mexico y Zona Metropolitana del Valle de Mexico",
		vigencia: "Permanente (desde 1989)",
		fuente: "Comision Ambiental de la Megalopolis (CAMe)",
		ultima_actualizacion: "2024-01-01"
	};

	const restriccionesFiltradas = $derived(
		restriccionesPorDia.filter(r =>
			r.dia.toLowerCase().includes(searchTerm.toLowerCase()) ||
			r.terminacion_placa.some(t => t.includes(searchTerm)) ||
			r.engomado.some(e => e.toLowerCase().includes(searchTerm.toLowerCase()))
		)
	);

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load municipios from SQLite
			const results = await query<{ value: string }>('SELECT value FROM mexico_hoy_no_circula_cdmx ORDER BY value');
			municipiosEdomex = results.map(r => r.value);

		} catch (e) {
			// If SQLite fails, use fallback static data
			municipiosEdomex = [
				"Atizapan de Zaragoza",
				"Coacalco de Berriozabal",
				"Cuautitlan",
				"Cuautitlan Izcalli",
				"Chalco",
				"Chicoloapan",
				"Chimalhuacan",
				"Ecatepec de Morelos",
				"Huixquilucan",
				"Ixtapaluca",
				"La Paz",
				"Naucalpan de Juarez",
				"Nezahualcoyotl",
				"Nicolas Romero",
				"Tecamac",
				"Tlalnepantla de Baz",
				"Tultitlan",
				"Valle de Chalco Solidaridad"
			];
			console.error('Error loading hoy no circula data from SQLite, using fallback:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});

	function getEngomadoColor(engomado: string): string {
		const colors: Record<string, string> = {
			'amarillo': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
			'rosa': 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-400',
			'rojo': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
			'azul': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
			'verde': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
		};
		return colors[engomado.toLowerCase()] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
	}
</script>

<svelte:head>
	<title>Hoy No Circula - CDMX - catalogmx</title>
	<meta name="description" content="Programa de restriccion vehicular Hoy No Circula para Ciudad de Mexico y Zona Metropolitana." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/mexico" class="hover:text-brand-500">Mexico</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Hoy No Circula</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-orange-100 dark:bg-orange-900/30 p-3 rounded-lg">
				<Car class="h-6 w-6 text-orange-600 dark:text-orange-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Hoy No Circula - CDMX
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Programa de restriccion vehicular para la Ciudad de Mexico y Zona Metropolitana
				</p>
			</div>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catalogo desde SQLite...</span>
		</div>
	{:else if error}
		<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
			<div class="flex items-start gap-3">
				<AlertCircle class="h-5 w-5 text-red-500 mt-0.5" />
				<div>
					<p class="font-medium text-red-800 dark:text-red-200">Error al cargar datos</p>
					<p class="text-sm text-red-600 dark:text-red-300 mt-1">{error}</p>
					<button onclick={loadData} class="btn btn-secondary mt-3 text-sm">
						Reintentar
					</button>
				</div>
			</div>
		</div>
	{:else}
		<!-- Search bar -->
		<div class="mb-6">
			<input
				type="text"
				bind:value={searchTerm}
				placeholder="Buscar por dia o terminacion de placa..."
				class="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
			/>
		</div>

		<!-- Restricciones por dia -->
		<div class="mb-8">
			<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
				Restricciones por Dia de la Semana
			</h2>
			<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{#each restriccionesFiltradas as restriccion}
					<div class="card p-4">
						<h3 class="font-semibold text-slate-900 dark:text-white capitalize mb-3">
							{restriccion.dia}
						</h3>
						<div class="space-y-2 text-sm">
							<div>
								<span class="text-slate-500 dark:text-slate-400">Terminacion de placa:</span>
								<div class="flex gap-1 mt-1">
									{#each restriccion.terminacion_placa as terminacion}
										<span class="px-2 py-1 bg-slate-100 dark:bg-slate-700 rounded font-mono">
											{terminacion}
										</span>
									{/each}
								</div>
							</div>
							<div>
								<span class="text-slate-500 dark:text-slate-400">Engomado:</span>
								<div class="flex gap-1 mt-1">
									{#each restriccion.engomado as engomado}
										<span class="px-2 py-1 rounded capitalize {getEngomadoColor(engomado)}">
											{engomado}
										</span>
									{/each}
								</div>
							</div>
							<div>
								<span class="text-slate-500 dark:text-slate-400">Horario:</span>
								<span class="ml-1 text-slate-900 dark:text-white font-mono">
									{restriccion.horario_restriccion}
								</span>
							</div>
							{#if restriccion.notas}
								<p class="text-xs text-slate-500 dark:text-slate-400 mt-2">
									{restriccion.notas}
								</p>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Exenciones por holograma -->
		<div class="mb-8">
			<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
				Exenciones por Holograma
			</h2>
			<div class="grid gap-4 sm:grid-cols-2">
				{#each exencionesPorHolograma as holograma}
					<div class="card p-4">
						<div class="flex items-start justify-between mb-2">
							<h3 class="font-semibold text-slate-900 dark:text-white">
								Holograma {holograma.holograma}
							</h3>
							{#if holograma.exento}
								<span class="px-2 py-1 text-xs bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 rounded">
									Exento
								</span>
							{:else}
								<span class="px-2 py-1 text-xs bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 rounded">
									No exento
								</span>
							{/if}
						</div>
						<p class="text-sm text-slate-600 dark:text-slate-300 mb-2">
							{holograma.descripcion}
						</p>
						{#if holograma.dias_adicionales}
							<p class="text-xs text-slate-500 dark:text-slate-400">
								<strong>Dias adicionales:</strong> {holograma.dias_adicionales}
							</p>
						{/if}
						{#if holograma.notas}
							<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
								{holograma.notas}
							</p>
						{/if}
					</div>
				{/each}
			</div>
		</div>

		<!-- Vehiculos exentos -->
		<div class="mb-8">
			<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
				Tipos de Vehiculos Exentos
			</h2>
			<div class="card p-6">
				<ul class="grid gap-2 sm:grid-cols-2 text-sm text-slate-600 dark:text-slate-300">
					{#each tiposVehiculosExentos as tipo}
						<li class="flex items-start gap-2">
							<span class="text-green-500 mt-1">OK</span>
							<span>{tipo}</span>
						</li>
					{/each}
				</ul>
			</div>
		</div>

		<!-- Zonas de aplicacion -->
		<div class="grid gap-6 sm:grid-cols-2 mb-8">
			<div>
				<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
					Zonas de Aplicacion
				</h2>
				<div class="card p-6">
					<ul class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
						{#each zonasAplicacion as zona}
							<li class="flex items-start gap-2">
								<span class="text-brand-500 mt-1">-</span>
								<span>{zona}</span>
							</li>
						{/each}
					</ul>
				</div>
			</div>

			<div>
				<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
					Municipios Estado de Mexico
				</h2>
				<div class="card p-6 max-h-96 overflow-y-auto">
					<ul class="grid gap-2 text-sm text-slate-600 dark:text-slate-300">
						{#each municipiosEdomex as municipio}
							<li class="flex items-start gap-2">
								<span class="text-brand-500 mt-1">-</span>
								<span>{municipio}</span>
							</li>
						{/each}
					</ul>
				</div>
			</div>
		</div>

		<!-- Info section -->
		<div class="card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca del programa Hoy No Circula
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>Hoy No Circula</strong> es un programa de restriccion vehicular implementado en la Ciudad de Mexico
					y su zona metropolitana desde 1989 con el objetivo de reducir la contaminacion atmosferica.
				</p>
				<p>
					<strong>Funcionamiento:</strong> Los vehiculos no pueden circular un dia a la semana segun la terminacion
					de su placa y el color de su engomado, en el horario de 5:00 a 22:00 horas.
				</p>
				<p>
					<strong>Hologramas:</strong> Los vehiculos con holograma 00 y 0 estan exentos del programa. Los hologramas
					1 y 2 deben respetar las restricciones segun su engomado.
				</p>
				<p>
					<strong>Contingencias Ambientales:</strong> Durante fases de contingencia ambiental, se aplican
					restricciones adicionales que pueden incluir hologramas 1 y afectar sabados.
				</p>
				<p>
					<strong>Fuente:</strong> Comision Ambiental de la Megalopolis (CAMe)
				</p>
				<p>
					<strong>Ultima actualizacion:</strong> {metadata.ultima_actualizacion}
				</p>
			</div>
		</div>
	{/if}
</div>
