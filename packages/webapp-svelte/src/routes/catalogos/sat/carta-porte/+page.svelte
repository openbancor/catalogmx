<script lang="ts">
	import { base } from '$app/paths';
	import { ChevronRight, Plane, Ship, Truck, AlertTriangle, Package, FileText, Map } from 'lucide-svelte';

	interface Catalog {
		title: string;
		description: string;
		href: string;
		icon: typeof Plane;
		count?: string;
	}

	const catalogs: Catalog[] = [
		{
			title: 'Aeropuertos',
			description: 'Catálogo de aeropuertos nacionales e internacionales',
			href: `${base}/catalogos/sat/carta-porte/aeropuertos`,
			icon: Plane,
			count: '20+ aeropuertos'
		},
		{
			title: 'Puertos Marítimos',
			description: 'Puertos marítimos autorizados para comercio exterior',
			href: `${base}/catalogos/sat/carta-porte/puertos-maritimos`,
			icon: Ship,
			count: '25+ puertos'
		},
		{
			title: 'Carreteras',
			description: 'Principales carreteras federales de cuota y libre',
			href: `${base}/catalogos/sat/carta-porte/carreteras`,
			icon: Map,
			count: '20+ carreteras'
		},
		{
			title: 'Configuración Autotransporte',
			description: 'Tipos de configuración vehicular para transporte de carga',
			href: `${base}/catalogos/sat/carta-porte/config-autotransporte`,
			icon: Truck,
			count: '15 configuraciones'
		},
		{
			title: 'Material Peligroso',
			description: 'Clasificación de materiales peligrosos según normativa',
			href: `${base}/catalogos/sat/carta-porte/material-peligroso`,
			icon: AlertTriangle,
			count: '24 materiales'
		},
		{
			title: 'Tipo de Embalaje',
			description: 'Tipos de embalaje según clasificación ONU',
			href: `${base}/catalogos/sat/carta-porte/tipo-embalaje`,
			icon: Package,
			count: '35+ tipos'
		},
		{
			title: 'Tipo de Permiso',
			description: 'Permisos SCT para autotransporte federal',
			href: `${base}/catalogos/sat/carta-porte/tipo-permiso`,
			icon: FileText,
			count: '12 permisos'
		}
	];
</script>

<svelte:head>
	<title>Catálogos SAT Carta Porte 3.0 - catalogmx</title>
	<meta name="description" content="Catálogos oficiales del SAT para el Complemento Carta Porte versión 3.0" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Carta Porte 3.0</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<Truck class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogos SAT para Carta Porte 3.0
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogos oficiales del SAT para el Complemento Carta Porte versión 3.0
				</p>
			</div>
		</div>
	</div>

	<!-- Catalog Grid -->
	<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
		{#each catalogs as catalog}
			<a
				href={catalog.href}
				class="card p-6 hover:shadow-lg transition-shadow duration-200 group"
			>
				<div class="flex items-start gap-4 mb-4">
					<div class="bg-brand-100 dark:bg-brand-900/30 p-3 rounded-lg group-hover:bg-brand-200 dark:group-hover:bg-brand-800/40 transition-colors">
						<svelte:component this={catalog.icon} class="h-5 w-5 text-brand-600 dark:text-brand-400" />
					</div>
					<div class="flex-1">
						<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-2 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
							{catalog.title}
						</h2>
						<p class="text-sm text-slate-600 dark:text-slate-300">
							{catalog.description}
						</p>
					</div>
				</div>
				{#if catalog.count}
					<div class="text-xs text-slate-500 dark:text-slate-400 mt-2">
						{catalog.count}
					</div>
				{/if}
			</a>
		{/each}
	</div>

	<!-- Info section -->
	<div class="mt-8 card p-6">
		<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
			Acerca de estos catálogos
		</h2>
		<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
			<p>
				<strong>Complemento Carta Porte:</strong> Estos catálogos son utilizados para generar
				el Comprobante Fiscal Digital por Internet (CFDI) con Complemento Carta Porte versión 3.0,
				que es obligatorio para la emisión de comprobantes de transporte de mercancías.
			</p>
			<p>
				<strong>Vigencia:</strong> La versión 3.0 del Complemento Carta Porte entró en vigor
				el 1 de diciembre de 2023, sustituyendo a las versiones anteriores.
			</p>
			<p>
				<strong>Modalidades de transporte:</strong> Los catálogos cubren todas las modalidades
				de transporte: autotransporte, transporte marítimo, transporte aéreo, transporte ferroviario
				y transporte por ductos.
			</p>
			<p>
				<strong>Fuente:</strong> Servicio de Administración Tributaria (SAT)
			</p>
			<p>
				<strong>Uso:</strong> Estos catálogos son fundamentales para la correcta emisión de
				CFDIs con Complemento Carta Porte y aseguran el cumplimiento de las obligaciones fiscales
				en materia de transporte de mercancías.
			</p>
		</div>
	</div>
</div>