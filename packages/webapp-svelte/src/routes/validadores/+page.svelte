<script lang="ts">
	import { CheckCircle2, CreditCard, User, Building2, IdCard } from 'lucide-svelte';

	const validators = [
		{
			id: 'rfc',
			name: 'RFC',
			description: 'Registro Federal de Contribuyentes',
			longDescription: 'Valida RFC de personas físicas (13 caracteres) y morales (12 caracteres)',
			href: '/validadores/rfc',
			icon: Building2,
			color: 'bg-blue-500',
			features: [
				'Persona física (13 caracteres)',
				'Persona moral (12 caracteres)',
				'Verificación de dígito verificador',
				'Decodifica fecha de nacimiento'
			],
			status: 'available'
		},
		{
			id: 'curp',
			name: 'CURP',
			description: 'Clave Única de Registro de Población',
			longDescription: 'Valida CURP de 18 caracteres y decodifica información personal',
			href: '/validadores/curp',
			icon: User,
			color: 'bg-purple-500',
			features: [
				'18 caracteres',
				'Decodifica género',
				'Decodifica estado de nacimiento',
				'Decodifica fecha de nacimiento'
			],
			status: 'available'
		},
		{
			id: 'clabe',
			name: 'CLABE',
			description: 'Clave Bancaria Estandarizada',
			longDescription: 'Valida cuentas CLABE de 18 dígitos y muestra información bancaria',
			href: '/validadores/clabe',
			icon: CreditCard,
			color: 'bg-green-500',
			features: [
				'18 dígitos',
				'Identifica banco',
				'Decodifica plaza/sucursal',
				'Verificación de dígito de control'
			],
			status: 'available'
		},
		{
			id: 'nss',
			name: 'NSS / IMSS',
			description: 'Número de Seguridad Social',
			longDescription: 'Valida NSS del IMSS de 11 dígitos y decodifica información',
			href: '/validadores/nss',
			icon: IdCard,
			color: 'bg-teal-500',
			features: [
				'11 dígitos',
				'Decodifica subdelegación',
				'Decodifica año de alta',
				'Verificación de dígito de control'
			],
			status: 'available'
		}
	];
</script>

<svelte:head>
	<title>Validadores - catalogmx</title>
	<meta name="description" content="Validadores de identificadores mexicanos: RFC, CURP, CLABE, NSS. Validación en tiempo real con decodificación de información." />
</svelte:head>

<!-- Hero -->
<section class="py-12 md:py-16 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="max-w-3xl">
			<div class="flex items-center gap-3 mb-4">
				<div class="p-3 rounded-lg bg-green-100 dark:bg-green-900/30">
					<CheckCircle2 class="h-8 w-8 text-green-600 dark:text-green-400" />
				</div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">
					Validadores
				</h1>
			</div>
			<p class="text-lg text-slate-600 dark:text-slate-300">
				Herramientas para validar identificadores mexicanos en tiempo real.
				Verifica RFC, CURP, CLABE y NSS con decodificación de información.
			</p>
		</div>
	</div>
</section>

<!-- Validators Grid -->
<section class="py-12">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
			{#each validators as validator}
				{@const Icon = validator.icon}
				<div class="card p-6 relative overflow-hidden flex flex-col">
					<!-- Header -->
					<div class="flex flex-col items-center gap-4 mb-4">
						<div class="{validator.color} p-4 rounded-lg text-white">
							<Icon class="h-8 w-8" />
						</div>
						<div class="text-center">
							<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-1">
								{validator.name}
							</h2>
							<p class="text-sm text-slate-600 dark:text-slate-400">
								{validator.description}
							</p>
						</div>
					</div>

					<!-- Description -->
					<p class="text-slate-700 dark:text-slate-300 mb-4 text-sm text-center">
						{validator.longDescription}
					</p>

					<!-- Features -->
					<div class="mb-6 flex-1">
						<ul class="space-y-1.5">
							{#each validator.features as feature}
								<li class="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-400">
									<span class="text-brand-500 mt-0.5 flex-shrink-0">✓</span>
									<span>{feature}</span>
								</li>
							{/each}
						</ul>
					</div>

					<!-- Action button -->
					<a href={validator.href} class="btn btn-primary w-full">
						<CheckCircle2 class="h-4 w-4" />
						Validar {validator.name}
					</a>
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
				Validación en tiempo real
			</h2>
			<p class="text-slate-600 dark:text-slate-300 mb-6">
				Todos los validadores funcionan en tiempo real conforme escribes.
				La validación se realiza localmente en tu navegador, sin enviar datos a ningún servidor.
			</p>
			<div class="flex flex-wrap justify-center gap-4 text-sm text-slate-500 dark:text-slate-400">
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-green-500"></span>
					Validación instantánea
				</span>
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-blue-500"></span>
					100% privado (local)
				</span>
				<span class="flex items-center gap-2">
					<span class="w-2 h-2 rounded-full bg-purple-500"></span>
					Decodificación de datos
				</span>
			</div>
		</div>
	</div>
</section>
