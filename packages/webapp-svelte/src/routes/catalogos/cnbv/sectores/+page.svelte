<script lang="ts">
	import { base } from '$app/paths';
	import { ChevronRight, Building2, Scale, Users, Shield, Landmark, Wallet, Search } from 'lucide-svelte';
	import { onMount } from 'svelte';

	interface Sector {
		id: string;
		nombre: string;
		nombre_corto: string;
		descripcion: string;
		ley_aplicable: string;
		regulador_principal: string;
		supervisores_adicionales?: string[];
		ejemplos?: string[];
		subtipos?: { id: string; nombre: string; descripcion: string }[];
		caracteristicas?: string;
		nota?: string;
	}

	interface Regulador {
		id: string;
		nombre: string;
		siglas: string;
		funcion: string;
	}

	let sectores = $state<Sector[]>([]);
	let reguladores = $state<Regulador[]>([]);
	let searchQuery = $state('');
	let selectedRegulador = $state<string | null>(null);

	const sectorIcons: Record<string, typeof Building2> = {
		banca_multiple: Landmark,
		banca_desarrollo: Landmark,
		casas_bolsa: Building2,
		aseguradoras: Shield,
		fintech_ifpe: Users,
		fintech_ifondos: Wallet,
	};

	const filteredSectores = $derived(
		sectores.filter(s => {
			const matchesSearch = !searchQuery ||
				s.nombre.toLowerCase().includes(searchQuery.toLowerCase()) ||
				s.descripcion.toLowerCase().includes(searchQuery.toLowerCase()) ||
				s.nombre_corto.toLowerCase().includes(searchQuery.toLowerCase());

			const matchesRegulador = !selectedRegulador ||
				s.regulador_principal === selectedRegulador;

			return matchesSearch && matchesRegulador;
		})
	);

	onMount(async () => {
		// In production, this would come from an API or the SQLite database
		// For now, load directly from the JSON structure
		const data = {
			sectores: [
				{
					id: "banca_multiple",
					nombre: "Banca Multiple",
					nombre_corto: "Bancos",
					descripcion: "Instituciones de banca multiple autorizadas para realizar operaciones de captacion, credito y servicios",
					ley_aplicable: "Ley de Instituciones de Credito",
					regulador_principal: "CNBV",
					supervisores_adicionales: ["Banxico", "IPAB"],
					ejemplos: ["BBVA Mexico", "Banorte", "Santander", "Citibanamex", "HSBC", "Scotiabank"]
				},
				{
					id: "banca_desarrollo",
					nombre: "Banca de Desarrollo",
					nombre_corto: "Banca de Desarrollo",
					descripcion: "Instituciones de credito del Estado para fomentar actividades prioritarias",
					ley_aplicable: "Leyes Organicas de cada institucion",
					regulador_principal: "CNBV",
					supervisores_adicionales: ["SHCP", "Banxico"],
					ejemplos: ["NAFIN", "Bancomext", "Banobras", "SHF", "Banco del Bienestar", "FIRA"]
				},
				{
					id: "casas_bolsa",
					nombre: "Casas de Bolsa",
					nombre_corto: "Casas de Bolsa",
					descripcion: "Intermediarios autorizados para realizar operaciones con valores en el mercado bursatil",
					ley_aplicable: "Ley del Mercado de Valores",
					regulador_principal: "CNBV",
					supervisores_adicionales: ["BMV", "Indeval"],
					ejemplos: ["GBM Casa de Bolsa", "Actinver", "Vector Casa de Bolsa", "Finamex"]
				},
				{
					id: "sofomes_er",
					nombre: "SOFOM E.R.",
					nombre_corto: "SOFOM Reguladas",
					descripcion: "Sociedades Financieras de Objeto Multiple Reguladas (vinculadas a bancos)",
					ley_aplicable: "Ley General de Organizaciones y Actividades Auxiliares del Credito",
					regulador_principal: "CNBV",
					supervisores_adicionales: ["CONDUSEF"],
					ejemplos: ["Santander Consumo", "BBVA Leasing", "Banorte Arrendadora"]
				},
				{
					id: "sofomes_enr",
					nombre: "SOFOM E.N.R.",
					nombre_corto: "SOFOM No Reguladas",
					descripcion: "Sociedades Financieras de Objeto Multiple Entidades No Reguladas",
					ley_aplicable: "Ley General de Organizaciones y Actividades Auxiliares del Credito",
					regulador_principal: "CONDUSEF",
					supervisores_adicionales: ["UIF"],
					nota: "No estan reguladas por CNBV pero deben registrarse en CONDUSEF",
					ejemplos: ["Credito Real", "Unifin", "Credito Familiar"]
				},
				{
					id: "sofipos",
					nombre: "SOFIPO",
					nombre_corto: "SOFIPO",
					descripcion: "Sociedades Financieras Populares - entidades de ahorro y credito popular",
					ley_aplicable: "Ley de Ahorro y Credito Popular",
					regulador_principal: "CNBV",
					supervisores_adicionales: ["FOCOOP"],
					caracteristicas: "Pueden captar ahorro del publico general",
					ejemplos: ["Libertad Servicios Financieros", "Te Creemos", "Caja Popular Mexicana"]
				},
				{
					id: "socaps",
					nombre: "SOCAP",
					nombre_corto: "Cooperativas de Ahorro",
					descripcion: "Sociedades Cooperativas de Ahorro y Prestamo",
					ley_aplicable: "Ley para Regular las Actividades de las Sociedades Cooperativas de Ahorro y Prestamo",
					regulador_principal: "CNBV",
					supervisores_adicionales: ["FOCOOP"],
					caracteristicas: "Solo pueden operar con socios cooperativistas",
					ejemplos: ["Caja Popular Mexicana", "Caja Morelia Valladolid"]
				},
				{
					id: "aseguradoras",
					nombre: "Instituciones de Seguros",
					nombre_corto: "Aseguradoras",
					descripcion: "Compañias de seguros autorizadas para operar en Mexico",
					ley_aplicable: "Ley de Instituciones de Seguros y de Fianzas",
					regulador_principal: "CNBV",
					supervisores_adicionales: ["CNSF"],
					ejemplos: ["GNP", "AXA", "Metlife", "Zurich", "Mapfre"]
				},
				{
					id: "fintech_ifpe",
					nombre: "Instituciones de Financiamiento Colectivo",
					nombre_corto: "Crowdfunding",
					descripcion: "Plataformas de financiamiento colectivo (crowdfunding)",
					ley_aplicable: "Ley para Regular las Instituciones de Tecnologia Financiera (Ley Fintech)",
					regulador_principal: "CNBV",
					supervisores_adicionales: ["Banxico", "CONDUSEF"],
					ejemplos: ["Crowdfunder", "Briq.mx", "Playbusiness", "100 Ladrillos"]
				},
				{
					id: "fintech_ifondos",
					nombre: "Instituciones de Fondos de Pago Electronico",
					nombre_corto: "Wallets / IFPE",
					descripcion: "Emisores de fondos de pago electronico (monederos electronicos)",
					ley_aplicable: "Ley para Regular las Instituciones de Tecnologia Financiera (Ley Fintech)",
					regulador_principal: "CNBV",
					supervisores_adicionales: ["Banxico"],
					ejemplos: ["Mercado Pago", "Clip", "Sr. Pago", "Spin by OXXO"]
				},
				{
					id: "afores",
					nombre: "AFORE",
					nombre_corto: "AFORE",
					descripcion: "Administradoras de Fondos para el Retiro",
					ley_aplicable: "Ley de los Sistemas de Ahorro para el Retiro",
					regulador_principal: "CONSAR",
					supervisores_adicionales: ["CNBV"],
					ejemplos: ["Profuturo", "XXI Banorte", "Citibanamex Afore", "Sura"]
				}
			],
			reguladores: [
				{ id: "cnbv", nombre: "Comision Nacional Bancaria y de Valores", siglas: "CNBV", funcion: "Supervision y regulacion de entidades financieras y mercado de valores" },
				{ id: "condusef", nombre: "Comision Nacional para la Proteccion y Defensa de los Usuarios de Servicios Financieros", siglas: "CONDUSEF", funcion: "Proteccion al usuario de servicios financieros" },
				{ id: "consar", nombre: "Comision Nacional del Sistema de Ahorro para el Retiro", siglas: "CONSAR", funcion: "Regulacion del sistema de pensiones" }
			]
		};

		sectores = data.sectores;
		reguladores = data.reguladores;
	});
</script>

<svelte:head>
	<title>Sectores Financieros CNBV - catalogmx</title>
	<meta name="description" content="Catalogo de sectores y entidades financieras reguladas por la CNBV en Mexico. Bancos, SOFOM, Fintech, Aseguradoras y mas." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/cnbv" class="hover:text-brand-500">CNBV</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Sectores Financieros</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
			Sectores Financieros de Mexico
		</h1>
		<p class="text-slate-600 dark:text-slate-300">
			Entidades reguladas por la CNBV y otros organismos del sistema financiero mexicano
		</p>
	</div>

	<!-- Filters -->
	<div class="flex flex-col sm:flex-row gap-4 mb-8">
		<div class="relative flex-1 max-w-md">
			<Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
			<input
				type="search"
				placeholder="Buscar sectores..."
				bind:value={searchQuery}
				class="input pl-10"
			/>
		</div>
		<select
			class="input w-full sm:w-48"
			bind:value={selectedRegulador}
		>
			<option value={null}>Todos los reguladores</option>
			{#each reguladores as reg}
				<option value={reg.siglas}>{reg.siglas}</option>
			{/each}
		</select>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-3 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total sectores</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">{sectores.length}</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Regulados por CNBV</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{sectores.filter(s => s.regulador_principal === 'CNBV').length}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Fintech (Ley Fintech)</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{sectores.filter(s => s.id.startsWith('fintech')).length}
			</p>
		</div>
	</div>

	<!-- Sectors grid -->
	<div class="grid gap-6 md:grid-cols-2">
		{#each filteredSectores as sector}
			{@const Icon = sectorIcons[sector.id] || Building2}
			<div class="card p-6">
				<div class="flex items-start gap-4">
					<div class="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-lg">
						<Icon class="h-6 w-6 text-purple-600 dark:text-purple-400" />
					</div>
					<div class="flex-1 min-w-0">
						<div class="flex items-center gap-2 mb-1">
							<h3 class="font-semibold text-slate-900 dark:text-white">
								{sector.nombre}
							</h3>
							<span class="badge badge-purple text-xs">
								{sector.regulador_principal}
							</span>
						</div>
						<p class="text-sm text-slate-500 dark:text-slate-400 mb-3">
							{sector.descripcion}
						</p>

						<div class="space-y-2 text-sm">
							<div class="flex items-start gap-2">
								<Scale class="h-4 w-4 text-slate-400 mt-0.5 flex-shrink-0" />
								<span class="text-slate-600 dark:text-slate-300">{sector.ley_aplicable}</span>
							</div>

							{#if sector.supervisores_adicionales && sector.supervisores_adicionales.length > 0}
								<div class="flex items-start gap-2">
									<Shield class="h-4 w-4 text-slate-400 mt-0.5 flex-shrink-0" />
									<span class="text-slate-600 dark:text-slate-300">
										Supervision adicional: {sector.supervisores_adicionales.join(', ')}
									</span>
								</div>
							{/if}

							{#if sector.ejemplos && sector.ejemplos.length > 0}
								<div class="flex flex-wrap gap-1.5 mt-3">
									{#each sector.ejemplos.slice(0, 4) as ejemplo}
										<span class="text-xs px-2 py-1 bg-slate-100 dark:bg-slate-700 rounded text-slate-600 dark:text-slate-300">
											{ejemplo}
										</span>
									{/each}
									{#if sector.ejemplos.length > 4}
										<span class="text-xs px-2 py-1 text-slate-500">
											+{sector.ejemplos.length - 4} mas
										</span>
									{/if}
								</div>
							{/if}

							{#if sector.nota}
								<p class="text-xs text-amber-600 dark:text-amber-400 mt-2">
									Nota: {sector.nota}
								</p>
							{/if}
						</div>
					</div>
				</div>
			</div>
		{/each}
	</div>

	{#if filteredSectores.length === 0}
		<div class="text-center py-12">
			<Building2 class="h-12 w-12 mx-auto text-slate-300 dark:text-slate-600 mb-4" />
			<p class="text-slate-500 dark:text-slate-400">
				No se encontraron sectores con los filtros seleccionados
			</p>
		</div>
	{/if}

	<!-- Regulators section -->
	<div class="mt-12">
		<h2 class="text-xl font-semibold text-slate-900 dark:text-white mb-6">
			Reguladores del Sistema Financiero
		</h2>
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
			{#each reguladores as regulador}
				<div class="card p-4">
					<div class="flex items-center gap-3 mb-2">
						<span class="font-bold text-brand-500">{regulador.siglas}</span>
					</div>
					<p class="text-sm font-medium text-slate-900 dark:text-white mb-1">
						{regulador.nombre}
					</p>
					<p class="text-xs text-slate-500 dark:text-slate-400">
						{regulador.funcion}
					</p>
				</div>
			{/each}
		</div>
	</div>
</div>