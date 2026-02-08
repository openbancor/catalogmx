<script lang="ts">
	import { User, CheckCircle2, XCircle, Info, Calendar, MapPin, Users } from 'lucide-svelte';
	import { base } from '$app/paths';
	import { CURPValidator } from '$lib/catalogmx';
	const SITE_URL = 'https://catalogmx.openbancor.com';
	const canonicalUrl = `${SITE_URL}/validadores/curp`;
	const curpJsonLd = {
		'@context': 'https://schema.org',
		'@graph': [
			{
				'@type': 'WebPage',
				name: 'Validador CURP y Calculadora CURP',
				url: canonicalUrl,
				description:
					'Valida CURP de 18 caracteres y decodifica fecha de nacimiento, sexo y estado.'
			},
			{
				'@type': 'FAQPage',
				mainEntity: [
					{
						'@type': 'Question',
						name: '¿Cuántos caracteres tiene la CURP?',
						acceptedAnswer: {
							'@type': 'Answer',
							text: 'La CURP siempre tiene 18 caracteres.'
						}
					},
					{
						'@type': 'Question',
						name: '¿Este validador revisa el dígito verificador?',
						acceptedAnswer: {
							'@type': 'Answer',
							text: 'Sí, valida estructura, datos embebidos y dígito verificador de la CURP.'
						}
					}
				]
			}
		]
	};

	// State
	let curp = $state('');
	let validationResult = $state<{
		isValid: boolean;
		gender: string | null;
		birthDate: string | null;
		birthState: string | null;
		errors: string[];
	} | null>(null);

	const STATE_CODES: { [key: string]: string } = {
		'AS': 'Aguascalientes',
		'BC': 'Baja California',
		'BS': 'Baja California Sur',
		'CC': 'Campeche',
		'CL': 'Coahuila',
		'CM': 'Colima',
		'CS': 'Chiapas',
		'CH': 'Chihuahua',
		'DF': 'Ciudad de México',
		'DG': 'Durango',
		'GT': 'Guanajuato',
		'GR': 'Guerrero',
		'HG': 'Hidalgo',
		'JC': 'Jalisco',
		'MC': 'Estado de México',
		'MN': 'Michoacán',
		'MS': 'Morelos',
		'NT': 'Nayarit',
		'NL': 'Nuevo León',
		'OC': 'Oaxaca',
		'PL': 'Puebla',
		'QT': 'Querétaro',
		'QR': 'Quintana Roo',
		'SP': 'San Luis Potosí',
		'SL': 'Sinaloa',
		'SR': 'Sonora',
		'TC': 'Tabasco',
		'TS': 'Tamaulipas',
		'TL': 'Tlaxcala',
		'VZ': 'Veracruz',
		'YN': 'Yucatán',
		'ZS': 'Zacatecas',
		'NE': 'Nacido en el Extranjero'
	};

	function validateCURP(value: string): void {
		const errors: string[] = [];
		let gender: string | null = null;
		let birthDate: string | null = null;
		let birthState: string | null = null;

		const curpUpper = value.toUpperCase().trim();

		if (curpUpper.length !== 18) {
			errors.push('La CURP debe tener exactamente 18 caracteres');
			validationResult = { isValid: false, gender: null, birthDate: null, birthState: null, errors };
			return;
		}

		const validator = new CURPValidator(curpUpper);
		if (!validator.isValid()) {
			errors.push('El formato de la CURP no es válido');
		}

		const date = validator.getBirthDate();
		if (date) {
			birthDate = date.toISOString().slice(0, 10);
		} else {
			errors.push('La fecha de nacimiento en la CURP no es válida');
		}

		const genderChar = validator.getGender();
		if (genderChar === 'H') {
			gender = 'Hombre';
		} else if (genderChar === 'M') {
			gender = 'Mujer';
		} else {
			errors.push('El carácter de género no es válido');
		}

		const stateCode = validator.getStateCode();
		if (stateCode && STATE_CODES[stateCode]) {
			birthState = STATE_CODES[stateCode];
		} else if (stateCode) {
			birthState = stateCode;
			errors.push('El código de estado no es reconocido');
		} else {
			errors.push('El código de estado no es válido');
		}

		if (!validator.validateCheckDigit()) {
			errors.push('El dígito verificador es incorrecto');
		}

		const isValid = errors.length === 0;
		validationResult = { isValid, gender, birthDate, birthState, errors };
	}

	// Auto-validate when CURP changes
	$effect(() => {
		if (curp.trim()) {
			validateCURP(curp);
		} else {
			validationResult = null;
		}
	});
</script>

<svelte:head>
	<title>Validador CURP y Calculadora CURP - catalogmx</title>
	<meta
		name="description"
		content="Valida CURP en línea con reglas RENAPO. Verifica formato de 18 caracteres, dígito verificador y decodifica fecha, sexo y estado."
	/>
	<meta
		name="keywords"
		content="calculadora CURP, validador CURP, validar CURP, CURP 18 caracteres, dígito verificador CURP"
	/>
	<meta name="robots" content="index, follow, max-image-preview:large" />
	<link rel="canonical" href={canonicalUrl} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="Validador CURP y Calculadora CURP - catalogmx" />
	<meta property="og:description" content="Valida CURP y decodifica fecha de nacimiento, sexo y estado." />
	<meta property="og:url" content={canonicalUrl} />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Validador CURP - catalogmx" />
	<meta name="twitter:description" content="Calculadora y validador CURP con reglas RENAPO." />
	{@html `<script type="application/ld+json">${JSON.stringify(curpJsonLd)}</script>`}
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/validadores" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Validadores
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">CURP</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-purple-100 dark:bg-purple-900/30">
				<User class="h-8 w-8 text-purple-600 dark:text-purple-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Validador de CURP
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Clave Única de Registro de Población
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
			<Info class="h-5 w-5 text-purple-600 dark:text-purple-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-purple-900 dark:text-purple-300">
				<p class="font-medium mb-1">CURP - Clave Única de Registro de Población</p>
				<p>La CURP es un código único de 18 caracteres que identifica a cada persona en México. Contiene información sobre nombre, fecha de nacimiento, género y lugar de nacimiento.</p>
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
					<User class="h-5 w-5 text-brand-500" />
					CURP a validar
				</h2>

				<div class="space-y-5">
					<div>
						<label for="curp" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							CURP (18 caracteres)
						</label>
						<input
							id="curp"
							type="text"
							bind:value={curp}
							maxlength="18"
							class="input uppercase font-mono"
							placeholder="VECJ880326HDFLRN09"
						/>
						<p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
							Debe contener exactamente 18 caracteres
						</p>
					</div>

					<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<p class="text-sm text-slate-600 dark:text-slate-400 mb-2">
							<span class="font-medium">Formato:</span>
						</p>
						<ul class="text-xs text-slate-500 dark:text-slate-400 space-y-1 font-mono">
							<li>• 4 letras: Iniciales del nombre</li>
							<li>• 6 dígitos: Fecha de nacimiento (AAMMDD)</li>
							<li>• 1 letra: Género (H/M)</li>
							<li>• 2 letras: Estado de nacimiento</li>
							<li>• 3 consonantes: Del nombre</li>
							<li>• 2 caracteres: Homoclave</li>
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
									<span class="font-semibold text-green-900 dark:text-green-100">CURP Válida</span>
								{:else}
									<XCircle class="h-5 w-5 text-red-600 dark:text-red-400" />
									<span class="font-semibold text-red-900 dark:text-red-100">CURP Inválida</span>
								{/if}
							</div>
						</div>

						<!-- Decoded Information -->
						{#if validationResult.birthDate || validationResult.gender || validationResult.birthState}
							<div class="space-y-3">
								<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2">
									Información decodificada
								</h3>

								<div class="space-y-2 text-sm">
									{#if validationResult.birthDate}
										<div class="flex items-start gap-2 py-2">
											<Calendar class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Fecha de nacimiento</div>
												<div class="font-medium text-slate-900 dark:text-slate-100">{validationResult.birthDate}</div>
											</div>
										</div>
									{/if}

									{#if validationResult.gender}
										<div class="flex items-start gap-2 py-2">
											<Users class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Género</div>
												<div class="font-medium text-slate-900 dark:text-slate-100">{validationResult.gender}</div>
											</div>
										</div>
									{/if}

									{#if validationResult.birthState}
										<div class="flex items-start gap-2 py-2">
											<MapPin class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Estado de nacimiento</div>
												<div class="font-medium text-slate-900 dark:text-slate-100">{validationResult.birthState}</div>
											</div>
										</div>
									{/if}
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
							<User class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Ingresa una CURP para validar</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Este validador verifica el formato y estructura de la CURP, y decodifica la información contenida.
				La existencia real de la CURP solo puede verificarse en el sistema oficial de RENAPO.
			</p>
		</div>

		<div class="mt-6 p-4 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
			<h2 class="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-2">
				Herramientas relacionadas
			</h2>
			<p class="text-xs text-slate-600 dark:text-slate-400">
				Para generar una CURP de prueba usa el
				<a href="{base}/generadores/curp" class="text-brand-600 dark:text-brand-400 hover:underline">
					generador de CURP
				</a>.
				También puedes validar
				<a href="{base}/validadores/rfc" class="text-brand-600 dark:text-brand-400 hover:underline">
					RFC
				</a>
				y
				<a href="{base}/validadores/clabe" class="text-brand-600 dark:text-brand-400 hover:underline">
					CLABE
				</a>
				desde la misma suite.
			</p>
		</div>
	</div>
</section>
