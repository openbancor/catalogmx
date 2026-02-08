<script lang="ts">
	import { Building2, CheckCircle2, XCircle, Info, Calendar, User } from 'lucide-svelte';
	import { base } from '$app/paths';
	import { RFCValidator } from '$lib/catalogmx';
	const SITE_URL = 'https://catalogmx.openbancor.com';
	const canonicalUrl = `${SITE_URL}/validadores/rfc`;
	const rfcJsonLd = {
		'@context': 'https://schema.org',
		'@graph': [
			{
				'@type': 'WebPage',
				name: 'Validador RFC y Calculadora RFC',
				url: canonicalUrl,
				description:
					'Valida RFC de persona física y moral, verifica dígito verificador y decodifica tipo y fecha.'
			},
			{
				'@type': 'FAQPage',
				mainEntity: [
					{
						'@type': 'Question',
						name: '¿Cuántos caracteres tiene un RFC?',
						acceptedAnswer: {
							'@type': 'Answer',
							text: 'Persona moral: 12 caracteres. Persona física: 13 caracteres.'
						}
					},
					{
						'@type': 'Question',
						name: '¿Este validador revisa el dígito verificador?',
						acceptedAnswer: {
							'@type': 'Answer',
							text: 'Sí, valida estructura, homoclave, fecha y dígito verificador del RFC.'
						}
					}
				]
			}
		]
	};

	// State
	let rfc = $state('');
	let validationResult = $state<{
		isValid: boolean;
		tipo: string;
		fecha: string | null;
		errors: string[];
		checksumValid: boolean;
	} | null>(null);

	function validateRFC(value: string): void {
		const errors: string[] = [];
		const validator = new RFCValidator(value);
		const details = validator.getValidationDetails(true);

		if (!details.generalRegex) {
			errors.push('El formato del RFC no es válido');
		}
		if (details.generalRegex && !details.dateFormat) {
			errors.push('La fecha del RFC no es válida');
		}
		if (details.generalRegex && !details.homoclave) {
			errors.push('La homoclave del RFC no es válida');
		}
		if (details.generalRegex && !details.checksum) {
			errors.push('El dígito verificador es incorrecto');
		}

		const type = validator.detectType();
		const tipo =
			type === 'fisica'
				? 'Persona Física'
				: type === 'moral'
					? 'Persona Moral'
					: type === 'generico'
						? 'Genérico'
						: 'RFC Inválido';

		const fecha = validator.getDate()?.toISOString().slice(0, 10) ?? null;
		const checksumValid = details.checksum ?? false;
		const isValid = validator.validate(true);

		validationResult = { isValid, tipo, fecha, errors, checksumValid };
	}

	// Auto-validate when RFC changes
	$effect(() => {
		if (rfc.trim()) {
			validateRFC(rfc);
		} else {
			validationResult = null;
		}
	});
</script>

<svelte:head>
	<title>Validador RFC y Calculadora RFC SAT - catalogmx</title>
	<meta
		name="description"
		content="Valida RFC de personas físicas y morales. Calcula y verifica formato, homoclave, fecha y dígito verificador con reglas SAT."
	/>
	<meta
		name="keywords"
		content="calculadora RFC, validador RFC, validar RFC SAT, RFC persona física, RFC persona moral, dígito verificador RFC"
	/>
	<meta name="robots" content="index, follow, max-image-preview:large" />
	<link rel="canonical" href={canonicalUrl} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="Validador RFC y Calculadora RFC SAT - catalogmx" />
	<meta property="og:description" content="Valida RFC y revisa homoclave, tipo de contribuyente y dígito verificador." />
	<meta property="og:url" content={canonicalUrl} />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Validador RFC - catalogmx" />
	<meta name="twitter:description" content="Calculadora y validador RFC para persona física y moral." />
	{@html `<script type="application/ld+json">${JSON.stringify(rfcJsonLd)}</script>`}
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/validadores" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Validadores
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">RFC</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-blue-100 dark:bg-blue-900/30">
				<Building2 class="h-8 w-8 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Validador de RFC
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Registro Federal de Contribuyentes
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
			<Info class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-blue-900 dark:text-blue-300">
				<p class="font-medium mb-1">RFC - Registro Federal de Contribuyentes</p>
				<p>El RFC es la clave única de identificación fiscal en México. Persona física: 13 caracteres. Persona moral: 12 caracteres.</p>
			</div>
		</div>
	</div>
</section>

<!-- Validator -->
<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Input Form -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<Building2 class="h-5 w-5 text-brand-500" />
					RFC a validar
				</h2>

				<div class="space-y-5">
					<div>
						<label for="rfc" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							RFC (12 o 13 caracteres)
						</label>
						<input
							id="rfc"
							type="text"
							bind:value={rfc}
							maxlength="13"
							class="input uppercase font-mono"
							placeholder="VECJ880326XXX"
						/>
						<p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
							12 caracteres = Persona Moral | 13 caracteres = Persona Física
						</p>
					</div>

					<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<p class="text-sm text-slate-600 dark:text-slate-400 mb-2">
							<span class="font-medium">Ejemplos válidos:</span>
						</p>
						<ul class="text-xs text-slate-500 dark:text-slate-400 space-y-1 font-mono">
							<li>• VECJ880326XXX (Persona Física)</li>
							<li>• ABC123456XXX (Persona Moral)</li>
							<li>• XAXX010101000 (Genérico Nacional)</li>
						</ul>
					</div>
				</div>
			</div>

			<!-- Results -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<CheckCircle2 class="h-5 w-5 text-green-500" />
					Resultado de validación
				</h2>

				{#if validationResult}
					<div class="space-y-4">
						<!-- Validation Status Badge -->
						<div class="p-4 rounded-lg border {validationResult.isValid ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'}">
							<div class="flex items-center gap-2 mb-2">
								{#if validationResult.isValid}
									<CheckCircle2 class="h-5 w-5 text-green-600 dark:text-green-400" />
									<span class="font-semibold text-green-900 dark:text-green-100">RFC Válido</span>
								{:else}
									<XCircle class="h-5 w-5 text-red-600 dark:text-red-400" />
									<span class="font-semibold text-red-900 dark:text-red-100">RFC Inválido</span>
								{/if}
							</div>
						</div>

						<!-- Decoded Information -->
						{#if validationResult.isValid || validationResult.tipo !== 'RFC Inválido'}
							<div class="space-y-3">
								<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2">
									Información decodificada
								</h3>

								<div class="space-y-2 text-sm">
									<div class="flex items-start gap-2 py-2">
										<User class="h-4 w-4 text-slate-400 mt-0.5" />
										<div class="flex-1">
											<div class="text-slate-600 dark:text-slate-400">Tipo</div>
											<div class="font-medium text-slate-900 dark:text-slate-100">{validationResult.tipo}</div>
										</div>
									</div>

									{#if validationResult.fecha}
										<div class="flex items-start gap-2 py-2">
											<Calendar class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Fecha</div>
												<div class="font-medium text-slate-900 dark:text-slate-100">{validationResult.fecha}</div>
												<div class="text-xs text-slate-500 dark:text-slate-400">
													{validationResult.tipo === 'Persona Física' ? 'Fecha de nacimiento' : 'Fecha de constitución'}
												</div>
											</div>
										</div>
									{/if}

									<div class="flex items-start gap-2 py-2">
										<CheckCircle2 class="h-4 w-4 text-slate-400 mt-0.5" />
										<div class="flex-1">
											<div class="text-slate-600 dark:text-slate-400">Dígito verificador</div>
											<div class="font-medium {validationResult.checksumValid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}">
												{validationResult.checksumValid ? 'Válido ✓' : 'Inválido ✗'}
											</div>
										</div>
									</div>
								</div>
							</div>
						{/if}

						<!-- Errors -->
						{#if validationResult.errors.length > 0}
							<div class="space-y-2">
								<h3 class="text-sm font-semibold text-red-700 dark:text-red-300">
									Errores encontrados:
								</h3>
								<ul class="space-y-1">
									{#each validationResult.errors as error}
										<li class="text-sm text-red-600 dark:text-red-400 flex items-start gap-2">
											<span class="text-red-500 mt-0.5">•</span>
											<span>{error}</span>
										</li>
									{/each}
								</ul>
							</div>
						{/if}
					</div>
				{:else}
					<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
						<div class="text-center">
							<Building2 class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Ingresa un RFC para validar</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Este validador verifica el formato, estructura y dígito verificador del RFC.
				La existencia real del RFC en el SAT solo puede verificarse en el sistema oficial del SAT.
			</p>
		</div>

		<div class="mt-6 p-4 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
			<h2 class="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-2">
				Herramientas relacionadas
			</h2>
			<p class="text-xs text-slate-600 dark:text-slate-400">
				Si buscabas calculadora de RFC para generar claves de prueba, usa el
				<a href="{base}/generadores/rfc" class="text-brand-600 dark:text-brand-400 hover:underline">
					generador de RFC
				</a>.
				También puedes validar
				<a href="{base}/validadores/curp" class="text-brand-600 dark:text-brand-400 hover:underline">
					CURP
				</a>
				y
				<a href="{base}/validadores/clabe" class="text-brand-600 dark:text-brand-400 hover:underline">
					CLABE
				</a>
				en línea.
			</p>
		</div>
	</div>
</section>
