<script lang="ts">
	import { CreditCard, Info, User, Building2, AlertCircle, CheckCircle2 } from 'lucide-svelte';
	import { base } from '$app/paths';
	import { generateRfcPersonaFisica, generateRfcPersonaMoral, RFCValidator } from '$lib/catalogmx';
	const SITE_URL = 'https://catalogmx.openbancor.com';
	const canonicalUrl = `${SITE_URL}/generadores/rfc`;
	const rfcGeneratorJsonLd = {
		'@context': 'https://schema.org',
		'@type': 'WebPage',
		name: 'Calculadora RFC SAT',
		url: canonicalUrl,
		description:
			'Genera RFC para persona física o moral con homoclave y dígito verificador usando reglas SAT.',
		mainEntity: {
			'@type': 'SoftwareApplication',
			name: 'Generador RFC catalogmx',
			applicationCategory: 'FinanceApplication',
			operatingSystem: 'Web'
		}
	};

	type PersonType = 'fisica' | 'moral';

	// State
	let personType = $state<PersonType>('fisica');

	// Persona Física
	let nombre = $state('');
	let apellidoPaterno = $state('');
	let apellidoMaterno = $state('');
	let fechaNacimiento = $state('');

	// Persona Moral
	let razonSocial = $state('');
	let fechaConstitucion = $state('');

	let rfcGenerado = $state('');
	let pasos = $state<string[]>([]);

	function formatDate(date: Date | null): string {
		if (!date) return 'Fecha no disponible';
		const dd = date.getDate().toString().padStart(2, '0');
		const mm = (date.getMonth() + 1).toString().padStart(2, '0');
		const yyyy = date.getFullYear();
		return `${dd}/${mm}/${yyyy}`;
	}

	function getTypeLabel(type: 'fisica' | 'moral' | 'generico' | 'invalido'): string {
		switch (type) {
			case 'fisica':
				return 'Persona Física';
			case 'moral':
				return 'Persona Moral';
			case 'generico':
				return 'RFC Genérico';
			default:
				return 'RFC Inválido';
		}
	}

	function generateRFC(): void {
		pasos = [];
		rfcGenerado = '';

		try {
			if (personType === 'fisica') {
				if (!nombre || !apellidoPaterno || !fechaNacimiento) {
					pasos.push('❌ Por favor completa todos los campos requeridos');
					return;
				}

				rfcGenerado = generateRfcPersonaFisica({
					nombre,
					apellidoPaterno,
					apellidoMaterno,
					fechaNacimiento
				});
			} else {
				if (!razonSocial || !fechaConstitucion) {
					pasos.push('❌ Por favor completa todos los campos requeridos');
					return;
				}

				rfcGenerado = generateRfcPersonaMoral({
					razonSocial,
					fechaConstitucion
				});
			}

			const validator = new RFCValidator(rfcGenerado);
			const details = validator.getValidationDetails();
			const type = validator.detectType();
			const date = validator.getDate();

			pasos.push(`✅ RFC generado: ${rfcGenerado}`);
			pasos.push(`Tipo: ${getTypeLabel(type)}`);
			pasos.push(`Fecha en RFC: ${formatDate(date)}`);
			pasos.push(`Formato: ${details.generalRegex ? 'OK' : 'Error'}`);
			pasos.push(`Fecha válida: ${details.dateFormat ? 'OK' : 'Error'}`);
			pasos.push(`Homoclave: ${details.homoclave ? 'OK' : 'Error'}`);
			if ('checksum' in details) {
				pasos.push(`Dígito verificador: ${details.checksum ? 'OK' : 'Error'}`);
			}
		} catch (error) {
			if (error instanceof Error) {
				pasos.push(`❌ Error: ${error.message}`);
			}
		}
	}

	// Track previous values to avoid infinite loops
	let prevInputs = $state('');

	// Auto-generate when inputs change (with deduplication)
	$effect(() => {
		const currentInputs =
			personType === 'fisica'
				? `${personType}|${nombre}|${apellidoPaterno}|${apellidoMaterno}|${fechaNacimiento}`
				: `${personType}|${razonSocial}|${fechaConstitucion}`;

		// Only regenerate if inputs actually changed
		if (currentInputs !== prevInputs) {
			prevInputs = currentInputs;

			if (personType === 'fisica') {
				if (nombre && apellidoPaterno && fechaNacimiento) {
					generateRFC();
				}
			} else {
				if (razonSocial && fechaConstitucion) {
					generateRFC();
				}
			}
		}
	});
</script>

<svelte:head>
	<title>Calculadora RFC SAT | Generador RFC - catalogmx</title>
	<meta
		name="description"
		content="Calculadora RFC para persona física y moral. Genera RFC con homoclave y dígito verificador con algoritmo oficial del SAT."
	/>
	<meta
		name="keywords"
		content="calculadora RFC, generador RFC, RFC SAT, RFC persona física, RFC persona moral, homoclave RFC"
	/>
	<meta name="robots" content="index, follow, max-image-preview:large" />
	<link rel="canonical" href={canonicalUrl} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="Calculadora RFC SAT | Generador RFC - catalogmx" />
	<meta property="og:description" content="Genera RFC de prueba con homoclave y dígito verificador." />
	<meta property="og:url" content={canonicalUrl} />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Calculadora RFC SAT - catalogmx" />
	<meta name="twitter:description" content="Generador RFC para persona física y moral." />
	{@html `<script type="application/ld+json">${JSON.stringify(rfcGeneratorJsonLd)}</script>`}
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/generadores" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Generadores
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">RFC</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-blue-100 dark:bg-blue-900/30">
				<CreditCard class="h-8 w-8 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Generador RFC
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Genera RFC con homoclave según algoritmo oficial del SAT
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
			<Info class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-blue-900 dark:text-blue-300">
				<p class="font-medium mb-1">Algoritmo oficial SAT</p>
				<p>Generación de RFC con homoclave calculada y dígito verificador. Incluye validación de palabras inconvenientes.</p>
			</div>
		</div>
	</div>
</section>

<!-- Generator -->
<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Type selector -->
		<div class="mb-6">
			<div class="inline-flex rounded-lg border border-slate-200 dark:border-slate-700 p-1 bg-slate-50 dark:bg-slate-800/50">
				<button
					class="px-4 py-2 rounded-md text-sm font-medium transition-colors {personType === 'fisica' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
					onclick={() => {
						personType = 'fisica';
						rfcGenerado = '';
						pasos = [];
					}}
				>
					<User class="h-4 w-4 inline mr-2" />
					Persona Física
				</button>
				<button
					class="px-4 py-2 rounded-md text-sm font-medium transition-colors {personType === 'moral' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
					onclick={() => {
						personType = 'moral';
						rfcGenerado = '';
						pasos = [];
					}}
				>
					<Building2 class="h-4 w-4 inline mr-2" />
					Persona Moral
				</button>
			</div>
		</div>

		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Input Form -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					{#if personType === 'fisica'}
						<User class="h-5 w-5 text-brand-500" />
						Datos personales
					{:else}
						<Building2 class="h-5 w-5 text-brand-500" />
						Datos de la empresa
					{/if}
				</h2>

				{#if personType === 'fisica'}
					<div class="space-y-5">
						<div>
							<label for="nombre" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Nombre(s) *
							</label>
							<input
								id="nombre"
								type="text"
								bind:value={nombre}
								class="input"
								placeholder="Juan Carlos"
							/>
						</div>

						<div>
							<label for="paterno" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Apellido Paterno *
							</label>
							<input
								id="paterno"
								type="text"
								bind:value={apellidoPaterno}
								class="input"
								placeholder="García"
							/>
						</div>

						<div>
							<label for="materno" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Apellido Materno
							</label>
							<input
								id="materno"
								type="text"
								bind:value={apellidoMaterno}
								class="input"
								placeholder="López"
							/>
						</div>

						<div>
							<label for="fecha" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Fecha de Nacimiento *
							</label>
							<input
								id="fecha"
								type="date"
								bind:value={fechaNacimiento}
								class="input"
							/>
						</div>
					</div>
				{:else}
					<div class="space-y-5">
						<div>
							<label for="razon" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Razón Social *
							</label>
							<input
								id="razon"
								type="text"
								bind:value={razonSocial}
								class="input"
								placeholder="Comercializadora de Productos del Norte S.A. de C.V."
							/>
						</div>

						<div>
							<label for="fechaConst" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Fecha de Constitución *
							</label>
							<input
								id="fechaConst"
								type="date"
								bind:value={fechaConstitucion}
								class="input"
							/>
						</div>

						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
							<div class="flex gap-2 text-sm text-slate-600 dark:text-slate-400">
								<AlertCircle class="h-4 w-4 flex-shrink-0 mt-0.5" />
								<p>
									Se eliminarán automáticamente las palabras reservadas como S.A., DE, C.V., etc.
								</p>
							</div>
						</div>
					</div>
				{/if}
			</div>

			<!-- Results -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<CheckCircle2 class="h-5 w-5 text-green-500" />
					RFC Generado
				</h2>

				{#if rfcGenerado}
					<div class="space-y-6">
						<!-- RFC Result -->
						<div class="p-6 bg-gradient-to-br from-brand-50 to-brand-100 dark:from-brand-900/20 dark:to-brand-800/20 rounded-lg border border-brand-200 dark:border-brand-800">
							<div class="text-sm font-medium text-brand-700 dark:text-brand-300 mb-2">
								RFC Generado
							</div>
							<div class="text-4xl font-bold text-brand-900 dark:text-brand-100 tracking-wider font-mono">
								{rfcGenerado}
							</div>
						</div>

						<!-- Steps -->
						<div>
							<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
								Pasos de generación
							</h3>
							<div class="space-y-2">
								{#each pasos as paso}
									<div class="text-sm p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg font-mono">
										{paso}
									</div>
								{/each}
							</div>
						</div>

						<!-- Copy button -->
						<button
							class="btn btn-primary w-full"
							onclick={() => {
								navigator.clipboard.writeText(rfcGenerado);
							}}
						>
							Copiar RFC
						</button>
					</div>
				{:else}
					<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
						<div class="text-center">
							<CreditCard class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Completa los campos para generar el RFC</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Este generador utiliza el algoritmo oficial del SAT para calcular el RFC.
				El RFC generado incluye la homoclave y dígito verificador calculados. Para obtener el RFC oficial,
				debes tramitarlo ante el SAT con documentación válida.
			</p>
		</div>

		<div class="mt-6 p-4 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
			<h2 class="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-2">
				Validación y recursos
			</h2>
			<p class="text-xs text-slate-600 dark:text-slate-400">
				Verifica el RFC generado en el
				<a href="{base}/validadores/rfc" class="text-brand-600 dark:text-brand-400 hover:underline">
					validador de RFC
				</a>
				y complementa tus pruebas con
				<a href="{base}/generadores/curp" class="text-brand-600 dark:text-brand-400 hover:underline">
					generador de CURP
				</a>
				y
				<a href="{base}/generadores/clabe" class="text-brand-600 dark:text-brand-400 hover:underline">
					generador de CLABE
				</a>.
			</p>
		</div>
	</div>
</section>
