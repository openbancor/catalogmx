<script lang="ts">
	import { IdCard, CheckCircle2, XCircle, Info, Building2, Calendar, Hash } from 'lucide-svelte';
	import { base } from '$app/paths';

	// State
	let nss = $state('');
	let validationResult = $state<{
		isValid: boolean;
		subdelegation: string | null;
		registrationYear: string | null;
		birthYear: string | null;
		sequential: string | null;
		checkDigit: string | null;
		checkDigitValid: boolean;
		errors: string[];
	} | null>(null);

	// NSS Validation Logic
	const NSS_LENGTH = 11;

	function calculateCheckDigit(nss10: string): string {
		let total = 0;

		// Process from right to left
		for (let i = 0; i < 10; i++) {
			let digit = parseInt(nss10[9 - i]);

			// Alternate between multiplying by 2 and 1 (starting with 2 for rightmost)
			if (i % 2 === 0) {
				digit = digit * 2;
				// If result > 9, sum its digits
				if (digit > 9) {
					digit = Math.floor(digit / 10) + (digit % 10);
				}
			}

			total += digit;
		}

		// Calculate check digit
		const checkDigit = (10 - (total % 10)) % 10;
		return checkDigit.toString();
	}

	function validateNSS(value: string): void {
		const errors: string[] = [];
		let isValid = false;
		let subdelegation: string | null = null;
		let registrationYear: string | null = null;
		let birthYear: string | null = null;
		let sequential: string | null = null;
		let checkDigit: string | null = null;
		let checkDigitValid = false;

		const nssTrimmed = value.trim();

		// Length validation
		if (nssTrimmed.length !== NSS_LENGTH) {
			errors.push(`El NSS debe tener exactamente ${NSS_LENGTH} dígitos`);
			validationResult = {
				isValid: false,
				subdelegation: null,
				registrationYear: null,
				birthYear: null,
				sequential: null,
				checkDigit: null,
				checkDigitValid: false,
				errors
			};
			return;
		}

		// Check if all digits
		if (!/^\d+$/.test(nssTrimmed)) {
			errors.push('El NSS debe contener solo dígitos');
			validationResult = {
				isValid: false,
				subdelegation: null,
				registrationYear: null,
				birthYear: null,
				sequential: null,
				checkDigit: null,
				checkDigitValid: false,
				errors
			};
			return;
		}

		// Extract parts
		subdelegation = nssTrimmed.substring(0, 2);
		registrationYear = nssTrimmed.substring(2, 4);
		birthYear = nssTrimmed.substring(4, 6);
		sequential = nssTrimmed.substring(6, 10);
		checkDigit = nssTrimmed.substring(10, 11);

		// Validate check digit
		const expectedCheckDigit = calculateCheckDigit(nssTrimmed.substring(0, 10));
		checkDigitValid = expectedCheckDigit === checkDigit;

		if (!checkDigitValid) {
			errors.push(`Dígito de control incorrecto (esperado: ${expectedCheckDigit}, actual: ${checkDigit})`);
		}

		isValid = errors.length === 0;

		validationResult = {
			isValid,
			subdelegation,
			registrationYear,
			birthYear,
			sequential,
			checkDigit,
			checkDigitValid,
			errors
		};
	}

	// Auto-validate when NSS changes
	$effect(() => {
		if (nss.trim()) {
			validateNSS(nss);
		} else {
			validationResult = null;
		}
	});
</script>

<svelte:head>
	<title>Validador NSS - catalogmx</title>
	<meta name="description" content="Valida NSS (Número de Seguridad Social del IMSS). Verifica formato, dígito de control y decodifica subdelegación y años." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/validadores" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Validadores
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">NSS</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-teal-100 dark:bg-teal-900/30">
				<IdCard class="h-8 w-8 text-teal-600 dark:text-teal-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Validador de NSS
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Número de Seguridad Social del IMSS
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-teal-50 dark:bg-teal-900/20 rounded-lg border border-teal-200 dark:border-teal-800">
			<Info class="h-5 w-5 text-teal-600 dark:text-teal-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-teal-900 dark:text-teal-300">
				<p class="font-medium mb-1">NSS - Número de Seguridad Social</p>
				<p>El NSS es el número único de 11 dígitos emitido por el IMSS para identificar a cada trabajador afiliado al seguro social en México.</p>
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
					<IdCard class="h-5 w-5 text-brand-500" />
					NSS a validar
				</h2>

				<div class="space-y-5">
					<div>
						<label for="nss" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							NSS (11 dígitos)
						</label>
						<input
							id="nss"
							type="text"
							bind:value={nss}
							maxlength="11"
							class="input font-mono tabular-nums"
							placeholder="12345678903"
						/>
						<p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
							Debe contener exactamente 11 dígitos numéricos
						</p>
					</div>

					<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<p class="text-sm text-slate-600 dark:text-slate-400 mb-2">
							<span class="font-medium">Estructura:</span>
						</p>
						<ul class="text-xs text-slate-500 dark:text-slate-400 space-y-1 font-mono">
							<li>• 2 dígitos: Subdelegación IMSS</li>
							<li>• 2 dígitos: Año de alta (YY)</li>
							<li>• 2 dígitos: Año de nacimiento (YY)</li>
							<li>• 4 dígitos: Número secuencial</li>
							<li>• 1 dígito: Dígito de control</li>
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
									<span class="font-semibold text-green-900 dark:text-green-100">NSS Válido</span>
								{:else}
									<XCircle class="h-5 w-5 text-red-600 dark:text-red-400" />
									<span class="font-semibold text-red-900 dark:text-red-100">NSS Inválido</span>
								{/if}
							</div>
						</div>

						<!-- Decoded Information -->
						{#if validationResult.subdelegation || validationResult.registrationYear || validationResult.birthYear}
							<div class="space-y-3">
								<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2">
									Información decodificada
								</h3>

								<div class="space-y-2 text-sm">
									{#if validationResult.subdelegation}
										<div class="flex items-start gap-2 py-2">
											<Building2 class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Subdelegación IMSS</div>
												<div class="font-medium text-slate-900 dark:text-slate-100 font-mono">
													{validationResult.subdelegation}
												</div>
											</div>
										</div>
									{/if}

									{#if validationResult.registrationYear}
										<div class="flex items-start gap-2 py-2">
											<Calendar class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Año de alta</div>
												<div class="font-medium text-slate-900 dark:text-slate-100 font-mono">
													{validationResult.registrationYear}
												</div>
												<div class="text-xs text-slate-500 dark:text-slate-400">
													(19{validationResult.registrationYear} o 20{validationResult.registrationYear})
												</div>
											</div>
										</div>
									{/if}

									{#if validationResult.birthYear}
										<div class="flex items-start gap-2 py-2">
											<Calendar class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Año de nacimiento</div>
												<div class="font-medium text-slate-900 dark:text-slate-100 font-mono">
													{validationResult.birthYear}
												</div>
												<div class="text-xs text-slate-500 dark:text-slate-400">
													(19{validationResult.birthYear} o 20{validationResult.birthYear})
												</div>
											</div>
										</div>
									{/if}

									{#if validationResult.sequential}
										<div class="flex items-start gap-2 py-2">
											<Hash class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Número secuencial</div>
												<div class="font-medium text-slate-900 dark:text-slate-100 font-mono">
													{validationResult.sequential}
												</div>
											</div>
										</div>
									{/if}

									{#if validationResult.checkDigit}
										<div class="flex items-start gap-2 py-2">
											<CheckCircle2 class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Dígito de control</div>
												<div class="font-medium {validationResult.checkDigitValid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'} font-mono">
													{validationResult.checkDigit} {validationResult.checkDigitValid ? '✓' : '✗'}
												</div>
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
							<IdCard class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Ingresa un NSS para validar</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Este validador verifica el formato, estructura y dígito de control del NSS usando el algoritmo de Luhn modificado.
				El estado de afiliación y vigencia solo puede verificarse con el IMSS.
			</p>
		</div>
	</div>
</section>
