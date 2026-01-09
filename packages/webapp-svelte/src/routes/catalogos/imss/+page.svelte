<script lang="ts">
	import { base } from '$app/paths';
	import { ChevronRight, FileText, Users, Activity, UserX, Shield, TrendingUp, Calendar } from 'lucide-svelte';

	interface Catalog {
		title: string;
		description: string;
		href: string;
		icon: typeof FileText;
		count?: string;
	}

	const catalogs: Catalog[] = [
		{
			title: 'Tipos de Movimiento Afiliatorio',
			description: 'Claves de movimientos para el Sistema Único de Autodeterminación (SUA)',
			href: `${base}/catalogos/imss/tipos-movimiento`,
			icon: Activity,
			count: '4 tipos'
		},
		{
			title: 'Tipos de Trabajador',
			description: 'Clasificación de trabajadores según su régimen laboral',
			href: `${base}/catalogos/imss/tipos-trabajador`,
			icon: Users,
			count: '4 tipos'
		},
		{
			title: 'Tipos de Incapacidad',
			description: 'Clasificación de incapacidades y subsidios del IMSS',
			href: `${base}/catalogos/imss/tipos-incapacidad`,
			icon: UserX,
			count: '3 tipos'
		},
		{
			title: 'Seguros del IMSS',
			description: 'Ramos de aseguramiento y prestaciones del Instituto',
			href: `${base}/catalogos/imss/seguros`,
			icon: Shield,
			count: '6 seguros'
		},
		{
			title: 'Tabulador de Pensiones',
			description: 'Montos mínimos de pensiones y asignaciones familiares',
			href: `${base}/catalogos/imss/pensiones`,
			icon: TrendingUp,
			count: '2024-2026'
		},
		{
			title: 'Semanas Cotizadas',
			description: 'Requisitos de semanas cotizadas para pensiones',
			href: `${base}/catalogos/imss/semanas-cotizadas`,
			icon: Calendar,
			count: '3 modalidades'
		}
	];
</script>

<svelte:head>
	<title>Catálogos IMSS - catalogmx</title>
	<meta name="description" content="Catálogos oficiales del IMSS (Instituto Mexicano del Seguro Social) para SUA y trámites patronales" />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">IMSS</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-green-100 dark:bg-green-900/30 p-3 rounded-lg">
				<Shield class="h-6 w-6 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catálogos del IMSS
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogos oficiales del Instituto Mexicano del Seguro Social para el Sistema Único de Autodeterminación (SUA)
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
				<strong>Sistema Único de Autodeterminación (SUA):</strong> Estos catálogos son utilizados por los patrones
				para presentar los movimientos afiliatoriOS, calcular cuotas obrero-patronales y cumplir con sus obligaciones
				ante el IMSS.
			</p>
			<p>
				<strong>Fuente:</strong> Instituto Mexicano del Seguro Social (IMSS) - Vigente 2024-2026
			</p>
			<p>
				<strong>Uso:</strong> Estos catálogos son fundamentales para la correcta presentación de movimientos afiliatoriOS,
				cálculo de cuotas, y gestión de trámites patronales ante el IMSS.
			</p>
		</div>
	</div>
</div>