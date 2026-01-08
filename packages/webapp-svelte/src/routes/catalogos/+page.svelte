<script lang="ts">
	import { Search, Database, ArrowRight } from 'lucide-svelte';

	let searchQuery = $state('');

	const allCatalogs = [
		// SAT CFDI 4.0
		{ source: 'SAT', id: 'cfdi', name: 'Productos y Servicios (c_ClaveProdServ)', count: 52000, description: 'Claves de productos y servicios para CFDI 4.0' },
		{ source: 'SAT', id: 'unidades', name: 'Claves de Unidad (c_ClaveUnidad)', count: 2800, description: 'Unidades de medida para facturación' },
		{ source: 'SAT', id: 'regimen-fiscal', name: 'Regímenes Fiscales', count: 25, description: 'Tipos de régimen fiscal para personas físicas y morales' },
		{ source: 'SAT', id: 'uso-cfdi', name: 'Uso de CFDI', count: 22, description: 'Claves de uso para comprobantes fiscales' },
		{ source: 'SAT', id: 'forma-pago', name: 'Formas de Pago', count: 18, description: 'Métodos de pago aceptados para CFDI' },
		{ source: 'SAT', id: 'metodo-pago', name: 'Métodos de Pago', count: 3, description: 'PUE, PPD, etc.' },
		{ source: 'SAT', id: 'moneda', name: 'Monedas', count: 180, description: 'Divisas para facturación' },
		{ source: 'SAT', id: 'pais', name: 'Países', count: 250, description: 'Catálogo de países para comercio exterior' },
		{ source: 'SAT', id: 'tipo-comprobante', name: 'Tipos de Comprobante', count: 6, description: 'Ingreso, egreso, traslado, nómina, pago' },
		{ source: 'SAT', id: 'impuesto', name: 'Impuestos', count: 5, description: 'ISR, IVA, IEPS, etc.' },

		// SAT Nómina
		{ source: 'SAT Nómina', id: 'nomina', name: 'Catálogos de Nómina', count: 6, description: 'Todos los catálogos para timbrado de nómina' },
		{ source: 'SAT Nómina', id: 'nomina/banco', name: 'Bancos para Nómina', count: 100, description: 'Instituciones bancarias para depósito de nómina' },
		{ source: 'SAT Nómina', id: 'nomina/tipo-contrato', name: 'Tipos de Contrato', count: 10, description: 'Contrato indefinido, temporal, por obra, etc.' },
		{ source: 'SAT Nómina', id: 'nomina/tipo-regimen', name: 'Tipos de Régimen', count: 14, description: 'Sueldos, asimilados, jubilados, etc.' },
		{ source: 'SAT Nómina', id: 'nomina/periodicidad', name: 'Periodicidad de Pago', count: 10, description: 'Diario, semanal, quincenal, mensual' },
		{ source: 'SAT Nómina', id: 'nomina/tipo-jornada', name: 'Tipos de Jornada', count: 6, description: 'Diurna, nocturna, mixta, reducida' },
		{ source: 'SAT Nómina', id: 'nomina/riesgo-puesto', name: 'Riesgo de Puesto', count: 5, description: 'Clases de riesgo para prima IMSS' },

		// INEGI
		{ source: 'INEGI', id: 'estados', name: 'Estados de México', count: 32, description: 'Entidades federativas' },
		{ source: 'INEGI', id: 'municipios', name: 'Municipios', count: 2469, description: 'Municipios y alcaldías' },
		{ source: 'INEGI', id: 'localidades', name: 'Localidades', count: 304000, description: 'Poblaciones y colonias' },
		{ source: 'INEGI', id: 'scian', name: 'SCIAN', count: 1800, description: 'Sistema de Clasificación Industrial de América del Norte' },

		// Banxico
		{ source: 'Banxico', id: 'bancos', name: 'Instituciones Bancarias', count: 150, description: 'Bancos y SOFOMES con clave SPEI' },
		{ source: 'Banxico', id: 'plazas', name: 'Códigos de Plaza', count: 900, description: 'Plazas bancarias para CLABE' },
		{ source: 'Banxico', id: 'instituciones', name: 'Instituciones Financieras', count: 20, description: 'Tipos de instituciones del sistema financiero' },
		{ source: 'Banxico', id: 'monedas', name: 'Monedas y Divisas', count: 180, description: 'Monedas internacionales con ISO 4217' },
		{ source: 'Banxico', id: 'tipo-cambio', name: 'Tipo de Cambio USD/MXN', count: 10000, description: 'Histórico del tipo de cambio FIX' },
		{ source: 'Banxico', id: 'udis', name: 'Valor de la UDI', count: 12000, description: 'Unidades de Inversión históricas' },
		{ source: 'Banxico', id: 'tiie', name: 'TIIE', count: 8000, description: 'Tasa de Interés Interbancaria de Equilibrio' },
		{ source: 'Banxico', id: 'inflacion', name: 'Inflación', count: 400, description: 'Índice Nacional de Precios al Consumidor' },

		// SEPOMEX
		{ source: 'SEPOMEX', id: 'codigos-postales', name: 'Códigos Postales', count: 145000, description: 'Códigos postales con colonias, municipios y estados' },

		// IFT
		{ source: 'IFT', id: 'operadores', name: 'Operadores Telefónicos', count: 50, description: 'Claves de operadores de telefonía (LADA)' },

		// IMSS
		{ source: 'IMSS', id: 'tipos-movimiento', name: 'Tipos de Movimiento Afiliatorio', count: 4, description: 'Claves de movimientos para el SUA' },
		{ source: 'IMSS', id: 'tipos-trabajador', name: 'Tipos de Trabajador', count: 4, description: 'Clasificación de trabajadores según régimen laboral' },
		{ source: 'IMSS', id: 'tipos-incapacidad', name: 'Tipos de Incapacidad', count: 3, description: 'Clasificación de incapacidades y subsidios' },
		{ source: 'IMSS', id: 'seguros', name: 'Seguros del IMSS', count: 6, description: 'Ramos de aseguramiento y prestaciones' },
		{ source: 'IMSS', id: 'pensiones', name: 'Tabulador de Pensiones', count: 3, description: 'Montos mínimos de pensiones 2024-2026' },
		{ source: 'IMSS', id: 'semanas-cotizadas', name: 'Semanas Cotizadas', count: 3, description: 'Requisitos para pensiones por modalidad' },

		// CNBV
		{ source: 'CNBV', id: 'sectores', name: 'Sectores Financieros', count: 15, description: 'Sectores regulados por la CNBV' },

		// México General
		{ source: 'México', id: 'uma', name: 'UMA', count: 10, description: 'Unidad de Medida y Actualización' },
		{ source: 'México', id: 'salarios-minimos', name: 'Salarios Mínimos', count: 30, description: 'Histórico de salarios mínimos' },
		{ source: 'México', id: 'hoy-no-circula', name: 'Hoy No Circula', count: 7, description: 'Restricciones vehiculares por día' },
	];

	const sourceColors: Record<string, string> = {
		'SAT': 'bg-red-500',
		'SAT Nómina': 'bg-red-600',
		'INEGI': 'bg-blue-500',
		'Banxico': 'bg-green-600',
		'SEPOMEX': 'bg-amber-500',
		'IFT': 'bg-cyan-500',
		'IMSS': 'bg-teal-500',
		'CNBV': 'bg-purple-500',
		'México': 'bg-emerald-500',
	};

	const filteredCatalogs = $derived(
		searchQuery.trim()
			? allCatalogs.filter(c =>
					c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
					c.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
					c.source.toLowerCase().includes(searchQuery.toLowerCase())
				)
			: allCatalogs
	);

	const groupedCatalogs = $derived(
		filteredCatalogs.reduce((acc, catalog) => {
			if (!acc[catalog.source]) acc[catalog.source] = [];
			acc[catalog.source].push(catalog);
			return acc;
		}, {} as Record<string, typeof allCatalogs>)
	);

	function formatCount(num: number): string {
		if (num >= 1000) {
			return (num / 1000).toFixed(num >= 10000 ? 0 : 1) + 'k';
		}
		return num.toString();
	}

	function getCatalogUrl(source: string, id: string): string {
		// Map source names to URL paths
		const sourceMap: Record<string, string> = {
			'SAT': 'sat',
			'SAT Nómina': 'sat',
			'INEGI': 'inegi',
			'Banxico': 'banxico',
			'SEPOMEX': 'sepomex',
			'IFT': 'ift',
			'IMSS': 'imss',
			'CNBV': 'cnbv',
			'México': 'mexico',
		};
		const basePath = sourceMap[source] || source.toLowerCase();
		return `/catalogos/${basePath}/${id}`;
	}
</script>

<svelte:head>
	<title>Catálogos - catalogmx</title>
	<meta name="description" content="Explora más de 470,000 registros de catálogos oficiales mexicanos: SAT, INEGI, Banxico, SEPOMEX." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Header -->
	<div class="mb-8">
		<h1 class="text-3xl font-bold text-slate-900 dark:text-white mb-2">
			Catálogos de México
		</h1>
		<p class="text-slate-600 dark:text-slate-300">
			Explora más de 470,000 registros de fuentes oficiales
		</p>
	</div>

	<!-- Search -->
	<div class="relative max-w-md mb-8">
		<Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
		<input
			type="search"
			placeholder="Buscar catálogos..."
			bind:value={searchQuery}
			class="input pl-11"
		/>
	</div>

	<!-- Results count -->
	{#if searchQuery}
		<p class="text-sm text-slate-500 dark:text-slate-400 mb-6">
			{filteredCatalogs.length} catálogo{filteredCatalogs.length !== 1 ? 's' : ''} encontrado{filteredCatalogs.length !== 1 ? 's' : ''}
		</p>
	{/if}

	<!-- Grouped catalogs -->
	<div class="space-y-10">
		{#each Object.entries(groupedCatalogs) as [source, catalogs]}
			<section>
				<div class="flex items-center gap-3 mb-4">
					<div class="{sourceColors[source]} w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-xs">
						{source.slice(0, 2)}
					</div>
					<h2 class="text-xl font-semibold text-slate-900 dark:text-white">
						{source}
					</h2>
					<span class="text-sm text-slate-500 dark:text-slate-400">
						({catalogs.length} catálogo{catalogs.length !== 1 ? 's' : ''})
					</span>
				</div>

				<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
					{#each catalogs as catalog}
						<a
							href={getCatalogUrl(source, catalog.id)}
							class="card p-4 hover:border-brand-300 dark:hover:border-brand-600 transition-colors group"
						>
							<div class="flex items-start justify-between mb-2">
								<h3 class="font-medium text-slate-900 dark:text-white group-hover:text-brand-500">
									{catalog.name}
								</h3>
								<span class="text-xs text-slate-400 dark:text-slate-500 tabular-nums bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
									{formatCount(catalog.count)}
								</span>
							</div>
							<p class="text-sm text-slate-500 dark:text-slate-400">
								{catalog.description}
							</p>
						</a>
					{/each}
				</div>
			</section>
		{/each}
	</div>

	{#if filteredCatalogs.length === 0}
		<div class="text-center py-12">
			<Database class="h-12 w-12 mx-auto text-slate-300 dark:text-slate-600 mb-4" />
			<p class="text-slate-500 dark:text-slate-400">
				No se encontraron catálogos con "{searchQuery}"
			</p>
		</div>
	{/if}
</div>
