<script lang="ts">
	import { ChevronRight, Car, Loader2, AlertCircle } from 'lucide-svelte';
	import { onMount } from 'svelte';

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

	interface HoyNoCirculaData {
		metadata: {
			programa: string;
			jurisdiccion: string;
			vigencia: string;
			fuente: string;
			ultima_actualizacion: string;
		};
		restricciones_por_dia: Restriccion[];
		exenciones_por_holograma: Holograma[];
		tipos_vehiculos_exentos: string[];
		zonas_aplicacion: string[];
		municipios_edomex: string[];
	}

	let data = $state<HoyNoCirculaData | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let searchTerm = $state('');

	const restriccionesFiltradas = $derived(
		data?.restricciones_por_dia.filter(r =>
			r.dia.toLowerCase().includes(searchTerm.toLowerCase()) ||
			r.terminacion_placa.some(t => t.includes(searchTerm)) ||
			r.engomado.some(e => e.toLowerCase().includes(searchTerm.toLowerCase()))
		) || []
	);

	const diasSemana = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load hoy no circula data from JSON
			const response = await fetch('/data/mexico/hoy_no_circula_cdmx.json');
			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}
			const hoyNoCirculaData = await response.json();
			data = hoyNoCirculaData;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading hoy no circula data:', e);
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
	<meta name="description" content="Programa de restricción vehicular Hoy No Circula para Ciudad de México y Zona Metropolitana." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="/catalogos/mexico" class="hover:text-brand-500">México</a>
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
					Programa de restricción vehicular para la Ciudad de México y Zona Metropolitana
				</p>
			</div>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catálogo...</span>
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
	{:else if data}
		<!-- Search bar -->
		<div class="mb-6">
			<input
				type="text"
				bind:value={searchTerm}
				placeholder="Buscar por día o terminación de placa..."
				class="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
			/>
		</div>

		<!-- Restricciones por día -->
		<div class="mb-8">
			<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
				Restricciones por Día de la Semana
			</h2>
			<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
				{#each restriccionesFiltradas as restriccion}
					<div class="card p-4">
						<h3 class="font-semibold text-slate-900 dark:text-white capitalize mb-3">
							{restriccion.dia}
						</h3>
						<div class="space-y-2 text-sm">
							<div>
								<span class="text-slate-500 dark:text-slate-400">Terminación de placa:</span>
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
				{#each data.exenciones_por_holograma as holograma}
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
								<strong>Días adicionales:</strong> {holograma.dias_adicionales}
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

		<!-- Vehículos exentos -->
		<div class="mb-8">
			<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
				Tipos de Vehículos Exentos
			</h2>
			<div class="card p-6">
				<ul class="grid gap-2 sm:grid-cols-2 text-sm text-slate-600 dark:text-slate-300">
					{#each data.tipos_vehiculos_exentos as tipo}
						<li class="flex items-start gap-2">
							<span class="text-green-500 mt-1">✓</span>
							<span>{tipo}</span>
						</li>
					{/each}
				</ul>
			</div>
		</div>

		<!-- Zonas de aplicación -->
		<div class="grid gap-6 sm:grid-cols-2 mb-8">
			<div>
				<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
					Zonas de Aplicación
				</h2>
				<div class="card p-6">
					<ul class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
						{#each data.zonas_aplicacion as zona}
							<li class="flex items-start gap-2">
								<span class="text-brand-500 mt-1">•</span>
								<span>{zona}</span>
							</li>
						{/each}
					</ul>
				</div>
			</div>

			<div>
				<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-4">
					Municipios Estado de México
				</h2>
				<div class="card p-6 max-h-96 overflow-y-auto">
					<ul class="grid gap-2 text-sm text-slate-600 dark:text-slate-300">
						{#each data.municipios_edomex as municipio}
							<li class="flex items-start gap-2">
								<span class="text-brand-500 mt-1">•</span>
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
					<strong>Hoy No Circula</strong> es un programa de restricción vehicular implementado en la Ciudad de México
					y su zona metropolitana desde 1989 con el objetivo de reducir la contaminación atmosférica.
				</p>
				<p>
					<strong>Funcionamiento:</strong> Los vehículos no pueden circular un día a la semana según la terminación
					de su placa y el color de su engomado, en el horario de 5:00 a 22:00 horas.
				</p>
				<p>
					<strong>Hologramas:</strong> Los vehículos con holograma 00 y 0 están exentos del programa. Los hologramas
					1 y 2 deben respetar las restricciones según su engomado.
				</p>
				<p>
					<strong>Contingencias Ambientales:</strong> Durante fases de contingencia ambiental, se aplican
					restricciones adicionales que pueden incluir hologramas 1 y afectar sábados.
				</p>
				<p>
					<strong>Fuente:</strong> Comisión Ambiental de la Megalópolis (CAMe)
				</p>
				<p>
					<strong>Última actualización:</strong> {data.metadata.ultima_actualizacion}
				</p>
			</div>
		</div>
	{/if}
</div>
