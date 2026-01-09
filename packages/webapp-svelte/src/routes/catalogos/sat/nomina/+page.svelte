<script lang="ts">
	import { base } from '$app/paths';
	import { ChevronRight, FileText, Briefcase, Users, Calendar, Clock, AlertTriangle, Building2 } from 'lucide-svelte';

	interface Catalog {
		title: string;
		description: string;
		href: string;
		icon: typeof FileText;
		count?: string;
	}

	const catalogs: Catalog[] = [
		{
			title: 'Bancos',
			description: 'Catálogo de instituciones bancarias para nómina',
			href: `${base}/catalogos/sat/nomina/banco`,
			icon: Building2,
			count: '50+ registros'
		},
		{
			title: 'Tipos de Contrato',
			description: 'Modalidades de contratación laboral',
			href: `${base}/catalogos/sat/nomina/tipo-contrato`,
			icon: FileText,
			count: '10 tipos'
		},
		{
			title: 'Tipos de Régimen',
			description: 'Regímenes fiscales para empleados',
			href: `${base}/catalogos/sat/nomina/tipo-regimen`,
			icon: Briefcase,
			count: '14 regímenes'
		},
		{
			title: 'Periodicidad de Pago',
			description: 'Frecuencias de pago de nómina',
			href: `${base}/catalogos/sat/nomina/periodicidad`,
			icon: Calendar,
			count: '11 opciones'
		},
		{
			title: 'Tipos de Jornada',
			description: 'Clasificación de jornadas laborales',
			href: `${base}/catalogos/sat/nomina/tipo-jornada`,
			icon: Clock,
			count: '8 tipos'
		},
		{
			title: 'Riesgo de Puesto',
			description: 'Clases de riesgo laboral (IMSS)',
			href: `${base}/catalogos/sat/nomina/riesgo-puesto`,
			icon: AlertTriangle,
			count: '5 clases'
		}
	];
</script>

<svelte:head>
	<title>Catálogos SAT Nómina - catalogmx</title>
	<meta name="description" content="Catálogos oficiales del SAT para facturación electrónica de nómina versión 1.2" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Nómina</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-blue-100 dark:bg-blue-900/30 p-3 rounded-lg">
				<Users class="h-6 w-6 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogos SAT para Nómina
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogos oficiales del SAT para el Complemento de Nómina versión 1.2
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
				<strong>Complemento de Nómina:</strong> Estos catálogos son utilizados para generar
				el Comprobante Fiscal Digital por Internet (CFDI) con Complemento de Nómina versión 1.2,
				que es obligatorio para la emisión de recibos de pago de nómina.
			</p>
			<p>
				<strong>Fuente:</strong> Servicio de Administración Tributaria (SAT)
			</p>
			<p>
				<strong>Uso:</strong> Estos catálogos son fundamentales para la correcta emisión de
				CFDIs de nómina y aseguran el cumplimiento de las obligaciones fiscales en materia laboral.
			</p>
		</div>
	</div>
</div>