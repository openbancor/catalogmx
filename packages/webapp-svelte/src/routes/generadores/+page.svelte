<script lang="ts">
	import { Sparkles, CreditCard, User, Building2 } from 'lucide-svelte';

	const generators = [
		{
			id: 'rfc',
			name: 'RFC',
			description: 'Registro Federal de Contribuyentes',
			longDescription: 'Genera RFC para personas físicas y morales con homoclave calculada',
			href: '/generadores/rfc',
			icon: CreditCard,
			color: 'bg-blue-500',
			features: [
				'Persona física con homoclave',
				'Persona moral con homoclave',
				'Generación paso a paso',
				'Verificación de palabras inconvenientes'
			],
			status: 'available'
		},
		{
			id: 'curp',
			name: 'CURP',
			description: 'Clave Única de Registro de Población',
			longDescription: 'Genera CURP basado en datos personales con dígito verificador',
			href: '/generadores/curp',
			icon: User,
			color: 'bg-green-500',
			features: [
				'Generación con dígito verificador',
				'Todos los estados de México',
				'Visualización paso a paso',
				'Decodificación de CURP generada'
			],
			status: 'available'
		},
		{
			id: 'clabe',
			name: 'CLABE',
			description: 'Clave Bancaria Estandarizada',
			longDescription: 'Genera CLABE con dígito verificador para transferencias interbancarias',
			href: '/generadores/clabe',
			icon: Building2,
			color: 'bg-purple-500',
			features: [
				'Bancos habilitados para SPEI',
				'Dígito verificador calculado',
				'Generación de número aleatorio',
				'Desglose completo de la CLABE'
			],
			status: 'available'
		}
	];
</script>

<svelte:head>
	<title>Generadores - catalogmx</title>
	<meta name="description" content="Generadores de identificadores oficiales de México: RFC, CURP y CLABE. Basados en algoritmos oficiales." />
</svelte:head>

<!-- Hero -->
<section class="py-12 md:py-16 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="max-w-3xl">
			<div class="flex items-center gap-3 mb-4">
				<div class="p-3 rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
					<Sparkles class="h-8 w-8 text-indigo-600 dark:text-indigo-400" />
				</div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">
					Generadores
				</h1>
			</div>
			<p class="text-lg text-slate-600 dark:text-slate-300">
				Herramientas para generar identificadores oficiales de México como RFC, CURP y CLABE.
				Todas basadas en algoritmos oficiales del SAT, RENAPO y Banco de México.
			</p>
		</div>
	</div>
</section>

<!-- Generators Grid -->
<section class="py-12">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
			{#each generators as gen}
				{@const Icon = gen.icon}
				<div class="card p-6 relative overflow-hidden flex flex-col">
					<!-- Status badge -->
					{#if gen.status === 'coming-soon'}
						<div class="absolute top-4 right-4">
							<span class="badge badge-warning">Próximamente</span>
						</div>
					{/if}

					<!-- Header -->
					<div class="flex items-start gap-4 mb-4">
						<div class="{gen.color} p-3 rounded-lg text-white flex-shrink-0">
							<Icon class="h-6 w-6" />
						</div>
						<div class="flex-1 min-w-0">
							<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-1 truncate">
								{gen.name}
							</h2>
							<p class="text-sm text-slate-600 dark:text-slate-400">
								{gen.description}
							</p>
						</div>
					</div>

					<!-- Description -->
					<p class="text-slate-700 dark:text-slate-300 mb-4 text-sm">
						{gen.longDescription}
					</p>

					<!-- Features -->
					<div class="mb-6 flex-1">
						<ul class="space-y-1.5">
							{#each gen.features as feature}
								<li class="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
									<span class="text-brand-500 mt-0.5 flex-shrink-0">✓</span>
									<span>{feature}</span>
								</li>
							{/each}
						</ul>
					</div>

					<!-- Action button -->
					{#if gen.status === 'available'}
						<a href={gen.href} class="btn btn-primary w-full">
							<Sparkles class="h-4 w-4" />
							Abrir generador
						</a>
					{:else}
						<button class="btn btn-secondary w-full" disabled>
							Próximamente
						</button>
					{/if}
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- Info section -->
<section class="py-12 bg-slate-50 dark:bg-slate-800/50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="max-w-3xl mx-auto text-center">
			<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-4">
				Algoritmos oficiales
			</h2>
			<p class="text-slate-600 dark:text-slate-300 mb-6">
				Todos los generadores utilizan los algoritmos oficiales documentados por las autoridades:
				SAT para RFC, RENAPO para CURP, y Banco de México para CLABE. Los resultados son precisos y siguen las reglas oficiales.
			</p>
			<div class="flex flex-wrap justify-center gap-4 text-sm text-slate-500 dark:text-slate-400">
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-blue-500"></span>
					RFC con homoclave
				</span>
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-green-500"></span>
					CURP con dígito verificador
				</span>
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-purple-500"></span>
					CLABE con dígito verificador
				</span>
			</div>
		</div>
	</div>
</section>
