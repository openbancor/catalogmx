<script lang="ts">
	import { CreditCard, CheckCircle2, XCircle, Info, Building2, MapPin, Hash } from 'lucide-svelte';
	import banksData from '../../../../../shared-data/banxico/banks.json';

	// State
	let clabe = $state('');
	let validationResult = $state<{
		isValid: boolean;
		bankCode: string | null;
		bankName: string | null;
		branchCode: string | null;
		accountNumber: string | null;
		checkDigit: string | null;
		checkDigitValid: boolean;
		errors: string[];
	} | null>(null);

	// CLABE Validation Logic
	const CLABE_LENGTH = 18;
	const WEIGHTS = [3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7];

	function calculateCheckDigit(clabe17: string): string {
		let weightedSum = 0;

		for (let i = 0; i < 17; i++) {
			const digit = parseInt(clabe17[i]);
			const product = digit * WEIGHTS[i];
			weightedSum += product % 10;
		}

		const checkDigit = (10 - (weightedSum % 10)) % 10;
		return checkDigit.toString();
	}

	function findBank(bankCode: string) {
		return banksData.find(bank => bank.code === bankCode);
	}

	function validateCLABE(value: string): void {
		const errors: string[] = [];
		let isValid = false;
		let bankCode: string | null = null;
		let bankName: string | null = null;
		let branchCode: string | null = null;
		let accountNumber: string | null = null;
		let checkDigit: string | null = null;
		let checkDigitValid = false;

		const clabeTrimmed = value.trim();

		// Length validation
		if (clabeTrimmed.length !== CLABE_LENGTH) {
			errors.push(`La CLABE debe tener exactamente ${CLABE_LENGTH} dígitos`);
			validationResult = {
				isValid: false,
				bankCode: null,
				bankName: null,
				branchCode: null,
				accountNumber: null,
				checkDigit: null,
				checkDigitValid: false,
				errors
			};
			return;
		}

		// Check if all digits
		if (!/^\d+$/.test(clabeTrimmed)) {
			errors.push('La CLABE debe contener solo dígitos');
			validationResult = {
				isValid: false,
				bankCode: null,
				bankName: null,
				branchCode: null,
				accountNumber: null,
				checkDigit: null,
				checkDigitValid: false,
				errors
			};
			return;
		}

		// Extract parts
		bankCode = clabeTrimmed.substring(0, 3);
		branchCode = clabeTrimmed.substring(3, 6);
		accountNumber = clabeTrimmed.substring(6, 17);
		checkDigit = clabeTrimmed.substring(17, 18);

		// Find bank
		const bank = findBank(bankCode);
		if (bank) {
			bankName = bank.name;
		} else {
			errors.push('Código de banco no reconocido');
		}

		// Validate check digit
		const expectedCheckDigit = calculateCheckDigit(clabeTrimmed.substring(0, 17));
		checkDigitValid = expectedCheckDigit === checkDigit;

		if (!checkDigitValid) {
			errors.push(`Dígito de control incorrecto (esperado: ${expectedCheckDigit}, actual: ${checkDigit})`);
		}

		isValid = errors.length === 0;

		validationResult = {
			isValid,
			bankCode,
			bankName,
			branchCode,
			accountNumber,
			checkDigit,
			checkDigitValid,
			errors
		};
	}

	// Auto-validate when CLABE changes
	$effect(() => {
		if (clabe.trim()) {
			validateCLABE(clabe);
		} else {
			validationResult = null;
		}
	});
</script>

<svelte:head>
	<title>Validador CLABE - catalogmx</title>
	<meta name="description" content="Valida CLABE (Clave Bancaria Estandarizada). Verifica formato, dígito de control y decodifica banco, plaza y cuenta." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="/validadores" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Validadores
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">CLABE</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-green-100 dark:bg-green-900/30">
				<CreditCard class="h-8 w-8 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Validador de CLABE
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Clave Bancaria Estandarizada
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
			<Info class="h-5 w-5 text-green-600 dark:text-green-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-green-900 dark:text-green-300">
				<p class="font-medium mb-1">CLABE - Clave Bancaria Estandarizada</p>
				<p>La CLABE es el número de cuenta estandarizado de 18 dígitos usado en México para transferencias electrónicas (SPEI). Incluye código de banco, plaza/sucursal y número de cuenta.</p>
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
					<CreditCard class="h-5 w-5 text-brand-500" />
					CLABE a validar
				</h2>

				<div class="space-y-5">
					<div>
						<label for="clabe" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							CLABE (18 dígitos)
						</label>
						<input
							id="clabe"
							type="text"
							bind:value={clabe}
							maxlength="18"
							class="input font-mono tabular-nums"
							placeholder="002010077777777771"
						/>
						<p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
							Debe contener exactamente 18 dígitos numéricos
						</p>
					</div>

					<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<p class="text-sm text-slate-600 dark:text-slate-400 mb-2">
							<span class="font-medium">Estructura:</span>
						</p>
						<ul class="text-xs text-slate-500 dark:text-slate-400 space-y-1 font-mono">
							<li>• 3 dígitos: Código de banco</li>
							<li>• 3 dígitos: Código de plaza/sucursal</li>
							<li>• 11 dígitos: Número de cuenta</li>
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
									<span class="font-semibold text-green-900 dark:text-green-100">CLABE Válida</span>
								{:else}
									<XCircle class="h-5 w-5 text-red-600 dark:text-red-400" />
									<span class="font-semibold text-red-900 dark:text-red-100">CLABE Inválida</span>
								{/if}
							</div>
						</div>

						<!-- Decoded Information -->
						{#if validationResult.bankCode || validationResult.branchCode || validationResult.accountNumber}
							<div class="space-y-3">
								<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2">
									Información decodificada
								</h3>

								<div class="space-y-2 text-sm">
									{#if validationResult.bankCode}
										<div class="flex items-start gap-2 py-2">
											<Building2 class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Banco</div>
												<div class="font-medium text-slate-900 dark:text-slate-100">
													{validationResult.bankName || 'Desconocido'}
												</div>
												<div class="text-xs text-slate-500 dark:text-slate-400 font-mono">
													Código: {validationResult.bankCode}
												</div>
											</div>
										</div>
									{/if}

									{#if validationResult.branchCode}
										<div class="flex items-start gap-2 py-2">
											<MapPin class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Plaza / Sucursal</div>
												<div class="font-medium text-slate-900 dark:text-slate-100 font-mono">
													{validationResult.branchCode}
												</div>
											</div>
										</div>
									{/if}

									{#if validationResult.accountNumber}
										<div class="flex items-start gap-2 py-2">
											<Hash class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Número de cuenta</div>
												<div class="font-medium text-slate-900 dark:text-slate-100 font-mono">
													{validationResult.accountNumber}
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
							<CreditCard class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Ingresa una CLABE para validar</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Este validador verifica el formato, estructura y dígito de control de la CLABE, e identifica el banco emisor.
				La existencia y estado de la cuenta solo puede verificarse con el banco correspondiente.
			</p>
		</div>
	</div>
</section>
